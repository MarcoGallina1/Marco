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
from ..exceptions.exceptions import CheckInOtherPaymentError, DeleteNonDraftCheckError, PostReceiptNonDraftCheckError,\
    PostPaymentNonWalletCheckError, PostPaymentNotToOrderCheckError, CancelReceiptNonWalletCheckError,\
    CancelPaymentNonHandedCheckError, InvalidSentRateError


class AccountThirdCheck(models.Model):
    _inherit = 'account.abstract.check'
    _name = 'account.third.check'
    _description = 'Cheque de terceros'

    issue_name = fields.Char(
        'Nombre de emisor',
        track_visibility='onchange'
    )

    destination_payment_id = fields.Many2one(
        'account.payment',
        'Pago destino',
        help="Pago donde se utilizó el cheque",
    )

    not_to_order = fields.Boolean(
        string="No a la orden",
        help="Si está establecido, este cheque no podrá ser utilizado para realizar pagos."
    )

    sent_rate = fields.Float(
        string="Cotización de envío",
        digits=(12, 6)
    )

    sent_payment_currency_amount = fields.Float(
        string="Monto en moneda de pago en envío",
        currency_field='sent_payment_currency_id'
    )

    sent_payment_currency_id = fields.Many2one(
        related='destination_payment_id.currency_id',
        store=True
    )

    same_currency_as_sent_payment = fields.Boolean(
        compute='get_same_currency_as_sent_payment'
    )
    partner_id = fields.Many2one(
        related='payment_id.partner_id',
        string="Partner de Origen",
        store=True
    )
    destination_partner_id = fields.Many2one(
        related='destination_payment_id.partner_id',
        string="Partner de Destino",
        store=True
    )

    @api.depends('currency_id', 'sent_payment_currency_id')
    def get_same_currency_as_sent_payment(self):
        for r in self:
            if r.env.context.get('payment_currency'):
                r.same_currency_as_sent_payment = r.currency_id.id == r.env.context.get('payment_currency')
            else:
                r.same_currency_as_sent_payment = r.currency_id == r.sent_payment_currency_id

    def validate_sent_rate(self):
        return all(not r.destination_payment_id or r.sent_rate > 0 for r in self)

    @api.constrains('sent_rate')
    def check_sent_rate(self):
        if not self.validate_sent_rate():
            raise InvalidSentRateError("La cotización de la línea debe ser positiva.")

    @api.onchange('sent_rate')
    def onchange_sent_rate(self):
        """ Al modificar el monto actualizo el monto en moneda de pago según la tasa de la línea """
        if self.env.context.get('sent_payment_currency_amount_modified'):
            return
        ctx = self.env.context.copy()
        ctx['sent_rate_modified'] = True
        self.env.context = ctx
        self.sent_payment_currency_amount = round(self.amount / self.sent_rate, 2) if self.sent_rate else 0

    @api.onchange('sent_payment_currency_amount')
    def onchange_sent_payment_currency_amount(self):
        """
        Al modificar el monto en moneda de pago actualizo la tasa (siempre y cuando la moneda del método y la del pago
        sean distintas, si son iguales actualizo el monto de la línea)
        """
        if self.env.context.get('sent_rate_modified'):
            return
        ctx = self.env.context.copy()
        ctx['sent_payment_currency_amount_modified'] = True
        self.env.context = ctx
        payment_amount = self.sent_payment_currency_amount
        if self.currency_id != self.sent_payment_currency_id:
            self.sent_rate = self.amount / payment_amount if payment_amount else 0

    def get_states(self):
        res = super(AccountThirdCheck, self).get_states()
        res.insert(2, ('deposited', 'Depositado'))
        res.insert(1, ('wallet', 'En cartera'))
        return res

    def _check_unlink_state(self):
        return self.state == 'draft'

    def unlink(self):
        if any(not r._check_unlink_state() for r in self):
            raise DeleteNonDraftCheckError("Solamente se pueden borrar cheques en borrador.")
        super(AccountThirdCheck, self).unlink()

    def _check_post_receipt_state(self):
        return self.state == 'draft'

    def post_receipt(self):
        """ Lo que deberia pasar con el cheque cuando se valida un recibo """
        if any(not r._check_post_receipt_state() for r in self):
            raise PostReceiptNonDraftCheckError("Los cheques de terceros recibidos deben estar en borrador.")
        self.next_state('draft')

    def _check_post_payment_state(self):
        return self.state == 'wallet'

    def post_payment(self):
        """ Lo que deberia pasar con el cheque cuando se valida un pago """
        for r in self:
            if not r._check_post_payment_state():
                raise PostPaymentNonWalletCheckError("Los cheques de terceros entregados deben estar en cartera.")
            if r.not_to_order:
                raise PostPaymentNotToOrderCheckError('No se puede validar un pago con cheques que son "no a la orden".')
        self.next_state('wallet_handed')

    def _check_cancel_receipt_state(self):
        return self.state == 'wallet'

    def cancel_receipt(self):
        """ Lo que deberia pasar con el cheque cuando se cancela un recibo """
        if any(not check._check_cancel_receipt_state() for check in self):
            raise CancelReceiptNonWalletCheckError("Los cheques de tercero deberian estar en "
                                                   "cartera para poder cancelar el pago.")
        self.cancel_state('wallet')

    def cancel_payment(self):
        """ Lo que deberia pasar con el cheque cuando se cancela una orden de pago """
        if any(not check._check_state_for_cancel_payment() for check in self):
            raise CancelPaymentNonHandedCheckError("Los cheques de tercero deberian estar en "
                                                 "entregados para poder cancelar el pago.")
        self.cancel_state('handed')

    def get_cancel_states(self):
        return {
            'wallet': 'draft',
            'handed': 'wallet',
        }

    def get_next_states(self):
        return {
            'draft': 'wallet',
            'wallet_handed': 'handed',
        }

    def get_payment_currency_field(self, payment):
        return 'sent_payment_currency_id' if payment.payment_type == 'outbound' \
            else super(AccountThirdCheck, self).get_payment_currency_field(payment)

    def get_rate_field(self, payment):
        return 'sent_rate' if payment.payment_type == 'outbound' else super(AccountThirdCheck, self).get_rate_field(payment)

    def get_amount_field(self, payment):
        return 'sent_payment_currency_amount' if payment.payment_type == 'outbound' \
            else super(AccountThirdCheck, self).get_amount_field(payment)

    def get_first_move_line_name(self):
        return 'CHEQUE DE TERCEROS N° {}'.format(super(AccountThirdCheck, self).get_first_move_line_name())

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
