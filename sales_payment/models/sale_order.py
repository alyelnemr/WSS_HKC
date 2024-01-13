from odoo import fields, models, api,_


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_ids = fields.Many2many('account.payment', string='Payments')
    payment_amount = fields.Monetary('Payment Amount', compute='_calc_payment_amount', compute_sudo=True, store=True)

    @api.depends('payment_ids.amount', 'payment_ids.currency_id', 'payment_ids.state')
    def _calc_payment_amount(self):
        for record in self:
            total_amount = 0
            for payment in record.payment_ids:
                if payment.state == 'cancelled':
                    continue
                amount = payment.amount #payment.with_context(date=payment.date).currency_id.compute(payment.amount, record.currency_id)
                total_amount += amount
            record.payment_amount = total_amount

    def action_payment_view(self):
        self.ensure_one()
        action, = self.env.ref('account.action_account_payments').sudo().read()
        action['domain'] = [('id', 'in', self.payment_ids.ids)]
        context = self.env.context.copy()
        context.update({'create': False})
        action['context'] = context
        return action

    def action_register_payment(self):
        ''' Open the account.payment.register wizard to pay the selected journal items.
        :return: An action opening the sale.payment.register wizard.
        '''
        return {
            'name': _('Register Payment'),
            'res_model': 'sale.payment.register',
            'view_mode': 'form',
            '': [[self.env.ref('sales_payment.view_sale_payment_register_form').sudo().id, 'form']],
            'context': {
                'active_model': 'sale.order',
                'active_ids': self.ids,
                'default_order_id': self.id,
                'default_amount': self.amount_total,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }


