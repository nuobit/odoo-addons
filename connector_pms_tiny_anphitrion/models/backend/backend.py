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

    tax_percent = fields.Float(required=True, default=0.1)

    currency = fields.Char(
        required=True,
        default="EUR",
    )

    agency_codes = fields.Char(required=True)

    import_reservations_since_date = fields.Datetime("Import Reservations since")

    def import_reservations_since(self):
        for rec in self:
            since_date = rec.import_reservations_since_date
            rec.import_reservations_since_date = fields.Datetime.now()
            self.env["anphitrion.pms.tiny.reservation"].import_data(rec, since_date)

    # # view buttons
    # def _check_connection(self):
    #     self.ensure_one()
    #     with self.work_on("anphitrion.backend") as work:
    #         adapter = work.component_by_name(name="anphitrion.backend.adapter")
    #         self.version = adapter.get_version()
    #
    # def button_check_connection(self):
    #     for rec in self:
    #         rec._check_connection()
    #         rec.write({"state": "checked"})
    #
    # def button_reset_to_draft(self):
    #     self.ensure_one()
    #     self.write({"state": "draft"})

    # scheduler
    @api.model
    def _scheduler_import(self):
        for backend in self.env["anphitrion.backend"].search([]):
            backend.import_reservations_since()
