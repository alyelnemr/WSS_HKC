# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Inter Branch Transfer',
    'version': '1.1',
    'summary': 'Control stock transfer between company branches, valuation',
    'description': """ this module is remove merge pickings when using routes, and receipt product with cost of transfer branch
    """,
    'depends': ['stock', 'stock_account'],
    'category': 'Hidden',
    'sequence': 16,
    'data': [
       
    ],
    'installable': True,
    'auto_install': True,

    'license': 'OPL-1',
}
