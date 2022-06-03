# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.brand"

    veloconnect_bind_ids = fields.One2many(
        comodel_name="veloconnect.product.brand",
        inverse_name="odoo_id",
        string="Veloconnect Bindings",
    )


class ProductSupplierinfoBinding(models.Model):
    _name = "veloconnect.product.brand"
    _inherit = "veloconnect.binding"
    _inherits = {"product.brand": "odoo_id"}

    odoo_id = fields.Many2one(
        comodel_name="product.brand", string="Brand", required=True, ondelete="cascade"
    )

    veloconnect_manufacturer_name = fields.Char(
        string="Veloconnect ManufacturersItemIdentificationName", required=True
    )

    _sql_constraints = [
        (
            "vp_external_uniq",
            "unique(backend_id, veloconnect_manufacturer_name)",
            "A binding already exists with the same External (veloconnect) ID.",
        ),
    ]
