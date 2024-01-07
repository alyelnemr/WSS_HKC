from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    price_vat_incl = fields.Float(
        compute="_compute_price_vat_incl_excl",
        string="Sales Price (Incl.)",
        help="Sale Price, All Taxes Included"
    )

    @api.depends(
        "list_price", "taxes_id", "taxes_id.amount_type", "taxes_id.amount",
        "taxes_id.include_base_amount")
    def _compute_price_vat_incl_excl(self):
        for template in self:
            info = template.taxes_id.sudo().compute_all(
                template.list_price, quantity=1.0)
            template.price_vat_incl = info["total_included"]
