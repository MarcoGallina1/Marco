# -*- coding: utf-8 -*-
from odoo import http, models, fields, api, _
import base64
from odoo.exceptions import UserError

class ImportVendorBills(models.TransientModel):
    _name = 'import.vendor.bills'

    date_from = fields.Date(string="Date From",require=True)
    date_to = fields.Date(string="Date To",require=True)
    csv_file = fields.Binary(string="Load File")
    #default_product_id = fields.Many2one('product.product',string="Default Product")
    csv_file_name = fields.Char(string="File Name")

    def doit(self):
        # if not self.date_from:
        #     raise UserError(_("please fill date from in form"))
        # if not self.date_to:
        #     raise UserError(_("please fill date to in form"))
        if self.csv_file:
            file_content = base64.b64decode(self.csv_file).decode('utf-8')
            file_content = file_content.replace("\"","")
            #file_content = file_content.replace(".", "")
            #file_content = file_content.replace(",", ".")
            #file_content = file_content.replace(";",",")
            #file_content = file_content.replace("=", "")
            #file_content = file_content.replace(" ", "")
            lines = file_content.split('\n')
            del lines[0]

            for line in lines:
                list_line = line.split(',')
#['17/09/2020', '1-FacturaA', '1', '74', '', '70383435094124', 'CUIT', '30716095173', 'REMIXCOMSRL', '1', '$', '50400', '0', '0', '10584', '60984']
                if len(list_line) > 5:
                    id_number = self.env['res.partner'].search([('vat', '=', list_line[7])],limit=1)
                    defaults = self.env.user.company_id
                    if not id_number:
                        if not defaults.def_expense_product_id.id:
                            raise UserError(_("at least fill default product code in settings"))
                        id_category = self.env['partner.document.type'].search([('name', '=', list_line[6])])
                        code = list_line[1].split('-')[0].replace(' ','')
                        if code in ('11', '12', '13', '15', '16', '68', '211', '212', '213') \
                                and list_line[7][0:1] == '3':
                            code = '4'
                        if code in ('11', '12', '13', '15', '16', '68', '211', '212', '213') \
                                and list_line[7][0:1] == '2':
                            code = '6'
                        resp_type = self.env['account.fiscal.position'].search([('afip_code', '=', code)])
                        partner = self.env['res.partner'].create({
                            'name': list_line[8],
                            'partner_document_type_id': id_category.id,
                            'default_product_id': defaults.def_expense_product_id.id,
                            'supplier_rank': 1,
                            'customer_rank': 0,
                            'company_type': 'company',
                            'property_account_position_id': resp_type.id,
                            'vat': list_line[7],
                        })
                    else:
                        partner = self.env['res.partner'].search([('vat', '=', list_line[7])],limit=1)

                    voucher_id = self.env['voucher.type'].search([('code', '=', list_line[1].replace(" ", "").split('-')[0])],limit=1)

                    currency = self.env['res.currency'].search(['|', ('name', '=', list_line[10]),('symbol', '=', list_line[10])],limit=1)
                    date_invoice = list_line[0][6:10] + '-' + list_line[0][3:5] + '-' + list_line[0][0:2]

                    prev_invs = self.env['account.move'].search([
                        ('partner_id', '=', partner.id),
                        ('voucher_name', '=', "{:0>5}".format(list_line[2]) + '-' + "{:0>8}".format(list_line[3])),
                        ('invoice_date', '=', date_invoice),
                        ('import_afip_file_flag', '=', True),
                    ])
                    if not prev_invs:
                        type = 'in_invoice'
                        if list_line[1].replace(" ", "").split('-')[0] in ('3','8','13','21','53','203','208','213'):
                            type = 'in_refund'
                        invoice = self.env['account.move'].create({
                            'journal_id': self.env['account.journal'].search([
                                ('type', '=', 'purchase'),('no_documents','=',False)],limit=1).id,
                            'currency_id': currency.id,
                            'partner_id': partner.id,
                            'partner_shipping_id': partner.address_get(['delivery'])['delivery'],
                            'invoice_date': date_invoice,
                            'invoice_date_due': date_invoice,
                            'date': date_invoice,
                            'type': type,
                            'voucher_type_id': voucher_id.id,
                            'voucher_name': "{:0>5}".format(list_line[2]) + '-' + "{:0>8}".format(list_line[3]),
                            'currency_rate': list_line[9],


                            'import_date': fields.Datetime.now(),
                            'import_afip_file_flag': True,
                            'import_user_id': self.env.user.id,
                            'import_cae': list_line[5],
                            'import_inv_type': list_line[1].split('-')[0].replace(' ',''),
                            'import_inv_currrency': list_line[10],
                            'import_taxable_nett_amount': list_line[11],
                            'import_non_taxable_nett_amount': list_line[12],
                            'import_exempt_amount': list_line[13],
                            'import_vat_amount': list_line[14],
                            'import_tot_amount': list_line[15],
                        })
                        nett_tax = list_line[11]
                        nett_no_tax = list_line[12]
                        exempt = list_line[13]
                        vat_ = list_line[14]
                        tot = list_line[15]
                        if not partner.default_product_id:
                            prod = defaults.def_expense_product_id
                        else:
                            prod = partner.default_product_id
                        price = 0
                        if tot and tot!='0':
                            price = float(tot)
                            vat = defaults.vat_monotribute_id
                        if nett_tax and nett_tax!='0':
                            price = float(nett_tax)
                            vat = defaults.vat_resp_insc_id
                        #print vat
                        print ('nett_no_tax',nett_no_tax)
                        print ('exempt',exempt)
                        if price:
                            print (1)
                            line = self.env['account.move.line'].create({
                                'move_id': invoice.id,
                                'product_id': prod.id,
                                'name': prod.name,
                                'account_id': prod.property_account_expense_id.id,
                            })
                            line._onchange_product_id()
                            cur = invoice.currency_id
                            if invoice.currency_id.id == invoice.company_id.currency_id.id:
                                cur = self.env['res.currency']
                            line.with_context(check_move_validity=False).write({
                                    'tax_ids': [(6,0,[vat.id])],
                                    'price_unit': price,
                                    #'debit': price,
                                    'account_id': prod.property_account_expense_id.id,
                                    'partner_id': invoice.partner_id.commercial_partner_id.id,
                                    'date': invoice.date,
                                    'recompute_tax_line': True,
                                    'currency_id': cur.id,
                            })

                        invoice.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes=True, recompute_tax_base_amount=True)
                        if nett_no_tax and nett_no_tax!='0':
                            print (2)
                            price = float(nett_no_tax)
                            vat = defaults.non_taxable_amount_id
                            line = self.env['account.move.line'].create({
                                'move_id': invoice.id,
                                'product_id': prod.id,
                                'name': prod.name,
                                'account_id': prod.property_account_expense_id.id,
                            })
                            line._onchange_product_id()
                            cur = invoice.currency_id
                            if invoice.currency_id.id == invoice.company_id.currency_id.id:
                                cur = self.env['res.currency']
                            line.with_context(check_move_validity=False).write({
                                    'tax_ids': [(6,0,[vat.id])],
                                    'price_unit': price,
                                    #'debit': price,
                                    'account_id': prod.property_account_expense_id.id,
                                    'partner_id': invoice.partner_id.commercial_partner_id.id,
                                    'date': invoice.date,
                                    'recompute_tax_line': True,
                                    'currency_id': cur.id,
                            })

                        invoice.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes=True, recompute_tax_base_amount=True)
                        if exempt and exempt!='0':
                            print (3)
                            price = float(exempt)
                            vat = defaults.exempt_amount_id
                            line = self.env['account.move.line'].create({
                                'move_id': invoice.id,
                                'product_id': prod.id,
                                'name': prod.name,
                                'account_id': prod.property_account_expense_id.id,
                            })
                            line._onchange_product_id()
                            cur = invoice.currency_id
                            if invoice.currency_id.id == invoice.company_id.currency_id.id:
                                cur = self.env['res.currency']
                            line.with_context(check_move_validity=False).write({
                                    'tax_ids': [(6,0,[vat.id])],
                                    'price_unit': price,
                                    #'debit': price,
                                    'account_id': prod.property_account_expense_id.id,
                                    'partner_id': invoice.partner_id.commercial_partner_id.id,
                                    'date': invoice.date,
                                    'recompute_tax_line': True,
                                    'currency_id': cur.id,
                            })
                        invoice.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes=True, recompute_tax_base_amount=True)

                        invoice._onchange_invoice_line_ids()


