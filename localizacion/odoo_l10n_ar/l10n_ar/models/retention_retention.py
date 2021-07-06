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

from odoo import models


class RetentionRetention(models.Model):

    _inherit = 'account.tax.ar'
    _name = 'retention.retention'
    _description = 'Retención'

    def get_retention_groups(self):
        return self.get_retention_iibb_groups() | \
               self.get_retention_vat_groups() | \
               self.get_retention_profit_groups()

    def get_retention_iibb_groups(self):
        return self.env.ref('l10n_ar.tax_group_retention_iibb_caba', None) | \
               self.env.ref('l10n_ar.tax_group_retention_iibb_pba', None)

    def get_retention_vat_groups(self):
        return self.env.ref('l10n_ar.tax_group_retention_vat', None)

    def get_retention_profit_groups(self):
        return self.env.ref('l10n_ar.tax_group_retention_profit', None)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
