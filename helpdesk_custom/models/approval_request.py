from odoo import fields, models, api,_
from odoo.fields import Command


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    approval_type = fields.Selection(selection_add=[
        ('create_ticket', 'Create Helpdesk Ticket')])


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    ticket_count = fields.Integer(string="Ticket Count", compute='_get_ticket')
    ticket_ids = fields.One2many('helpdesk.ticket', 'approval_request_id', string="Tickets", copy=False)
    ticket_type_id = fields.Many2one('helpdesk.ticket.type')
    tag_ids = fields.Many2many('helpdesk.tag', string='Tags',)

    @api.depends('ticket_ids')
    def _get_ticket(self):

        for rec in self:
            rec.ticket_count = len(rec.ticket_ids)

    def action_view_open_ticket_view(self, tickets=False):
        action = self.env["ir.actions.actions"]._for_xml_id("helpdesk.helpdesk_ticket_action_team")
        if not tickets:
            tickets = self.mapped('ticket_ids')
        if len(tickets) > 1:
            action['domain'] = [('id', 'in', tickets.ids)]
        elif len(tickets) == 1:
            form_view = [(self.env.ref('helpdesk.helpdesk_ticket_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = tickets.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        action['display_name'] = self.name
        action.update({
            'display_name': _("Tickets"),
        })
        return action

    def action_create_ticket(self):
        """Create the ticket associated to the approval request.
                """

        ticket_vals = {
            'name': self.name or '',
            'user_id': 2,
            'partner_id': self.request_owner_id.partner_id.id,
            'ticket_type_id': self.ticket_type_id.id,
            'description': self.reason,
            'tag_ids': '',
            'company_id': self.company_id.id,
            'approval_request_id': self.id,
            'tag_ids': [Command.set(self.tag_ids.ids)],
        }

        ticket_model = self.env['helpdesk.ticket']
        ticket = ticket_model.with_company(ticket_vals['company_id']).create(ticket_vals)

        return self.action_view_open_ticket_view(ticket)
