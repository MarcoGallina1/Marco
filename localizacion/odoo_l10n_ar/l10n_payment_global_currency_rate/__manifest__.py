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

    'name': 'L10n payment global currency rate',

    'version': '1.1',

    'category': '',

    'summary': 'Cotización global para pagos',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'depends': [
        'l10n_payment_line',
        'invoice_currency_rate',
    ],

    'data': [
        'views/account_payment.xml',
        'wizard/payment_imputation_wizard_view.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': 'Cotización global para pagos',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: