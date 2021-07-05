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

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    property_stock_production = fields.Many2one(domain="[('usage', '=', 'production')]", check_company=False)
    property_stock_inventory = fields.Many2one(domain="[('usage', '=', 'inventory')]", check_company=False)

    def set_property_stock_location_globally(self):
        current_company_id = self.env.company.id
        self = self.sudo()
        proxy = self.env['ir.property']
        source_property = proxy.with_context(force_company=current_company_id)
        values_stock_production = source_property.get_multi('property_stock_production', 'product.template', self.ids)
        values_stock_inventory = source_property.get_multi('property_stock_inventory', 'product.template', self.ids)
        for company in self.env['res.company'].search([('id', '!=', current_company_id)]):
            target_property = proxy.with_context(force_company=company.id)
            target_property.set_multi('property_stock_production', 'product.template', values_stock_production)
            target_property.set_multi('property_stock_inventory', 'product.template', values_stock_inventory)

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        if res.property_stock_production or res.property_stock_inventory:
            res.set_property_stock_location_globally()
        return res

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if 'property_stock_production' in vals or 'property_stock_inventory' in vals:
            self.set_property_stock_location_globally()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
