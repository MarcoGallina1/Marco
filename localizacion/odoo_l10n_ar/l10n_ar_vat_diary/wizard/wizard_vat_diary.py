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
from odoo import models, fields, http, api
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception, content_disposition


class WizardVatDiary(models.TransientModel):
    _name = 'wizard.vat.diary'
    _description = 'Wizard de subdiario de IVA'

    type = fields.Selection([
        ('sales', 'Ventas'),
        ('purchases', 'Compras')
    ], 'Tipo', required=True)
    include_suffered_retentions = fields.Boolean(string="Incluir retenciones sufridas")
    separate_not_taxable_from_exempt = fields.Boolean(string="Separar No Gravado y Exento")
    date_from = fields.Date('Desde', required=True)
    date_to = fields.Date('Hasta', required=True)
    report = fields.Binary('Reporte')

    @api.onchange('type')
    def onchange_type(self):
        self.include_suffered_retentions = False

    @api.constrains('date_from', 'date_to')
    def validate_date_range(self):
        if self.date_from > self.date_to:
            raise ValidationError("Rango invalido de fechas")
    
    def _get_retentions_search_domain(self):
        return [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('payment_id.state', 'not in', ('draft', 'cancelled')),
            ('payment_id.payment_type', '=', 'inbound'),
            ('company_id', '=', self.env.company.id)
        ]

    def _get_retentions(self):
        domain = self._get_retentions_search_domain()
        retentions = self.env['account.payment.retention'].search(domain)
        return retentions

    def _get_invoices_search_domain(self):
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('state', 'not in', ('draft', 'cancel')),
            ('company_id', '=', self.env.company.id),
            ('fiscal_position_id.show_vat_diary', '=', True),
        ]
        if self.type == 'sales':
            domain.append(('type', 'in', ('out_invoice', 'out_refund')))
        else:
            domain.append(('type', 'in', ('in_invoice', 'in_refund')))
        return domain

    def _get_invoices(self):
        domain = self._get_invoices_search_domain()
        invoices = self.env['account.move'].search(domain)

        return invoices

    def _get_taxes_position(self, invoices, retentions=None):
        """
        Devuelve los impuestos de las facturas en un diccionario con un valor distinto para cada uno
        :param invoices: account.invoice - Del cual se obtendran todos los impuestos
        :param retentions: account.payment.retention o None - Del cual se obtendran los impuestos de retenciones
        :return dict: de la forma {account.tax(): posicion}
        """

        res = {}
        position = 0

        taxes = invoices.mapped('line_ids').filtered(
            lambda l: l.price_subtotal or (l.tax_line_id.is_vat and not l.tax_line_id.is_exempt)
        ).mapped('tax_line_id')
        
        if retentions:
            taxes |= retentions.mapped('retention_id').mapped('tax_id')
        
        # Ordenamos los impuestos para tener el IVA primero y removemos duplicados
        sorted_taxes = taxes.sorted(key=lambda x: (not x.is_vat, x.name))

        # Para el iva vamos a utilizar no solo el valor si no la base imponible
        for tax in sorted_taxes:
            res[tax] = position
            position += 2 if tax.is_vat else 1

        return res
    
    def get_last_position(self, taxes_position):
        # Obtenemos el ultimo impuesto para saber en que columna van los totales
        if taxes_position:
            last_tax = max(taxes_position, key=taxes_position.get)
            last_position = taxes_position[last_tax] + (2 if last_tax.is_vat else 1)
        else:
            last_position = 0
        return last_position

    def _get_header(self):
        """ Genero un diccionario con los valores basicos de la cabecera del reporte """
        header = {
            0: 'Fecha',
            1: 'Razon Social',
            2: 'Doc. Numero',
            3: 'Condicion IVA',
            4: 'Tipo',
            5: 'Comprobante',
            6: 'Jurisdiccion'
        }
        return header

    def get_header_values(self, taxes_position):
        """
        Crea la estructura de datos para la cabecera del reporte
        :param taxes_position: diccionario que contiene la posicion del impuesto y el impuesto
        :return header: diccionario con la posicion y valor, ej: {0: 'Fecha', 1: 'Razon Social'..}
        """
        header = self._get_header()
        last_header_position = len(header)
        for tax in taxes_position:
            if tax.is_vat:
                header[taxes_position[tax] + last_header_position] = tax.name + ' - Base'
                header[taxes_position[tax] + last_header_position + 1] = tax.name + ' - Importe'
            else:
                header[taxes_position[tax] + last_header_position] = tax.name

        if taxes_position:
            last_tax = max(taxes_position, key=taxes_position.get)
            last_position = taxes_position[last_tax] + (2 if last_tax.is_vat else 1)
        else:
            last_position = 0
        if self.separate_not_taxable_from_exempt:
            header[last_position + last_header_position] = 'No Gravado'
            header[last_position + last_header_position + 1] = 'Exento'
            header[last_position + last_header_position + 2] = 'Total'
        else:
            header[last_position + last_header_position] = 'No Gravado/Exento'
            header[last_position + last_header_position + 1] = 'Total'

        return header

    def _get_invoice_values(self, invoice, last_position, size):
        """ Seteo los valores para cada posicion de una fila"""
        vals = {
            0: invoice.invoice_date.strftime('%d/%m/%Y'),
            1: invoice.partner_id.name,
            2: invoice.partner_id.vat or '',
            3: invoice.fiscal_position_id.name or '',
            4: invoice.voucher_type_id.name or '',
            5: invoice.name,
            6: invoice.jurisdiction_id.name or invoice.partner_id.state_id.name or '',
        }
        if self.separate_not_taxable_from_exempt:
            vals[last_position + size + 2] = invoice.get_vat_diary_total()
        else:
            vals[last_position + size + 1] = invoice.get_vat_diary_total()
        return vals
    
    def _get_retention_values(self, retention, last_position, size):
        """ Seteo los valores para cada posicion de una fila"""
        if retention.certificate_no:
            name = "RET {}".format(retention.certificate_no)
        else:
            name = "{}".format(retention.payment_id.name)
        vals = {
            0: retention.date.strftime('%d/%m/%Y'),
            1: retention.partner_id.name,
            2: retention.partner_id.vat or '',
            3: retention.partner_id.property_account_position_id.name or '',
            4: 'RETENCION',
            5: name,
            6: retention.jurisdiction,
        }
        # Si se seleccionó para separar no gravado de exento debo mover los totales
        # de las retenciones una columna más para que no caigan en la de exento
        if self.separate_not_taxable_from_exempt:
            vals[last_position + size + 2] = retention.get_vat_diary_total()
        else:
            vals[last_position + size + 1] = retention.get_vat_diary_total()
        return vals
    
    def get_invoices_details(self, taxes_position, invoices, size_header, last_position):
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
            invoice_values = self._get_invoice_values(invoice, last_position, size_header)
            invoice.with_context(separate_not_taxable_from_exempt=self.separate_not_taxable_from_exempt).update_vat_diary_values(taxes_position, invoice_values, size_header)

            res.append(invoice_values)
        return res
    
    def get_retentions_details(self, taxes_position, retentions, size_header, last_position):
        """
        Crea la estructura de datos para los detalle del reporte, los cuales son datos de invoices,
        o de retenciones si estas fueran informadas.
        :param taxes_position: diccionario que contiene la posicion del impuesto y el impuesto
        :param retentions: account.payment.retention o None - De donde se tomaran los datos segun filtros del wizard
        :size_header: int - Tamaño del encabezado
        :last_position: int - Indice de la última posición de las columnas
        :return: lista de diccionarios, cada uno con la posicion y valor, ej: {0: '01/01/2000'}
        """
        res = []
        for retention in retentions:
            retention_values = self._get_retention_values(retention, last_position, size_header)
            retention.with_context(separate_not_taxable_from_exempt=self.separate_not_taxable_from_exempt).update_vat_diary_values(taxes_position, retention_values, size_header)

            res.append(retention_values)
        return res

    def get_details_values(self, taxes_position, invoices, retentions=None):
        """
        Crea la estructura de datos para los detalle del reporte, los cuales son datos de invoices,
        o de retenciones si estas fueran informadas.
        :param taxes_position: diccionario que contiene la posicion del impuesto y el impuesto
        :param invoices: account.invoice - De donde se tomaran los datos segun filtros del wizard
        :param retentions: account.payment.retention o None - De donde se tomaran los datos segun filtros del wizard
        :return: lista de diccionarios, cada uno con la posicion y valor, ej: {0: '01/01/2000'}
        """
        res = []

        last_position = self.get_last_position(taxes_position)

        size_header = len(self._get_header())
        
        invoices_details = self.get_invoices_details(taxes_position, invoices, size_header, last_position)
        res.extend(invoices_details)
        if retentions:
            retentions_details = self.get_retentions_details(taxes_position, retentions, size_header, last_position)
            res.extend(retentions_details)

        return res
    
    def sort_detail_values(self, detail_values):
        # Ordeno por fecha, tipo y nombre según las claves de los dict
        # devueltos por _get_invoice_values y _get_retention_values
        return sorted(detail_values, key=lambda x: (x.get(0), x.get(4), x.get(5)))

    def get_report_values(self):
        """
        Devuelve los datos de cabecera y detalles del reporte a armar de las invoices obtenidas del wizard
        :return list: Lista de diccionarios con la cabecera y detalles
            [{0: 'Fecha',...}{0: '01/01/2000,...}]
        """

        invoices = self._get_invoices()
        if self.include_suffered_retentions:
            retentions = self._get_retentions()
            if not (invoices or retentions):
                raise ValidationError("No se han encontrado documentos para ese rango de fechas")
            taxes_position = self._get_taxes_position(invoices, retentions)
            header = self.get_header_values(taxes_position)
            details = self.get_details_values(taxes_position, invoices, retentions)
            details = self.sort_detail_values(details)
        else:
            if not invoices:
                raise ValidationError("No se han encontrado documentos para ese rango de fechas")
            taxes_position = self._get_taxes_position(invoices)
            header = self.get_header_values(taxes_position)
            details = self.get_details_values(taxes_position, invoices)
            details = self.sort_detail_values(details)

        return [header] + details

    def generate_xls_report(self):
        """ Crea un xls con los valores obtenidos de get_report_values"""
        values = self.get_report_values()

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
        sheet.col(0).width = 2500
        sheet.col(1).width = 6000
        sheet.col(2).width = 4000
        sheet.col(3).width = 6000
        sheet.col(4).width = 5000
        sheet.col(5).width = 5000
        sheet.col(6).width = 4000

        row_number = 0
        total_cols = 0
        # Header
        for col in values[0]:
            # Le asignamos el ancho a las columnas de importes
            if total_cols > 7:
                sheet.col(col).width = 3500
            sheet.write(row_number, col, values[0][col], style)
            total_cols += 1

        # Detalles
        row_number += 1
        for value in values[1:]:
            for col in value:
                sheet.write(row_number, col, value[col])
            row_number += 1
        header = self._get_header()
        size_header = len(header)
        for x in range(size_header, total_cols):
            column_start = xlwt.Utils.rowcol_to_cell(1, x)
            column_end = xlwt.Utils.rowcol_to_cell(row_number - 1, x)
            sheet.write(row_number, x, xlwt.Formula('SUM(' + column_start + ':' + column_end + ')'))

        # Exportamos y guardamos
        file_data = io.BytesIO()
        wbk.save(file_data)
        out = base64.encodebytes(file_data.getvalue())
        self.report = out

        date_from = self.date_from.strftime('%d-%m-%Y')
        date_to = self.date_to.strftime('%d-%m-%Y')

        filename = 'Subdiario ' + name + ' ' + date_from + ' a ' + date_to

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_vat_diary?wizard_id=%s&filename=%s' % (self.id, filename + '.xls'),
            'target': 'new',
        }

class WizardVatDiaryRoute(http.Controller):
    @http.route('/web/binary/download_vat_diary', type='http', auth="public")
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
