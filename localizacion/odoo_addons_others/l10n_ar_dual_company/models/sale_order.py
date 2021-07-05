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


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    warehouse_id = fields.Many2one(check_company=False)
    fiscal_position_id = fields.Many2one(check_company=False)

    def action_confirm_new(self):
        """
        Función nueva que muestra ventana emergente para seleccionar la compañia de la venta.
        """
        view_form_id = self.env.ref('l10n_ar_dual_company.sale_change_company_wizard_form_view').id
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.change.company.wizard',
            'views': [(view_form_id, 'form')],
            'view_id': view_form_id,
            'target': 'new'
        }

    def get_fixed_invoice_values_by_invoicing_picking_company(self):
        self.ensure_one()
        company = self.company_id
        return {
            'journal_id': self.env['account.journal'].search([('company_id', '=', company.id), ('type', '=', 'sale')], limit=1).id,
            'fiscal_position_id': self.fiscal_position_id.id or self.with_context(force_company=company.id).partner_invoice_id.property_account_position_id.id,
        }

    def _prepare_invoice(self):
        """ Asigno el diario y posicion fiscal a la factura en base a la compañia de la venta
        luego de confirmar aunque este parado en otra compañia """
        company = self.company_id
        res = super(SaleOrder, self.with_context(force_company=company.id))._prepare_invoice()
        res.update(self.get_fixed_invoice_values_by_invoicing_picking_company())
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
