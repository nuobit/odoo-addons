# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    woocommerce_bind_ids = fields.One2many(
        comodel_name="woocommerce.product.template",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        context={"active_test": False},
    )
    woocommerce_write_date = fields.Datetime(
        compute="_compute_woocommerce_write_date",
        store=True,
    )
    has_attributes = fields.Boolean(
        compute="_compute_has_attributes",
        search="_search_has_attributes",
    )

    @api.depends("attribute_line_ids")
    def _compute_has_attributes(self):
        for rec in self:
            rec.has_attributes = bool(rec.attribute_line_ids)

    def _search_has_attributes(self, operator, value):
        if operator == "=" and value:
            return [("attribute_line_ids", "!=", False)]
        return [("attribute_line_ids", operator, value)]

    @api.depends(
        "is_published",
        "name",
        "lst_price",
        "active",
        "qty_available",
        "image_1920",
        "default_code",
        "description",
        "public_categ_ids",
        "attribute_line_ids",
        "public_description",
        "inventory_availability",
        "has_attributes",
        "document_ids",
        "woocommerce_enabled",
    )
    def _compute_woocommerce_write_date(self):
        for rec in self:
            if (
                rec.woocommerce_enabled
                or rec.is_published
                or rec.woocommerce_write_date
            ):
                rec.woocommerce_write_date = fields.Datetime.now()

    website_name = fields.Char(
        translate=True,
    )
    public_description = fields.Text(
        translate=True,
    )
    public_short_description = fields.Text(
        translate=True,
    )
    slug_name = fields.Char(
        translate=True,
    )
    is_published = fields.Boolean(
        compute="_compute_template_is_published",
        inverse="_inverse_template_is_published",
        store=True,
        readonly=False,
    )
    button_is_published = fields.Boolean(
        related="is_published",
    )
    woocommerce_enabled = fields.Boolean(
        compute="_compute_woocommerce_enabled",
        store=True,
        readonly=False,
    )

    def _compute_woocommerce_enabled(self):
        for rec in self:
            rec.woocommerce_enabled = rec.is_published

    @api.depends("product_variant_ids.variant_is_published")
    def _compute_template_is_published(self):
        for rec in self:
            published_variants = rec._origin.product_variant_ids.filtered(
                lambda x: x.variant_is_published
            )
            rec.is_published = bool(published_variants)

    def _inverse_template_is_published(self):
        for rec in self:
            rec.product_variant_ids.variant_is_published = rec.is_published

    inventory_availability = fields.Selection(
        compute="_compute_inventory_availability",
        inverse="_inverse_inventory_availability",
        store=True,
        readonly=False,
    )

    @api.depends("product_variant_ids.variant_inventory_availability")
    def _compute_inventory_availability(self):
        for rec in self:
            never_variants_availability = rec.product_variant_ids.filtered(
                lambda x: x.variant_inventory_availability == "never"
            )
            if never_variants_availability:
                rec.inventory_availability = "never"
            else:
                rec.inventory_availability = "always"

    def _inverse_inventory_availability(self):
        for rec in self:
            if rec.inventory_availability in ("always", "never"):
                rec.product_variant_ids.variant_inventory_availability = (
                    rec.inventory_availability
                )

    def write(self, vals):
        res = super().write(vals)
        if "has_attributes" in vals:
            for rec in self:
                if (
                    rec.woocommerce_bind_ids
                    and rec.has_attributes != vals["has_attributes"]
                ):
                    raise ValidationError(
                        _(
                            "You can't change the attributes if the "
                            "product has a woocommerce binding"
                        )
                    )
        return res
