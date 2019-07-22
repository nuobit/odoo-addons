# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class LightingCatalog(models.Model):
    _name = 'lighting.catalog'
    _order = 'name'

    name = fields.Char(string='Catalog', required=True)

    description_show_ip = fields.Boolean(string='Description show IP',
                                         help="If checked, IP and IP2 will be shown on a generated product description "
                                              "for every product in this catalog")

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['lighting.product'].search_count([('catalog_ids', '=', record.id)])

    color = fields.Integer(string='Color Index')

    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary(
        "Image", attachment=True,
        help="This field holds the image used as image for the product, limited to 1024x1024px.")
    image_medium = fields.Binary(
        "Medium-sized image", attachment=True,
        help="Medium-sized image of the product. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved, "
             "only when the image exceeds one of those sizes. Use this field in form views or some kanban views.")
    image_small = fields.Binary(
        "Small-sized image", attachment=True,
        help="Small-sized image of the product. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")

    _sql_constraints = [('name_uniq', 'unique (name)', 'The name of catalog must be unique!'),
                        ]

    @api.model
    def create(self, values):
        tools.image_resize_images(values)
        res = super().create(values)

        return res

    @api.multi
    def write(self, values):
        tools.image_resize_images(values)
        res = super().write(values)

        return res

    @api.multi
    def unlink(self):
        records = self.env['lighting.product'].search([('catalog_ids', 'in', self.ids)])
        if records:
            raise UserError(_("You are trying to delete a record that is still referenced!"))
        return super(LightingCatalog, self).unlink()
