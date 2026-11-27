# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QueueJob(models.Model):
    _inherit = "queue.job"

    sage_payslip_id = fields.Many2one(
        comodel_name="payroll.sage.payslip",
        string="Sage payslip",
        help="The payslip this job imports from Sage",
        index=True,
        ondelete="set null",
        readonly=True,
    )
