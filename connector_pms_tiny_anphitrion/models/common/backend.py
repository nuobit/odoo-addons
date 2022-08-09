# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

import pytz

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

_tzs = [
    (tz, tz)
    for tz in sorted(
        pytz.all_timezones, key=lambda tz: tz if not tz.startswith("Etc/") else "_"
    )
]


def _tz_get(self):
    return _tzs


class AnphitrionBackend(models.Model):
    _name = "anphitrion.backend"
    _inherit = "connector.backend"
    _description = "Anphitrion Backend"

    @api.model
    def _select_state(self):
        return [
            ("draft", "Draft"),
            ("checked", "Checked"),
            ("production", "In Production"),
        ]

    name = fields.Char("Name", required=True)
    state = fields.Selection(selection="_select_state", string="State", default="draft")
    active = fields.Boolean(string="Active", default=True)

    property_id = fields.Many2one(
        comodel_name="pms.tiny.property",
        string="Property",
        required=True,
        ondelete="restrict",
    )

    company_id = fields.Many2one(
        related="property_id.company_id", store=True, string="Company", readonly=True
    )

    tz = fields.Selection(
        _tz_get,
        string="Timezone",
        required=True,
        default=lambda self: self._context.get("tz") or self.env.user.tz or "UTC",
        help="This field is used in order to define in which timezone the backend will work.",
    )

    hostname = fields.Char(string="Hostname", required=True)
    port = fields.Integer(string="Port", required=True)
    username = fields.Char(string="Username", required=True)
    password = fields.Char(string="Password", required=True)
    database = fields.Char("Database", required=True)
    schema = fields.Char("Schema", required=True, default="dbo")

    version = fields.Text("Version", readonly=True)

    tax_percent = fields.Float(string="Tax Percent", required=True, default=0.1)

    currency = fields.Char(
        string="Currency",
        required=True,
        default="EUR",
    )

    agency_codes = fields.Char(string="Agency Codes", required=True)

    import_reservations_since_date = fields.Datetime("Import Reservations since")

    def import_reservations_since(self):
        for rec in self:
            since_date = rec.import_reservations_since_date
            rec.import_reservations_since_date = fields.Datetime.now()
            self.env["anphitrion.pms.tiny.reservation"].import_data(rec, since_date)

    # view buttons
    def _check_connection(self):
        self.ensure_one()
        with self.work_on("anphitrion.backend") as work:
            adapter = work.component_by_name(name="anphitrion.backend.adapter")
            self.version = adapter.get_version()

    def button_check_connection(self):
        for rec in self:
            rec._check_connection()
            rec.write({"state": "checked"})

    def button_reset_to_draft(self):
        self.ensure_one()
        self.write({"state": "draft"})

    # scheduler
    @api.model
    def _scheduler_import(self):
        for backend in self.env["anphitrion.backend"].search([]):
            backend.import_reservations_since()

    def tz_to_utc(self, datetime_local_naive):
        datetime_local = pytz.timezone(self.tz).localize(datetime_local_naive)
        datetime_utc = datetime_local.astimezone(pytz.utc)
        datetime_utc_naive = datetime_utc.replace(tzinfo=None)
        return datetime_utc_naive

    def tz_to_local(self, datetime_utc_naive):
        local_tz = pytz.timezone(self.tz)
        datetime_utc = pytz.utc.localize(datetime_utc_naive)
        datetime_local = datetime_utc.astimezone(local_tz)
        datetime_local_naive = datetime_local.replace(tzinfo=None)
        return datetime_local_naive
