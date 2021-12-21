# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ProductBuyerInfo(models.Model):
    _name = "product.buyerinfo"
    _description = "Buyer Info"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        ondelete="cascade",
        string="Customer",
        required=True,
    )

    code = fields.Char(string="Product code")

    name = fields.Text(string="Product name", translate=True)

    product_id = fields.Many2one(
        comodel_name="product.product", required=True, ondelete="cascade"
    )

    _sql_constraints = [
        (
            "buyerinfo_uniq",
            "unique(product_id, partner_id)",
            "Already exists this same line!",
        ),
    ]

    def name_get(self):
        vals = []
        for record in self:
            key_name = "%s - %s" % (
                record.partner_id.display_name,
                record.product_id.display_name,
            )
            data_name_l = ["[%s]" % record.code or ""]
            if record.name:
                data_name_l.append(record.name)

            vals.append((record.id, "%s: %s" % (key_name, " ".join(data_name_l))))

        return vals

    @api.constrains("code", "name")
    def _check_code_name(self):
        for rec in self:
            if not rec.code and not rec.name:
                raise ValidationError(
                    _(
                        "If you're not gonna define code and name, "
                        "you better remove the entire line"
                    )
                )
