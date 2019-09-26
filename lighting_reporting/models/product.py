# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from PIL import Image, ImageChops
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


class LightingProduct(models.Model):
    _inherit = 'lighting.product'

    def get_sheet_sources(self):
        res = []
        for s in self.source_ids:
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

    def get_included_lamps(self):
        return self.source_ids.mapped('line_ids'). \
            filtered(lambda x: x.is_lamp_included).mapped('type_id.code')

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


class LightingAttachment(models.Model):
    _inherit = 'lighting.attachment'

    def get_optimized_image(self):
        datas = base64.decodebytes(self.datas)
        im = Image.open(io.BytesIO(datas))

        im9 = autocrop(im, (255, 255, 255))
        if not im9:
            return self.datas

        im99 = expand2square(im9, (255, 255, 255))

        in_mem_file = io.BytesIO()
        im99.save(in_mem_file, format=im.format)

        datas_cropped = base64.b64encode(in_mem_file.getvalue())

        return datas_cropped
