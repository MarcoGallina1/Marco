# -*- encoding: utf-8 -*-
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

    'name': 'Cash Count Report',

    'version': '1.0.1',

    'summary': 'Reporte de arqueo de caja',

    'description': 'Reporte de arqueo de caja',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'category': '',

    'depends': [
        'others',
        'l10n_payment_line',
        'l10n_ar_point_of_sale',
    ],

    'data': [
        'report/cash_count_report_template.xml',
        'report/cash_count_report.xml',
        'wizard/cash_count_report_wizard.xml',
    ],

    'active': False,

    'application': True,

    'installable': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
