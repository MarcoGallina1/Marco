# -*- coding: utf-8 -*-
{
    'name': "l10n_ar_import_vendor_bills",
    'summary': """import vendor bills""",
    'description': """Importación de facturas de compras desde archivo Mis Comprobantes Recibidos""",
    'author': "Moogah",
    'website': "http://www.Moogah.com",
    'category': 'Uncategorized',
    'version': '13.0.1.1.4'
               '',
    'depends': [
        'account',
        'purchase',
        'l10n_ar_posfiscal2afipcode',
        'l10n_voucher_type',
    ],
    'data': [
        'views/view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'application': True,
}
