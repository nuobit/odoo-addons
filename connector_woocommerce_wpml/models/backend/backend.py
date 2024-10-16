# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class WooCommerceWPMLBackend(models.Model):
    _name = "woocommerce.wpml.backend"
    _inherit = "connector.extension.backend"
    _description = "WooCommerce WPML Backend"

    name = fields.Char(
        required=True,
    )
    url = fields.Char(
        help="WooCommerce URL",
        required=True,
    )
    consumer_key = fields.Char(
        help="WooCommerce Consumer Key",
        required=True,
    )
    consumer_secret = fields.Char(
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company,
        ondelete="restrict",
    )
    client_order_ref_prefix = fields.Char(
        string="Client Order Reference Prefix",
        help="Prefix to add to the client order reference",
        required=True,
    )
    verify_ssl = fields.Boolean(
        default=True,
    )
    discount_pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
    )
    wordpress_backend_id = fields.Many2one(
        comodel_name="wordpress.backend",
    )
    use_main_product_image = fields.Selection(
        selection=[
            ("no", "Don't use main image"),
            ("first", "Use main image as first image"),
            ("last", "Use main image as last image"),
        ],
        default="first",
    )
    export_product_tmpl_since_date = fields.Datetime(
        string="Export Product Templates Since",
    )
    export_products_since_date = fields.Datetime(
        string="Export Products Since",
    )
    export_sale_orders_since_date = fields.Datetime(
        string="Export Sale Orders Since",
    )
    export_product_public_category_since_date = fields.Datetime(
        string="Export Product public category Since",
    )
    export_product_attribute_since_date = fields.Datetime(
        string="Export Product attributes Since",
    )
    export_product_attribute_value_since_date = fields.Datetime(
        string="Export Product attribute values Since",
    )
    export_checksum_since_date = fields.Datetime(
        string="Export Product Checksum Since",
    )
    import_sale_order_since_date = fields.Datetime(
        string="Import Sale Order Since",
    )
    stock_location_ids = fields.Many2many(
        string="Locations",
        comodel_name="stock.location",
        readonly=False,
        required=True,
        domain="[('usage', 'in', ['internal','view'])]",
    )
    language_id = fields.Many2one(
        required=False,
    )

    language_ids = fields.Many2many(
        string="Languages for WPML",
        comodel_name="res.lang",
        required=True,
    )
    payment_mode_ids = fields.One2many(
        comodel_name="woocommerce.wpml.backend.payment.mode",
        inverse_name="backend_id",
    )
    tax_map_ids = fields.One2many(
        comodel_name="woocommerce.wpml.backend.account.tax",
        inverse_name="backend_id",
    )
    tax_class_ids = fields.One2many(
        comodel_name="woocommerce.wpml.backend.tax.class",
        inverse_name="backend_id",
    )
    shipping_product_id = fields.Many2one(
        comodel_name="product.product",
    )

    page_size = fields.Integer(
        help="Number of records to fetch at a time. Max: 100",
    )

    @api.constrains("page_size")
    def _check_page_size(self):
        for rec in self:
            if rec.page_size > 100:
                raise ValidationError(_("Page size must be less than 100"))

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
    def export_sale_orders_since(self):
        self.env.user.company_id = self.company_id
        for rec in self:
            since_date = fields.Datetime.from_string(rec.export_sale_orders_since_date)
            rec.export_sale_orders_since_date = fields.Datetime.now()
            self.env["woocommerce.wpml.sale.order"].export_sale_orders_since(
                backend_record=rec, since_date=since_date
            )

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
    #         self.env["wordpress.wpml.ir.checksum"].export_checksum_since(
    #             backend_record=rec, since_date=since_date
    #         )

    def import_sale_orders_since(self):
        self.env.user.company_id = self.company_id
        for rec in self:
            since_date = fields.Datetime.from_string(rec.import_sale_order_since_date)
            rec.import_sale_order_since_date = fields.Datetime.now()
            self.env["woocommerce.wpml.sale.order"].import_sale_orders_since(
                backend_record=rec, since_date=since_date
            )

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
