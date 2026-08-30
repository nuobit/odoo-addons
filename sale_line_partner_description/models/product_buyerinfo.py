# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBit Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression
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

    @api.model
    def search_by_partner(self, partner_id, domain):
        partner_domain = [("partner_id", "=", partner_id)]
        parent = self.env["res.partner"].browse(partner_id).parent_id
        if parent:
            partner_domain = expression.OR(
                [
                    partner_domain,
                    [("partner_id", "=", parent.id)],
                ]
            )
        domain = expression.AND([partner_domain, domain])
        return self.env["product.buyerinfo"].search(domain)

    @api.depends("partner_id", "product_id", "code", "name")
    def _compute_display_name(self):
        for record in self:
            key_name = (
                f"{record.partner_id.display_name} - {record.product_id.display_name}"
            )
            data_name_l = [f"[{record.code}]" if record.code else ""]
            if record.name:
                data_name_l.append(record.name)

            record.display_name = "{}: {}".format(key_name, " ".join(data_name_l))

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
