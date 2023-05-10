# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class WooCommerceProductProduct(models.Model):
    _name = "woocommerce.product.product"
    _inherit = "woocommerce.binding"
    _inherits = {"product.product": "odoo_id"}
    _description = "WooCommerce Product product Binding"

    odoo_id = fields.Many2one(
        comodel_name="product.product",
        string="Product product",
        required=True,
        ondelete="cascade",
    )
    woocommerce_idproduct = fields.Integer(
        string="ID Product",
        readonly=True,
    )
    woocommerce_idparent = fields.Integer(
        string="ID Parent",
        readonly=True,
    )
    _sql_constraints = [
        (
            "external_uniq",
            "unique(backend_id, woocommerce_idproduct)",
            "A binding already exists with the same External (idProduct) ID.",
        ),
    ]

    @api.model
    def _get_base_domain(self):
        return [
            # ("is_published", "=", True),
        ]

    def export_products_since(self, backend_record=None, since_date=None):
        domain = self._get_base_domain()
        # TODO: descomentar
        # if since_date:
        # domain = expression.OR(
        #     [
        #         domain,
        #         [
        #             (
        #                 "woocommerce_write_date",
        #                 ">",
        #                 fields.Datetime.to_string(since_date),
        #             )
        #         ],
        #     ]
        # )
        domain += [
            #     # ("woocommerce_write_date", ">", fields.Datetime.to_string(since_date)),
            #     # ("is_published", "=", True),
            ("id", "in", (62558, 62559, 62560))  # variable product+simple product
            # ("id", "in", (62558, 62559))  # variable product
            # ("id", "=", 62560)  # simple product
        ]
        self.export_batch(backend_record, domain=domain)
        return True

    def resync(self):
        for record in self:
            with record.backend_id.work_on(record._name) as work:
                binder = work.component(usage="binder")
                relation = binder.unwrap_binding(self)
            func = record.export_record
            if record.env.context.get("connector_delay"):
                func = record.export_record.delay
            func(record.backend_id, relation)
        return True
