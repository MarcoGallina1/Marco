# -*- coding: utf-8 -*-
from odoo import http, models, fields, api, _
from datetime import datetime
import calendar
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    cae = fields.Char('CAE', states={'draft': [('readonly', False)]})
    cae_due_date = fields.Date('Vencimiento CAE', states={'draft': [('readonly', False)]})
    cae_group = fields.Boolean(compute="_compute_cae_group")

    def _compute_cae_group(self):
        group = self.env.ref('account.group_account_manager')
        res = self.env.user.id in group.users.ids
        for rec in self:
            rec.cae_group = res

    def check_invoice_duplicity(self):
        """ Valida que la factura no este duplicada. """

        if self.is_invoice():
            domain = [
                ('voucher_name', '=', self.voucher_name),
                ('voucher_type_id', '=', self.voucher_type_id.id),
                ('type', '=', self.type),
                ('state', 'not in', ['draft', 'cancel']),
                ('id', '!=', self.id),
                ('company_id', '=', self.company_id.id)
            ]

            if self.is_purchase_document():
                domain.append(('partner_id', '=', self.partner_id.id))

            if self.search_count(domain) > 1:
                raise ValidationError(
                    "Ya existe un documento del tipo {} con el número {}!".format(
                        self.voucher_type_id.name,
                        self.voucher_name
                    )
                )
