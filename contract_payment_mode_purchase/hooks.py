# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """Copy payment mode from partner to the new field at contract."""
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        m_contract = env['account.analytic.account']
        contracts = m_contract.search([
            ('payment_mode_id', '=', False),
        ])
        if contracts:
            _logger.info('Setting supplier payment mode: %d contracts' %
                         len(contracts))
        for contract in contracts:
            if contract.journal_id.type == 'sale':
                if contract.partner_id.customer:
                    contract.payment_mode_id = contract.partner_id.customer_payment_mode_id.id
                else:
                    contract.payment_mode_id = False
            elif contract.journal_id.type == 'purchase':
                if contract.partner_id.supplier:
                    contract.payment_mode_id = contract.partner_id.supplier_payment_mode_id.id
                else:
                    contract.payment_mode_id = False

        _logger.info('Setting supplier payment mode: Done')
