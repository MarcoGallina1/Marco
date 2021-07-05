# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from itertools import groupby

from odoo import models


class WizardVatDiary(models.TransientModel):
    _inherit = 'wizard.vat.diary'

    def _get_coupon_reconcile_values(self, coupon_reconcile_docs, coupon_reconcile):     
        """Obtiene los datos de la liquidación para el 
        encabezado genérico del subdiario 

        :param coupon_reconcile_docs: Retenciones y facturas de la liquidación
        :type coupon_reconcile_docs: list
        :param coupon_reconcile: Liquidación de la que obtener los datos
        :type coupon_reconcile: credit.card.coupon.reconcile()
        :return: Diccionario con los valores de la liquidación para el subdiario
        :rtype: dict
        """        
        coupon_reconcile_invoice = next(filter(lambda crd: crd._name == 'account.move', coupon_reconcile_docs))
        return {
            0: coupon_reconcile.acreditation_date.strftime('%d/%m/%Y'),
            1: coupon_reconcile.partner_id.name,
            2: coupon_reconcile.partner_id.vat or '',
            3: coupon_reconcile.partner_id.property_account_position_id.name or '',
            4: coupon_reconcile_invoice.voucher_type_id.name or '',
            5: coupon_reconcile.name,
            6: coupon_reconcile_invoice.jurisdiction_id.name or coupon_reconcile_invoice.partner_id.state_id.name or ''
        }

    def get_coupon_reconcile_details(self, taxes_position, coupon_reconcile_documents, size_header, last_position):
        """Obtengo el detalle de las filas del subdiario que corresponden a liquidaciones

        :param taxes_position: Diccionario con las posiciones de los 
        impuestos en el subdiario
        :type taxes_position: dict
        :param coupon_reconcile_documents: Retenciones y facturas de liquidaciones 
        :type coupon_reconcile_documents: list
        :param size_header: Tamaño del encabezado genérico del subdiario
        :type size_header: int
        :param last_position: Última posición de los impuestos en el subdiario
        :type last_position: int
        :return: Lista con todas las filas de liquidaciones
        :rtype: list
        """        
        res = []
        # Agrupo las retenciones y facturas por liquidación
        coupon_reconcile_documents.sort(key=lambda crd: crd.credit_card_coupon_reconcile_ids[0].id)
        for k, g in groupby(coupon_reconcile_documents, key=lambda crd: crd.credit_card_coupon_reconcile_ids[0].id):
            coupon_reconcile = self.env['credit.card.coupon.reconcile'].browse(k)
            coupon_reconcile_docs = list(g)
            coupon_reconcile_values = self._get_coupon_reconcile_values(coupon_reconcile_docs, coupon_reconcile)
            coupon_reconcile_total = 0
            for doc in coupon_reconcile_docs:
                doc.with_context(separate_not_taxable_from_exempt=self.separate_not_taxable_from_exempt).update_vat_diary_values(taxes_position, coupon_reconcile_values, size_header)
                coupon_reconcile_total += doc.get_vat_diary_total()
            if self.separate_not_taxable_from_exempt:
                coupon_reconcile_values[last_position + size_header + 2] = coupon_reconcile_total
            else:
                coupon_reconcile_values[last_position + size_header + 1] = coupon_reconcile_total
            res.append(coupon_reconcile_values)
        return res

    def get_details_values(self, taxes_position, invoices, retentions=None):
        """ Heredo el método que obtiene los datos de las filas del subdiario para
        agrupar las retenciones y facturas según liquidación de cupones """  
        coupon_reconcile_invoices = invoices.filtered(lambda inv: inv.credit_card_coupon_reconcile_ids)
        # Al método del padre paso las retenciones y facturas que no sean de liquidaciones 
        # para que obtenga sus datos normalmente
        invoices = invoices - coupon_reconcile_invoices
        if retentions:
            coupon_reconcile_retentions = retentions.filtered(lambda ret: ret.credit_card_coupon_reconcile_ids)
            retentions = retentions - coupon_reconcile_retentions
        res = super().get_details_values(taxes_position, invoices, retentions)

        # Paso los recorset a lista para tener un iterable con todos los datos
        coupon_reconcile_documents = list(coupon_reconcile_invoices)
        if retentions:
            coupon_reconcile_documents.extend(list(coupon_reconcile_retentions))

        last_position = self.get_last_position(taxes_position)

        size_header = len(self._get_header())
        res.extend(self.get_coupon_reconcile_details(taxes_position, coupon_reconcile_documents, size_header, last_position))
        
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
