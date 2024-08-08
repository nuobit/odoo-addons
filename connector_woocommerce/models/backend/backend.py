# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class WooCommerceBackend(models.Model):
    _name = "woocommerce.backend"
    _inherit = "connector.extension.backend"
    _description = "WooCommerce Backend"

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
    payment_mode_ids = fields.One2many(
        comodel_name="woocommerce.backend.payment.mode",
        inverse_name="backend_id",
        string="Payment Mode",
    )
    tax_map_ids = fields.One2many(
        comodel_name="woocommerce.backend.account.tax",
        inverse_name="backend_id",
        string="Tax Mapping",
    )
    tax_class_ids = fields.One2many(
        comodel_name="woocommerce.backend.tax.class",
        inverse_name="backend_id",
        string="Tax Class",
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

    language_id = fields.Many2one(
        comodel_name="res.lang",
        string="Language",
        required=True,
    )
    client_order_ref_prefix = fields.Char(
        string="Client Order Reference Prefix",
        help="Prefix to add to the client order reference",
        required=True,
    )
    verify_ssl = fields.Boolean(
        default=True,
    )
    wordpress_backend_id = fields.Many2one(
        comodel_name="wordpress.backend",
    )
    use_main_product_image = fields.Boolean(
        default=True,
        help="If it's True, product image in the upper right "
        "corner of the form will be exported",
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

    def export_product_tmpl_since(self):
        self.env.user.company_id = self.company_id
        for rec in self:
            since_date = fields.Datetime.from_string(rec.export_product_tmpl_since_date)
            rec.export_product_tmpl_since_date = fields.Datetime.now()
            self.env["woocommerce.product.template"].export_product_tmpl_since(
                backend_record=rec, since_date=since_date
            )

    def export_products_since(self):
        self.env.user.company_id = self.company_id
        for rec in self:
            since_date = fields.Datetime.from_string(rec.export_products_since_date)
            rec.export_products_since_date = fields.Datetime.now()
            self.env["woocommerce.product.product"].export_products_since(
                backend_record=rec, since_date=since_date
            )

    def export_sale_orders_since(self):
        self.env.user.company_id = self.company_id
        for rec in self:
            since_date = fields.Datetime.from_string(rec.export_sale_orders_since_date)
            rec.export_sale_orders_since_date = fields.Datetime.now()
            self.env["woocommerce.sale.order"].export_sale_orders_since(
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
                "woocommerce.product.public.category"
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
            self.env["woocommerce.product.attribute"].export_product_attribute_since(
                backend_record=rec, since_date=since_date
            )

    def export_product_attribute_value_since(self):
        self.env.user.company_id = self.company_id
        for rec in self:
            since_date = fields.Datetime.from_string(
                rec.export_product_attribute_value_since_date
            )
            rec.export_product_attribute_value_since_date = fields.Datetime.now()
            self.env[
                "woocommerce.product.attribute.value"
            ].export_product_attribute_value_since(
                backend_record=rec, since_date=since_date
            )

    def import_sale_orders_since(self):
        self.env.user.company_id = self.company_id
        for rec in self:
            since_date = fields.Datetime.from_string(rec.import_sale_order_since_date)
            rec.import_sale_order_since_date = fields.Datetime.now()
            self.env["woocommerce.sale.order"].import_sale_orders_since(
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
