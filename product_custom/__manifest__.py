
{
    "name": "Product Custom",
    "summary": "Product restriction ",
    "version": "17.0.0.0.0",
    "category": "Product",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["product", "stock"],
    "data": [
        "security/security.xml",
        'security/ir.model.access.csv',
        "views/product_views.xml"],
}
