# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    service_group_product = fields.Many2one(
        comodel_name="product.product",
        string="Product for Service Grouping",
        help="Default product that will be used to group service billing",
    )
