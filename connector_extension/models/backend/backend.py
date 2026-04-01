# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
import logging
from contextlib import contextmanager

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

_tzs = [
    (tz, tz)
    for tz in sorted(
        pytz.all_timezones, key=lambda tz: tz if not tz.startswith("Etc/") else "_"
    )
]


def _tz_get(self):
    return _tzs


class ConnectorBackend(models.AbstractModel):
    _name = "connector.extension.backend"
    _inherit = "connector.backend"
    _description = "Connector Backend Extension"

    @api.model
    def _select_state(self):
        return [
            ("draft", "Draft"),
            ("validated", "Validated"),
        ]

    name = fields.Char(
        string="Name",
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        index=True,
        required=True,
        default=lambda self: self.env.company,
        string="Company",
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        help="User used as the default responsible for records created by "
        "this backend. If set, all operations (imports, exports, jobs) "
        "will run under this user context.",
    )

    lang_ids = fields.Many2many(
        comodel_name="res.lang",
        column1="backend_id",
        column2="lang_id",
        required=True,
        string="Languages",
    )

    # TODO: REVIEW: Create a template view to be inherited
    state = fields.Selection(
        selection="_select_state",
        default="draft",
    )
    active = fields.Boolean(
        default=True,
    )

    version = fields.Text(readonly=True)

    tz = fields.Selection(
        _tz_get,
        string="Timezone",
        required=True,
        default=lambda self: self._context.get("tz") or self.env.user.tz or "UTC",
        help="The timezone of the business data in the external system. "
        "All imported datetime values are assumed to be in this timezone "
        "and will be converted to UTC for storage in Odoo. "
        "On export, Odoo UTC values are converted back to this timezone.",
    )
    server_tz = fields.Selection(
        _tz_get,
        string="Server Timezone",
        required=True,
        default=lambda self: self._context.get("tz") or self.env.user.tz or "UTC",
        help="The timezone of the external system's server. "
        "Used for technical timestamps managed by the server itself "
        "(e.g. modification dates, audit trails) which may differ from "
        "the business data timezone when the server is hosted in a "
        "different region.",
    )

    chunk_size = fields.Integer(
        string="Chunk Size",
        default=-1,
        help="This field is used to define the chunk size to import from the backend.",
    )
    page_size = fields.Integer(
        string="Page Size",
        default=-1,
        help="This field is used in order to define the "
        "number of records imported at the same time.",
    )

    sync_offset = fields.Integer(
        required=True,
        default=0,
        help="Minutes to start the synchronization "
        "before(negative)/after(positive) the last one",
    )

    def _check_connection(self):
        self.ensure_one()
        with self.work_on(self._name) as work:
            component = work.component(usage="backend.adapter")
            self.version = component.get_version()

    def button_check_connection(self):
        for rec in self:
            rec._check_connection()
            rec.state = "validated"
        return

    def button_reset_to_draft(self):
        self.ensure_one()
        self.write({"state": "draft", "version": False})

    @staticmethod
    def _convert_tz(dt_naive, from_tz, to_tz):
        dt = pytz.timezone(from_tz).localize(dt_naive)
        dt = dt.astimezone(pytz.timezone(to_tz))
        return dt.replace(tzinfo=None)

    def tz_to_utc(self, datetime_local_naive):
        return self._convert_tz(datetime_local_naive, self.tz, "UTC")

    def utc_to_local(self, datetime_utc_naive):
        return self._convert_tz(datetime_utc_naive, "UTC", self.tz)

    # Deprecated: use utc_to_local instead
    def tz_to_local(self, datetime_utc_naive):
        return self.utc_to_local(datetime_utc_naive)

    def server_tz_to_utc(self, datetime_server_naive):
        return self._convert_tz(datetime_server_naive, self.server_tz, "UTC")

    def utc_to_server_tz(self, datetime_utc_naive):
        return self._convert_tz(datetime_utc_naive, "UTC", self.server_tz)

    @contextmanager
    def work_on(self, model_name, **kwargs):
        backend = self
        if self.user_id:
            backend = self.with_user(self.user_id)
        with super(ConnectorBackend, backend).work_on(model_name, **kwargs) as work:
            yield work

    # Scheduler methods
    @api.model
    def _get_current_user_company(self):
        if self.env.user.id == self.env.ref("base.user_root").id:
            raise ValidationError(_("The cron user cannot be admin"))
        if self.env.company != self.env.user.company_id:
            raise ValidationError(
                _(
                    "The current company must be the same as the default company of the user. "
                )
            )
        if self.env.company != self.env.user.company_ids:
            raise ValidationError(
                _("The current company must be one of the companies of the user. ")
            )
        return self.env.company

    @api.model
    def scheduler(self, function_name):
        company_id = self._get_current_user_company()
        domain = [("company_id", "=", company_id.id)]
        func = getattr(self.search(domain), function_name)
        return func()
