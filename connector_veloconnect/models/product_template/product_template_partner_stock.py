# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductTemplatePartnerStock(models.Model):
    _name = 'product.template.partner.stock'

    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Template',
        required=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        ondelete="cascade",
    )

    status = fields.Char(string="Status", required=True)
    quantity = fields.Float(string="Quantity", required=True)
    last_update = fields.Datetime(string="Last Update")

    _sql_constraints = [
        (
            "vtps_uniq",
            "unique(product_tmpl_id,partner_id)",
            "Already exists a partner with the same product.",
        ),
    ]
