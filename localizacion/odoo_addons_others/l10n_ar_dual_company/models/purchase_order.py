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

from odoo import models, api, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    company_parent_id = fields.Many2one(
        comodel_name='res.company',
        related='company_id.parent_id',
        copy=False,
        store=True
    )

    def button_confirm(self):
        """ Heredo la confirmacion para colocar la empresa en los remitos generados de la compra """
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            order.picking_ids.write({'company_id': order.company_id.id})
            order.picking_ids.mapped('move_ids_without_package').write({'company_id': order.company_id.id})
            order.picking_ids.mapped('move_line_ids_without_package').write({'company_id': order.company_id.id})
        return res

    def button_confirm_new(self):
        """
        Devuelve un wizard para seleccionar una compañia hija
        """
        view_form_id = self.env.ref('l10n_ar_dual_company.purchase_change_company_wizard_form_view').id
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.change.company.wizard',
            'views': [(view_form_id, 'form')],
            'view_id': view_form_id,
            'target': 'new'
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
