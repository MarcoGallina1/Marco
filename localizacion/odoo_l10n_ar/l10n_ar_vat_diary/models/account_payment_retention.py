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


class AccountPaymentRetention(models.Model):
    _inherit = 'account.payment.retention'

    def _get_retention_currency_rate(self):
        """ Obtengo el rate de la retención """
        self.ensure_one()
        return self.rate if self.company_id.currency_id != self.currency_id else 1

    def update_vat_diary_values(self, taxes_position, vals, size_header):
        """Actualiza un diccionario con los datos de una fila del subdiario 
        para las retenciones

        :param taxes_position: Diccionario con las posiciones de los 
        impuestos en el subdiario
        :type taxes_position: dict
        :param vals: Diccionario con los datos de una fila del subdiario
        :type vals: dict
        :param size_header: Tamaño del encabezado genérico del subdiario
        :type size_header: int
        """
        rate = self._get_retention_currency_rate()
        tax_id = self.retention_id.tax_id
        vals[taxes_position[tax_id] + size_header] = round(self.amount * rate, 2)
    
    def get_vat_diary_total(self):
        self.ensure_one()
        return abs(self.amount) * self._get_retention_currency_rate()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
