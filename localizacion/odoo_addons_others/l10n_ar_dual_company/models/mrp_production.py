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


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    location_dest_id = fields.Many2one(check_company=False)
    location_src_id = fields.Many2one(check_company=False)
    picking_type_id = fields.Many2one(check_company=False)
    bom_id = fields.Many2one(check_company=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: