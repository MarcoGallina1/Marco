# -*- encoding: utf-8 -*-
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

from odoo import models, tools
from odoo.exceptions import ValidationError
from collections import defaultdict


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _format_amount(self, amount):
        return tools.format_amount(self.env, amount, self.env.user.company_id.currency_id)

    def _get_cash_count_domain(self, partner_type, date_from, date_to, company_id, pos_ar_id):
        domain = [('company_id', 'child_of', company_id), ('partner_type', '=', partner_type),
            ('payment_date', '>=', date_from), ('payment_date', '<=', date_to),
            ('state', 'in', ('posted', 'sent', 'reconciled'))]
        if pos_ar_id:
            domain.append(('journal_id.pos_ar_id', '=', pos_ar_id))
        return domain

    def _get_cash_count_payments(self, partner_type, date_from, date_to, company_id, pos_ar_id):
        payments = self.search(self._get_cash_count_domain(partner_type, date_from, date_to, company_id, pos_ar_id))
        if not payments:
            raise ValidationError("No se han encontrado pagos coincidentes con los parámetros introducidos.")
        return payments

    def _group_payments_by_company(self):
        grouped_payments = {}
        for r in self:
            if r.company_id.name not in grouped_payments:
                grouped_payments[r.company_id.name] = self.env['account.payment']
            grouped_payments[r.company_id.name] |= r
        return grouped_payments

    def get_header(self):
        header = set([journal for journal in self.mapped('journal_id').filtered(
            lambda l: not l.multiple_payment_journal
        )])
        for r in self:
            for recordset in r._get_payment_line_recordsets():
                header.update([criteria for criteria in recordset.get_criteria_group_cash_count()])
        return header

    def get_amounts_by_column(self):
        res = defaultdict(list)
        for r in self.filtered(lambda l: not l.journal_id.multiple_payment_journal):
            factor = 1
            if r.payment_type == 'outbound' and r.partner_type == 'customer' or \
                    r.payment_type == 'inbound' and r.partner_type == 'supplier':
                factor = -1
            res[r.journal_id].append(r.amount * factor)
        for recordset in self._get_payment_line_recordsets():
            for record in recordset:
                factor = 1
                if record.payment_id.payment_type == 'outbound' and record.payment_id.partner_type == 'customer' or \
                        record.payment_id.payment_type == 'inbound' and record.payment_id.partner_type == 'supplier':
                    factor = -1
                res[next(iter(record.get_criteria_group_cash_count()))].append(record.amount * factor)
        return res

    def get_totals_by_column(self, header_columns):
        amounts_by_column = self.get_amounts_by_column()
        return [sum(amounts_by_column[column]) for column in header_columns]

    def _get_cash_count_data(self, header_columns):
        """
        Devuelvo los datos comunes para el arqueo de caja
        @param header_columns: set de todas las columnas que se van a mostrar en el arqueo
        @return: lista de listas, cada lista corresponde a los datos de un pago. Los montos de cada diario estarán
                 expresados en listas, con un elemento por cada línea de método de pago que use dicho diario
        """
        data = []
        for r in self:
            payment_data = [r.name, r.partner_id.display_name]
            amounts_by_column = r.get_amounts_by_column()
            for column in header_columns:
                payment_data.append(amounts_by_column[column])
            data.append(payment_data)
        return data

    def get_cash_count_xls_data(self, header_columns):
        """
        Tomo los datos comunes y creo líneas nuevas para cada monto de diario, de modo que cada línea tenga un importe
        solo. De la segunda fila en adelante no se mostrará fecha y número de pago ni cliente
        """
        data = self._get_cash_count_data(header_columns)
        formatted_data = []
        for row in data:
            new_rows = []
            new_rows_qty = max([len(i) for i in row[2:]])
            for i in range(new_rows_qty):
                new_row = ['', '']
                for j in range(len(row) - 2):
                    new_row.append(row[2 + j][i] if i < len(row[2 + j]) else '')
                new_rows.append(new_row)
            if not new_rows:
                new_rows.append(['', ''])
            new_rows[0][0] = row[0] or ''
            new_rows[0][1] = row[1] or ''
            formatted_data.extend(new_rows)
        return formatted_data

    def get_cash_count_pdf_data(self, header_columns):
        """ Tomo los datos comunes y junto los montos de cada diario en una fila, separándolos con saltos de línea """
        data = self._get_cash_count_data(header_columns)
        for i, row in enumerate(data):
            for j, col in enumerate(row):
                if isinstance(col, list):
                    row[j] = "<br/>".join(self._format_amount(x) for x in col)
            data[i] = row
        return data

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
