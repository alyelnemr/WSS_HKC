{
    'name': 'Destination Operation',
    'version': '1.1',
    'category': 'Warehouse',
    'summary': 'Add destination picking operation for internal transfers.',
    'description': """
        This module adds a boolean field to stock picking types to allow destination pickings.
        It also adds a many2one field on stock pickings to reference the destination picking type.
        If enabled, a new picking is created with the destination picking type upon validation.
    """,
    'depends': ['stock', 'account_accountant'],
    'data': [
        'views/stock_picking_type_views.xml',
    ],
    'installable': True,
    'application': True,
}
