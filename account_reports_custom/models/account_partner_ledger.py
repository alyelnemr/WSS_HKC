# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json

from odoo import api, models, _, fields
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.misc import format_date, get_lang

from datetime import timedelta
from collections import defaultdict


class PartnerLedgerCustomHandler(models.AbstractModel):
    _inherit = 'account.partner.ledger.report.handler'

    def _build_partner_lines(self, report, options, level_shift=0):
        lines = []

        totals_by_column_group = {
            column_group_key: {
                total: 0.0
                for total in ['initial','debit', 'credit', 'balance']
            }
            for column_group_key in options['column_groups']
        }
        for partner, results in self._query_partners(options):
            partner_values = defaultdict(dict)
            for column_group_key in options['column_groups']:
                partner_sum = results.get(column_group_key, {})
                partner_values[column_group_key]['initial'] = 0.0
                partner_values[column_group_key]['debit'] = partner_sum.get('debit', 0.0)
                partner_values[column_group_key]['credit'] = partner_sum.get('credit', 0.0)
                partner_values[column_group_key]['balance'] = partner_sum.get('balance', 0.0)
                if partner:
                    initial_balance = self.with_context(initial_balance=True)._get_initial_balance_values([partner.id], options)
                    if 'balance' in initial_balance[partner.id][column_group_key]:
                        partner_values[column_group_key]['initial'] = initial_balance[partner.id][column_group_key]['balance']
                        partner_values[column_group_key]['balance'] = partner_sum.get('balance', 0.0) - initial_balance[partner.id][column_group_key]['balance']

                totals_by_column_group[column_group_key]['initial'] += partner_values[column_group_key]['initial']
                totals_by_column_group[column_group_key]['debit'] += partner_values[column_group_key]['debit']
                totals_by_column_group[column_group_key]['credit'] += partner_values[column_group_key]['credit']
                totals_by_column_group[column_group_key]['balance'] += partner_values[column_group_key]['balance']

            lines.append(self._get_report_line_partners(options, partner, partner_values, level_shift=level_shift))
        return lines, totals_by_column_group
        ####################################################
        # COLUMNS/LINES
        ####################################################

    def _get_report_line_move_line(self, options, aml_query_result, partner_line_id, init_bal_by_col_group,
                                   level_shift=0):
        aml_query_result['initial'] = 0
        res = super(PartnerLedgerCustomHandler, self)._get_report_line_move_line(options, aml_query_result, partner_line_id, init_bal_by_col_group,level_shift)
        return res


    def _get_initial_balance_values(self, partner_ids, options):
        queries = []
        params = []
        report = self.env.ref('account_reports.partner_ledger_report')
        ct_query = report._get_query_currency_table(options)
        for column_group_key, column_group_options in report._split_options_per_column_group(options).items():
            # Get sums for the initial balance.
            # period: [('date' <= options['date_from'] - 1)]
            new_options = self._get_options_initial_balance(column_group_options)
            tables, where_clause, where_params = report._query_get(new_options, 'normal', domain=[('partner_id', 'in', partner_ids)])
            params.append(column_group_key)
            params += where_params
            queries.append(f"""
                SELECT
                    account_move_line.partner_id,
                    %s                                                                                    AS column_group_key,
                    SUM(ROUND(account_move_line.debit * currency_table.rate, currency_table.precision))   AS debit,
                    SUM(ROUND(account_move_line.credit * currency_table.rate, currency_table.precision))  AS credit,
                    SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) AS balance
                FROM {tables}
                LEFT JOIN {ct_query} ON currency_table.company_id = account_move_line.company_id
                WHERE {where_clause}
                GROUP BY account_move_line.partner_id
            """)

        self._cr.execute(" UNION ALL ".join(queries), params)

        init_balance_by_col_group = {
            partner_id: {column_group_key: {} for column_group_key in options['column_groups']}
            for partner_id in partner_ids
        }
        for result in self._cr.dictfetchall():
            init_balance_by_col_group[result['partner_id']][result['column_group_key']] = result
            if not self._context.get('initial_balance'):
                init_balance_by_col_group[result['partner_id']][result['column_group_key']] = {}
        return init_balance_by_col_group

