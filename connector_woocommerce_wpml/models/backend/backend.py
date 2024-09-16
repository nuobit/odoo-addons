# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class WooCommerceWPMLBackend(models.Model):
    _name = "woocommerce.wpml.backend"
    _inherit = "woocommerce.backend"
    _description = "WooCommerce WPML Backend"

    language_id = fields.Many2one(
        required=False,
    )

    language_ids = fields.Many2many(
        string="Languages for WPML",
        comodel_name="res.lang",
    )
    payment_mode_ids = fields.One2many(
        comodel_name="woocommerce.wpml.backend.payment.mode",
    )
    tax_map_ids = fields.One2many(
        comodel_name="woocommerce.wpml.backend.account.tax",
    )
    tax_class_ids = fields.One2many(
        comodel_name="woocommerce.wpml.backend.tax.class",
    )

    @api.constrains("language_ids")
    def check_language_ids(self):
        for rec in self:
            for lang in rec.language_ids:
                if not lang.wordpress_wpml_lang_code:
                    raise ValidationError(
                        _(
                            "The language %s has no WPML code, please define "
                            "this code in language before using it." % lang.name
                        )
                    )

    def export_product_tmpl_since(self):
        self.env.user.company_id = self.company_id
        for rec in self:
            since_date = fields.Datetime.from_string(rec.export_product_tmpl_since_date)
            rec.export_product_tmpl_since_date = fields.Datetime.now()
            self.env["woocommerce.wpml.product.template"].export_product_tmpl_since(
                backend_record=rec, since_date=since_date
            )

    def export_products_since(self):
        self.env.user.company_id = self.company_id
        for rec in self:
            since_date = fields.Datetime.from_string(rec.export_products_since_date)
            rec.export_products_since_date = fields.Datetime.now()
            self.env["woocommerce.wpml.product.product"].export_products_since(
                backend_record=rec, since_date=since_date
            )

    # TODO: Uncomment this method when the sale order wpml will be implemented
    # def export_sale_orders_since(self):
    #     self.env.user.company_id = self.company_id
    #     for rec in self:
    #         since_date = fields.Datetime.from_string(rec.export_sale_orders_since_date)
    #         rec.export_sale_orders_since_date = fields.Datetime.now()
    #         self.env["woocommerce.wpml.sale.order"].export_sale_orders_since(
    #             backend_record=rec, since_date=since_date
    #         )

    def export_product_public_category_since(self):
        self.env.user.company_id = self.company_id
        for rec in self:
            since_date = fields.Datetime.from_string(
                rec.export_product_public_category_since_date
            )
            rec.export_product_public_category_since_date = fields.Datetime.now()
            self.env[
                "woocommerce.wpml.product.public.category"
            ].export_product_public_category_since(
                backend_record=rec, since_date=since_date
            )

    def export_product_attribute_since(self):
        self.env.user.company_id = self.company_id
        for rec in self:
            since_date = fields.Datetime.from_string(
                rec.export_product_attribute_since_date
            )
            rec.export_product_attribute_since_date = fields.Datetime.now()
            self.env[
                "woocommerce.wpml.product.attribute"
            ].export_product_attribute_since(backend_record=rec, since_date=since_date)

    def export_product_attribute_value_since(self):
        self.env.user.company_id = self.company_id
        for rec in self:
            since_date = fields.Datetime.from_string(
                rec.export_product_attribute_value_since_date
            )
            rec.export_product_attribute_value_since_date = fields.Datetime.now()
            self.env[
                "woocommerce.wpml.product.attribute.value"
            ].export_product_attribute_value_since(
                backend_record=rec, since_date=since_date
            )

    # TODO: This functions will be used when checksum_wpml will be ready
    # def export_checksum_since(self):
    #     self.env.user.company_id = self.company_id
    #     for rec in self:
    #         since_date = fields.Datetime.from_string(rec.export_checksum_since_date)
    #         rec.export_checksum_since_date = fields.Datetime.now()
    #         self.env["wordpress.ir.checksum"].export_checksum_since(
    #             backend_record=rec, since_date=since_date
    #         )
    #
    # def import_sale_orders_since(self):
    #     self.env.user.company_id = self.company_id
    #     for rec in self:
    #         since_date = fields.Datetime.from_string(rec.import_sale_order_since_date)
    #         rec.import_sale_order_since_date = fields.Datetime.now()
    #         self.env["woocommerce.wpml.sale.order"].import_sale_orders_since(
    #             backend_record=rec, since_date=since_date
    #         )

    # scheduler
    @api.model
    def _scheduler_export_products(self):
        for backend in self.env[self._name].search([("state", "=", "validated")]):
            backend.export_products_since()

    # scheduler
    @api.model
    def _scheduler_export_product_tmpl(self):
        for backend in self.env[self._name].search([("state", "=", "validated")]):
            backend.export_product_tmpl_since()

    @api.model
    def _scheduler_export_sale_orders(self):
        for backend in self.env[self._name].search([("state", "=", "validated")]):
            backend.export_sale_orders_since()

    @api.model
    def _scheduler_import_sale_orders(self):
        for backend in self.env[self._name].search([("state", "=", "validated")]):
            backend.import_sale_orders_since()

    @api.model
    def _scheduler_export_product_public_category(self):
        for backend in self.env[self._name].search([("state", "=", "validated")]):
            backend.export_product_public_category_since()

    @api.model
    def _scheduler_export_product_attribute(self):
        for backend in self.env[self._name].search([("state", "=", "validated")]):
            backend.export_product_attribute_since()

    @api.model
    def _scheduler_export_product_attribute_value(self):
        for backend in self.env[self._name].search([("state", "=", "validated")]):
            backend.export_product_attribute_value_since()

    @api.model
    def _scheduler_export_checksum(self):
        for backend in self.env[self._name].search([("state", "=", "validated")]):
            backend.export_checksum_since()
