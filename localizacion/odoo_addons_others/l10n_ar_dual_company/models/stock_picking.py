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


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    location_dest_id = fields.Many2one(check_company=False)
    location_id = fields.Many2one(check_company=False)
    backorder_id = fields.Many2one(check_company=False)

    def _create_backorder(self):
        """ Heredo la funcion de generar remito de entrega parcial
         para cargar la misma compañia que el remito origianl"""
        res = super(StockPicking, self)._create_backorder()
        for backorder in res:
            backorder.write({'company_id': backorder.backorder_id.company_id.id})
            backorder.mapped('move_ids_without_package').write({'company_id': backorder.backorder_id.company_id.id})
            backorder.mapped('move_line_ids_without_package').write({'company_id': backorder.backorder_id.company_id.id})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
