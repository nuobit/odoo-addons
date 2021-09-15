# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import models, fields, api, exceptions, _
from ...components.adapter import api_handle_errors

_logger = logging.getLogger(__name__)


class OxigestiBackend(models.Model):
    _name = 'oxigesti.backend'
    _inherit = 'connector.backend'

    _description = 'Oxigesti Backend Configuration'

    @api.model
    def _select_state(self):
        """Available States for this Backend"""
        return [('draft', 'Draft'),
                ('checked', 'Checked'),
                ('production', 'In Production')]

    name = fields.Char('Name', required=True)

    server = fields.Char('Server', required=True)
    port = fields.Integer('Port', required=True)

    database = fields.Char('Database', required=True)
    schema = fields.Char('Schema', required=True)

    version = fields.Text('Version', readonly=True)

    username = fields.Char('Username', required=True)
    password = fields.Char('Password', required=True)

    company_id = fields.Many2one(
        comodel_name='res.company',
        index=True,
        required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'oxigesti.backend'),
        string='Company',
    )

    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string="Warehouse")

    lang_id = fields.Many2one(comodel_name='res.lang', string="Language",
                              default=lambda self: self.env.ref('base.lang_es'), required=True)

    active = fields.Boolean(
        string='Active',
        default=True
    )
    state = fields.Selection(
        selection='_select_state',
        string='State',
        default='draft'
    )

    @api.multi
    def button_reset_to_draft(self):
        self.ensure_one()
        self.write({'state': 'draft', 'version': None})

    @api.multi
    def _check_connection(self):
        self.ensure_one()
        with self.work_on('oxigesti.backend') as work:
            component = work.component_by_name(name='oxigesti.adapter.test')
            with api_handle_errors('Connection failed'):
                self.version = component.get_version()

    @api.multi
    def button_check_connection(self):
        self._check_connection()
        self.write({'state': 'checked'})

    import_customers_since_date = fields.Datetime('Import Customers since')
    export_products_since_date = fields.Datetime('Export Products since')
    export_product_categories_since_date = fields.Datetime('Export Product Categories since')
    export_products_by_customer_since_date = fields.Datetime('Export Products by customer since')
    export_product_prices_by_customer_since_date = fields.Datetime('Export Product prices by customer since')
    export_stock_production_lot_since_date = fields.Datetime('Export Lots since')
    import_services_since_date = fields.Datetime('Import Services since')

    # Backend data methods
    @api.multi
    def import_customers_since(self):
        for rec in self:
            since_date = fields.Datetime.from_string(rec.import_customers_since_date)
            self.env['oxigesti.res.partner'].with_delay(
            ).import_customers_since(
                backend_record=rec, since_date=since_date)

        return True

    @api.multi
    def export_products_since(self):
        for rec in self:
            since_date = rec.export_products_since_date
            self.env['oxigesti.product.product'].with_delay(
            ).export_products_since(
                backend_record=rec, since_date=since_date)

        return True

    @api.multi
    def export_product_categories_since(self):
        for rec in self:
            since_date = rec.export_product_categories_since_date
            self.env['oxigesti.product.category'].with_delay(
            ).export_product_categories_since(
                backend_record=rec, since_date=since_date)

        return True

    @api.multi
    def export_products_by_customer_since(self):
        for rec in self:
            since_date = rec.export_products_by_customer_since_date
            self.env['oxigesti.product.buyerinfo'].with_delay(
            ).export_products_by_customer_since(
                backend_record=rec, since_date=since_date)

        return True

    @api.multi
    def export_product_prices_by_customer_since(self):
        for rec in self:
            since_date = rec.export_product_prices_by_customer_since_date
            self.env['oxigesti.product.pricelist.item'].with_delay(
            ).export_product_prices_by_customer_since(
                backend_record=rec, since_date=since_date)

        return True

    @api.multi
    def export_stock_production_lot_since(self):
        for rec in self:
            since_date = rec.export_stock_production_lot_since_date
            self.env['oxigesti.stock.production.lot'].with_delay(
            ).export_stock_production_lot_since(
                backend_record=rec, since_date=since_date)

        return True

    @api.multi
    def import_services_since(self):
        for rec in self:
            since_date = fields.Datetime.from_string(rec.import_services_since_date)
            rec.import_services_since_date = fields.Datetime.now()
            self.env['oxigesti.sale.order'].with_delay(
            ).import_services_since(
                backend_record=rec, since_date=since_date)

        return True

    # Scheduler methods
    @api.model
    def get_current_user_company(self):
        if self.env.user.id == self.env.ref('base.user_root').id:
            raise exceptions.ValidationError(_("The cron user cannot be admin"))

        return self.env.user.company_id

    @api.model
    def _scheduler_import_customers(self):
        company_id = self.get_current_user_company()
        domain = [
            ('company_id', '=', company_id.id)
        ]
        self.search(domain).import_customers_since()

    @api.model
    def _scheduler_export_products(self):
        company_id = self.get_current_user_company()
        domain = [
            ('company_id', '=', company_id.id)
        ]
        self.search(domain).export_products_since()

    @api.model
    def _scheduler_export_product_categories(self):
        self.search([]).export_product_categories_since()

    @api.model
    def _scheduler_export_products_by_customer(self):
        company_id = self.get_current_user_company()
        domain = [
            ('company_id', '=', company_id.id)
        ]
        self.search(domain).export_products_by_customer_since()

    @api.model
    def _scheduler_export_product_prices_by_customer(self):
        company_id = self.get_current_user_company()
        domain = [
            ('company_id', '=', company_id.id)
        ]
        self.search(domain).export_product_prices_by_customer_since()

    @api.model
    def _scheduler_export_stock_production_lot(self):
        company_id = self.get_current_user_company()
        domain = [
            ('company_id', '=', company_id.id)
        ]
        self.search(domain).export_stock_production_lot_since()

    @api.model
    def _scheduler_import_services(self):
        company_id = self.get_current_user_company()
        domain = [
            ('company_id', '=', company_id.id)
        ]
        self.search(domain).import_services_since()
