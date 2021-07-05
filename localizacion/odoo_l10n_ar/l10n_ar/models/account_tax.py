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

from odoo import models, fields


class AccountTax(models.Model):

    _inherit = 'account.tax'

    is_exempt = fields.Boolean('Exento')
    is_vat = fields.Boolean('IVA')
    amount_type = fields.Selection(selection_add=[('perception', 'Percepcion')])

    def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None):
        res = super(AccountTax, self)._compute_amount(base_amount, price_unit, quantity, product, partner)
        if self.amount_type == 'perception':
            return base_amount
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: