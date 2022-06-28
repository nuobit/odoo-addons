# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models
from odoo.odoo import api
from odoo.addons.connector_veloconnect.models.common import tools


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    veloconnect_bind_ids = fields.One2many(
        comodel_name='veloconnect.product.supplierinfo',
        inverse_name='odoo_id',
        string='Veloconnect Bindings',
    )

    backend_id = fields.Many2one(
        string="Backend id",
        comodel_name="veloconnect.backend",
        required=True,
        ondelete="cascade",
    )

    veloconnect_readonly = fields.Boolean(compute="_compute_veloconnect_readonly")

    def _compute_veloconnect_readonly(self):
        for rec in self:
            binding_partner = rec.veloconnect_bind_ids.filtered(lambda x: x.backend_id.partner_id == rec.name)
            rec.veloconnect_readonly = bool(binding_partner)
