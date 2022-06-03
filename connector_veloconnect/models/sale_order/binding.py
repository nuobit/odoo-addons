# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import datetime


class VeloconnectSaleOrderBinding(models.Model):
    _name = "veloconnect.sale.order"
    _inherit = "veloconnect.binding"
    _inherits = {"sale.order": "odoo_id"}

    # binding fields
    odoo_id = fields.Many2one(
        comodel_name="sale.order",
        string="Odoo ID",
        required=True,
        ondelete="cascade",
    )

    veloconnect_order_line_ids = fields.One2many(
        string="Veloconnect Order Line ids",
        help="Order Lines in Veloconnect sale orders",
        comodel_name="veloconnect.sale.order.line",
        inverse_name="veloconnect_order_id",
    )



    def import_sale_orders_since(self, backend_record=None, since_date=None):
        """ Prepare the batch import of partners modified on Veloconnect """
        if since_date:
            domain = [('updated_from', '=', since_date)]
        else:
            domain = [('updated_from', '=', datetime(1900, 1, 1, 0, 0, 0))]
        self.import_batch(
            backend_record, domain=domain)
        return True
