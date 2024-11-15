# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = "stock.move"

    def _account_entry_move(self, qty, description, svl_id, cost):
        res = super()._account_entry_move(qty, description, svl_id, cost)
        if len(res) > 0:
            for rec in res:
                rec['invoice_origin'] = self.picking_id.origin
                # for line in rec['line_ids']:
                #     line[2]['invoice_origin'] = self.picking_id.origin
        return res



    # def _get_in_svl_vals(self, forced_quantity):
    #     svl_vals_list = []
    #     for move in self:
    #         company_id = move.company_id
    #         if move.rule_id:
    #             company_id = self.env['stock.picking'].search([('name', '=', self.origin)]).company_id
    #         move = move.with_company(company_id)
    #         valued_move_lines = move._get_in_move_lines()
    #         valued_quantity = 0
    #         for valued_move_line in valued_move_lines:
    #             valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.quantity, move.product_id.uom_id)
    #         unit_cost = move.product_id.standard_price
    #         if move.product_id.cost_method != 'standard':
    #             unit_cost = abs(move._get_price_unit())  # May be negative (i.e. decrease an out move).
    #         svl_vals = move.product_id._prepare_in_svl_vals(forced_quantity or valued_quantity, unit_cost)
    #         svl_vals.update(move._prepare_common_svl_vals())
    #         if forced_quantity:
    #             svl_vals['description'] = 'Correction of %s (modification of past move)' % (move.picking_id.name or move.name)
    #         svl_vals_list.append(svl_vals)
    #     return svl_vals_list
    #
    # def _search_picking_for_assignation_domain(self):
    #     domain = [
    #         ('group_id', '=', self.group_id.id),
    #         ('location_id', '=', self.location_id.id),
    #         ('location_dest_id', '=', self.location_dest_id.id),
    #         ('picking_type_id', '=', self.picking_type_id.id),
    #         ('printed', '=', False),('origin', '=', self.origin),
    #         ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])]
    #     if self.partner_id and (self.location_id.usage == 'transit' or self.location_dest_id.usage == 'transit'):
    #         domain += [('partner_id', '=', self.partner_id.id)]
    #     return domain
    #
