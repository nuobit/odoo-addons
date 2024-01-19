# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class LengowBackendMarketplace(models.Model):
    _name = "lengow.backend.marketplace"
    _description = "Lengow Backend marketplace"

    backend_id = fields.Many2one(
        string="Backend id",
        comodel_name="lengow.backend",
        required=True,
        ondelete="cascade",
    )

    partner_id = fields.Many2one(
        string="Odoo Partner",
        comodel_name="res.partner",
        required=True,
        ondelete="restrict",
    )
    country_id = fields.Many2one(
        string="Odoo Partner Country", readonly=True, related="partner_id.country_id"
    )
    lengow_marketplace = fields.Char(string="Lengow Marketplace", required=True)

    _sql_constraints = [
        (
            "lbp_partner_uniq",
            "unique(backend_id, partner_id)",
            "A mapping already exists with the same Partner.",
        ),
    ]

    @api.constrains("backend_id", "partner_id", "lengow_marketplace")
    def _check_marketplace_country(self):
        for rec in self:
            other = self.env[self._name].search(
                [
                    ("id", "!=", rec.id),
                    ("backend_id", "=", rec.backend_id.id),
                    ("partner_id.country_id", "=", rec.partner_id.country_id.id),
                    ("lengow_marketplace", "=", rec.lengow_marketplace),
                ]
            )
            if other:
                raise ValidationError(
                    _("A mapping already exists with the same country and marketplace")
                )
