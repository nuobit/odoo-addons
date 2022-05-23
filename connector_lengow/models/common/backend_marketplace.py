# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import fields, models

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
    lengow_marketplace = fields.Char(string="Lengow Marketplace", required=True)
    partner_id = fields.Many2one(
        string="Odoo Partner",
        comodel_name="res.partner",
        required=True,
        ondelete="restrict",
    )

    _sql_constraints = [
        (
            "lbp_partner_uniq",
            "unique(backend_id, partner_id)",
            "A binding already exists with the same Internal (Odoo) ID.",
        ), ]