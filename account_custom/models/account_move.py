from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def button_process_edi_web_services(self):
        self.sudo().action_process_edi_web_services(with_commit=False)

    def action_retry_edi_documents_error(self):
        self.sudo()._retry_edi_documents_error_hook()
        self.sudo().edi_document_ids.write({'error': False, 'blocking_level': False})
        self.sudo().action_process_edi_web_services()


