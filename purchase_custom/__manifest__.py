# -*- coding: utf-8 -*-

{
    'name': 'Purchase Custom',
    'version': '1.0',
    'category': 'Inventory/Purchase',
    'sequence': 60,
    'summary': 'Purchase Orders, Purchase Reports',
    'depends': ['purchase'],
    'data': [
      "report/purchase_report_views.xml",
    ],
    
    'installable': True,
    'auto_install': True,
    'license': 'OPL-1',
}
