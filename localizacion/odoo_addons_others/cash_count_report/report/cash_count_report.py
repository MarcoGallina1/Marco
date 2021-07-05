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


class CashCountReport(models.AbstractModel):
    _name = 'report.cash_count_report.cash_count_report'
    _description = 'Reporte de arqueo de caja'
    _table = 'report_cash_count'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = fields.Date.from_string(data['date_from'])
        date_to = fields.Date.from_string(data['date_to'])
        partner_type = data['partner_type']
        pos_ar_id = data['pos_ar_id']
        company_id = data['company_id']
        payments = self.env['account.payment']._get_cash_count_payments(
            partner_type, date_from, date_to, company_id, pos_ar_id)
        docargs = {
            'date_from': date_from.strftime("%d/%m/%Y"),
            'date_to': date_to.strftime("%d/%m/%Y"),
            'payments': payments,
            'payment_type': "Egresos" if partner_type == 'supplier' else "Ingresos",
            'partner_type': "Proveedor" if partner_type == 'supplier' else "Cliente",
            'pos_ar': self.env['pos.ar'].browse(pos_ar_id).display_name if pos_ar_id else False,
            'company': self.env['res.company'].browse(company_id).name,
        }
        return docargs

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
