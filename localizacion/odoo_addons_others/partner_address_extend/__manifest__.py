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
	'name' : 'Partner Address extension',

	'version': '1.0',

	'author' : 'BLUEORANGE GROUP S.R.L.',

	'website': 'https://www.blueorange.com.ar',

	'category': "Partner",

	'depends': [
		'l10n_ar',
		'others',
		'account',
	],

	'data': [
		'views/res_partner_view.xml',
	],

	'installable': True,

	'application': True,

	'active': False,

	'description': """Adds fields in Partners about address (department, number, flat)""",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
