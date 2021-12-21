# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    service_time = fields.Float(
        string="Service Time",
        digits="Product UoM",
        help="Time to complete this service.",
    )

    @api.constrains("service_time")
    def _check_service_time(self):
        for record in self:
            if record.service_time < 0:
                raise ValidationError(_("Time cannot be negative."))
