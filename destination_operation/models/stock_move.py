from odoo import models, fields
from odoo.tools import float_is_zero, float_compare


class StockMove(models.Model):
    _inherit = 'stock.move'

    reference_cost = fields.Float(string='Reference Cost')

    def create(self, vals_list):
        res = super(StockMove, self).create(vals_list)
        return res

    def _get_price_unit(self):
        """ Returns the unit price to value this stock move """
        self.ensure_one()
        price_unit = self.price_unit
        precision = self.env['decimal.precision'].precision_get('Product Price')
        # If the move is a return, use the original move's price unit.
        if self.origin_returned_move_id and self.origin_returned_move_id.sudo().stock_valuation_layer_ids:
            layers = self.origin_returned_move_id.sudo().stock_valuation_layer_ids
            # dropshipping create additional positive svl to make sure there is no impact on the stock valuation
            # We need to remove them from the computation of the price unit.
            if self.origin_returned_move_id._is_dropshipped() or self.origin_returned_move_id._is_dropshipped_returned():
                layers = layers.filtered(
                    lambda l: float_compare(l.value, 0, precision_rounding=l.product_id.uom_id.rounding) <= 0)
            layers |= layers.stock_valuation_layer_ids
            quantity = sum(layers.mapped("quantity"))
            return sum(layers.mapped("value")) / quantity if not float_is_zero(quantity,
                                                                               precision_rounding=layers.uom_id.rounding) else 0
        if self.picking_id.linked_picking_id.allow_destination_picking:
            return self.price_unit
        return price_unit if not float_is_zero(price_unit,
                                               precision) or self._should_force_price_unit() else self.product_id.standard_price

    def _get_in_svl_vals(self, forced_quantity):
        svl_vals_list = []
        for move in self:
            move = move.with_company(move.company_id)
            valued_move_lines = move._get_in_move_lines()
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.quantity,
                                                                                     move.product_id.uom_id)
                # changed line to get price_unit if the picking allows it, otherwise use standard_price
            unit_cost = move.product_id.standard_price if not move.picking_id.linked_picking_id.allow_destination_picking else move.price_unit
            if move.product_id.cost_method != 'standard' and not move.picking_id.linked_picking_id.allow_destination_picking:
                unit_cost = abs(move._get_price_unit())  # May be negative (i.e. decrease an out move).
            svl_vals = move.product_id._prepare_in_svl_vals(forced_quantity or valued_quantity, unit_cost)
            if move.picking_id.allow_destination_picking:
                move.reference_cost = unit_cost
            svl_vals.update(move._prepare_common_svl_vals())
            if forced_quantity:
                svl_vals['description'] = 'Correction of %s (modification of past move)' % (
                            move.picking_id.name or move.name)
            svl_vals_list.append(svl_vals)
        return svl_vals_list

    def _create_out_svl(self, forced_quantity=None):
        svl_vals_list = []
        for move in self:
            move = move.with_company(move.company_id)
            valued_move_lines = move._get_out_move_lines()
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.quantity,
                                                                                     move.product_id.uom_id)
            if float_is_zero(forced_quantity or valued_quantity, precision_rounding=move.product_id.uom_id.rounding):
                continue
            quantity = forced_quantity or valued_quantity
            svl_vals = move.product_id._prepare_out_svl_vals(quantity, move.company_id)

            if move.picking_id.allow_destination_picking:
                move.reference_cost = svl_vals['unit_cost']
            if move.picking_id.linked_picking_id.allow_destination_picking:
                company_id = self.env.context.get('force_company', self.env.company.id)
                company = self.env['res.company'].browse(company_id)
                currency = company.currency_id
                svl_vals['unit_cost'] = move.price_unit
                svl_vals['value'] = currency.round(quantity * move.price_unit)
            svl_vals.update(move._prepare_common_svl_vals())
            if forced_quantity:
                svl_vals['description'] = 'Correction of %s (modification of past move)' % (
                            move.picking_id.name or move.name)
            svl_vals['description'] += svl_vals.pop('rounding_adjustment', '')
            svl_vals_list.append(svl_vals)
        return self.env['stock.valuation.layer'].sudo().create(svl_vals_list)

    def _create_dropshipped_svl(self, forced_quantity=None):
        """Create a `stock.valuation.layer` from `self`.

        :param forced_quantity: under some circunstances, the quantity to value is different than
            the initial demand of the move (Default value = None)
        """
        svl_vals_list = []
        for move in self:
            move = move.with_company(move.company_id)
            valued_move_lines = move.move_line_ids
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.quantity,
                                                                                     move.product_id.uom_id)
            quantity = forced_quantity or valued_quantity

            unit_cost = move._get_price_unit()
            if move.product_id.cost_method == 'standard' and not move.picking_id.linked_picking_id.allow_destination_picking:
                unit_cost = move.product_id.standard_price

            if move.picking_id.allow_destination_picking:
                move.reference_cost = unit_cost

            common_vals = dict(move._prepare_common_svl_vals(), remaining_qty=0)

            # create the in if it does not come from a valued location (eg subcontract -> customer)
            if not move.location_id._should_be_valued():
                in_vals = {
                    'unit_cost': unit_cost,
                    'value': unit_cost * quantity,
                    'quantity': quantity,
                }
                in_vals.update(common_vals)
                svl_vals_list.append(in_vals)

            # create the out if it does not go to a valued location (eg customer -> subcontract)
            if not move.location_dest_id._should_be_valued():
                out_vals = {
                    'unit_cost': unit_cost,
                    'value': unit_cost * quantity * -1,
                    'quantity': quantity * -1,
                }
                out_vals.update(common_vals)
                svl_vals_list.append(out_vals)

        return self.env['stock.valuation.layer'].sudo().create(svl_vals_list)
