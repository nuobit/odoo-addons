# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class OxigestiBackendProductAttributeMap(models.Model):
    _name = "oxigesti.backend.product.attribute.map"

    backend_id = fields.Many2one(
        comodel_name="oxigesti.backend",
        string="Oxigesti Backend",
        ondelete="cascade",
    )

    attribute_id = fields.Many2one(
        comodel_name="product.attribute",
        string="Odoo Product Attribute",
        required=True,
        ondelete="restrict",
    )

    oxigesti_attribute = fields.Char(
        string="Oxigesti Attribute",
        required=True,
    )

    _sql_constraints = [
        (
            "uniq",
            "unique(backend_id, attribute_id, external_id)",
            "Attribute mapping line must be unique",
        ),
        (
            "attribute_uniq",
            "unique(backend_id, attribute_id)",
            "Odoo Attribute used in another map line",
        ),
        (
            "external_uniq",
            "unique(backend_id, external_id)",
            "External ID used in another map line",
        ),
    ]
