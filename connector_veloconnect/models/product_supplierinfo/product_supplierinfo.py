# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    veloconnect_readonly = fields.Boolean(compute="_compute_veloconnect_readonly")

    def _compute_veloconnect_readonly(self):
        for rec in self:
            binding_partner = rec.product_tmpl_id.veloconnect_bind_ids.filtered(
                lambda x: x.backend_id.partner_id == rec.name
            )
            rec.veloconnect_readonly = bool(binding_partner)
