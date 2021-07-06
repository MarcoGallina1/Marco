# -*- coding: utf-8 -*-
from odoo import http, models, fields, api, _
from datetime import datetime
import calendar
from odoo.exceptions import AccessError, UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    fl_picking_status = fields.Selection(
        [('pending', 'Pendiente'), ('ready', 'Preparado'), ('delivered', 'Entregado')],
        string="Status", translate=True,default="pending",
    )

    def _get_items(self):
        for record in self:
            res = ""
            for item in record.order_line:
                res += str(item.product_uom_qty) + " " + item.product_id.name + ", "
            record.get_items = res

    get_items = fields.Char(string="Items",compute="_get_items")

    def action_chg(self):
        for record in self:
            if not record.fl_picking_status:
                state = 'pending'
            if record.fl_picking_status == 'pending':
                state = 'ready'
            if record.fl_picking_status == 'ready':
                state = 'delivered'
            record.write({'fl_picking_status': state})
            if record.fl_picking_status == 'delivered':
                if record.process == 1 and record.state in ('draft', 'sent'):
                    record.action_cancel()
                if record.process == 0 and record.state in ('draft', 'sent'):
                    raise UserError(_("Caja no procesó la orden"))
                if record.state == 'sale':
                    deliveries = self.env['stock.picking'].search([('sale_id', '=', record.id)])
                    for deli in deliveries:
                        deli.button_validate()
            record.invalidate_cache()
