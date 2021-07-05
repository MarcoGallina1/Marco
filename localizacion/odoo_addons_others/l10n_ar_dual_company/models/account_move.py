# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_invoice_register_payment(self):
        new_context = self.env.context.copy()
        new_context.update({'force_company': self.company_id.id})
        self.env.context = new_context
        return super(AccountMove, self).action_invoice_register_payment()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
