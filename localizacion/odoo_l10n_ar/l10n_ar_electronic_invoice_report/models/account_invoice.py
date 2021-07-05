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

from odoo import models, fields, _
from odoo.exceptions import ValidationError
import num2words
import ast
import base64
from datetime import datetime
from l10n_ar_api.afip_webservices.wsfe.qr_generator import QrGeneratorElectronicInvoice
from io import BytesIO


class AccountMove(models.Model):
    _inherit = 'account.move'

    def invoice_print(self):
        """
        En el caso de que la factura tenga un talonario del tipo electronico
        se imprime el reporte de factura electronica.
        """
        res = super(AccountMove, self).invoice_print()
        self.ensure_one()

        if self.document_book_type == 'electronic':
            res = self.env.ref('l10n_ar_electronic_invoice_report.action_electronic_invoice').report_action(self)

        return res

    def get_qr_code(self):
        """
        Devuelve el codigo QR del documento segun
        Resoluci�n General A.F.I.P. 4892/2020
        https://www.afip.gob.ar/fe/qr/vigencia-y-aplicacion.asp
        """

        wsfe_request = self.wsfe_request_detail_ids.filtered(lambda x: x.result == 'A')
        try:
            request = ast.literal_eval(
                wsfe_request[0].request_sent
            )
            response = ast.literal_eval(
                wsfe_request[0].request_received
            )
            request_received = wsfe_request[0].request_received
            res = getattr(self, 'get_qr_code{}'.format(request_received.split('\'')[1]))(request, response)
        except Exception:
            if self.cae:
                # En este caso al no haber respuesta de la Afip, debo tomar datos de la factura.
                res = self.get_qr_from_invoice_data()
            else:
                # Este caso no deberia darse nunca.
                res = ""

        qr = QrGeneratorElectronicInvoice(res)
        # Desde el punto de venta se puede configurar si se quiere invertir los colores del QR.
        qr.reverse_color = self.pos_ar_id.invert_colors_qr
        qr.generate_qr()
        qr_img = qr.get_qr_image()
        buffered = BytesIO()
        qr_img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue())

    def get_qr_from_invoice_data(self):
        """
        Esta funcion se utiliza en el caso de no haber respuesta de la Afip,
        y retorna un diccionario con los datos directamente sacados de la factura para la generacion del QR.
        """
        data = {
            # La especificación del JSON con los datos del comprobante  (versión 1)
            'ver': int(1),
            "fecha": str(datetime.strftime(datetime.now(), '%Y-%m-%d')
                         if not self.invoice_date or fields.Date.context_today(self) else self.invoice_date),
            "cuit": int(self.company_id.partner_id.vat),
            "ptoVta": int(self.voucher_name.split('-')[0]),
            "tipoCmp": int(self.voucher_type_id.code),
            "nroCmp": int(self.voucher_name.split('-')[1]),
            "importe": float(round(self.amount_total, 2)),
            "moneda": str(self.env['codes.models.relation'].get_code(
                'res.currency',
                self.currency_id.id
            )),
            "ctz": float(self.currency_rate or self.convert_currency(
                from_currency=self.currency_id,
                to_currency=self.company_id.currency_id,
                d=self.invoice_date or fields.Date.context_today(self)
                ) if self.need_rate else 1
                ),
            # “E” para comprobante autorizado por CAE
            'tipoCodAut': "E",
            "codAut": int(self.cae)
        }
        cuit = self.env['codes.models.relation'].get_code(
            'partner.document.type',
            self.partner_id.partner_document_type_id.id
        )
        if cuit and self.partner_id.vat:
            data['nroDocRec'] = int(self.partner_id.vat)
            data['tipoDocRec'] = int(cuit)

        return data

    def _get_qr_code_BFEResultAuth(self, request, response):
        data = {
            # La especificación del JSON con los datos del comprobante  (versión 1)
            'ver': int(1),
            "fecha": str(response.get('BFEResultAuth').get('Fch_cbte')),
            "cuit": int(response.get('BFEResultAuth').get('Cuit')),
            "ptoVta": int(request.get('Punto_vta')),
            "tipoCmp": int(request.get('Tipo_cbte')),
            "nroCmp": int(request.get('Cbte_nro')),
            "importe": float(request.get('Imp_total')),
            "moneda": str(request.get('Imp_moneda_Id')),
            "ctz": float(request.get('Imp_moneda_ctz')),
            # “E” para comprobante autorizado por CAE
            'tipoCodAut': "E",
            "codAut": int(response.get('BFEResultAuth').get('Cae'))
        }

        if request.get('Nro_doc') and request.get('Tipo_doc'):
            data['nroDocRec'] = int(request.get('Nro_doc'))
            data['tipoDocRec'] = int(request.get('Tipo_doc'))

        return data

    def _get_qr_code_FeCabResp(self, request, response):
        list_FECAED = response.get('FeDetResp').get('FECAEDetResponse')
        list_FECAEDetRequest = request.get('FeDetReq').get('FECAEDetRequest')

        invoice_data = {

            # La especificación del JSON con los datos del comprobante  (versión 1)
            'ver': int(1),
            "fecha": str(list_FECAED[0].get('CbteFch')),
            "cuit": int(response.get('FeCabResp').get('Cuit')),
            "ptoVta": int(response.get('FeCabResp').get('PtoVta')),
            "tipoCmp": int(response.get('FeCabResp').get('CbteTipo')),
            "nroCmp": int(list_FECAED[0].get('CbteDesde')),
            "importe": float(list_FECAEDetRequest[0].get('ImpTotal')),
            "moneda": str(list_FECAEDetRequest[0].get('MonId')),
            "ctz": float(list_FECAEDetRequest[0].get('MonCotiz')),
            # “E” para comprobante autorizado por CAE
            'tipoCodAut': "E",
            "codAut": int(list_FECAED[0].get('CAE'))
        }
        # Elementos necesarios DE CORRESPONDER
        if list_FECAED[0].get('DocNro') and list_FECAED[0].get('DocTipo'):
            invoice_data['nroDocRec'] = int(list_FECAED[0].get('DocNro'))
            invoice_data['tipoDocRec'] = int(list_FECAED[0].get('DocTipo'))

        return invoice_data

    def _get_qr_code_FEXResultAuth(self, request, response):
        invoice_data_factura_exportacion = {
            # La especificación del JSON con los datos del comprobante  (versión 1)
            'ver': int(1),
            "fecha": str(response.get('FEXResultAuth').get('Fch_cbte')),
            "cuit": int(response.get('FEXResultAuth').get('Cuit')),
            "ptoVta": int(response.get('FEXResultAuth').get('Punto_vta')),
            "tipoCmp": int(response.get('FEXResultAuth').get('Cbte_tipo')),
            "nroCmp": int(response.get('FEXResultAuth').get('Cbte_nro')),
            "importe": float(request.get('Imp_total')),
            "moneda": str(request.get('Moneda_Id')),
            "ctz": float(request.get('Moneda_ctz')),
            # “E” para comprobante autorizado por CAE
            'tipoCodAut': "E",
            "codAut": int(response.get('FEXResultAuth').get('Cae'))
        }
        return invoice_data_factura_exportacion

    def validate_electronic_invoice_fields(self):
        """
        Valida que esten los campos necesarios para la impresión del reporte de factura electronica
        """
        self.ensure_one()
        company = self.company_id
        if not (company.start_date and company.iibb_number and company.street and company.city):
            raise ValidationError("Antes de imprimir, configurar la fecha de inicio de actividades"
                                  ", numero de IIBB y direccion de la empresa")

        if not self.cae:
            raise ValidationError("No se puede imprimir un documento sin CAE")

        if self.state != 'posted':
            raise ValidationError("No se puede imprimir un documento en estado borrador o cancelado")

    def get_invoice_total_as_numbers(self):
        lang = 'us'
        if self.partner_id.lang == 'es_AR':
            lang = 'es_CO'
        amount_in_words = num2words.num2words(self.amount_total, lang=lang, to='currency')
        return 'SON {} {}'.format(self.currency_id.name, amount_in_words.upper())

    def get_sales_client_order_ref(self):
        sales_client_order_ref_list = self.mapped('invoice_line_ids.sale_line_ids.order_id').filtered(
            lambda x: x.client_order_ref).mapped('client_order_ref')
        return ', '.join(sales_client_order_ref_list) if sales_client_order_ref_list else ''

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
