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

from odoo import models, fields


class SaleChangeCompanyWizard(models.TransientModel):
    _name = 'sale.change.company.wizard'
    _description = 'Seleccion de compañia de venta'

    def get_domain_company(self):
        """ Busco las compañias hijas de la matriz """
        companies = self.env['res.company'].search([('parent_id', '=', self.env.company.id)])
        return [('id', 'in', companies.ids)]

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañia de venta',
        ondelete='cascade',
        required=True,
        domain=get_domain_company
    )

    def confirm(self):
        """ Confirmamos la venta con la compañia seleccionada """
        sale = self.env['sale.order'].browse(self.env.context.get('active_id'))
        sale.update({'company_id': self.company_id.id})
        for line in sale.order_line:
            if line.tax_id:
                tax_relation = self.env['multicompany.taxes.relation'].get_dest_tax(line.tax_id[0], self.company_id)
                line.tax_id = [(6, 0, [tax_relation.id])]
        sale.action_confirm()
        sale.picking_ids.write({'company_id': self.company_id.id})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
