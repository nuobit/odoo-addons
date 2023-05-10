# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class WooCommerceProductTemplate(models.Model):
    _name = "woocommerce.product.template"
    _inherit = "woocommerce.binding"
    _inherits = {"product.template": "odoo_id"}
    _description = "WooCommerce Product template Binding"

    odoo_id = fields.Many2one(
        comodel_name="product.template",
        string="Product template",
        required=True,
        ondelete="cascade",
    )
    woocommerce_idproduct = fields.Integer(
        string="ID Product",
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
            # ("boat_id", "!=", False),
        ]

    def export_product_tmpl_since(self, backend_record=None, since_date=None):
        domain = self._get_base_domain()
        # TODO: descomentar
        # if since_date:
        domain += [
            # ("write_date", ">", fields.Datetime.to_string(since_date)),
            # ("id", "=", 40593)
            ("id", "=", 40762)
            # ("id", "=", 62850) simple_product
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
