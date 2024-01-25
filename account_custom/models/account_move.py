from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def button_process_edi_web_services(self):
        self.sudo().action_process_edi_web_services(with_commit=False)


