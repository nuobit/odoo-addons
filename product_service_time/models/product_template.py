# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models

import odoo.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    service_time = fields.Float(
        string='Service Time',
        digits=dp.get_precision('Product UoM'),
        help='Time to complete this service.',
        compute='_compute_service_time',
        inverse='_set_service_time', store=True
    )

    @api.depends('product_variant_ids', 'product_variant_ids.service_time')
    def _compute_service_time(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.service_time = template.product_variant_ids.service_time
        for template in (self - unique_variants):
            template.service_time = False

    @api.one
    def _set_service_time(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.service_time = self.service_time
