# -*- coding: utf-8 -*-
from odoo import http, models, fields, api, _
from odoo.exceptions import RedirectWarning, UserError,ValidationError
from datetime import datetime, timedelta
import io
import base64


class EarcibaFiles(models.Model):
    _name = 'earciba.files'
    _desc = 'earciba.files'
    _order = 'name desc'

    name = fields.Char(string="Name",required=True,translate=True)
    date_from = fields.Date(string="Date From",required=True,translate=True)
    date_to = fields.Date(string="Date To",required=True,translate=True)
    percep_tax_code_ids = fields.Many2many('perception.perception',string="Perception Tax Code",translate=True,required=True,
        domain="[('type', '=', 'gross_income'),('jurisdiction', '=', 'provincial'),('type_tax_use', '=', 'sale')]")
    with_tax_code_ids = fields.Many2many('retention.retention',string="Withholding Tax Code",translate=True,required=True,
        domain="[('type', '=', 'gross_income'),('jurisdiction', '=', 'provincial'),('type_tax_use', '=', 'purchase')]")
    earciba_wh_perc = fields.Binary('Download eArciba Whold Perc',translate=True)
    earciba_wh_perc_name = fields.Char('eArciba Whold Perc', size=64,translate=True)
    earciba_cred_motes = fields.Binary('Download eArciba Cred Notes',translate=True)
    earciba_cred_notes_name = fields.Char('eArciba Cred Notes', size=64,translate=True)
    company_id = fields.Many2one('res.company',string="Company",translate=True,default=lambda self: self.env.company.id)
    generation_time = fields.Datetime(string="Fecha y hora de generacion",translate=True)

    _sql_constraints = [
        ('dates_name', 'unique (name, date_from, date_to)', _('The name and Date From and Date To combination must be Unique'))
    ]

    def generate_files(self):
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            #('payment_id.state', 'not in', ('draft', 'cancel')),
            #('payment_id.payment_type', '=', 'inbound'),
            ('company_id', '=', self.env.company.id),
            ('retention_id', 'in', list(self.with_tax_code_ids._ids)),
        ]
        rets = self.env['account.payment.retention'].search(domain)
        #print (rets)

        domain2 = [
            ('date_invoice', '>=', self.date_from),
            ('date_invoice', '<=', self.date_to),
            ('perception_id', 'in', list(self.percep_tax_code_ids._ids)),
            ('company_id', '=', self.env.company.id),
            #('move_id.state', '!=', 'draft'),
        ]
        perceps = self.env['account.invoice.perception'].search(domain2)
        #print (perceps)

        tstr = ""
        tstrnc = ""
        if not self.date_from <= self.date_to:
            raise UserError(_("Error: las fechas no tienen un rago valido"))
        else:
            the_date = fields.Date.from_string(self.date_from)
            while (the_date <= self.date_to):
                for ret in rets:
                    if  ret.date == the_date:
                        rate = 1
                        if ret.payment_id.currency_id != ret.payment_id.company_id.currency_id:
                            rate = ret.payment_id.currency_rate
                        tstr += "1"
                        tstr += ret.retention_id.norm_code
                        dd = fields.Date.to_string(ret.date).replace('-','')
                        tstr += dd[6:8] + '/' + dd[4:6] + '/' + dd[0:4]
                        tstr += "03"
                        tstr += " "
                        tmp = ret.payment_id.name[-14:].replace('-','').replace(' ','')
                        tmp = ''.join(i for i in tmp if i.isdigit())
                        tstr += "{:0>16}".format(tmp)
                        dd = fields.Date.to_string(ret.date).replace('-','')
                        tstr += dd[6:8] + '/' + dd[4:6] + '/' + dd[0:4]
                        tstr += "{:0>16}".format(str("{:.2f}".format(sum(ret.payment_id.invoice_ids.mapped('amount_total'))*rate)))
                        tstr += "{:<16}".format(ret.certificate_no)
                        tstr += ret.partner_id.partner_document_type_id.arciba_doc_type
                        tstr += ret.partner_id.vat
                        tstr += ret.partner_id.iibb_sit
                        if ret.partner_id.iibb_number:
                            tstr += ret.partner_id.iibb_number
                        else:
                            tstr += "?????"
                        tstr += str(ret.payment_id.invoice_ids[0].fiscal_position_id.arciba_code)
                        tstr += "{:<30}".format(ret.partner_id.name[0:30])
                        tmp = sum(ret.payment_id.retention_ids.filtered(lambda x: x.retention_id.state_id.code != 'C').mapped('amount'))*rate
                        tstr += "{:0>16}".format(str("{:.2f}".format(tmp)))
                        tstr += "{:0>16}".format('0')
                        tstr += "\n"

                for perc in perceps:
                    if  perc.date_invoice == the_date:
                        if perc.move_id.type != 'out_refund':
                            rate = 1
                            if perc.move_id.currency_id != perc.move_id.company_id.currency_id:
                                rate = perc.move_id.currency_rate
                            tstr += "2"
                            tstr += perc.perception_id.norm_code
                            dd = fields.Date.to_string(perc.date_invoice).replace('-','')
                            tstr += dd[6:8] + '/' + dd[4:6] + '/' + dd[0:4]
                            if perc.move_id.voucher_type_id.code in (1,2,6,7,11,12,51,52):
                                tstr += "01"
                            elif perc.move_id.voucher_type_id.code == 99:
                                tstr += "09"
                            elif perc.move_id.voucher_type_id.code in (201,202,206,207,211,21):
                                tstr += "10"
                            else:
                                tstr += "  "

                            tstr += perc.move_id.voucher_type_id.denomination_id.name
                            tmp = perc.move_id.name[-14:].replace('-', '')
                            tstr += "{:0>16}".format(tmp)
                            dd = fields.Date.to_string(perc.date_invoice).replace('-','')
                            tstr += dd[6:8] + '/' + dd[4:6] + '/' + dd[0:4]
                            tstr += "{:0>16}".format(str("{:.2f}".format(perc.move_id.amount_total*rate)))
                            tstr += "{:<16}".format(" ")
                            tstr += perc.partner_id.partner_document_type_id.arciba_doc_type
                            tstr += perc.partner_id.vat
                            tstr += str(perc.partner_id.iibb_sit)
                            tstr += str(perc.partner_id.iibb_number)
                            tstr += str(perc.move_id.fiscal_position_id.arciba_code)
                            tstr += "{:<30}".format(perc.partner_id.name[0:30])
                            tmp = sum(perc.move_id.perception_ids.filtered(lambda x: x.perception_id.state_id.code != 'C').mapped('amount'))*rate
                            tstr += "{:0>16}".format(str("{:.2f}".format(tmp)))
                            tmp = 0
                            name = perc.move_id.name.split(" ")
                            if name[1] in ('A','M'):
                                print (perc.move_id.name)
                                for line in perc.move_id.line_ids:
                                    for tax in line.tax_ids:
                                        if tax.amount_type == 'percent' and tax.type_tax_use == 'sale' and \
                                            tax.is_vat == True and tax.active == True:
                                                tmp += line.price_subtotal * tax.amount / 100

                            tstr += "{:0>16}".format(str("{:.2f}".format(tmp*rate)))
                            tstr += "\n"
                        else:
                            foundf = False
                            nc = self.env['account.move']
                            for line in perc.move_id.fce_associated_document_ids:
                                nc = line.associated_invoice_id
                                if nc.invoice_date >= self.date_from and nc.invoice_date <= self.date_to \
                                        and nc.amount_total == perc.move_id.amount_total:
                                    foundf = True
                                    pass
                            if foundf:
                                rate = 1
                                if perc.move_id.currency_id != perc.move_id.company_id.currency_id:
                                    rate = perc.move_id.currency_rate
                                tstrnc += "2"
                                tmp = perc.move_id.name[-14:].replace('-', '')[-12:]
                                tstrnc += "{:<12}".format(tmp)
                                dd = fields.Date.to_string(perc.date_invoice).replace('-','')
                                tstrnc += dd[6:8] + '/' + dd[4:6] + '/' + dd[0:4]
                                tstrnc += "{:0>16}".format(str("{:.2f}".format(perc.move_id.amount_total*rate)))
                                tstrnc += "{:<16}".format(" ")
                                if nc.voucher_type_id.code in (1,2,6,7,11,12,51,52):
                                    tstrnc += "01"
                                elif nc.voucher_type_id.code == 99:
                                    tstrnc += "09"
                                elif nc.voucher_type_id.code in (201,202,206,207,211,21):
                                    tstrnc += "10"
                                else:
                                    tstrnc += "  "
                                tstrnc += perc.move_id.voucher_type_id.denomination_id.name
                                tmp = perc.move_id.name[-14:].replace('-', '')
                                tstrnc += "{:0>16}".format(tmp)
                                tmp = perc.move_id.partner_id.vat.replace('-', '')
                                tstrnc += "{:0>11}".format(tmp)

                                #tmp = perc.move_id.fce_associated_document_ids[0].associated_invoice_id.name[-14:].replace('-', '')
                                #tstrnc += "{:0>16}".format(tmp)
                                tstrnc += perc.perception_id.norm_code[-3:]
                                dd = fields.Date.to_string(perc.date_invoice).replace('-','')
                                tstrnc += dd[6:8] + '/' + dd[4:6] + '/' + dd[0:4]
                                tstrnc += "{:0>16}".format(str("{:.2f}".format(perc.amount*rate)))
                                tstrnc += "{:0>5}".format(str("{:.2f}".format(perc.aliquot)))
                                tstrnc += "\n"


                the_date = the_date + timedelta(days=1)

        print (tstr)
        sio = io.StringIO(tstr)
        fp = io.BytesIO(sio.read().encode('utf8'))
        self.write({'earciba_wh_perc': base64.b64encode(fp.read()), 'earciba_wh_perc_name': "eARCIBA_Retention_Perception.TXT"})
        sio = io.StringIO(tstrnc)
        fp = io.BytesIO(sio.read().encode('utf8'))
        self.write({'earciba_cred_motes': base64.b64encode(fp.read()), 'earciba_cred_notes_name': "eARCIBA_Cred_Notes.TXT"})





