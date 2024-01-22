# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    # TODO: Review use deleter to mark items as deprecated
    def unlink(self):
        for rec in self:
            if rec.item_ids.oxigesti_bind_ids:
                raise ValidationError(
                    _(
                        "You can't delete the pricelist %s that has been exported "
                        "the product prices by customer to Oxigesti. If you want to"
                        "delete it, you must first delete the items of the pricelist."
                    )
                    % rec.name
                )
        return super().unlink()


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    oxigesti_bind_ids = fields.One2many(
        comodel_name="oxigesti.product.pricelist.item",
        inverse_name="odoo_id",
        string="Oxigesti Bindings",
    )

    @api.constrains("compute_price", "applied_on", "product_tmpl_id")
    def _check_binding(self):
        for rec in self:
            if rec.oxigesti_bind_ids:
                partners = (
                    self.env["res.partner"]
                    .search(
                        [
                            ("company_id", "=?", rec.company_id.id),
                        ]
                    )
                    .filtered(
                        lambda x: x.property_product_pricelist == rec.pricelist_id
                    )
                )
                if partners:
                    raise ValidationError(
                        _(
                            "You can't change the product, the price calculation "
                            "method or the applied on field of a pricelist item "
                            "because they have been exported the product prices by "
                            "customer to Oxigesti.\nIf you need to change any of "
                            "these fields, you can delete the pricelist item and "
                            "create a new one."
                        )
                    )

    def is_deprecated(self, partner):
        self.ensure_one()
        return (
            partner.property_product_pricelist != self.pricelist_id
            or not self.active
            or not self.product_tmpl_id.active
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

    deprecated = fields.Boolean(
        required=True,
        compute="_compute_deprecated",
        store=True,
    )

    @api.depends(
        "active", "product_tmpl_id.active", "odoo_partner_id.property_product_pricelist"
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
        domain = [("company_id", "in", (backend.company_id.id, False))]
        if since_date:
            domain += [("write_date", ">", since_date)]
        self.with_delay().export_batch(backend, domain=domain)

    def resync(self):
        for record in self:
            func = record.export_record
            if record.env.context.get("connector_delay"):
                func = record.export_record.delay
            func(record.backend_id, record)
        return True
