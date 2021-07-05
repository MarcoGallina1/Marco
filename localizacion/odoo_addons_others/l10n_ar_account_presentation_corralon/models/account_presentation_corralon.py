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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64


class AccountPresentationCorralon(models.Model):
    _name = "account.presentation.corralon"
    _description = "Presentación Corralón"

    name = fields.Char(string="Nombre", required=True)
    date_from = fields.Date(string="Fecha desde", required=True)
    date_to = fields.Date(string="Fecha hasta", required=True)
    minimum_amount = fields.Float(string="Monto mínimo", required=True)
    corralon_file = fields.Binary(string="Archivo", filename="filename", readonly=True)
    filename = fields.Char(string="Nombre de archivo", default=lambda self: self.get_filename())
    company_id = fields.Many2one(comodel_name="res.company", string="Compañía", default=lambda self: self.env.company)
    @api.constrains("minimum_amount")
    def check_minimum_amount_negative(self):
        if any(rec.minimum_amount < 0 for rec in self):
            raise ValidationError("El monto mínimo debe ser mayor o igual a 0.")

    @staticmethod
    def get_filename():
        return 'CORRALON_SICORE.txt'

    @staticmethod
    def get_corralon_query(date_from, date_to, company_id, minimum_amount):
        return """SELECT rpad(RP.name, 50) as name,
                CASE WHEN RDT.name = 'DNI' THEN '1'
                    ELSE '7'
                END as tdoc,
                CASE WHEN RP.vat is NULL THEN rpad('11111111',11)
                    ELSE rpad(RP.vat,11)
                END as ndoc,
                to_char(AM.invoice_date, 'DD-MM-YYYY') as date,
                AM.voucher_name as number,
                replace(to_char(AM.amount_total ,'fm00000000.0'),'.','') as total,
                rpad(RP.custom_street,40) as custom_street,
                RP.street_number as street_number,
                rpad(RP.city,40) as city,
                RP.zip as zip,
                RP.flat as flat,
                RP.department as department,
                AD.name as invoice_type
        FROM account_move as AM
        INNER JOIN res_country_state as RCS ON AM.jurisdiction_id = RCS.id
        INNER JOIN voucher_type as VC ON AM.voucher_type_id = VC.id
        INNER JOIN account_denomination as AD ON VC.denomination_id = AD.id
        INNER JOIN res_partner as RP ON AM.partner_id = RP.id
        INNER JOIN partner_document_type as RDT ON RDT.id = RP.partner_document_type_id
        WHERE
                RCS.code = 'B' and
                AM.type = 'out_invoice' and
                AM.invoice_date >= '{}' and
                AM.invoice_date <= '{}' and
                AM.company_id = {} and
                AM.amount_total >= {}
        ORDER BY
                AM.invoice_date""".format(date_from, date_to, company_id, minimum_amount)

    @staticmethod
    def get_corralon_reg_string(vals):
        return "{name};{tdoc};{ndoc};{date};{number};{blank:13};{total};{custom_street};{street_number:0>5};{street_code};{blank:0>6};{blank:6};\
{blank:3};{flat:0>3};{department:0>4};{blank:3};{city};{state_code:0>2};{zip:0>4};{blank:5};{blank:0>10};{blank:5};{blank:10};\
{blank:40};{comment};{blank:0>10};{locality};{invoice_type};".format(**vals, blank='')

    def generate_file(self):
        self.ensure_one()
        query_string = self.get_corralon_query(self.date_from, self.date_to, self.company_id.id, self.minimum_amount)
        self.env.cr.execute(query_string)

        regs = self.env.cr.dictfetchall()

        regs_string_list = []

        for reg in regs:

            if str(reg['tdoc']) != '1':
                reg['ndoc'] = '{}-{}-{}'.format(reg['ndoc'][0:2],reg['ndoc'][2:10],reg['ndoc'][10])

            reg['number'] = reg['number'].replace('-',';')

            if str(reg['street_number']).isdigit():
                reg['street_number'] = '{:0>5}'.format(reg['street_number'])
                reg['street_code'] = '0'
                reg['comment'] = '{:25}'.format('')
            else:
                reg['street_number'] = '{:0>5}'.format('')
                reg['street_code'] = '1'
                reg['comment'] = '{:25}'.format('NO SE INFORMA DIRECCION')

            reg['state_code'] = '2'

            reg['zip'] = reg['zip'] if str(reg['zip']).isdigit() else ''

            reg['locality'] = '2'

            regs_string_list.append(self.get_corralon_reg_string(reg))
        file_content = '\r\n'.join(regs_string_list)
        if file_content:
            corralon_file = base64.encodestring(file_content.encode())
            self.write({'corralon_file': corralon_file})
        else:
            raise ValidationError("No se encontró ninguna factura coincidente con los parámetros utilizados.")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
