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


class PurchaseChangeCompanyWizard(models.TransientModel):
    _name = 'purchase.change.company.wizard'
    _description = 'Seleccion de compañia de compra'

    def get_domain_company(self):
        """ Busco las compañias hijas de la matriz """
        companies = self.env['res.company'].search([('parent_id', '=', self.env.company.id)])
        return [('id', 'in', companies.ids)]

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañia de compra',
        ondelete='cascade',
        required=True,
        domain=get_domain_company
    )

    def confirm(self):
        """ Confirmamos la compra con la compañia seleccionada """
        purchase = self.env['purchase.order'].browse(self.env.context.get('active_id'))
        for line in purchase.order_line:
            if line.taxes_id:
                tax_relation = self.env['multicompany.taxes.relation'].get_dest_tax(line.taxes_id[0], self.company_id)
                line.taxes_id = [(6, 0, [tax_relation.id])]
        purchase.write({'company_id': self.company_id.id})
        purchase.button_confirm()
        purchase.picking_ids.write({'company_id': self.company_id.id})
        purchase.picking_ids.mapped('move_ids_without_package').write({'company_id': self.env.company.id})
        purchase.picking_ids.mapped('move_line_ids_without_package').write({'company_id': self.env.company.id})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
