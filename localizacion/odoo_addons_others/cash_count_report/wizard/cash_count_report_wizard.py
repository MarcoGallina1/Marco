# - coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from blueorange.xls.xls import XlsBuilder


class CashCountReportWizard(models.TransientModel):
    _name = 'cash.count.report.wizard'

    report_type = fields.Selection([('customer', "Ingresos"), ('supplier', "Egresos")], string="Tipo", required=True)
    date_from = fields.Date("Desde", required=True)
    date_to = fields.Date("Hasta", required=True)
    company_id = fields.Many2one('res.company', "Compañía", required=True)
    pos_ar_id = fields.Many2one('pos.ar', "Punto de venta", domain="[('company_id', 'child_of', company_id)]")
    xls_file = fields.Binary()

    @api.onchange('company_id')
    def onchange_company(self):
        self.pos_ar_id = False

    @api.constrains('date_from', 'date_to')
    def check_dates(self):
        if any(r.date_from > r.date_to for r in self):
            raise ValidationError('La fecha "desde" no puede ser posterior a la fecha "hasta".')

    def export_pdf(self):
        data = {
            'partner_type': self.report_type,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'company_id': self.company_id.id,
            'pos_ar_id': self.pos_ar_id.id if self.pos_ar_id else False,
        }
        return self.env.ref('cash_count_report.cash_count_report_action').report_action(False, data=data)

    def export_xls(self):
        styles = {
            'header': ['font: bold on, height 220; align: horiz left;'],
            'bold': ['font: bold on; align: horiz left;'],
            'bold_amount': ['font: bold on; align: horiz left;', '$0.00'],
            'regular': ['align: horiz left;'],
            'regular_amount': ['align: horiz left;', '$0.00'],
        }
        xls = XlsBuilder("Arqueo de caja", styles)
        xls.sheet.col(0).width = 5632
        xls.sheet.col(1).width = 8448
        pos = self.pos_ar_id
        payments = self.env['account.payment']._get_cash_count_payments(
            self.report_type, self.date_from, self.date_to, self.company_id.id, pos.id if pos else False)
        curr_row = 1

        # Escribo el encabezado global con los parámetros del reporte
        header_columns = payments.get_header()
        for i in range(len(header_columns)):
            xls.sheet.col(i + 2).width = 4224
        company_header = [
            "Arqueo de caja - {}".format(dict(self._fields['report_type']._description_selection(self.env)).get(self.report_type)),
            self.company_id.name,
            "{} - {}".format(self.date_from.strftime("%d/%m/%Y"), self.date_to.strftime("%d/%m/%Y"))
        ]
        if pos:
            company_header.insert(1, "Punto de venta {}".format(pos.display_name))

        for row in company_header:
            xls.merge_cells(curr_row, curr_row, 1, len(header_columns) + 3, row, 'header')
            curr_row += 1

        # Escribo el encabezado de la tabla
        header = ["Número", "Proveedor" if self.report_type == 'supplier' else "Cliente"]
        header.extend([j.name for j in header_columns])
        xls.write_row(curr_row, header, ['bold'])
        curr_row += 1

        # Escribo las líneas de datos
        line_styles = ['regular', 'regular']
        line_styles.extend(['regular_amount' for i in range(len(header_columns))])
        for data in payments.get_cash_count_xls_data(header_columns):
            xls.write_row(curr_row, data, line_styles)
            curr_row += 1

        # Escribo los totales
        xls.merge_cells(curr_row, curr_row, 1, 2, "Total", 'bold')
        for i, total in enumerate(payments.get_totals_by_column(header_columns)):
            xls.write_cell(curr_row, i + 3, total, 'bold_amount')
        curr_row += 2

        self.xls_file = xls.get_file()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/cash_count_report?wizard_id=%s&filename=%s' % (self.id, 'Arqueo de caja.xls'),
            'target': 'new',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
