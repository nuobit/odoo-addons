# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError
from odoo.modules import get_module_resource

import base64

from odoo.tools import pycompat


def get_resized_images(base64_source, medium_name='image_medium', small_name='image_small',
                       medium_size=(500, 500), small_size=(64, 64),
                       encoding='base64', filetype=None):
    if isinstance(base64_source, pycompat.text_type):
        base64_source = base64_source.encode('ascii')

    return_dict = dict()
    return_dict[medium_name] = tools.image_resize_image(base64_source, medium_size, encoding, filetype, True)
    return_dict[small_name] = tools.image_resize_image(base64_source, small_size, encoding, filetype, True)

    return return_dict


def get_preview_images(datas, is_image=True):
    resized_images = {}
    if is_image:
        try:
            resized_images = get_resized_images(datas)
        except IOError:
            img_path = get_module_resource('web', 'static/src/img', 'placeholder.png')
            if img_path:
                with open(img_path, 'rb') as f:
                    return get_resized_images(base64.b64encode(f.read()))
    else:
        img_path = get_module_resource('lighting', 'static/src/img', 'doc.png')
        if img_path:
            with open(img_path, 'rb') as f:
                resized_images = get_resized_images(
                    base64.b64encode(f.read()))

    return resized_images


class LightingAttachment(models.Model):
    _name = 'lighting.attachment'
    _order = 'sequence,id'

    def _sequence_default(self):
        max_sequence = self.env['lighting.attachment'] \
            .search([('product_id', '=', self.env.context.get('default_product_id'))],
                    order='sequence desc', limit=1).sequence

        return max_sequence + 1

    sequence = fields.Integer(required=True, default=_sequence_default,
                              help="The sequence field is used to define order")

    name = fields.Char(string='Description', translate=True)
    type_id = fields.Many2one(comodel_name='lighting.attachment.type', ondelete='restrict', required=True,
                              string='Type')

    datas = fields.Binary(string="Document", attachment=True, required=True)
    datas_fname = fields.Char(string='Filename', required=True)
    datas_size = fields.Char(string='Size', compute="_compute_datas_size", store=True)

    @api.depends('datas')
    def _compute_datas_size(self):
        for rec in self:
            size = rec.attachment_id.file_size
            if size < 1000:
                magn = 'Bytes'
            else:
                size /= 1000
                if size < 1000:
                    magn = 'Kb'
                else:
                    size /= 1000
                    magn = 'Mb'

            if size - int(size) == 0.0:
                rec.datas_size = "{:d} {}".format(int(size), magn)
            else:
                rec.datas_size = "{:.2f} {}".format(size, magn)

    image_small = fields.Binary("Small-sized image", attachment=True, store=True, compute="_compute_images")
    image_medium = fields.Binary("Medium-sized image", attachment=True, store=True, compute="_compute_images")

    @api.depends('datas', 'type_id', 'type_id.is_image')
    def _compute_images(self):
        for rec in self:
            if rec.id:
                resized_images = get_preview_images(rec.datas, rec.type_id.is_image)
                rec.image_medium = resized_images['image_medium']
                rec.image_small = resized_images['image_small']

    attachment_id = fields.Many2one(comodel_name='ir.attachment',
                                    compute='_compute_ir_attachment', readonly=True)

    @api.depends('datas')
    def _compute_ir_attachment(self):
        for rec in self:
            attachment_obj = rec.env['ir.attachment'] \
                .search([('res_field', '=', 'datas'),
                         ('res_id', '=', rec.id),
                         ('res_model', '=', rec._name)]) \
                .sorted('id', reverse=True)
            if attachment_obj:
                rec.attachment_id = attachment_obj[0]
            else:
                rec.attachment_id = False

    checksum = fields.Char(related='attachment_id.checksum', string='Checksum', readonly=True)

    public = fields.Boolean(related='attachment_id.public', string='Public')
    url = fields.Char(string='URL', compute='_compute_url', readonly=True)

    @api.depends('attachment_id')
    def _compute_url(self):
        for rec in self:
            self.url = self.url_get()

    date = fields.Date(string='Date')
    is_default = fields.Boolean(string='Default')

    lang_id = fields.Many2one(comodel_name='lighting.language', ondelete='restrict', string='Language')

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='cascade', string='Product')

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '%s (%s)' % (record.datas_fname, record.type_id.display_name)
            vals.append((record.id, name))

        return vals

    def url_get(self, resolution=None, set_public=False):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        pattern_l = ['%s/web/image/h/%s']
        if resolution:
            pattern_l.append(resolution)
        pattern_l.append('%s')

        if set_public and not self.attachment_id.public:
            self.sudo().attachment_id.public = True

        return '/'.join(pattern_l) % (base_url, self.attachment_id.checksum, self.datas_fname)

    @api.multi
    def get_main_image_attachments(self):
        images = self.filtered(lambda x: x.type_id.is_image)
        if images:
            images = images.sorted(lambda x: (x.type_id.sequence, x.sequence, x.id))

        return images

    @api.multi
    def get_main_resized_images(self):
        for im in self.get_main_image_attachments():
            if im.attachment_id.store_fname:
                imageb64 = self.env['ir.attachment']._file_read(im.attachment_id.store_fname)
                try:
                    return get_resized_images(imageb64)
                except IOError:
                    continue

        img_path = get_module_resource('web', 'static/src/img', 'placeholder.png')
        if img_path:
            with open(img_path, 'rb') as f:
                return get_resized_images(base64.b64encode(f.read()))

        return {}

    @api.multi
    def regenerate_preview(self):
        for rec in self:
            if rec.datas:
                resized_images = get_preview_images(rec.datas, rec.type_id.is_image)
                rec.write(resized_images)

        return True


class LightingAttachmentType(models.Model):
    _name = 'lighting.attachment.type'
    _order = 'sequence,code'

    def _sequence_default(self):
        max_sequence = self.env['lighting.attachment.type'] \
            .search([], order='sequence desc', limit=1).sequence

        return max_sequence + 1

    sequence = fields.Integer(required=True, default=_sequence_default,
                              help="The sequence field is used to define order")

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', translate=True)
    is_image = fields.Boolean(string='Is image', default=False)

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['lighting.product'].search_count(
                [('attachment_ids.type_id', '=', record.id)])

    _sql_constraints = [('name_uniq', 'unique (code)', 'The attachment type description must be unique!'),
                        ]

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            if record.name:
                name = '%s (%s)' % (record.name, record.code)
            else:
                name = record.code

            vals.append((record.id, name))

        return vals
