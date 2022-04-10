# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import requests

from odoo import _, fields, models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SapBackend(models.Model):
    _name = "sap.backend.res.partner"
    _description = "SAP Backend Res Partner"

    backend_id = fields.Many2one(
        string="Backend id",
        comodel_name="sap.backend",
        required=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        string="Odoo Partner",
        comodel_name="res.partner",
        required=True,
        ondelete="cascade",
    )
    sap_cardcode = fields.Char(string="SAP CardCode", required=True)

