# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    veloconnect_bind_ids = fields.One2many(
        comodel_name="veloconnect.product.template",
        inverse_name="odoo_id",
        string="Veloconnect Bindings",
    )

    partner_stock_ids = fields.One2many(
        comodel_name="product.template.partner.stock",
        inverse_name="product_tmpl_id",
        string="Partner Stock",
    )

    veloconnect_readonly = fields.Boolean(compute="_compute_veloconnect_readonly")

    def _compute_veloconnect_readonly(self):
        for rec in self:
            rec.veloconnect_readonly = bool(rec.veloconnect_bind_ids)

    def resync_import_all(self):
        for binding in self.veloconnect_bind_ids:
            binding.sudo().resync_import()
