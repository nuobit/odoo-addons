# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    rental_require_signature_validation = fields.Boolean(
        related="company_id.rental_require_signature_validation",
        readonly=False,
    )

    rental_signature_terms = fields.Html(
        related="company_id.rental_signature_terms",
        readonly=False,
    )
