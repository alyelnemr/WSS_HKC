# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import AccessDenied


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[
            ('to_approve', 'To Approve'),
            ('sale', )],
        ondelete={'to_approve': 'set default'})

    def action_confirm(self):
        '''
        Check the partner credit limit and existing due of the partner
        before confirming the order. The order is set to credit limit approval  if existing
        due is greater than  limit of the partner.
        '''
        if self.partner_credit_warning != '':
            if self._approval_allowed():
                self.action_approve()
            else:
                self.write({'state': 'to_approve'})
                return {
                    'warning': {
                        'title': _("Warning for Customer credit limit exceeded"),
                        'message': self.partner_credit_warning,
                    }
                }
        res = super(SaleOrder, self).action_confirm()
        return res

    def _approval_allowed(self):
        """Returns whether the order qualifies to be approved by the current user"""
        self.ensure_one()
        return (
                self.partner_credit_warning == ''
                or self.user_has_groups('sale_credit_limit_approval.group_approve_sales_credit_limit'))

    def action_approve(self, force=False):
        self = self.filtered(lambda order: order._approval_allowed())
        self.write({'state': 'sale'})
        return {}

