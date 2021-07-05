# -*- coding: utf-8 -*-
from odoo import http, models, fields, api, _
from datetime import datetime
import calendar
    
class RetentionRetention(models.Model):
    _inherit = 'retention.retention'

    norm_code = fields.Char(string="Norm Code",size=3)

class PerceptionPerception(models.Model):
    _inherit = 'perception.perception'

    norm_code = fields.Char(string="Norm Code",size=3)

class PartnerDocumentType(models.Model):
    _inherit = 'partner.document.type'

    arciba_doc_type = fields.Char(string="Arciba Doc Type",size=2,translate=True)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    iibb_sit = fields.Selection(
        [('0', 'None'),('1','Local'),('2','Convenio Mutilateral'),('3','No Inscripto'),('5','Reg Simplificado')],
        string="IIBB Situation",
        translate=True,
        required=True,
        default='2',
    )

class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    arciba_code = fields.Selection(
        [('0', 'None'),('1','Responsable Inscripto'),('3','Exento'),('4','Monotributo')],
        string="ARCIBA Code",
        translate=True,
        required=True,
        default='0',
    )
