# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    document_page_distribution_template_id = fields.Many2one(
        related="company_id.document_page_distribution_template_id",
        readonly=False,
        string="Document Distribution Template",
        domain="[('model', '=', 'document.page')]",
    )
