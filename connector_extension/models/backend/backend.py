# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
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


class ConnectorBackend(models.AbstractModel):
    # _name = "connector.backend.extension"
    _inherit = "connector.backend"
    _description = "Connector Backend Extension"

    @api.model
    def _select_state(self):
        return [
            ("draft", "Draft"),
            ("validated", "Validated"),
        ]

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
