# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class SapB1Backend(models.Model):
    _name = "sapb1.backend.res.partner"
    _description = "SAP B1 Backend Res Partner"

    backend_id = fields.Many2one(
        string="Backend id",
        comodel_name="sapb1.backend",
        required=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        string="Odoo Partner",
        comodel_name="res.partner",
        required=True,
        ondelete="restrict",
    )
    sapb1_cardcode = fields.Char(string="SAP B1 CardCode", required=True)

    _sql_constraints = [
        (
            "sapb1_backend_res_partner_external_uniq",
            "unique(backend_id, partner_id)",
            "A mapping already exists with the same partner.",
        ),
    ]
