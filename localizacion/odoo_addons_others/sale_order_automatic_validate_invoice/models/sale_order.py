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


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        create_invoice_teams = self.mapped('team_id').filtered(lambda x: x.automatic_create_invoices)
        if self.env.context.get('create_invoices') or create_invoice_teams:
            sales = self if self.env.context.get('create_invoices') else self.filtered(
                lambda x: x.team_id in create_invoice_teams
            )
            if sales:
                self.env['sale.advance.payment.inv'].with_context(
                    active_model='sale.order', active_id=sales[0].id, active_ids=sales.ids,
                ).create({'deduct_down_payments': False}).create_invoices()
            validate_invoices_sales = sales.filtered(lambda x: x.team_id.automatic_validate_invoices)
            for invoice in validate_invoices_sales.mapped('invoice_ids'):
                invoice.action_post()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
