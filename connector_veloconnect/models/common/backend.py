# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class VeloconnectBackend(models.Model):
    _name = "veloconnect.backend"
    _inherit = "connector.backend"
    _description = "Veloconnect Backend"

    @api.model
    def _select_state(self):
        return [
            ("draft", "Draft"),
            ("checked", "Checked"),
            ("production", "In Production"),
        ]

    name = fields.Char("Name", required=True)
    state = fields.Selection(selection="_select_state", string="State", default="draft")
    active = fields.Boolean(string="Active", default=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        ondelete="restrict",
    )
    chunk_size = fields.Integer(default=500, string="Chunk Size")
    product_search_retry_time = fields.Integer(
        string="Product Search Retry Time (minutes) ", default=10
    )
    buyer = fields.Char(help="Buyer ID", required=True, default="")
    password = fields.Char(
        help="WebService Password",
        required=True,
        default="",
    )
    url = fields.Char(help="WebService URL")
    ignore_availablequantity = fields.Boolean(
        string="Ignore AvailableQuantity", default=False
    )
    ignore_uom = fields.Boolean(string="Ignore quantityUnitCode", default=False)
    import_sale_orders_since_date = fields.Datetime("Import Services since")
    import_products_name = fields.Char("Import Products with Name")
    is_manufacturer = fields.Boolean(string="Is Manufacturer")
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Veloconnect Partner",
        required=True,
    )
    product_uom_ids = fields.One2many(
        comodel_name="veloconnect.backend.uom",
        inverse_name="backend_id",
        string="product_uom",
        required=True,
    )

    def _check_connection(self):
        self.ensure_one()

    def button_check_connection(self):
        for rec in self:
            rec._check_connection()
            rec.write({"state": "checked"})

    def button_reset_to_draft(self):
        self.ensure_one()
        self.write({"state": "draft"})

    def import_products(self):
        self.env.user.company_id = self.company_id
        for rec in self:
            self.env["veloconnect.product.template"].import_data(backend_record=rec)

    # scheduler
    @api.model
    def _scheduler_import(self):
        for backend in self.env[self._name].search([]):
            backend.import_products()

    def get_product_uom_map(self, product_uom_veloconnect):
        self.ensure_one()
        product_uom_map = self.product_uom_ids.filtered(
            lambda r: r.quantityunitcode == product_uom_veloconnect
        )
        if not product_uom_map:
            raise ValidationError(
                _("Can't found a product uom %s. Please, add it on backend mappings")
                % product_uom_veloconnect
            )
        if len(product_uom_map) > 1:
            raise ValidationError(
                _(
                    "Multiple mappings found for product uom %s"
                    "Please, check the unit on uom.uom"
                )
                % product_uom_map
            )
        return product_uom_map.uom_id
