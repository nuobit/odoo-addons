# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class RepairOrder(models.Model):
    _inherit = "repair.order"

    invoice_ids = fields.One2many(
        comodel_name="account.move",
        inverse_name="repair_order_id",
        string="Invoices",
        help="Invoices related to this repair order",
    )
