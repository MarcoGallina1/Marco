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

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StockWarehouse(models.Model):

    _inherit = 'crm.team'

    automatic_create_invoices = fields.Boolean(
        'Create invoices',
        help='Check this if you want to automatic create invoices when confirming sale orders.'
    )
    automatic_validate_invoices = fields.Boolean(
        'Validate invoices',
        help='Check this if you want to automatic validate invoices when confirming sale orders.'
    )

    @api.onchange('automatic_validate_invoices')
    def onchange_automatic_validate_invoices(self):
        for team in self:
            if team.automatic_validate_invoices:
                team.automatic_create_invoices = True

    @api.onchange('automatic_create_invoices')
    def onchange_automatic_validate_invoices(self):
        for team in self:
            if not team.automatic_create_invoices:
                team.automatic_validate_invoices = False

    @api.constrains('automatic_validate_invoices', 'automatic_create_invoices')
    def constraint_automatic_invoices(self):
        if any(team.automatic_validate_invoices and not team.automatic_create_invoices for team in self):
            raise ValidationError("You can't set automatic validate invoices if automatic create invoices isn't set")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
