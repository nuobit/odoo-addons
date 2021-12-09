# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    oxigesti_bind_ids = fields.One2many(
        comodel_name="oxigesti.product.pricelist.item",
        inverse_name="odoo_id",
        string="Oxigesti Bindings",
    )


class ProductPricelistItemBinding(models.Model):
    _name = "oxigesti.product.pricelist.item"
    _inherit = "oxigesti.binding"
    _inherits = {"product.pricelist.item": "odoo_id"}
    _description = "Product pricelist item binding"

    odoo_id = fields.Many2one(
        comodel_name="product.pricelist.item",
        string="Product pricelist item",
        required=True,
        ondelete="cascade",
    )

    odoo_partner_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", required=True, ondelete="cascade"
    )
    _sql_constraints = [
        (
            "oxigesti_external_uniq",
            "unique(backend_id, external_id_hash)",
            "An ODoo record with same ID already exists on Oxigesti.",
        ),
        (
            "oxigesti_odoo_uniq",
            "unique(backend_id, odoo_id, odoo_partner_id)",
            "An ODoo record with same ID already exists on Oxigesti.",
        ),
    ]

    @api.model
    def export_product_prices_by_customer_since(
        self, backend_record=None, since_date=None
    ):
        """ Prepare the batch export of product prices by customer modified on Odoo """
        domain = [("company_id", "in", (backend_record.company_id.id, False))]
        if since_date:
            domain += [("write_date", ">", since_date)]
        now_fmt = fields.Datetime.now()
        self.export_batch(backend=backend_record, domain=domain)
        backend_record.export_product_prices_by_customer_since_date = now_fmt
        return True

    def resync(self):
        for record in self:
            func = record.export_record
            if record.env.context.get("connector_delay"):
                func = record.export_record.delay
            func(record.backend_id, record)
        return True
