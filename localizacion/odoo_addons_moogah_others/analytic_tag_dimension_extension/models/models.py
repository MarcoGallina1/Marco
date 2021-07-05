# -*- coding: utf-8 -*-
from odoo import http, models, fields, api, _
from datetime import datetime
import calendar
    

class ResCompany(models.Model):
    _inherit = 'res.company'

    an_tags_rec = fields.Boolean(string="Analytic Tags in Receivable & Payable accounts",readonly=False)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    an_tags_rec = fields.Boolean(
        related="company_id.an_tags_rec",
        string="Analytic Tags in Receivable & Payable accounts",
        readonly = False,
    )

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('invoice_line_ids','line_ids')
    def _onchange_invoice_line_ids(self):
        res = super(AccountMove, self)._onchange_invoice_line_ids()

        if self.partner_id.property_account_receivable_id in self.line_ids.mapped('account_id') or \
            self.partner_id.property_account_payable_id in self.line_ids.mapped('account_id'):

            tags = self.invoice_line_ids.mapped('analytic_tag_ids')._ids
            if tags:
                if self.type in ('out_invoice','out_refund'):
                    line = self.line_ids.filtered(lambda a: a.account_id == self.partner_id.property_account_receivable_id)
                    line.analytic_tag_ids = [(6,0, list(tags))]
                if self.type in ('in_invoice','in_refund'):
                    line = self.line_ids.filtered(lambda a: a.account_id == self.partner_id.property_account_payable_id)
                    line.analytic_tag_ids = [(6,0, list(tags))]
        return res