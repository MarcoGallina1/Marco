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
        warehouses = self.mapped('warehouse_id').filtered(lambda x: x.automatic_process_pickings)
        if self.env.context.get('process_picking') or warehouses:
            sales = self if self.env.context.get('process_picking') else self.filtered(
                lambda x: x.warehouse_id in warehouses
            )
            for picking in sales.mapped('picking_ids'):
                self.env['stock.immediate.transfer'].create(
                    {'pick_ids': [(6, 0, [picking.id])]}
                ).process()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
