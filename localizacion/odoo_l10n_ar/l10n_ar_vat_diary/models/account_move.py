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

from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_vat_diary_invoice_sign(self):
        return self.type in ['in_refund', 'out_refund'] and -1 or 1

    def _get_invoice_currency_rate(self):
        """ Calculo el rate de la factura """
        rate = 1
        currency_lines = self.line_ids.filtered(lambda x: x.amount_currency).sorted(
            lambda x: x.product_id, reverse=True
        )  # Las cuentas de ingresos/gastos
        if (self.company_id.currency_id != self.currency_id) and currency_lines:
            line_currency = currency_lines[0]
            rate = abs((line_currency.credit + line_currency.debit) / line_currency.amount_currency)
        return rate

    def update_vat_diary_values(self, taxes_position, vals, size_header):
        """Actualiza un diccionario con los datos de una fila del subdiario 
        para las facturas

        :param taxes_position: Diccionario con las posiciones de los 
        impuestos en el subdiario
        :type taxes_position: dict
        :param vals: Diccionario con los datos de una fila del subdiario
        :type vals: dict
        :param size_header: Tamaño del encabezado genérico del subdiario
        :type size_header: int
        """        
        separate_not_taxable_from_exempt = self.env.context.get('separate_not_taxable_from_exempt')
        last_position = self.env['wizard.vat.diary'].get_last_position(taxes_position)
        rate = self._get_invoice_currency_rate()
        sign = self.get_vat_diary_invoice_sign()
        for invoice_tax in self.line_ids.filtered(
            lambda x: x.price_subtotal and x.tax_line_id or (
                x.tax_line_id.is_vat and not x.tax_line_id.is_exempt)
        ):
            if invoice_tax.tax_line_id.is_vat:
                base = sum(
                    self.invoice_line_ids.filtered(
                        lambda x: any(tax.is_vat and not tax.is_exempt and tax ==
                                      invoice_tax.tax_line_id for tax in x.tax_ids)
                    ).mapped('price_subtotal')
                )
                vals[taxes_position[invoice_tax.tax_line_id] +
                               size_header] = round(base * sign * rate, 2)
                vals[taxes_position[invoice_tax.tax_line_id] + size_header + 1] = round(
                    invoice_tax.price_subtotal * sign * rate, 2)
            else:
                vals[taxes_position[invoice_tax.tax_line_id] + size_header] = round(
                    invoice_tax.price_subtotal * sign * rate, 2)
        # Separo no gravado de exento si así lo requiriera el usuario
        if separate_not_taxable_from_exempt:
            vals[last_position + size_header] = self.amount_not_taxable * sign * rate
            vals[last_position + size_header + 1] = self.amount_exempt * sign * rate
        else:
            vals[last_position + size_header] = (self.amount_not_taxable + self.amount_exempt) * sign * rate
    
    def get_vat_diary_total(self):
        self.ensure_one()
        return abs(self.amount_total_signed) * self.get_vat_diary_invoice_sign()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
