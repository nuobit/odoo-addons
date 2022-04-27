# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    ambugest_bind_ids = fields.One2many(
        comodel_name="ambugest.product.product",
        inverse_name="odoo_id",
        string="Ambugest Bindings",
    )


class ProductProductBinding(models.Model):
    _name = "ambugest.product.product"
    _inherit = "ambugest.binding"
    _inherits = {"product.product": "odoo_id"}
    _description = "Product binding"

    odoo_id = fields.Many2one(
        comodel_name="product.product",
        string="Odoo Product",
        required=True,
        ondelete="cascade",
    )

    # id
    ambugest_empresa = fields.Integer(string="Empresa on Ambugest", required=True)
    ambugest_id = fields.Integer(string="Id on Ambugest", required=True)

    _sql_constraints = [
        (
            "uniq",
            "unique(ambugest_id, ambugest_empresa)",
            "Product with same ID on Ambugest already exists.",
        ),
    ]

    def import_products_since(self, backend_record=None, since_date=None):
        """Prepare the import of products modified on Ambugest"""
        filters = {
            "Empresa": backend_record.ambugest_company_id,
        }
        now_fmt = fields.Datetime.now()
        self.env["ambugest.product.product"].import_batch(
            backend=backend_record, filters=filters
        )
        backend_record.import_products_since_date = now_fmt

        return True
