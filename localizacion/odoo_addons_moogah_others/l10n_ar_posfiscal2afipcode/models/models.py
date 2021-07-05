# -*- coding: utf-8 -*-
from odoo import http, models, fields, api, _
from datetime import datetime
import calendar
    
class AccountFiscalPOsition(models.Model):
    _inherit = 'account.fiscal.position'

    afip_code = fields.Char(string="afip code")

