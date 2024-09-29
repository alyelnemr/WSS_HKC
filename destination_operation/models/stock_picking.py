
from odoo import models, fields, api


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    allow_destination_picking = fields.Boolean(string="Allow Destination Picking")


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    allow_destination_picking = fields.Boolean(related='picking_type_id.allow_destination_picking', store=True)
    destination_picking_type_id = fields.Many2one('stock.picking.type', string="Destination Operation Type")
    linked_picking_id = fields.Many2one('stock.picking', string="Master Picking",
                                        help="The original picking linked to this destination picking")

    def button_validate(self):
        # Override the button_validate method to create a destination picking upon validation
        res = super(StockPicking, self).button_validate()
        if self.picking_type_id.allow_destination_picking and self.destination_picking_type_id:
            # Create a new picking with the destination picking type and set the product cost from the original picking
            new_picking = self.env['stock.picking'].with_company(self.destination_picking_type_id.company_id).create({
                'picking_type_id': self.destination_picking_type_id.id,
                'move_ids': [(0, 0, {
                    'product_id': move.product_id.id,
                    'name': move.product_id.name,
                    'product_uom_qty': move.product_uom_qty,
                    'product_uom': move.product_uom.id,
                    'location_id': move.location_dest_id.id,
                    'location_dest_id': move.location_id.id,
                    'product_packaging_id': move.product_packaging_id.id,
                    'company_id': self.destination_picking_type_id.company_id.id,
                    'price_unit': move.reference_cost,  # Copying the product cost (price_unit) from the previous picking
                }) for move in self.move_ids],
                'linked_picking_id': self.id,  # Link the newly created picking to the original picking
                'partner_id': self.partner_id.id,
            })
            new_picking.action_confirm()
        return res
