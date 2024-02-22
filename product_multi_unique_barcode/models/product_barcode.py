# Copyright 2024 NuoBiT Solutions S.L. - Eric Antones <eantones@nuobit.com>
# Copyright 2024 NuoBiT Solutions S.L. - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _


class ProductBarcode(models.Model):
    _inherit = "product.barcode"

    company_id = fields.Many2one(
        comodel_name="res.company",
        compute="_compute_company_id",
        store=True,
        readonly=True,
        required=True,
    )

    @api.depends("product_id.company_id", "product_tmpl_id.company_id")
    def _compute_company_id(self):
        for rec in self:
            if rec.product_id and rec.product_tmpl_id:
                if rec.product_id.company_id != rec.product_tmpl_id.company_id:
                    raise ValidationError(
                        _(
                            "The product %(product)s and its template %(template) "
                            "have different companies"
                        )
                        % dict(
                            product=rec.product_id.display_name,
                            template=rec.product_tmpl_id.display_name,
                        )
                    )
                if rec.product_id and rec.product_id.company_id:
                    rec.company_id = rec.product_id.company_id
                elif rec.product_tmpl_id and rec.product_tmpl_id.company_id:
                    rec.company_id = rec.product_tmpl_id.company_id
                else:
                    rec.company_id = False
            else:
                raise ValidationError(
                    _("There's no link to a product or variant, cannot get the company")
                )

    @api.constrains("name", "company_id")
    def _check_duplicates(self):
        for rec in self:
            domain = [("id", "!=", rec.id), ("name", "=", rec.name)]
            if rec.company_id:
                domain.append(("company_id", "in", (False, rec.company_id.id)))
            others = self.search(domain)
            if others:
                raise UserError(
                    _(
                        'The Barcode "%(barcode_name)s" already exists for '
                        'products: "%(product_names)s"'
                    )
                    % dict(
                        barcode_name=rec.name,
                        product_names=", ".join(
                            [
                                f"({x.id}) {x.display_name}"
                                for x in others.sudo().product_id
                            ]
                        ),
                    )
                )
