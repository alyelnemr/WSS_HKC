
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
    child_picking_ids = fields.One2many('stock.picking', 'linked_picking_id', string="Child Pickings")

    def action_view_linked_picking(self):
        self.ensure_one()
        action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]
        action['domain'] = [('id', '=', self.linked_picking_id.id)]
        action['context'] = dict(self.env.context, create=False)
        return action

    def action_view_child_pickings(self):
        """Action to view the child pickings"""
        self.ensure_one()
        action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]
        action['domain'] = [('id', 'in', self.child_picking_ids.ids)]
        action['context'] = dict(self.env.context, create=False)
        return action

    @api.depends('state')
    def _compute_hide_picking_type(self):
        for picking in self:
            # picking.hide_picking_type = picking.state != "draft" and picking.ids and 'default_picking_type_id' in picking.env.context
            picking.hide_picking_type = False

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
                    'location_id': self.destination_picking_type_id.default_location_dest_id.id,# move.location_dest_id.id,
                    'location_dest_id': self.destination_picking_type_id.default_location_src_id.id, #move.location_id.id,
                    'product_packaging_id': move.product_packaging_id.id,
                    'company_id': self.destination_picking_type_id.company_id.id,
                    'price_unit': move.reference_cost,  # Copying the product cost (price_unit) from the previous picking
                }) for move in self.move_ids],
                'linked_picking_id': self.id,  # Link the newly created picking to the original picking
                'partner_id': self.partner_id.id,
                'origin': self.name,  # Copying the original picking name to the new picking
            })
            new_picking.action_confirm()
        return res
