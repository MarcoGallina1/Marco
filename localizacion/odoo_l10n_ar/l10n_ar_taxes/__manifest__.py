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

{

    'name': 'l10n_ar_taxes',

    'version': '1.0',

    'category': 'Accounting',

    'summary': 'Manejo de importes de impuestos para Argentina',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'http://www.blueorange.com.ar',

    'depends': [
        'base_codes',
        'l10n_ar'
    ],

    'data': [
        'views/account_invoice_view.xml',
        'views/account.xml',
        'views/taxes_menu_view.xml',
        'data/codes_modes_relation.xml',
        'data/security.xml',
    ],

    'qweb': [
        "static/src/xml/account_info.xml",
    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': 'Manejo de importes de impuestos para Argentina',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
