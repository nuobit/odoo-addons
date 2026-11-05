# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import fields, models


class ConnectorExtensionTestBackend(models.Model):
    _name = "connector.extension.test.backend"
    _inherit = "connector.extension.backend"
    _description = "Connector Extension Test Backend"


class ConnectorExtensionTestBinding(models.Model):
    _name = "connector.extension.test.binding"
    _inherit = "connector.extension.external.binding"
    _inherits = {"res.partner": "odoo_id"}
    _description = "Connector Extension Test Binding"

    odoo_id = fields.Many2one(
        comodel_name="res.partner",
        string="Bound Partner",
        required=True,
        ondelete="cascade",
    )
    backend_id = fields.Many2one(
        comodel_name="connector.extension.test.backend",
        string="Test Backend",
        required=True,
        ondelete="restrict",
    )
    external_id = fields.Integer(
        string="Remote ID",
    )
