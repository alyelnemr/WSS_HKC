# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import frozendict


class SalePaymentRegister(models.TransientModel):
    _name = 'sale.payment.register'
    _description = 'Sales Register Payment'
    _check_company_auto = True

    journal_id = fields.Many2one('account.journal', store=True, readonly=False,
                                 compute='_compute_journal_id',
                                 domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]")
    partial_reconcile = fields.Boolean(string='Partial Reconcile')
    amount = fields.Float(string='Amount')
    order_id = fields.Many2one('sale.order')
    payment_date = fields.Date(string="Payment Date", required=True,
                               default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', related='order_id.company_id')
    partner_id = fields.Many2one('res.partner', related='order_id.partner_id')

    @api.depends('company_id')
    def _compute_journal_id(self):
        for wizard in self:
            wizard.journal_id = self.env['account.journal'].search([
                ('type', 'in', ('bank', 'cash')),
                ('company_id', '=', wizard.company_id.id),
            ], limit=1)

    def action_sales_create_payments(self):
        vals = {
            'payment_type': 'inbound',
            'journal_id': self.journal_id.id,
            'partner_id': self.partner_id.id,
            'amount': self.amount,
            'date': self.payment_date,
            'ref': self.order_id.name,
            'partner_type': 'customer',
        }
        payment = self.env['account.payment'].create(vals)
        if payment:
            self.order_id.write({'payment_ids': [(4, payment.id)]})
            payment.action_post()
