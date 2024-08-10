{

    'name': 'Accounting Security',
    'version': '1.0',
    'author': 'hassan',
    'summary': 'accounting security groups',
    'depends': ['account', 'sale'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menuitems.xml',
        'views/view.xml'
    ],
    'installable': True,
    'application': True
}
