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

from odoo import models, fields
from odoo.exceptions import ValidationError


class AfipImportDocumentsLineWizard(models.TransientModel):

    _name = 'afip.import.documents.line.wizard'

    date = fields.Date(
        string='Fecha'
    )
    voucher_type = fields.Char(
        string='Tipo'
    )
    point_of_sale = fields.Char(
        string='Punto de venta'
    )
    voucher_name = fields.Char(
        string='Numero'
    )
    cae = fields.Char(
        sring='CAE'
    )
    document_type = fields.Char(
        string='Tipo de documento'
    )
    document_number = fields.Char(
        string='Numero de documento'
    )
    name = fields.Char(
        string='Denominación'
    )
    currency_value = fields.Float(
        string='Tipo de cambio'
    )
    currency = fields.Char(
        string='Moneda'
    )
    amount_untaxed = fields.Float(
        string='Importe neto gravado'
    )
    amount_not_taxed = fields.Float(
        string='Importe no gravado'
    )
    amount_exempt = fields.Float(
        string='Importe exento'
    )
    amount_vat = fields.Float(
        string='Importe IVA'
    )
    amount_total = fields.Float(
        string='Importe Total'
    )
    wizard_id = fields.Many2one(
        comodel_name='afip.import.documents.wizard',
        string='Wizard',
    )

    def get_invoice_lines(self):
        self.ensure_one()
        lines = []
        line_vals = {
            'account_id': self._get_invoice_account().id,
            'quantity': 1,
            'price_unit': self.amount_untaxed,
            'name': 'Importación desde AFIP',
        }
        if self.amount_untaxed:
            lines.append((0, 0, line_vals))
        if self.amount_not_taxed:
            amount_not_taxed = line_vals.copy()
            amount_not_taxed['price_unit'] = self.amount_not_taxed
            lines.append(amount_not_taxed)
        if self.amount_exempt:
            exempt_vals = line_vals.copy()
            exempt_vals['price_unit'] = self.amount_exempt
            exempt_vals['tax_ids'] = [(6, 0, [self._get_exempt_tax().id])]
            lines.append(exempt_vals)

        return lines

    def _get_invoice_account(self):
        template_proxy = self.env['product.template'].sudo().with_context(
            company_id=self.wizard_id.company_id
        )
        return template_proxy.property_account_expense_id if self.wizard_id.type == 'received' else \
            template_proxy.property_account_income_id

    def _get_exempt_tax(self):
        tax = self.env['account.tax'].sudo().search([
            ('company_id', '=', self.wizard_id.company_id.id),
            ('is_exempt', '=', True),
            ('is_vat', '=', True),
            ('type_tax_use', '=', 'purchase' if self.wizard_id.type == 'received' else 'sale')
        ], limit=1)
        if not tax:
            raise ValidationError("No se encontro impuesto para Iva Exento")

        return tax

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
