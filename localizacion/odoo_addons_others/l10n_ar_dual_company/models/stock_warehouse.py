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

from odoo import models, api
from odoo.exceptions import UserError


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    @api.model
    def _get_production_location(self):
        if self.company_id.parent_id:
            location = self.env['stock.location'].with_context(force_company=self.company_id.parent_id.id).search(
                [('usage', '=', 'production'), ('company_id', '=', self.company_id.parent_id.id)], limit=1)
            if not location:
                raise UserError('No se puede encontrar ninguna ubicación de producción.')
            return location
        else:
            return super(StockWarehouse, self)._get_production_location()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
