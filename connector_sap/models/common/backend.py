# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import requests

from odoo import _, fields, models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SapBackend(models.Model):
    _name = "sap.backend"
    _inherit = "connector.backend"
    _description = "SAP Backend"

    @api.model
    def _select_state(self):
        return [('draft', 'Draft'),
                ('checked', 'Checked'),
                ('production', 'In Production')]

    name = fields.Char("Name", required=True)

    state = fields.Selection(
        selection='_select_state',
        string='State',
        default='draft'
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )

    partner_ids = fields.One2many(
        string="partner",
        comodel_name="sap.backend.res.partner",
        inverse_name="backend_id",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        ondelete="restrict",
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        ondelete="restrict",
    )

    db_host = fields.Char('Hostname', required=True)
    sl_port = fields.Integer('Port', default=50000, required=True)
    db_username = fields.Char('Username', required=True)
    db_password = fields.Char('Password', required=True)

    company_db = fields.Char(
        string="SAP Database",
        default="20190222_ACC_PROD_NOVOLUX"
    )

    sl_ssl_enabled = fields.Boolean('SSL enabled', default=True)
    sl_base_url = fields.Char('Base URL', default='/b1s/v1', required=True)

    sl_url = fields.Char(
        string='URL',
        store=True,
        compute="_compute_sl_url",
    )

    @api.depends('sl_ssl_enabled', 'db_host', 'sl_port', 'sl_base_url')
    def _compute_sl_url(self):
        for rec in self:
            rec.sl_url = requests.compat.urlunparse([
                'http%s' % (rec.sl_ssl_enabled and 's' or '',),
                '%s:%i' % (rec.db_host, rec.sl_port),
                rec.sl_base_url,
                None, None, None,
            ])

    export_sale_orders_since_date = fields.Datetime('Import Services since')

    @api.multi
    def _check_connection(self):
        self.ensure_one()
        with self.work_on('sap.backend') as work:
            work.component_by_name(name='sap.adapter')._exec('check_connection')

    @api.multi
    def button_check_connection(self):
        for rec in self:
            rec._check_connection()
            rec.write({'state': 'checked'})

    @api.multi
    def button_reset_to_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})

    @api.multi
    def export_sale_orders_since(self):
        for rec in self:
            since_date = fields.Datetime.from_string(rec.export_sale_orders_since_date)
            rec.export_sale_orders_since_date = fields.Datetime.now()
            # self.env['sap.sale.order'].with_delay(
            # ).export_sale_orders_since(
            #     backend_record=rec, since_date=since_date)
            self.env['sap.sale.order'].export_sale_orders_since(
                backend_record=rec, since_date=since_date)



    # @api.multi
    # def import_sale_orders_since(self):
    #     for rec in self:
    #         since_date = fields.Datetime.from_string(rec.import_sale_orders_since_date)
    #         rec.import_sale_orders_since_date = fields.Datetime.now()
    #         self.env['sap.sale.order'].with_delay(
    #         ).import_sale_orders_since(
    #             backend_record=rec, since_date=since_date)
