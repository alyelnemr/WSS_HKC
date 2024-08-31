# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    invoice_origin = fields.Char(related='move_id.invoice_origin', store=True)

