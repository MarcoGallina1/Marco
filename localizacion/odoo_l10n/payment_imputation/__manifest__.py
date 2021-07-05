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

    'name': 'Payment imputation',

    'version': '1.0.1',

    'category': 'Accounting',

    'summary': 'Multiple payments imputation',

    'author': 'BLUEORANGE GROUP S.R.L. / NEXIT',

    'website': 'https://www.blueorange.com.ar',

    'depends': [
        'account'
    ],

    'data': [
        'views/account_payment.xml',
        'wizard/account_payment_imputation_wizard_view.xml',
        'static/xml/create_payment_asset.xml',
        'security/ir.model.access.csv'
    ],

    'qweb': [
        'static/xml/create_payment.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': 'Multiple payments imputation',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: