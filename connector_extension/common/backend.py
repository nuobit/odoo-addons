# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


# TODO:REVIEW: GET_VERSION
class ConnectorBackend(models.AbstractModel):
    _inherit = "connector.backend"

    @api.model
    def _select_state(self):
        return [
            ("draft", "Draft"),
            ("validated", "Validated"),
        ]

    def _check_connection(self):
        raise NotImplementedError

    def button_check_connection(self):
        for rec in self:
            rec._check_connection()
            rec.state = "validated"
        return

    # TODO: REVIEW: Create a template view to be inhereted
    state = fields.Selection(
        selection="_select_state",
        default="draft",
    )
    active = fields.Boolean(
        default=True,
    )

    def check_connection(self):
        self.ensure_one()
        with self.work_on("connector.backend") as work:
            component = work.component(usage="backend.adapter")
            self.version = component.get_version()
