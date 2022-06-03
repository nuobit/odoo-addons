# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductTemplatePartnerStock(models.Model):
    _name = "product.template.partner.stock"

    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        string="Template",
        required=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Vendor",
        required=True,
        ondelete="cascade",
    )

    status = fields.Char(string="Status", required=True)
    quantity = fields.Float(
        string="Quantity",
        required=True,
        help="Quantity. If it's -1 means there's no information "
        "about quantity on that supplier",
    )
    sync_date = fields.Datetime(string="Updated at")

    _sql_constraints = [
        (
            "vtps_uniq",
            "unique(product_tmpl_id,partner_id)",
            "Already exists a partner with the same product.",
        ),
    ]
