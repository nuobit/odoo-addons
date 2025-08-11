# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

import requests

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SapB1Backend(models.Model):
    _name = "sapb1.backend"
    _inherit = "connector.extension.backend"
    _description = "SAP B1 Backend"

    name = fields.Char(
        required=True,
    )
    partner_ids = fields.One2many(
        string="partner",
        comodel_name="sapb1.backend.res.partner",
        inverse_name="backend_id",
    )
    tax_ids = fields.One2many(
        string="tax",
        comodel_name="sapb1.backend.account.tax",
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
    shipping_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Shipping Product",
        required=True,
    )

    db_host = fields.Char(
        string="Hostname",
        required=True,
    )
    sl_port = fields.Integer(
        string="Port",
        default=50000,
        required=True,
    )
    db_username = fields.Char(
        string="Username",
        required=True,
    )
    db_password = fields.Char(
        string="Password",
        required=True,
    )
    company_db = fields.Char(
        string="Database",
    )
    sl_ssl_enabled = fields.Boolean(
        string="SSL enabled",
        default=True,
    )
    sl_base_url = fields.Char(
        string="Base URL",
        default="/b1s/v1",
        required=True,
    )
    sl_url = fields.Char(
        string="URL",
        store=True,
        compute="_compute_sl_url",
    )

    @api.depends("sl_ssl_enabled", "db_host", "sl_port", "sl_base_url")
    def _compute_sl_url(self):
        for rec in self:
            rec.sl_url = requests.compat.urlunparse(
                [
                    "http%s" % (rec.sl_ssl_enabled and "s" or "",),
                    "%s:%i" % (rec.db_host, rec.sl_port),
                    rec.sl_base_url,
                    None,
                    None,
                    None,
                ]
            )

    export_sale_orders_since_date = fields.Datetime(
        string="Export Services Since",
    )

    def _check_connection(self):
        self.ensure_one()
        with self.work_on(self._name) as work:
            component = work.component(usage="backend.adapter")
            component._exec("check_connection")

    def _get_since_date(self, since_date):
        since_date = fields.Datetime.to_datetime(since_date) or None
        return since_date, fields.Datetime.now()

    def export_sale_orders_since(self):
        self.env.user.company_id = self.company_id
        for rec in self:
            since_date, rec.export_sale_orders_since_date = self._get_since_date(
                rec.export_sale_orders_since_date
            )
            self.env["sapb1.sale.order"].export_sale_orders_since(
                backend_record=rec, since_date=since_date
            )

    @api.model
    def _scheduler_export_sale_orders(self):
        """
        IF this is called using Odoo Cron job, the interval must be
        the same as the interval execution defined in job
        """
        for backend in self.env[self._name].search([("state", "=", "validated")]):
            backend.export_sale_orders_since()

    def get_tax_map(self, tax):
        if not tax:
            return None
        if len(tax) > 1:
            raise ValidationError(_("In SAP B1 only one tax can be applied to a line"))
        tax_map = self.tax_ids.filtered(lambda x: x.tax_id == tax)
        if not tax_map:
            raise ValidationError(_("No tax mapping found for tax %s") % tax.name)
        return tax_map.sapb1_tax
