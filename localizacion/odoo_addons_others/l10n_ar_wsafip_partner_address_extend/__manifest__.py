# -*- encoding: utf-8 -*-
##############################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
	'name': 'L10n ar wsafip partner address extension',

	'version': '1.0',

	'author': 'BLUEORANGE GROUP S.R.L.',

	'website': 'https://www.blueorange.com.ar',

	'category': "Partner",

	'depends': [
		'partner_address_extend',
		'l10n_ar_wsafip_partner',
	],

	'data': [   
	],

	'installable': True,

	'application': True,

	'auto_install': True,

	'active': False,

	'description': """Autoinstall para obtencion de datos de afip y campos extras para direccion.""",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
