
{
    "name": "Sales Payments",
    "summary": "Register collect customer payments from sales orders",
    "version": "17.0.0.0.0",
    "category": "Account",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale", "account"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "wizard/sale_payment_register_views.xml",
        "views/sale_order.xml",
    ],
}
