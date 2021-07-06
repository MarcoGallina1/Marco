# -*- encoding: utf-8 -*-
##############################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"
    
    custom_street = fields.Char(string="Calle")
    street_number = fields.Char(string="Número", size=128)
    flat = fields.Char(string="Piso", size=128)
    department = fields.Char(string="Departamento", size=128)
    street = fields.Char(compute="compute_partner_street", store=True)

    @api.depends("custom_street", "street_number", "flat", "department")
    def compute_partner_street(self):
        for rec in self:
            if rec.custom_street:
                street_list = [rec.custom_street or '', rec.street_number or '', rec.flat or '', rec.department or '']
                rec.street = ' '.join(filter(None, street_list))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
