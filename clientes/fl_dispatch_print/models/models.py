# -*- coding: utf-8 -*-
from odoo import http, models, fields, api, _
from datetime import datetime
import calendar

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def print_dispatch(self):
        return self.env.ref('fl_dispatch_print.action_report_fl_dispatch').report_action(self)