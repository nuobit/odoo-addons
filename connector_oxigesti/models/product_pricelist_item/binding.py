# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        compute="_compute_partner_ids",
    )

    def _compute_partner_ids(self):
        for rec in self:
            rec.partner_ids = (
                self.env["res.partner"]
                .search(
                    [
                        ("company_id", "", rec.company_id.id),
                    ]
                )
                .filtered(lambda x: x.property_product_pricelist == rec.pricelist_id)
            )

    oxigesti_write_date = fields.Datetime(
        compute="_compute_oxigesti_write_date",
        store=True,
        required=True,
    )

    @api.depends(
        "partner_ids.property_product_pricelist",
        "oxigesti_bind_ids",
        "oxigesti_bind_ids.oxigesti_write_date",
        "compute_price",
        "applied_on",
        "fixed_price",
    )
    def _compute_oxigesti_write_date(self):
        for rec in self:
            rec.oxigesti_write_date = (
                max(
                    rec.mapped("write_date")
                    + rec.oxigesti_bind_ids.mapped("oxigesti_write_date")
                    + rec.oxigesti_bind_ids.odoo_partner_id.mapped("write_date")
                )
                or False
            )

    oxigesti_bind_ids = fields.One2many(
        comodel_name="oxigesti.product.pricelist.item",
        inverse_name="odoo_id",
        string="Oxigesti Bindings",
    )

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

    def is_deprecated(self, partner):
        self.ensure_one()
        return (
            partner.property_product_pricelist != self.pricelist_id
            or not self.active
            or not self.product_tmpl_id.active
            or not partner.active
        )


class ProductPricelistItemBinding(models.Model):
    _name = "oxigesti.product.pricelist.item"
    _inherit = "oxigesti.binding"
    _inherits = {"product.pricelist.item": "odoo_id"}
    _description = "Product pricelist item binding"

    oxigesti_write_date = fields.Datetime(
        compute="_compute_oxigesti_write_date",
        store=True,
        required=True,
        default=fields.Datetime.now,
    )

    @api.depends("deprecated")
    def _compute_oxigesti_write_date(self):
        for rec in self:
            rec.oxigesti_write_date = rec.write_date

    odoo_id = fields.Many2one(
        comodel_name="product.pricelist.item",
        string="Product pricelist item",
        compute="_compute_odoo_id",
        store=True,
        readonly=False,
        required=True,
        ondelete="cascade",
    )

    @api.depends("odoo_partner_id.property_product_pricelist")
    def _compute_odoo_id(self):
        for rec in self:
            record = rec.odoo_partner_id.property_product_pricelist.item_ids.filtered(
                lambda r: r.product_tmpl_id == rec.product_tmpl_id
            )
            if len(record) > 1:
                raise ValidationError(
                    _(
                        "There are more than one pricelist item with the same "
                        "product and the same pricelist for the customer %s"
                    )
                    % rec.odoo_partner_id.name
                )
            if record:
                rec.odoo_id = record

    odoo_partner_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", required=True, ondelete="cascade"
    )

    odoo_fixed_price = fields.Float(
        compute="_compute_odoo_fixed_price",
        store=True,
        required=True,
    )

    @api.depends("odoo_id.fixed_price", "deprecated")
    def _compute_odoo_fixed_price(self):
        for rec in self:
            if not rec.deprecated:
                rec.odoo_fixed_price = rec.odoo_id.fixed_price

    deprecated = fields.Boolean(
        required=True,
        compute="_compute_deprecated",
        store=True,
    )

    @api.depends(
        "odoo_id",
        "odoo_id.active",
        "product_tmpl_id.active",
        "odoo_partner_id.property_product_pricelist",
        "odoo_partner_id.active",
    )
    def _compute_deprecated(self):
        for rec in self:
            rec.deprecated = rec.odoo_id.is_deprecated(rec.odoo_partner_id)

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
        domain = [
            ("company_id", "in", (backend.company_id.id, False)),
            ("compute_price", "=", "fixed"),
            ("applied_on", "=", "1_product"),
        ]
        if since_date:
            domain += [("oxigesti_write_date", ">", since_date)]
        self.with_delay().export_batch(backend, domain=domain)

    def resync(self):
        for record in self:
            func = record.export_record
            if record.env.context.get("connector_delay"):
                func = record.export_record.delay
            func(record.backend_id, record)
        return True
