# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    oxigesti_bind_ids = fields.One2many(
        comodel_name="oxigesti.product.pricelist.item",
        inverse_name="odoo_id",
        string="Oxigesti Bindings",
    )
    oxigesti_write_date = fields.Datetime(
        compute="_compute_oxigesti_write_date",
        store=True,
        required=True,
        default=fields.Datetime.now,
    )

    @api.depends(
        "product_tmpl_id.active",
        "oxigesti_bind_ids",
        "compute_price",
        "applied_on",
        "fixed_price",
    )
    def _compute_oxigesti_write_date(self):
        for rec in self:
            rec.oxigesti_write_date = rec.write_date

    @api.constrains("compute_price", "applied_on")
    def _check_binding(self):
        for rec in self:
            if rec.oxigesti_bind_ids:
                if rec.compute_price != "fixed":
                    raise ValidationError(
                        _(
                            "You can't change the price calculation method of a "
                            "pricelist item because they have been exported the "
                            "product prices by customer to Oxigesti.\nIf you need to "
                            "change the price calculation method, you can delete the "
                            "pricelist item and create a new one."
                        )
                    )
                if rec.applied_on != "1_product":
                    raise ValidationError(
                        _(
                            "You can't change the applied on field of a pricelist "
                            "item because they have been exported the product prices "
                            "by customer to Oxigesti.\nIf you need to change the "
                            "applied on field, you can delete the pricelist item and "
                            "create a new one."
                        )
                    )

    @api.constrains("product_tmpl_id")
    def _check_product_tmpl_id(self):
        for rec in self:
            if rec.oxigesti_bind_ids:
                raise ValidationError(
                    _(
                        "You can't change the product of a pricelist item "
                        "because they have been exported the product prices by "
                        "customer to Oxigesti.\nIf you need to change the product, "
                        "you can delete the pricelist item and create a new one."
                    )
                )


class ProductPricelistItemBinding(models.Model):
    _name = "oxigesti.product.pricelist.item"
    _inherit = "oxigesti.binding"
    _inherits = {"product.pricelist.item": "odoo_id"}
    _description = "Product pricelist item binding"

    odoo_id = fields.Many2one(
        comodel_name="product.pricelist.item",
        string="Product pricelist item",
        required=True,
        ondelete="cascade",
    )
    odoo_partner_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", required=True, ondelete="cascade"
    )
    deprecated = fields.Boolean(default=False)
    odoo_fixed_price = fields.Float(
        compute="_compute_odoo_fixed_price",
        store=True,
    )

    @api.depends("odoo_id.fixed_price", "deprecated", "external_id")
    def _compute_odoo_fixed_price(self):
        for rec in self:
            if not rec.deprecated or not rec.external_id:
                rec.odoo_fixed_price = rec.odoo_id.fixed_price

    _sql_constraints = [
        (
            "oxigesti_external_uniq",
            "unique(backend_id, external_id_hash)",
            "An ODoo record with same ID already exists on Oxigesti.",
        ),
        (
            "oxigesti_odoo_uniq",
            "unique(backend_id, odoo_id, odoo_partner_id)",
            "An ODoo record with same ID already exists on Oxigesti.",
        ),
    ]

    @api.model
    def export_data(self, backend, since_date):
        domain = [("company_id", "in", (backend.company_id.id, False))]
        if since_date:
            domain += [("write_date", ">", since_date)]
        self.with_delay().export_batch(backend, domain=domain)

    def is_deprecated(self):
        self.ensure_one()
        return (
            self.odoo_partner_id.property_product_pricelist != self.odoo_id.pricelist_id
            or not self.odoo_id.active
            or not self.odoo_id.product_tmpl_id.active
            or not self.odoo_partner_id.active
        )

    def resync(self):
        for record in self:
            func = record.export_record
            if record.env.context.get("connector_delay"):
                func = record.export_record.delay
            func(record.backend_id, record)
        return True
