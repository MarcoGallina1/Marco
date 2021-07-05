# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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


class MulticompanyTaxesRelation(models.Model):
    _name = 'multicompany.taxes.relation'
    _description = 'Mapeo de impuestos'

    src_tax_id = fields.Many2one('account.tax', 'Impuesto origen', required=True)
    dest_tax_id = fields.Many2one('account.tax', 'Impuesto destino', required=True)
    dest_company_id = fields.Many2one('res.company', 'Compañia destino', related='dest_tax_id.company_id')

    @api.constrains('src_tax_id', 'dest_company_id')
    def check_taxes(self):
        for t in self:
            if t.src_tax_id == t.dest_tax_id:
                raise ValidationError('El impuesto origen no puede ser el mismo que el destino.')
            domain = [('id', '!=', t.id), ('src_tax_id', '=', t.src_tax_id.id), ('dest_company_id', '=', t.dest_company_id.id)]
            if t.src_tax_id and t.dest_tax_id and self.sudo().search_count(domain):
                raise ValidationError("Ya existe un mapeo para los impuestos ingresados.")

    def name_get(self):
        return [(t.id, "{} ({}) - {} ({})".format(
            t.src_tax_id.name,
            t.src_tax_id.company_id.name,
            t.dest_tax_id.name,
            t.dest_tax_id.company_id.name)) for t in self]

    def get_dest_tax(self, src_tax, dest_company):
        relation = self.sudo().search([('src_tax_id', '=', src_tax.id), ('dest_company_id', '=', dest_company.id)])
        if not relation:
            raise ValidationError('No se encontro un mapeo para el impuesto "{} ({})" y la compañia a facturar "{}"'.format(
                src_tax.name,
                dict(src_tax._fields['type_tax_use']._description_selection(self.env)).get(src_tax.type_tax_use),
                dest_company.name
            ))
        return relation.dest_tax_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
