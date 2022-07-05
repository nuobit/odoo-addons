# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models
from odoo import api, _
from odoo.addons.connector_veloconnect.models.common import tools
from odoo.exceptions import ValidationError


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

    @api.constrains('name', 'product_code', 'product_tmpl_id', 'min_qty')
    def _check_unique_supplierinfo(self):
        for rec in self:
            domain = [
                ('id', '!=', rec.id),
                ('name', '=', rec.name.id),
            ]
            other = self.env['product.supplierinfo'].search([
                *domain,
                ('product_code', '=', rec.product_code),
                ('product_tmpl_id', '!=', rec.product_tmpl_id.id),
            ])
            if other:
                raise ValidationError(_("This product code and vendor already exists on another product"))
            other = self.env['product.supplierinfo'].search([
                *domain,
                ('product_code', '=', rec.product_code),
                ('product_tmpl_id', '=', rec.product_tmpl_id.id),
                ('min_qty', '=', rec.min_qty),
            ])
            if other:
                raise ValidationError(_("This supplierinfo already exists"))
            other = self.env['product.supplierinfo'].search([
                *domain,
                ('product_code', '!=', rec.product_code),
                ('product_code', '!=', False),
                ('product_tmpl_id', '=', rec.product_tmpl_id.id),
            ])
            if other:
                raise ValidationError(_("Only one product code is allowed for the same vendor"))
