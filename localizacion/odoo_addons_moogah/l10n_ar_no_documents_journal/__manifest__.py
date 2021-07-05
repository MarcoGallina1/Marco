# -*- coding: utf-8 -*-
{
    'name': "Restricción de Diarios en Exportaciones Impositivas",
    'summary': """Restricción para evitar incluir determinados diarios en las exportaciones impositivas.""",
    'description': """El app incluye una casilla para identificar los Diarios que no deben ser incluidos en exportaciones como IVA Digital.""",
    'author': "Moogah",
    'website': "http://www.Moogah.com",
    'category': 'Uncategorized',
    'version': '13.0.1.0.3',
    'depends': [
        'account',
        'l10n_ar_invoice_presentation',
    ],
    'data': [
        'views/view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'application': True,
}
