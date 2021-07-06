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

import io
import base64
from odoo import models, http, api
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception, content_disposition


class WizardVatDiary(models.TransientModel):
    _inherit = 'wizard.vat.diary'


    def get_header_summary(self):
        """ Genero un diccionario con los valores basicos de la cabecera del reporte resumido"""
        header = {
            0: 'Fecha',
            1: 'Razon Social',
            2: 'Posicion Fiscal',
            3: 'Tipo Doc.',
            4: 'Doc. Numero',
            5: 'Tipo',
            6: 'Comprobante',
            7: 'Subtotal',
            8: 'IVA',
            9: 'Otros impuestos',
            10: 'Total'
        }
        return header

    def _get_invoice_values_summary(self, invoice):
        """ Seteo los valores para cada posicion de una fila"""
        total_vat = round(sum(invoice.line_ids.filtered(
                    lambda x: x.tax_line_id and
                            x.tax_line_id.is_vat and not x.tax_line_id.is_exempt).mapped('price_subtotal')), 2)
        sign = invoice.get_vat_diary_invoice_sign()
        rate = invoice._get_invoice_currency_rate()
        return {
            0: invoice.invoice_date.strftime('%d/%m/%Y'),
            1: invoice.partner_id.name,
            2: invoice.fiscal_position_id.name or '',
            3: invoice.partner_id.partner_document_type_id.name or '',
            4: invoice.partner_id.vat or '',
            5: invoice.voucher_type_id.name or '',
            6: invoice.name,
            7: round(invoice.amount_untaxed * sign * rate, 2),
            8: round(total_vat * sign * rate, 2),
            9: round((invoice.amount_total - total_vat - invoice.amount_untaxed) * sign * rate, 2),
            10: invoice.get_vat_diary_total(),
        }

    def _get_retention_values_summary(self, retention):
        """ Seteo los valores para cada posicion de una fila"""
        if retention.certificate_no:
            name = "RET {}".format(retention.certificate_no)
        else:
            name = "{}".format(retention.payment_id.name)
        return {
            0: retention.date.strftime('%d/%m/%Y'),
            1: retention.partner_id.name,
            2: retention.partner_id.property_account_position_id.name or '',
            3: retention.partner_id.partner_document_type_id.name or '',
            4: retention.partner_id.vat or '',
            5: 'RETENCIÓN',
            6: name,
            9: retention.get_vat_diary_total(),
            10: retention.get_vat_diary_total()
        }

    def get_retentions_details_summary(self, retentions):
        """
        Crea la estructura de datos para los detalle del reporte, los cuales son datos de retenciones si estas fueran informadas.
        """
        res = []
        for retention in retentions:
            retention_values = self._get_retention_values_summary(retention)
            res.append(retention_values)
        return res

    def get_invoices_details_summary(self, invoices):
        """
        Crea la estructura de datos para los detalle del reporte, los cuales son datos de invoices,
        o de retenciones si estas fueran informadas.
        :param taxes_position: diccionario que contiene la posicion del impuesto y el impuesto
        :param invoices: account.invoice - De donde se tomaran los datos segun filtros del wizard
        :size_header: int - Tamaño del encabezado
        :last_position: int - Indice de la última posición de las columnas
        :return: lista de diccionarios, cada uno con la posicion y valor, ej: {0: '01/01/2000'}
        """
        res = []
        for invoice in invoices:
            invoice_values = self._get_invoice_values_summary(invoice)
            res.append(invoice_values)
        return res

    def get_details_values_summary(self, invoices, retentions=None):
        """
        Crea la estructura de datos para los detalle del reporte, los cuales son datos de invoices.
        """
        res = []
        invoices_details = self.get_invoices_details_summary(invoices)
        res.extend(invoices_details)
        if retentions:
            retentions_details = self.get_retentions_details_summary(retentions)
            res.extend(retentions_details)
        # Ordeno por fecha, tipo y nombre según las claves de los dict
        # devueltos por _get_invoice_values_summary y _get_retention_values_summary
        res = sorted(res, key=lambda x: (x.get(0), x.get(5), x.get(6)))
        return res

    def get_report_values_summary(self):
        """
        Devuelve los datos de cabecera y detalles del reporte a armar de las invoices obtenidas del wizard
        """

        invoices = self._get_invoices()
        if self.include_suffered_retentions:
            retentions = self._get_retentions()
            if not (invoices or retentions):
                raise ValidationError("No se han encontrado documentos para ese rango de fechas")
            header = self.get_header_summary()
            details = self.get_details_values_summary(invoices, retentions)
        else:
            if not invoices:
                raise ValidationError("No se han encontrado documentos para ese rango de fechas")
            header = self.get_header_summary()
            details = self.get_details_values_summary(invoices)

        return [header] + details

    def get_width_columns_summary(self):
        """ Ancho de columnas de reporte resumido"""
        return {
            0: 2500,
            1: 6000,
            2: 4000,
            3: 6000,
            4: 5000,
            5: 5000,
            6: 4000,
            7: 4000,
            8: 4000,
            9: 4000,
            10: 4000,
        }

    def generate_xls_report_summary(self):
        """ Crea un xls con los valores obtenidos de get_report_values_summary"""
        values = self.get_report_values_summary()

        # Preparamos el workbook y la hoja
        import xlwt
        wbk = xlwt.Workbook()
        style = xlwt.easyxf(
            'font: bold on,height 240,color_index 0X36;'
            'align: horiz center;'
            'borders: left thin, right thin, top thin'
        )
        name = 'Iva Ventas' if self.type == 'sales' else 'Iva Compras'
        sheet = wbk.add_sheet(name)
        # Ancho de las columnas
        for key, value in self.get_width_columns_summary().items():
            sheet.col(key).width = value
        row_number = 0
        # Header
        for col in values[0]:
            sheet.write(row_number, col, values[0][col], style)

        # Detalles
        row_number += 1
        for value in values[1:]:
            for col in value:
                sheet.write(row_number, col, value[col])
            row_number += 1

        # Exportamos y guardamos
        file_data = io.BytesIO()
        wbk.save(file_data)
        out = base64.encodebytes(file_data.getvalue())
        self.report = out

        date_from = self.date_from.strftime('%d-%m-%Y')
        date_to = self.date_to.strftime('%d-%m-%Y')

        filename = 'Resumen de subdiario ' + name + ' ' + date_from + ' a ' + date_to

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_vat_diary_summary?wizard_id=%s&filename=%s' % (self.id, filename + '.xls'),
            'target': 'new',
        }


class WizardVatDiarySummaryRoute(http.Controller):
    @http.route('/web/binary/download_vat_diary_summary', type='http', auth="public")
    @serialize_exception
    def download_vat_diary(self, debug=1, wizard_id=0, filename=''):  # pragma: no cover
        """ Descarga un documento cuando se accede a la url especificada en http route.
        :param debug: Si esta o no en modo debug.
        :param int wizard_id: Id del modelo que contiene el documento.
        :param filename: Nombre del archivo.
        :returns: :class:`werkzeug.wrappers.Response`, descarga del archivo excel.
        """
        filecontent = base64.b64decode(request.env['wizard.vat.diary'].browse(int(wizard_id)).report or '')
        return request.make_response(filecontent, [('Content-Type', 'application/excel'),
                                                   ('Content-Disposition', content_disposition(filename))])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

