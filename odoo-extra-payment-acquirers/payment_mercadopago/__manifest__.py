# coding=utf-8
{
    'name': 'MercadoPago Payment Acquirer',
    'category': 'Accounting',
    'summary': 'Payment Acquirer: MercadoPago Implementation',
    'version': '13.0.1.0.0',
    'author' : 'TechUltra Solutions',
    'website' : 'http://www.techultra.in',
    'description': """MercadoPago Payment Acquirer""",
    'depends': ['payment', 'website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_views.xml',
        'views/payment_mecradopago_templates.xml',
        'views/res_partner_modifications.xml',
        'views/log_payment_notification_view.xml',
        'data/payment_acquirer_data.xml',
        'data/ir_cron_transaction.xml',
    ],
    'installable': True,
}