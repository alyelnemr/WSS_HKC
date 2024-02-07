from odoo import fields, models, api,_


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    approval_request_id = fields.Many2one('approval.request')
