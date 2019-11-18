# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from PIL import Image, ImageChops, ImageEnhance
import io
import base64


def autocrop(im, bgcolor):
    if im.mode != "RGB":
        if im.mode in ('P'):
            im = im.convert("RGBA")
            im2 = Image.new('RGB', im.size, bgcolor)
            im2.paste(im, (0, 0), im)
            im = im2
        im = im.convert("RGB")

    bg = Image.new("RGB", im.size, bgcolor)

    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return None  # no contents


def expand2square(im, bgcolor):
    width, height = im.size
    if width == height:
        return im
    elif width > height:
        result = Image.new(im.mode, (width, width), bgcolor)
        result.paste(im, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(im.mode, (height, height), bgcolor)
        result.paste(im, ((height - width) // 2, 0))
        return result


def resize(im, asked_size, by_side_long=False, allow_scale=True):
    if asked_size and asked_size != (None, None):
        im_size = im.size
        if by_side_long and im.size[0] < im.size[1]:
            im_size = (im_size[1], im_size[0])

        hw_ratio = im_size[1] / im_size[0]
        asked_width, asked_height = asked_size
        if asked_height is None:
            asked_height = int(float(asked_width) * hw_ratio)
        if asked_width is None:
            asked_width = int(float(asked_height) * 1 / hw_ratio)

        asked_size = asked_width, asked_height
        if im_size != asked_size:
            if by_side_long and im.size[0] < im.size[1]:
                asked_size = (asked_size[1], asked_size[0])
            if not allow_scale and (asked_size[0] > im.size[0] or asked_size[1] > im.size[1]):
                return im
            return im.resize(asked_size, Image.ANTIALIAS)

    return im


def chunks(li, n):
    if not li:
        return
    yield li[:n]
    yield from chunks(li[n:], n)


class LightingProduct(models.Model):
    _inherit = 'lighting.product'

    datasheet_generation_date = fields.Datetime(compute='_compute_datasheet_generation_date')

    def _compute_datasheet_generation_date(self):
        for rec in self:
            rec.datasheet_generation_date = fields.Datetime.now()

    def get_sheet_sources(self):
        res = []
        for s in self.source_ids.sorted(lambda x: x.sequence):
            s_res = []
            s_type = s.get_source_type()
            if s_type:
                s_res.append(s_type[0])

            s_wattage = s.get_wattage()
            if s_wattage:
                s_res.append(s_wattage[0])

            s_flux = s.get_luminous_flux()
            if s_flux:
                s_res.append(s_flux[0])

            s_temp = s.get_color_temperature()
            if s_temp:
                s_res.append(s_temp[0])

            if s_res:
                res.append(' '.join(s_res))

        return res

    def get_sheet_beams(self):
        res = []
        for b in self.beam_ids:
            b_res = []
            s_angle = b.get_beam_angle()
            if s_angle:
                b_res.append(s_angle[0])

            s_phm = b.get_beam_photometric_distribution()
            if s_phm:
                b_res.append(s_phm[0])

            if b_res:
                res.append(' - '.join(b_res))

        return res

    def get_is_lamp_included(self):
        line_ids = self.source_ids.mapped('line_ids')
        integrated_line_ids = line_ids.filtered(lambda x: x.is_integrated)
        lamp_included_line_ids = line_ids.filtered(lambda x: not x.is_integrated).mapped('is_lamp_included')
        if integrated_line_ids:
            return any(lamp_included_line_ids) or None
        else:
            return any(lamp_included_line_ids)

    @api.multi
    def filter_by_catalogued(self):
        return self.filtered(
            lambda x: x.state_marketing in ('N', 'C', 'ES')
        )

    def get_usb(self):
        res = []
        if self.usb_ports:
            res.append("%gx" % self.usb_ports)

            if self.usb_voltage:
                res.append("%gV" % self.usb_voltage)

            if self.usb_current:
                res.append("%gmA" % self.usb_current)

            if res:
                return ' '.join(res)

        return None

    def get_datasheet_url(self):
        self.ensure_one()
        url = "{}/web/datasheet/{}/{}".format(
            self.env['ir.config_parameter'].sudo().get_param('web.base.url'),
            self.env.context.get('lang'),
            self.reference,
        )
        return url

    def get_attachments_by_type(self, atype, only_images=True):
        attachments = self.env['lighting.attachment']
        for rec in self:
            attachments |= rec.attachment_ids.filtered(
                lambda x: x.type_id.code == atype and
                          (not only_images or x.attachment_id.index_content == 'image')
            ).sorted(lambda x: (x.sequence, x.id))

        return attachments

    def get_complementary_fp_images(self, groupsof=None):
        # FP's current product
        attachments = self.get_attachments_by_type('FP')

        if not groupsof:
            groupsof = len(attachments)

        return list(chunks(attachments, groupsof))

    def get_complementary_fa_images(self, groupsof=None):
        # FA's current product
        attachments = self.get_attachments_by_type('FA')[2:]

        if not groupsof:
            groupsof = len(attachments)

        return list(chunks(attachments, groupsof))

    def get_groups_same_family(self, groupsof=None):
        groups = self.search([
            ('id', '!=', self.id),
            ('family_ids', 'in', self.family_ids.mapped('id')),
        ]).mapped('product_group_id') \
            .get_parent_group_by_type('PHOTO') \
            .filtered(lambda x: self not in x.flat_product_ids and
                                x.flat_product_ids.filter_by_catalogued() and
                                not all(x.flat_category_ids.mapped('root_id.is_accessory'))
                      ).sorted(lambda x: x.name)

        if not groupsof:
            groupsof = len(groups)

        return list(chunks(groups, groupsof))


class LightingAttachment(models.Model):
    _inherit = 'lighting.attachment'

    def get_optimized_image(self, enabled=True):
        if not enabled:
            return self.datas

        datas = base64.decodebytes(self.datas)
        im = Image.open(io.BytesIO(datas))

        im99 = resize(im, (500, None), by_side_long=True, allow_scale=False)

        # sharpener = ImageEnhance.Sharpness(im7)
        # im99 = sharpener.enhance(2.0)

        # im9 = autocrop(im7, (255, 255, 255))
        # if not im9:
        #     return self.datas
        #
        # im99 = expand2square(im9, (255, 255, 255))

        in_mem_file = io.BytesIO()
        im99.save(in_mem_file, format=im.format)

        datas_cropped = base64.b64encode(in_mem_file.getvalue())

        return datas_cropped
