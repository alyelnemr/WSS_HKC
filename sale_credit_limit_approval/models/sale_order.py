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
                return super(SaleOrder, self).action_confirm()
            else:
                self.write({'state': 'to_approve'})
                return {
                    'warning': {
                        'title': _("Warning for Customer credit limit exceeded"),
                        'message': self.partner_credit_warning,
                    }
                }
        else: return super(SaleOrder, self).action_confirm()
        return True

    def _approval_allowed(self):
        """Returns whether the order qualifies to be approved by the current user"""
        self.ensure_one()
        return (
                self.partner_credit_warning == ''
                or self.user_has_groups('sale_credit_limit_approval.group_approve_sales_credit_limit'))

    def action_approve(self, force=False):
        self = self.filtered(lambda order: order._approval_allowed())
        self.action_confirm()

    def _can_be_confirmed(self):
        self.ensure_one()
        return self.state in {'draft', 'sent', 'to_approve'}

    @api.depends('company_id', 'partner_id', 'amount_total')
    def _compute_partner_credit_warning(self):
        for order in self:
            order.with_company(order.company_id)
            order.partner_credit_warning = ''
            show_warning = order.state in ('draft', 'sent', 'to_approve') and \
                           order.company_id.account_use_credit_limit
            if show_warning:
                order.partner_credit_warning = self.env['account.move']._build_credit_warning_message(
                    order,
                    current_amount=(order.amount_total / order.currency_rate),
                )



