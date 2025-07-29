# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
import logging

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
        help="This field is used to define in which timezone the backend will work.",
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
