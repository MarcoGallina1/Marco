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


class AccountAbstractCheck(models.AbstractModel):
    _inherit = 'account.abstract.check'

    def get_criteria_group_cash_count(self):
        """ Criterio que vamos a utilizar para agrupar los metodos de pagos de cheques en arqueo de caja"""
        journal_check_without_location = self.filtered(
            lambda l: not l.check_location_id
        ).mapped('journal_id')
        location_check_with_location = self.filtered(
            lambda l:  l.check_location_id
        ).mapped('check_location_id')
        criteria_set = set([journal for journal in journal_check_without_location]) if journal_check_without_location else set([])
        criteria_set.update([criteria for criteria in location_check_with_location])
        return criteria_set

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
