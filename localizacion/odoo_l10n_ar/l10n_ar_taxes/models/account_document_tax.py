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
from odoo.exceptions import ValidationError


class AccountDocumentTax(models.AbstractModel):
    _name = 'account.document.tax'
    _description = 'Impuesto abstracto'

    currency_id = fields.Many2one('res.currency')
    amount = fields.Monetary('Importe', currency_field='currency_id', required=True)
    base = fields.Monetary('Base', currency_field='currency_id')
    aliquot = fields.Float('Alicuota')
    name = fields.Char('Nombre', required=True)

    @api.constrains('amount')
    def check_amount(self):
        for tax in self:
            if tax.amount <= 0:
                raise ValidationError('El monto del impuesto debe ser mayor a 0')

    @api.constrains('base')
    def check_base(self):
        for tax in self:
            if tax.base < 0:
                raise ValidationError('La base del impuesto no puede ser negativa')

    @api.constrains('aliquot')
    def check_aliquot(self):
        for tax in self:
            if tax.aliquot < 0 or tax.aliquot > 100:
                raise ValidationError('La alicuota no puede ser menor que 0% o mayor que 100%')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
