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
from . import perception_calculator


def _format_perception_message(message):
    return """         
    <div class="alert alert-info" role="alert" style="margin-bottom: -5px;">
       <string> Error! </strong> {}
    </div>
    """.format(message)


class AccountInvoice(models.Model):  # Se encarga de cargar las percepciones en la factura automaticamente

    _inherit = 'account.move'

    perception_message = fields.Char('Alerta percepcion', default='')

    def get_automatic_perceptions(self):
        self.ensure_one()
        calculator = perception_calculator.PerceptionCalculator(
            self.partner_id,
            self._get_untaxed_product_amounts(),
            self.jurisdiction_id,
            self.company_id
        )
        return calculator.get_perceptions_values()

    @api.onchange('invoice_line_ids')
    def onchange_invoice_line_perception(self):
        if self.type in ['out_invoice', 'out_refund']:
            message = ''
            perception_values = []

            if self.partner_id:
                try:
                    perception_values = self.get_automatic_perceptions()
                except Exception as e:
                    message = _format_perception_message(e.args[0])

            self.perception_message = message

            # El new nos sirve mucho porque lo cachea y nosotros no lo necesitamos en la base hasta el guardado, es un
            # comportamiento similar al de los impuestos.
            perception_proxy = self.env['account.invoice.perception']
            for perception_value in perception_values:
                perception_proxy |= perception_proxy.new(perception_value)

            self.perception_ids = perception_proxy
            self.onchange_perception_ids()

    @api.onchange('partner_id', 'jurisdiction_id', 'partner_shipping_id', 'currency_id', 'currency_rate')
    def _onchange_partner_id(self):
        if self.state == 'draft':
            if not self.jurisdiction_id:
                self.jurisdiction_id = self.partner_shipping_id.state_id or self.partner_id.state_id
            self.onchange_invoice_line_perception()
        return super(AccountInvoice, self)._onchange_partner_id()

    def _get_untaxed_product_amounts(self):
        """ Solo aplica percepcion en los casos de productos percibiles y que tengan neto gravado"""
        self.ensure_one()
        lines = self.invoice_line_ids.filtered(
            lambda x:
            x.product_id.perception_taxable and
            x.tax_ids.filtered(lambda y: y.is_vat and not y.is_exempt)
        )
        move_currency = self.currency_id
        if move_currency and self.currency_id != self.company_currency_id:
            if self.need_rate:
                move_currency = move_currency.with_context(
                    fixed_rate=self.currency_rate,
                    fixed_from_currency=move_currency,
                    fixed_to_currency=self.company_currency_id
                )
            price_subtotal = move_currency._convert(
                sum(line.price_subtotal for line in lines),
                self.company_currency_id,
                self.company_id,
                self.invoice_date or fields.Date.context_today(self)
            )
        else:
            price_subtotal = sum(line.price_subtotal for line in lines)

        return round(price_subtotal, 2)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
