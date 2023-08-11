# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AnphitrionBackend(models.Model):
    _name = "anphitrion.backend"
    _inherit = "connector.backend"
    _description = "Anphitrion Backend"

    name = fields.Char(required=True)

    property_id = fields.Many2one(
        comodel_name="pms.tiny.property",
        required=True,
        ondelete="restrict",
    )

    company_id = fields.Many2one(
        related="property_id.company_id", store=True, readonly=True
    )

    hostname = fields.Char(required=True)
    port = fields.Integer(required=True)
    username = fields.Char(required=True)
    password = fields.Char(required=True)
    database = fields.Char(required=True)
    schema = fields.Char(required=True, default="dbo")

    tax_percent = fields.Float(required=True, default=10)

    currency = fields.Char(
        required=True,
        default="EUR",
    )

    agency_codes = fields.Char(required=True)

    agency_codes_with_mandatory_subagency_str = fields.Char(
        string="Agencies with mandatory subagency",
    )

    agency_codes_with_mandatory_subagency = fields.Json(
        compute="_compute_agency_codes_with_mandatory_subagency",
    )

    @api.depends("agency_codes_with_mandatory_subagency_str")
    def _compute_agency_codes_with_mandatory_subagency(self):
        for rec in self:
            if rec.agency_codes_with_mandatory_subagency_str:
                rec.agency_codes_with_mandatory_subagency = list(
                    filter(
                        None,
                        [
                            x.strip()
                            for x in rec.agency_codes_with_mandatory_subagency_str.split(
                                ","
                            )
                        ],
                    )
                )
            else:
                rec.agency_codes_with_mandatory_subagency = []

    min_reservation_number = fields.Integer(
        string="Minimum Reservation Number",
        help="Minimum reservation number to import (included). "
        "It should be greater than 0, any other value will be ignored.",
    )

    debug_reservation_codes = fields.Char(string="Reservation Codes")

    import_reservations_since_date = fields.Datetime("Import Reservations since")

    def import_reservations_since(self):
        for rec in self:
            self.env["anphitrion.pms.tiny.reservation"].import_data(
                rec, rec.import_reservations_since_date
            )

    # scheduler
    @api.model
    def _scheduler_import(self):
        for backend in self.env["anphitrion.backend"].search([]):
            backend.import_reservations_since()
