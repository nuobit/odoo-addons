# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    maintenance_request_date_editable = fields.Boolean()
