# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ProductTemplateBinding(models.Model):
    _name = "veloconnect.product.template"
    _inherit = "veloconnect.binding"
    _inherits = {"product.template": "odoo_id"}

    odoo_id = fields.Many2one(
        comodel_name="product.template",
        string="Product",
        required=True,
        ondelete="cascade",
    )
    veloconnect_seller_item_id = fields.Char(
        string="Veloconnect SellersItemIdentificationID", required=True
    )
    veloconnect_hash = fields.Char(string="Veloconnect Hash", required=True)
    veloconnect_description = fields.Char(string="Veloconnect Description")
    veloconnect_price = fields.Float(
        string="Veloconnect RecommendedRetailPrice", required=True
    )
    veloconnect_uom = fields.Char(string="Veloconnect quantityUnitCode", required=True)

    _sql_constraints = [
        (
            "vp_external_uniq",
            "unique(backend_id, veloconnect_seller_item_id)",
            "A binding already exists with the same External (veloconnect) ID.",
        ),
    ]

    @api.model
    def import_data(self, backend_record=None):
        domain = [("StandardItemIdentification", "!=", None)]
        self.env[self._name].with_delay().import_batch(
            backend_record=backend_record, domain=domain
        )
        return True
