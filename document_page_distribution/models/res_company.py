# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    document_page_distribution_template_id = fields.Many2one(
        "mail.template",
        string="Document Distribution Template",
        domain="[('model', '=', 'document.page')]",
        help="Default email template used to distribute document pages of this "
        "company.",
    )
