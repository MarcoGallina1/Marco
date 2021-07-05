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

from odoo import models, api
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def get_fixed_invoice_line_values_by_invoicing_picking_company(self, product=False):
        self.ensure_one()
        company = self.order_id.company_id
        if not product:
            product = self.product_id

        # Toda esta parte fue copiada de base, pero agregando los force_company
        account = product.with_context(force_company=company.id).property_account_income_id or \
                  product.with_context(force_company=company.id).categ_id.property_account_income_categ_id

        if not account and self.product_id:
            raise UserError('Por favor defina la cuenta de ingresos para este '
                            'producto: "{}" (id:{}) o la de su categoría.'.format(product.name, product.id))

        fpos = self.order_id.fiscal_position_id or self.with_context(
            force_company=company.id).order_id.partner_id.property_account_position_id
        if fpos and account:
            account = fpos.map_account(account)

        return {
            'account_id': account.id,
        }

    def _prepare_invoice_line(self):
        """
        Asigno las cuentas contables a la factura en base a la compañia de la venta
        luego de confirmar aunque este parado en otra compañia
        """
        res = super(SaleOrderLine, self.with_context(force_company=self.order_id.company_id.id))._prepare_invoice_line()
        res.update(self.get_fixed_invoice_line_values_by_invoicing_picking_company())
        return res

    def _compute_tax_id(self):
        """ Si la compañia donde estoy parado es una sin matriz,
        muestro solo los impuestos de esa compañia para que no muestre todos"""
        if not self.env.company.parent_id:
            for line in self:
                fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
                # If company_id is set, always filter taxes by the company
                taxes = line.product_id.taxes_id.filtered(
                    lambda r: r.company_id == self.env.company or r.company_id == line.company_id)
                line.tax_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_shipping_id) if fpos else taxes
        else:
            return super(SaleOrderLine, self)._compute_tax_id()

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        """Heredo la funcion para que cada vez que se genere un procurement group y luego genere un remito se
        coloque la empresa correcta"""
        res = super(SaleOrderLine, self)._action_launch_stock_rule(previous_product_uom_qty)
        for line in self:
            company = line.order_id.company_id
            # Filtro los remitos de los moves asociados a la linea de venta que sean ya de la misma compañia
            pickings = line.move_ids.mapped('picking_id').filtered(lambda x: x.company_id != company)
            pickings.write({'company_id': company.id})
            pickings.mapped('move_ids_without_package').write({'company_id': company.id})
            pickings.mapped('move_line_ids_without_package').write({'company_id': company.id})
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
