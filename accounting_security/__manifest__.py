{

    'name': 'Accounting Security',
    'version': '1.0',
    'author': 'hassan',
    'summary': 'accounting security groups',
    'depends': ['account', 'sale', 'account_edi', 'l10n_sa_edi', 'sale_loyalty'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menuitems.xml',
        'views/account_move_view.xml',
        'views/sale_order_view.xml'
    ],
    'installable': True,
    'application': True
}
