# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class WooCommerceProductPublicCategory(models.Model):
    _name = "woocommerce.product.public.category"
    _inherit = "woocommerce.binding"
    _inherits = {"product.public.category": "odoo_id"}
    _description = "WooCommerce Product Public Category Binding"

    odoo_id = fields.Many2one(
        comodel_name="product.public.category",
        string="Product public category",
        required=True,
        ondelete="cascade",
    )
    woocommerce_idpubliccategory = fields.Integer(
        string="WooCommerce ID Public Category",
        readonly=True,
        required=True,
    )

    _sql_constraints = [
        (
            "external_uniq",
            "unique(backend_id, woocommerce_idpubliccategory)",
            "A binding already exists with the same External (idProduct) ID.",
        ),
    ]

    @api.model
    def _get_base_domain(self):
        return []

    def export_product_public_category_since(
        self, backend_record=None, since_date=None
    ):
        # with backend_record.work_on(self._name) as work:
        #     adapter = work.component(usage="backend.adapter")
        # url = "products/categories"
        # # domain=[('name', '=', 'Ventilació mecànica'), ('lang', '=', 'ca')]
        # # domain = [('id', '=', 3081), ('lang', '=', 'ca')]
        # domain = [
        #     #("id", "in", [2946, 2949, 2937, 2955, 3051, 2943, 2967, 2964]),
        #     ("lang", "=", "ca"),
        # ]
        # # values = adapter.get_total_items(url, domain)
        # # values = adapter._exec("get", url, offset=3, limit=11)
        # pairs = [(13, 10)]
        # for offset, limit in pairs:
        #     values = adapter._exec(
        #         "get", url, domain=domain, offset=offset, limit=limit, count=False
        #     )
        #     if isinstance(values, list):
        #         for v in values:
        #             # print(">", v)
        #             print(">", v["id"])
        #         print("--->", len(values))
        #     else:
        #         print(">>>", values)
        # exit()

        domain = self._get_base_domain()
        if since_date:
            domain += [
                ("write_date", ">", fields.Datetime.to_string(since_date)),
            ]
        self.with_delay().export_batch(backend_record, domain=domain)
        return True
