# -*- coding: utf-8 -*-
from odoo import http, models, fields, api, _
from datetime import datetime
import calendar


class MrpCategory(models.Model):
    _name = 'mrp.category'
    _description = 'mrp.category'

    name = fields.Char(string="Name",translate=True)
    desc = fields.Char(string="Desc",translate=True)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    fl_prod_categ_id = fields.Many2one('mrp.category',string="Production Category",translate=True)

    @api.onchange('fl_prod_categ_id')
    def _onchange_type_fresca(self):
        vars = self.env['product.product'].search([('product_tmpl_id', '=', self.id)])
        vars.write({'fl_prod_categ_id': self.fl_prod_categ_id})

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    fl_prod_categ_id = fields.Many2one('mrp.category',string="Production Category",translate=True)

    @api.onchange('product_id')
    def _onchange_product_fresca(self):
        self.fl_prod_categ_id = self.product_id.fl_prod_categ_id
