# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class SaleOrderLineBinding(models.Model):
    _name = "lengow.sale.order.line"
    _inherit = "lengow.binding"
    _inherits = {"sale.order.line": "odoo_id"}

    odoo_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Order line",
        required=True,
        ondelete="cascade",
    )

    backend_id = fields.Many2one(
        related="lengow_order_id.backend_id",
        string="Backend",
        readonly=True,
        store=True,
        required=False,
    )

    lengow_order_id = fields.Many2one(
        comodel_name="lengow.sale.order",
        string="Lengow Order",
        required=True,
        ondelete="cascade",
        index=True,
    )

    lengow_id = fields.Integer(string="Lengow ID", required=True)
    lengow_marketplace = fields.Char(string="Marketplace on Lengow", required=True)
    lengow_marketplace_order_id = fields.Char(string="Order on Lengow", required=True)

    _sql_constraints = [
        (
            "lol_ext_uniq",
            "unique(backend_id, lengow_id, lengow_marketplace, lengow_marketplace_order_id)",
            "A binding already exists with the same External (Lengow) ID.",
        ),
    ]

    @api.model
    def create(self, vals):
        lengow_order_id = vals["lengow_order_id"]
        binding = self.env["lengow.sale.order"].browse(lengow_order_id)
        vals["order_id"] = binding.odoo_id.id
        return super().create(vals)
        # FIXME triggers function field
        # The amounts (amount_total, ...) computed fields on 'sale.order' are
        # not triggered when magento.sale.order.line are created.
        # It might be a v8 regression, because they were triggered in
        # v7. Before getting a better correction, force the computation
        # by writing again on the line.
        # line = binding.odoo_id
        # line.write({'price_unit': line.price_unit})
        # return binding