class ResCompany(models.Model):
    _inherit = 'res.company'

    def_expense_product_id = fields.Many2one('product.product',string="Default Expense Product")
    vat_resp_insc_id = fields.Many2one('account.tax',string="Def. VAT Resp. Insc.",domain="[('type_tax_use', '=', 'purchase')]")
    vat_exempt_id = fields.Many2one('account.tax',string="Def. VAT Exempt VAT",domain="[('type_tax_use', '=', 'purchase')]")
    vat_monotribute_id = fields.Many2one('account.tax',string="Def. VAT Monotribute",domain="[('type_tax_use', '=', 'purchase')]")
    non_taxable_amount_id = fields.Many2one('account.tax',string="VAT Code Non Taxable Amounts",domain="[('type_tax_use', '=', 'purchase')]")
    exempt_amount_id = fields.Many2one('account.tax',string="VAT code for Exempt Values",domain="[('type_tax_use', '=', 'purchase')]")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def_expense_product_id = fields.Many2one('product.product',string="Default Expense Product",related="company_id.def_expense_product_id",readonly=False)
    vat_resp_insc_id = fields.Many2one('account.tax',string="Def. VAT Resp. Insc.",domain="[('type_tax_use', '=', 'purchase')]",related="company_id.vat_resp_insc_id",readonly=False)
    vat_exempt_id = fields.Many2one('account.tax',string="Def. VAT Exempt VAT",domain="[('type_tax_use', '=', 'purchase')]",related="company_id.vat_exempt_id",readonly=False)
    vat_monotribute_id = fields.Many2one('account.tax',string="Def. VAT Monotribute",domain="[('type_tax_use', '=', 'purchase')]",related="company_id.vat_monotribute_id",readonly=False)
    non_taxable_amount_id = fields.Many2one('account.tax',string="VAT Code Non Taxable Amounts",domain="[('type_tax_use', '=', 'purchase')]",related="company_id.non_taxable_amount_id",readonly=False)
    exempt_amount_id = fields.Many2one('account.tax',string="VAT code for Exempt Values",domain="[('type_tax_use', '=', 'purchase')]",related="company_id.exempt_amount_id",readonly=False)

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    import_date = fields.Date(string="Import Date",translate=True,readonly=True,index=True)
    import_afip_file_flag = fields.Boolean(string="Imported from AFIP file",translate=True,readonly=True,index=True)
    import_status = fields.Selection([('pending', _('Pending Revision')),('revised', _('Revised'))],
        string='Data Status', default="pending",translate=True)
    import_user_id = fields.Many2one('res.users',string="Revised by User",readonly=True,states={'draft': [('readonly', False)]})
    import_cae = fields.Char(string="CAE/CAI Code",readonly=True,translate=True)
    import_inv_type = fields.Char(string="Invoice Type",readonly=True,translate=True)
    import_inv_currrency = fields.Char(string="Invoice Currency",readonly=True,translate=True)
    import_taxable_nett_amount = fields.Char(string="Taxable Nett Amount",readonly=True,translate=True)
    import_non_taxable_nett_amount = fields.Char(string="Non Taxable Nett Amount",readonly=True,translate=True)
    import_exempt_amount = fields.Char(string="Exempt_amount",readonly=True,translate=True)
    import_vat_amount = fields.Char(string="Vat Amount",readonly=True,translate=True)
    import_tot_amount = fields.Char(string="Total Amount",readonly=True,translate=True)

    def action_invoice_open(self):
        for rec in self:
            if not rec.import_user_id and rec.type in ('in_invoice','in_refund') and rec.import_afip_file_flag:
                rec.import_user_id = self.env.user.id
                rec.import_status = 'revised'
        return super(AccountInvoice, self).action_invoice_open()

class ResPartner(models.Model):
    _inherit = 'res.partner'

    default_product_id = fields.Many2one('product.product',string="Default Product",translate=True)
