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


class StockRule(models.Model):
    _inherit = 'stock.rule'

    location_dest_id = fields.Many2one(check_company=False)
    location_id = fields.Many2one(check_company=False)
    location_src_id = fields.Many2one(check_company=False)
    picking_type_id = fields.Many2one(check_company=False)
    warehouse_id = fields.Many2one(check_company=False)

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values, bom):
        if values.get('sale_line_id'):
            company_id = self.env['sale.order.line'].browse(values.get('sale_line_id')).company_id
        return super(StockRule, self)._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name, origin, company_id, values, bom)

    def _get_matching_bom(self, product_id, company_id, values):
        if values.get('sale_line_id'):
            company_id = self.env['sale.order.line'].browse(values.get('sale_line_id')).company_id
        return super(StockRule, self)._get_matching_bom(product_id, company_id, values)

    def _make_po_get_domain(self, company_id, values, partner):
        if values.get('sale_line_id'):
            company_id = self.env['sale.order.line'].browse(values.get('sale_line_id')).company_id
        return super(StockRule, self)._make_po_get_domain(company_id, values, partner)

    @api.model
    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, company_id, values, po):
        if values.get('sale_line_id'):
            company_id = self.env['sale.order.line'].browse(values.get('sale_line_id')).company_id
        return super(StockRule, self)._prepare_purchase_order_line(product_id, product_qty, product_uom, company_id, values, po)

    def _update_purchase_order_line(self, product_id, product_qty, product_uom, company_id, values, line):
        if values.get('sale_line_id'):
            company_id = self.env['sale.order.line'].browse(values.get('sale_line_id')).company_id
        return super(StockRule, self)._update_purchase_order_line(product_id, product_qty, product_uom, company_id, values, line)

    def _prepare_purchase_order(self, company_id, origins, values):
        values_dict = values[0]
        if values_dict.get('sale_line_id'):
            company_id = self.env['sale.order.line'].browse(values_dict.get('sale_line_id')).company_id
        return super(StockRule, self)._prepare_purchase_order(company_id, origins, values)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
