# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from . import cbl

_logger = logging.getLogger(__name__)


class CBLBackend(models.Model):
    _name = "cbl.backend"
    _inherit = "connector.backend"

    _description = "CBL Backend Configuration"

    @api.model
    def _select_state(self):
        return [
            ("draft", "Draft"),
            ("checked", "Checked"),
            ("production", "In Production"),
        ]

    name = fields.Char(
        required=True,
    )
    sequence = fields.Integer(
        required=True,
        default=1,
    )
    username = fields.Char(
        required=True,
    )
    password = fields.Char(
        required=True,
    )
    output = fields.Text(
        readonly=True,
    )
    active = fields.Boolean(
        default=True,
    )
    state = fields.Selection(
        selection="_select_state",
        default="draft",
    )

    def button_reset_to_draft(self):
        self.ensure_one()
        self.write({"state": "draft", "output": None})

    def _check_connection(self):
        self.ensure_one()
        er = cbl.CBL(username=self.username, password=self.password)
        if not er.login():
            raise ValidationError(_("Error on logging in"))
        self.output = "OK"

    def button_check_connection(self):
        self._check_connection()
        self.write({"state": "checked"})
