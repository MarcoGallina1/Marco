# -*- coding: utf-8 -*-
{
    'name': "Modificar CAE",
    'summary': """Modificar CAE manualmente""",
    'description': """Este app permite modificar el CAE de forma manual, siempre que la factura se encuentre en estado Borrador y haya sido guardada al menos una vez""",
    'author': "Moogah",
    'website': "http://www.Moogah.com",
    'category': 'Uncategorized',
    'version': '13.0.1.0.6',
    'depends': [ 
        'l10n_ar_afip_webservices_wsfe',
    ],
    'data': [
        'views/view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'application': True,
}
