# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import timedelta
from markupsafe import Markup

from odoo import api, fields, models, tools,_
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, float_round, format_date, groupby


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_packaging_id')
    def _onchange_product_packaging_id(self):
        if self.product_packaging_id and self.product_uom_qty:
            newqty = self._check_packaging_qty(self.product_uom_qty, self.product_packaging_id, self.product_uom, "UP")
            if float_compare(newqty, self.product_uom_qty, precision_rounding=self.product_uom.rounding) != 0:
                return {
                    'warning': {
                        'title': _('Warning'),
                        'message': _(
                            "This product is packaged by %s %s. You should sell %s %s." %(self.product_packaging_id.qty,
                            self.product_id.uom_id.name,
                            newqty,
                            self.product_uom.name)
                        ),
                    },
                }

    def _check_packaging_qty(self, product_qty, product_packaging_id, uom_id, rounding_method="HALF-UP"):
        """Check if product_qty in given uom is a multiple of the packaging qty.
        If not, rounding the product_qty to closest multiple of the packaging qty
        according to the rounding_method "UP", "HALF-UP or "DOWN".
        """
        self.ensure_one()
        default_uom = product_packaging_id.product_id.uom_id
        packaging_qty = self._compute_quantity_packaging(default_uom, product_packaging_id.qty, uom_id)

        # We do not use the modulo operator to check if qty is a mltiple of q. Indeed the quantity
        # per package might be a float, leading to incorrect results. For example:
        # 8 % 1.6 = 1.5999999999999996
        # 5.4 % 1.8 = 2.220446049250313e-16
        if product_qty and packaging_qty:
            rounded_qty = float_round(product_qty / packaging_qty, precision_rounding=1.0,
                                      rounding_method=rounding_method) * packaging_qty
            return rounded_qty if float_compare(rounded_qty, product_qty,
                                                precision_rounding=default_uom.rounding) else product_qty
        return product_qty


    def _compute_quantity_packaging(self,default_uom, qty, to_unit, round=True, rounding_method='UP', raise_if_failure=True):
        """ Convert the given quantity from the current UoM `self` into a given one
            :param qty: the quantity to convert
            :param to_unit: the destination UoM record (uom.uom)
            :param raise_if_failure: only if the conversion is not possible
                - if true, raise an exception if the conversion is not possible (different UoM category),
                - otherwise, return the initial quantity
        """
        if not default_uom or not qty:
            return qty
        self.ensure_one()

        if default_uom != to_unit and default_uom.category_id.id != to_unit.category_id.id:
            if raise_if_failure:
                raise UserError(_(
                    'The unit of measure %s defined on the order line doesn\'t belong to the same category as the unit of measure %s defined on the product. Please correct the unit of measure defined on the order line or on the product, they should belong to the same category.',
                    default_uom.name, to_unit.name))
            else:
                return qty

        if default_uom == to_unit:
            amount = qty
        else:
            amount = qty / default_uom.factor
            if to_unit:
                amount = amount * to_unit.factor

        if to_unit and round:
            amount = tools.float_round(amount, precision_rounding=0.0001, rounding_method=rounding_method)

        return amount