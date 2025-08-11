# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class LengowBackend(models.Model):
    _name = "lengow.backend"
    _inherit = "connector.extension.backend"
    _description = "Lengow Backend"

    name = fields.Char(
        required=True,
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
    access_token = fields.Char(
        help="WebService Access Token",
        required=True,
    )
    secret = fields.Char(
        help="Webservice password",
        required=True,
    )
    base_url = fields.Char(
        default="https://api.lengow.io",
    )
    marketplace_ids = fields.One2many(
        comodel_name="lengow.backend.marketplace",
        inverse_name="backend_id",
        string="Marketplaces",
        required=True,
    )
    shipping_product_id = fields.Many2one(
        comodel_name="product.product",
    )

    import_sale_orders_since_date = fields.Datetime(
        string="Import Orders since",
    )
    import_sale_orders_order_number = fields.Char(
        string="Import specific orders",
        help="Comma separated order numbers",
    )
    min_order_date = fields.Date()
    sync_offset = fields.Integer(
        help="Minutes to start the synchronization before(negative)/after(positive) "
        "the last one (Lengow bug)",
    )

    # Rewrited method, no need version on lengow
    def _check_connection(self):
        self.ensure_one()
        with self.work_on(self._name) as work:
            component = work.component(usage="backend.adapter")
            token = component._exec("get_token")
        if not token:
            raise UserError(_("Invalid token"))

    def import_sale_orders_since(self):
        # if self.user_id:
        #     self = self.sudo(self.user_id)
        self.env.user.company_id = self.company_id
        for rec in self:
            since_date = fields.Datetime.to_datetime(rec.import_sale_orders_since_date)
            rec.import_sale_orders_since_date = fields.Datetime.to_datetime(
                fields.datetime.now() + datetime.timedelta(minutes=rec.sync_offset)
            )
            self.env["lengow.sale.order"].import_sale_orders_since(
                backend_record=rec,
                since_date=since_date,
                order_number=rec.import_sale_orders_order_number,
            )
            # self.env["lengow.sale.order"].with_delay().import_sale_orders_since(
            #     backend_record=rec,
            #     since_date=since_date,
            #     order_number=rec.import_sale_orders_order_number,
            # )

    # scheduler
    @api.model
    def _scheduler_import_sale_orders(self):
        for backend in self.env[self._name].search([("state", "=", "validated")]):
            backend.import_sale_orders_since()

    def get_marketplace_map(self, marketplace_name, country_iso_code):
        self.ensure_one()
        marketplace_map = self.marketplace_ids.filtered(
            lambda r: r.lengow_marketplace == marketplace_name
            and r.partner_id.country_id.code == country_iso_code
        )
        if not marketplace_map:
            raise ValidationError(
                _(
                    "Can't found a parent partner for marketplace %(marketplace)s "
                    "and country %(country)s. "
                    "Please, add it on backend mappings"
                )
                % {
                    "marketplace": marketplace_name,
                    "country": country_iso_code,
                }
            )
        if len(marketplace_map) > 1:
            raise ValidationError(
                _(
                    "Multiple mappings found for marketplace %(marketplace)s "
                    "and country %(country)s. "
                    "Please, check the country on partners"
                )
                % {
                    "marketplace": marketplace_name,
                    "country": country_iso_code,
                }
            )
        return marketplace_map
