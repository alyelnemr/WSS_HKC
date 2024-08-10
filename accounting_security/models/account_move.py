from odoo import models, api, fields
from lxml import etree


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        """
        Overrides orm field_view_get.
        @return: Dictionary of Fields, arch and toolbar.
        """

        res = super().get_view(view_id, view_type, **options)
        if view_type in ('tree', 'form', 'kanban') and (self.env.user.has_group('accounting_security.group_account_cashier') or self.env.user.has_group('accounting_security.group_bank_accountant')):
            arch = etree.XML(res['arch'])
            for node in arch.xpath("//tree | //form | //kanban"):
                node.set('create', 'false')
                node.set('delete', 'false')
                node.set('edit', 'false')
            res['arch'] = etree.tostring(arch)
        return res