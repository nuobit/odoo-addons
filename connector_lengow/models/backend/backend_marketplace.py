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
        string="Odoo Partner Country",
        readonly=True,
        related="partner_id.country_id",
    )
    lengow_marketplace = fields.Char(
        required=True,
    )
    name_source = fields.Selection(
        selection=[
            ("first_last", "First name + Last name"),
            ("full_name", "Full name"),
        ],
        string="Contact name source",
        required=True,
        default="first_last",
        help="Where the contact name of the imported order addresses is read"
        " from for this marketplace.\n\n"
        "Lengow order addresses (billing and delivery) carry the contact"
        " name in two places: the 'first_name'/'last_name' pair and the"
        " 'full_name' field. Which one holds the real person depends on the"
        " marketplace: most marketplaces always fill first/last name and"
        " leave 'full_name' empty or reuse it as a mutable delivery label"
        " (some rewrite it on later synchronizations of the same order,"
        " e.g. with a carrier or pick-up point label), while a few publish"
        " the contact name only in 'full_name' and leave first/last name"
        " empty.\n\n"
        "The connector reads the contact name STRICTLY from the source"
        " selected here, for both the billing and the delivery address of"
        " every order of this marketplace. There is deliberately no"
        " fallback to the other field: the partner name and its address"
        " identity hash derive from this value, so silently reading the"
        " other field could rename or duplicate customer addresses and"
        " repoint already confirmed orders when a marketplace rewrites"
        " 'full_name' on a re-synchronization.\n\n"
        "If the selected source comes empty on an order, its import job"
        " fails with an explicit error instead of guessing. If order"
        " imports of this marketplace fail systematically with that error"
        " while the other field is filled, this marketplace publishes"
        " names the other way: change this selection and import the"
        " affected orders again from the backend (an already-failed job"
        " carries the data prepared at download time, so requeuing it"
        " keeps the old values).",
    )

    _sql_constraints = [
        (
            "lbp_partner_uniq",
            "unique(backend_id, partner_id, lengow_marketplace)",
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
