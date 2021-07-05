# - coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from odoo import models


class PartnerDataGetWizard(models.TransientModel):
    _inherit = 'partner.data.get.wizard'

    def load_vals(self, data):
        """
        Heredo la funcion para cambiar la key de street por custom_street
        por campos adicionales de 'partner_address_extend'
        """
        res = super(PartnerDataGetWizard, self).load_vals(data)
        if res.get('street'):
            res['custom_street'] = res.pop('street')
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
