# -*- coding: utf-8 -*-
from odoo import http, models, fields, api, _
from datetime import datetime
import calendar
from odoo.exceptions import RedirectWarning, UserError,ValidationError
import pytz
from dateutil.relativedelta import relativedelta

class CaeRetrieveWizard(models.TransientModel):
    _name = 'cae.retrieve.wizard'

    document_type_id = fields.Many2one('voucher.type',string="Tipo Documento",translate=True)
    pos_nr_id = fields.Many2one('pos.ar',string="Pto de Venta",translate=True)
    inv_number = fields.Char(string="Nro Factura",required=True)
    move_id = fields.Many2one('account.move',string="Factura")

    @api.onchange('move_id')
    def _onchange_move_id(self):
        self.document_type_id = self.move_id.voucher_type_id.id
        self.pos_nr_id = self.move_id.pos_ar_id.id
        if self.move_id.name[-8:].isnumeric():
            self.inv_number = self.move_id.name[-8:]

    def action_retrieve_cae(self):
        if not self.inv_number.isdigit():
            raise UserError(_("The Invoice Number field needs to be completed "
                              "with only numbers. Please try again."))
        if self.move_id.state == 'draft':
            self.move_id.retrieve_cae(self.document_type_id, self.pos_nr_id, self.inv_number)
            self.move_id.action_post()
        else:
            raise UserError(_("solo en estado Draft"))

class AccountMove(models.Model):
    _inherit = 'account.move'

    def write_wsfe_response2(self, invoice_detail, response):
        """ Escribe el envio y respuesta de un envio a AFIP """
        if True:
            # Nos traemos el offset de la zona horaria para dejar en la base en UTC como corresponde
            offset = datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).utcoffset().total_seconds() / 3600
            fch_proceso = datetime.strptime(response['ResultGet']['FchProceso'], '%Y%m%d%H%M%S') - relativedelta(hours=offset)
            result = response['ResultGet']['Resultado']
            date = fch_proceso

        self.env['wsfe.request.detail'].sudo().create({
            'invoice_ids': [(4, invoice.id) for invoice in self],
            'request_sent': invoice_detail,
            'request_received': response,
            'result': result,
            'date': date,
        })

    def retrieve_cae(self, document_type_id, pos_nr_id, inv_number):
        afip_code_dict = {
            '80': 'CUIT',
            '86': 'CUIL',
            '94': 'Pasaporte',
            '96': 'DNI',
            '97': 'CDI',
            '89': 'LE',
            '90': 'LC',
            '91': 'CI extranjera',
            '92': 'en tramite',
            '99': 'Sin identificar/venta global diaria',
        }
        afip_cur_dict = {
            'PES': 'ARS',
            'DOL': 'USD',
            '60': 'EUR',
            '12': 'BRL',
            '11': 'UYU',
            '33': 'CLP',
            '35': 'PEN',
            '19': 'CNY',
            '23': 'VEF',
            '21': 'GBP',
        }
        for invoice in self:
            afip_wsfe = invoice._get_wsfe()
            afip_wsfe.check_webservice_status()
            res, req = afip_wsfe.retrieve_cae(int(document_type_id.code), int(inv_number), int(pos_nr_id.name))
            print (res)
            if res['Errors']:
                raise UserError(res['Errors']['Err'][0]['Msg'])
            if res and 'ResultGet' in res.keys():
                if afip_code_dict[str(res['ResultGet']['DocTipo'])] != invoice.partner_id.partner_document_type_id.name:
                    raise UserError(_("Error: not the same document type"))
                if str(res['ResultGet']['DocNro']) != str(invoice.partner_id.vat):
                    raise UserError(_("Error: not the same Partner Document Numbrer"))
                if res['ResultGet']['MonId'] in afip_cur_dict.keys() and \
                        afip_cur_dict[res['ResultGet']['MonId']] != invoice.currency_id.name:
                    raise UserError(_("Error: not the same Currency"))
                if res['ResultGet']['MonCotiz'] != invoice.currency_rate:
                    if res['ResultGet']['MonId'] != 'PES':
                        raise UserError(_("Error: not the same Currency Rate"))
                if res['ResultGet']['ImpTotal'] != invoice.amount_total:
                    raise UserError(_("Error: not the same Amount Total"))
                if res['ResultGet']['CbteFch'] != invoice.invoice_date.strftime("%Y-%m-%d").replace('-',''):
                    raise UserError(_("Error: Your invoice date does not match with this Invoice Number at "
                                      "the AFIP Server. Please check your data"))


                thedate = res['ResultGet']['FchVto'][0:4] + '-' + res['ResultGet']['FchVto'][4:6] + '-' + res['ResultGet']['FchVto'][6:8]
                invoice.write({
                    'cae': res['ResultGet']['CodAutorizacion'],
                    'cae_due_date': thedate,
                })
                invoice.write_wsfe_response2(req, res)

