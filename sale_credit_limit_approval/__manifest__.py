# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': "Customer Credit Limit With Approval",
    'version': '17.1.0',
    'summary': """ Configure Credit Limit for Customers and approve from sales and account manager""",
    'description': """ Activate and configure credit limit customer wise. If credit limit configured
    the system will warn or block the confirmation of a sales order if the existing due amount is greater
    than the configured warning or blocking credit limit. """,
    'category': 'Sales',
    'depends': ['sale_management'],
    'data': [
        'security/security.xml',
        'views/sale_order.xml',
    ],

    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
}
