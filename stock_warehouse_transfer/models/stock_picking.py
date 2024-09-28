import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"
    org_from_location = fields.Many2one(comodel_name="stock.location", string="From ", copy=False)
    org_dest_location = fields.Many2one(comodel_name="stock.location", string="To", copy=False)
    send_rec = fields.Selection(string='Type', selection=[('send', 'Send'), ('rec', 'Receive'), ])
    transfer = fields.Many2one(comodel_name="stock.warehouse.transfer", string="Transfer", copy=False )
    can_edit_qty = fields.Boolean(string='Can Edit Qty', compute="get_can_edit_qty")

    def get_can_edit_qty(self):
        for rec in self :
            rec.can_edit_qty = True
            if rec.transfer and rec.send_rec == 'rec' and not self.user_has_groups("stock_warehouse_transfer.user_change_done_qty"):
                rec.can_edit_qty = False

    original_location_id = fields.Many2one("stock.location")

    @api.model
    def search(self, domain, offset=0, limit=None, order=None):
        if self.env.user.has_group("stock_warehouse_transfer.access_own_operation_types") and self._context.get(
                "check_accesses", False):
            domain += [("picking_type_id.users_ids", "in", [self.env.user.id])]
        return super(StockPicking, self).search(domain=domain, offset=offset, limit=limit, order=order)

    def button_validate(self):
        # TDE FIXME: should work in batch
        transfer_id = self.sudo().transfer
        self.ensure_one()
        for xline in self.move_ids_without_package:
            if xline.quantity != xline.product_uom_qty and not self.user_has_groups(
                    "stock_warehouse_transfer.user_change_done_qty"):
                raise UserError(_('You are not authorized to receive quantities different from what is requested'))
        res = super(StockPicking, self).button_validate()

        transfer = False
        transfer_ids = (self.env["stock.picking"].with_context(check_accesses=False).sudo().search_count(
            [("transfer", "=", transfer_id.id)]))
        print(transfer_ids)
        if transfer_ids < 2:
            transfer = False
        if transfer_ids >= 2:
            transfer = True

        m_obj = self.env["stock.move"]
        if transfer_id:
            transit_location = transfer_id.trans_location.id

            picking_types = (self.env["stock.picking.type"].with_context(check_accesses=False).search([
                ("warehouse_id", "=", transfer_id.dest_warehouse.id),
                ("code", "=", "internal"),
            ], limit=1, ))

            if not picking_types:
                raise UserError("Please create operation for the destination warehouse")
            if not transfer:

                picking_vals = {
                    "picking_type_id": picking_types.id,
                    "transfer": transfer_id.id,
                    "origin": self.name + "  " + transfer_id.name,
                    "move_type": "one",
                    "location_dest_id": transfer_id.dest_location.id,
                    "location_id": transit_location,
                    "original_location_id": self.location_id.id,
                    "send_rec": "rec",
                    "org_from_location": transfer_id.source_location.id,
                    "org_dest_location": transfer_id.dest_location.id,
                }
                picking = self.create(picking_vals)

                for line in self.move_ids_without_package:
                    if line.product_qty > 0:
                        move_vals = {
                            "product_id": line.product_id.id,
                            "product_uom_qty": line.product_qty,
                            "product_uom": line.product_uom.id,
                            "name": line.product_id.name,
                            "location_dest_id": transfer_id.dest_location.id,
                            "location_id": transit_location,
                            "picking_id": picking.id,
                        }
                        m_obj.create(move_vals)
                picking.action_confirm()
                picking.action_assign()
                for line in picking.move_line_ids_without_package:
                    line.update(
                        {
                            "location_dest_id": transfer_id.dest_location.id,
                            "location_id": transit_location,
                            "lot_id": line.lot_id.id,
                        }
                    )
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'
    can_edit_qty = fields.Boolean(string='Can Edit Qty', related="picking_id.can_edit_qty")


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    can_edit_qty = fields.Boolean(string='Can Edit Qty', related="picking_id.can_edit_qty")
    org_from_location = fields.Many2one(comodel_name="stock.location", string="From ", copy=False, related="picking_id.org_from_location")
    org_dest_location = fields.Many2one(comodel_name="stock.location", string="To", copy=False, related="picking_id.org_dest_location")
    send_rec = fields.Selection(string='Type', selection=[('send', 'Send'), ('rec', 'Receive'), ], related="picking_id.send_rec")


class Warehouse(models.Model):
    _inherit = "stock.warehouse"
    transfer_user_ids = fields.Many2many("res.users", "transfer_warehouses_rel", "uuid", "ww_id", string="Transfer Users")


class PickingType(models.Model):
    _inherit = "stock.picking.type"
    users_ids = fields.Many2many("res.users", "users_operations_types_rel", string="Users")

    @api.model
    def search(self, domain, offset=0, limit=None, order=None):
        if self.env.user.has_group("stock_warehouse_transfer.access_own_operation_types") and self._context.get("check_accesses", False):
            domain += [("users_ids", "in", [self.env.user.id])]
        return super(PickingType, self).search(domain=domain, offset=offset, limit=limit, order=order)