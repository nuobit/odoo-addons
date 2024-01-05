# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

import logging

from odoo import _, api, exceptions, fields, models

from . import ertransit

_logger = logging.getLogger(__name__)


class ERTransitBackend(models.Model):
    _name = "ertransit.backend"
    _inherit = "connector.backend"

    _description = "ERTransit / Erhardt Backend Configuration"

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
        er = ertransit.ERTransit(username=self.username, password=self.password)
        if not er.login():
            raise exceptions.ValidationError(_("Error on logging in"))
        if not er.logout():
            raise exceptions.ValidationError(_("Error on logging out"))
        self.output = "OK"

    def button_check_connection(self):
        self._check_connection()
        self.write({"state": "checked"})
