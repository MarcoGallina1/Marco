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

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _create_or_update_picking(self):
        """Heredo la funcion para que cada vez que se genere un procurement group y luego genere un remito se
            coloque la empresa correcta"""
        res = super(PurchaseOrderLine, self)._create_or_update_picking()
        for line in self:
            company = line.order_id.company_id
            # Filtro los remitos de los moves asociados a la linea de venta que sean ya de la misma compañia
            pickings = line.move_ids.mapped('picking_id').filtered(lambda x: x.company_id != company)
            pickings.write({'company_id': company.id})
            pickings.mapped('move_ids_without_package').write({'company_id': company.id})
            pickings.mapped('move_line_ids_without_package').write({'company_id': company.id})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
