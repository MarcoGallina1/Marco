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
from odoo.tools.misc import formatLang

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    electronic_invoice_price_unit = fields.Char(compute='get_electronic_invoice_price_unit')

    def get_electronic_invoice_price_unit(self):
        for r in self:
            total_discount = 1 - (r.discount or 0.0) / 100.0
            price_to_use = r.price_subtotal if r.move_id.voucher_type_id.denomination_id.vat_discriminated else r.price_total
            price_unit = price_to_use/r.quantity / total_discount if total_discount and r.quantity else 0.0
            r.electronic_invoice_price_unit = formatLang(r.env, price_unit, dp='Product Price', currency_obj=r.currency_id or r.company_id.currency_id)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: