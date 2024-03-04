# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import datetime
import logging

import pytz

from odoo import _, api, exceptions, fields, models

from ...components.adapter import api_handle_errors

_logger = logging.getLogger(__name__)

_tzs = [
    (tz, tz)
    for tz in sorted(
        pytz.all_timezones, key=lambda tz: tz if not tz.startswith("Etc/") else "_"
    )
]


def _tz_get(self):
    return _tzs


class OxigestiBackend(models.Model):
    _name = "oxigesti.backend"
    _inherit = "connector.backend"

    _description = "Oxigesti Backend Configuration"

    @api.model
    def _select_state(self):
        """Available States for this Backend"""
        return [
            ("draft", "Draft"),
            ("checked", "Checked"),
            ("production", "In Production"),
        ]

    name = fields.Char("Name", required=True)

    server = fields.Char("Server", required=True)
    port = fields.Integer("Port", required=True)

    database = fields.Char("Database", required=True)
    schema = fields.Char("Schema", required=True)

    version = fields.Text("Version", readonly=True)

    username = fields.Char("Username", required=True)
    password = fields.Char("Password", required=True)

    company_id = fields.Many2one(
        comodel_name="res.company",
        index=True,
        required=True,
        default=lambda self: self.env["res.company"]._company_default_get(
            "oxigesti.backend"
        ),
        string="Company",
    )
    tz = fields.Selection(
        _tz_get,
        string="Timezone",
        required=True,
        default=lambda self: self._context.get("tz") or self.env.user.tz or "UTC",
        help="This field is used in order to define in which timezone the backend will work.",
    )
    warehouse_id = fields.Many2one(comodel_name="stock.warehouse", string="Warehouse")
    lang_id = fields.Many2one(
        comodel_name="res.lang",
        string="Language",
        default=lambda self: self.env.ref("base.lang_es"),
        required=True,
    )
    active = fields.Boolean(string="Active", default=True)
    state = fields.Selection(selection="_select_state", string="State", default="draft")
    product_attribute_map_ids = fields.One2many(
        comodel_name="oxigesti.backend.product.attribute.map",
        inverse_name="backend_id",
        string="Product Attribute Map",
    )

    def button_reset_to_draft(self):
        self.ensure_one()
        self.write({"state": "draft", "version": None})

    def _check_connection(self):
        self.ensure_one()
        with self.work_on("oxigesti.backend") as work:
            component = work.component_by_name(name="oxigesti.adapter.test")
            with api_handle_errors("Connection failed"):
                self.version = component.get_version()

    def button_check_connection(self):
        self._check_connection()
        self.write({"state": "checked"})

    import_customers_since_date = fields.Datetime("Import Customers since")
    export_products_since_date = fields.Datetime("Export Products since")
    export_product_categories_since_date = fields.Datetime(
        "Export Product Categories since"
    )
    export_products_by_customer_since_date = fields.Datetime(
        "Export Products by customer since"
    )
    export_product_prices_by_customer_since_date = fields.Datetime(
        "Export Product prices by customer since"
    )
    import_stock_production_lot_since_date = fields.Datetime("Import Lots since")
    export_stock_production_lot_since_date = fields.Datetime("Export Lots since")
    import_services_since_date = fields.Datetime("Import Services since")
    export_services_since_date = fields.Datetime("Export Services since")
    export_mrp_production_since_date = fields.Datetime("Export Productions since")

    sync_offset = fields.Integer(
        string="Sync Offset",
        help="Minutes to start the synchronization "
        "before(negative)/after(positive) the last one",
    )

    # Backend data methods
    def import_customers_since(self):
        for rec in self:
            since_date = rec.import_customers_since_date
            rec.import_customers_since_date = fields.Datetime.now()
            self.env["oxigesti.res.partner"].import_data(rec, since_date)

    def export_products_since(self):
        for rec in self:
            since_date = rec.export_products_since_date
            rec.export_products_since_date = fields.Datetime.now()
            self.env["oxigesti.product.product"].export_data(rec, since_date)

    def export_product_categories_since(self):
        for rec in self:
            since_date = rec.export_product_categories_since_date
            rec.export_product_categories_since_date = fields.Datetime.now()
            self.env["oxigesti.product.category"].export_data(rec, since_date)

    def export_products_by_customer_since(self):
        for rec in self:
            since_date = rec.export_products_by_customer_since_date
            rec.export_products_by_customer_since_date = fields.Datetime.now()
            self.env["oxigesti.product.buyerinfo"].export_data(rec, since_date)

    def export_product_prices_by_customer_since(self):
        for rec in self:
            since_date = rec.export_product_prices_by_customer_since_date
            rec.export_product_prices_by_customer_since_date = fields.Datetime.now()
            self.env["oxigesti.product.pricelist.item"].export_data(rec, since_date)

    def import_stock_production_lot_since(self):
        for rec in self:
            since_date = rec.import_stock_production_lot_since_date
            rec.import_stock_production_lot_since_date = fields.Datetime.now()
            self.env["oxigesti.stock.production.lot"].import_data(rec, since_date)

    def export_stock_production_lot_since(self):
        for rec in self:
            since_date = rec.export_stock_production_lot_since_date
            rec.export_stock_production_lot_since_date = (
                fields.datetime.now() + datetime.timedelta(minutes=rec.sync_offset)
            )
            self.env["oxigesti.stock.production.lot"].export_data(rec, since_date)

    def import_services_since(self):
        for rec in self:
            since_date = rec.import_services_since_date
            rec.import_services_since_date = fields.Datetime.now()
            self.env["oxigesti.sale.order"].import_data(rec, since_date)

    def export_services_since(self):
        for rec in self:
            since_date = rec.export_services_since_date
            rec.export_services_since_date = fields.Datetime.now()
            self.env["oxigesti.sale.order"].export_data(rec, since_date)

    def export_mrp_production_since(self):
        for rec in self:
            since_date = rec.export_mrp_production_since_date
            rec.export_mrp_production_since_date = fields.Datetime.now()
            self.env["oxigesti.mrp.production"].export_data(rec, since_date)

    # Scheduler methods
    @api.model
    def get_current_user_company(self):
        if self.env.user.id == self.env.ref("base.user_root").id:
            raise exceptions.ValidationError(_("The cron user cannot be admin"))

        return self.env.company

    @api.model
    def _scheduler_import_customers(self):
        company_id = self.get_current_user_company()
        domain = [("company_id", "=", company_id.id)]
        self.search(domain).import_customers_since()

    @api.model
    def _scheduler_export_products(self):
        company_id = self.get_current_user_company()
        domain = [("company_id", "=", company_id.id)]
        self.search(domain).export_products_since()

    @api.model
    def _scheduler_export_product_categories(self):
        self.search([]).export_product_categories_since()

    @api.model
    def _scheduler_export_products_by_customer(self):
        company_id = self.get_current_user_company()
        domain = [("company_id", "=", company_id.id)]
        self.search(domain).export_products_by_customer_since()

    @api.model
    def _scheduler_export_product_prices_by_customer(self):
        company_id = self.get_current_user_company()
        domain = [("company_id", "=", company_id.id)]
        self.search(domain).export_product_prices_by_customer_since()

    @api.model
    def _scheduler_import_stock_production_lot(self):
        company_id = self.get_current_user_company()
        domain = [("company_id", "=", company_id.id)]
        self.search(domain).import_stock_production_lot_since()

    @api.model
    def _scheduler_export_stock_production_lot(self):
        company_id = self.get_current_user_company()
        domain = [("company_id", "=", company_id.id)]
        self.search(domain).export_stock_production_lot_since()

    @api.model
    def _scheduler_import_services(self):
        company_id = self.get_current_user_company()
        domain = [("company_id", "=", company_id.id)]
        self.search(domain).import_services_since()

    def _scheduler_export_services(self):
        company_id = self.get_current_user_company()
        domain = [("company_id", "=", company_id.id)]
        self.search(domain).export_services_since()

    def _scheduler_export_mrp_production(self):
        company_id = self.get_current_user_company()
        domain = [("company_id", "=", company_id.id)]
        self.search(domain).export_mrp_production_since()

    def tz_to_utc(self, dt):
        t = pytz.timezone(self.tz).localize(dt)
        t = t.astimezone(pytz.utc)
        t = t.replace(tzinfo=None)
        return t

    def tz_to_local(self, dt):
        local_tz = pytz.timezone(self.tz)
        datetime_utc = pytz.utc.localize(dt)
        datetime_local = datetime_utc.astimezone(local_tz)
        return datetime_local
