# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
import base64

from PIL import Image

from odoo import tools
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

from .test_image import make_webp_base64

# name: (width, height, bitstream fourcc); real files written once with Pillow
SAMPLES = {
    "lossy.webp": (64, 48, b"VP8 "),
    "lossless_alpha.webp": (48, 64, b"VP8L"),
    "animated.webp": (32, 32, b"VP8X"),
}


def sample(name):
    with tools.file_open("base_image_webp/tests/samples/" + name, "rb") as f:
        return f.read()


def sample_base64(name):
    return base64.b64encode(sample(name))


def png_base64(width, height):
    return tools.image_to_base64(Image.new("RGB", (width, height)), "PNG")


def size_of(base64_source):
    return tools.base64_to_image(base64_source).size


class TestImageFieldWebp(TransactionCase):
    """A real WebP through `fields.Image` on `res.partner` (base only)."""

    def attachment(self, partner, field):
        return (
            self.env["ir.attachment"]
            .sudo()
            .search(
                [
                    ("res_model", "=", "res.partner"),
                    ("res_id", "=", partner.id),
                    ("res_field", "=", field),
                ]
            )
        )

    def test_samples_are_webp(self):
        """The committed fixtures: three bitstreams, sizes read from the header."""
        for name, (width, height, bitstream) in SAMPLES.items():
            raw = sample(name)
            self.assertEqual(raw[0:4], b"RIFF", name)
            self.assertEqual(raw[12:16], bitstream, name)
            self.assertEqual(tools.get_webp_size(raw), (width, height), name)

    def test_webp_kept_untouched(self):
        """Acceptance 1: the bytes stored are the bytes received, in every size."""
        for name in SAMPLES:
            webp = sample_base64(name)
            partner = self.env["res.partner"].create({"name": name, "image_1920": webp})
            self.assertEqual(partner.image_1920, webp, name)
            for field in ("image_1024", "image_512", "image_256", "image_128"):
                self.assertEqual(partner[field], webp, "%s %s" % (name, field))
            attachment = self.attachment(partner, "image_1920")
            self.assertEqual(len(attachment), 1, name)
            self.assertEqual(attachment.datas, webp, name)
            self.assertEqual(attachment.mimetype, "image/webp", name)

    def test_webp_replaces_png(self):
        """A write behaves as a create: the WebP replaces a resized PNG untouched."""
        partner = self.env["res.partner"].create(
            {"name": "png first", "image_1920": png_base64(2000, 1000)}
        )
        webp = sample_base64("lossy.webp")
        partner.write({"image_1920": webp})
        self.assertEqual(partner.image_1920, webp)
        self.assertEqual(partner.image_128, webp)
        self.assertEqual(self.attachment(partner, "image_1920").mimetype, "image/webp")

    def test_webp_oversize_rejected(self):
        """Acceptance 2: the 50 Mpx limit holds for WebP, on create and on write."""
        with self.assertRaises(UserError):
            self.env["res.partner"].create(
                {"name": "too big", "image_1920": make_webp_base64(8000, 8000)}
            )
        partner = self.env["res.partner"].create(
            {"name": "small", "image_1920": sample_base64("lossy.webp")}
        )
        with self.assertRaises(UserError):
            partner.write({"image_1920": make_webp_base64(7100, 7100)})

    def test_png_still_resized(self):
        """Acceptance 4: the other formats keep the 14.0 processing."""
        partner = self.env["res.partner"].create(
            {"name": "png", "image_1920": png_base64(2000, 1000)}
        )
        self.assertEqual(size_of(partner.image_1920), (1920, 960))
        self.assertEqual(size_of(partner.image_1024), (1024, 512))
        self.assertEqual(size_of(partner.image_512), (512, 256))
        self.assertEqual(size_of(partner.image_256), (256, 128))
        self.assertEqual(size_of(partner.image_128), (128, 64))
        self.assertEqual(self.attachment(partner, "image_1920").mimetype, "image/png")
