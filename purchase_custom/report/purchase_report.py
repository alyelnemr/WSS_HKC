# -*- coding: utf-8 -*-


from odoo import fields, models


class PurchaseReport(models.Model):
    _inherit = "purchase.report"


    date_planned = fields.Datetime(string="Expected Arrival")

    def _select(self):
        return super(PurchaseReport, self)._select() + ", po.date_planned as date_planned"


    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ", po.date_planned"
