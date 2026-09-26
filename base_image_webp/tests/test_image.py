# Backport of odoo/addons/base/tests/test_image.py, Odoo 17.0
# @ c98bc11e08d38cbc9f0e4bcfc552343ff9030583
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
import base64

from PIL import Image

from odoo import tools
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

from odoo.addons.base_image_webp.tools import image as image_webp


def make_webp(width, height):
    """Return the RIFF header of an extended (VP8X) WebP of the given size.

    Nothing in Odoo decodes a WebP: the header is all the patched code reads.
    """
    wm1, hm1 = width - 1, height - 1
    dims = bytes(
        (
            wm1 & 0xFF,
            (wm1 >> 8) & 0xFF,
            (wm1 >> 16) & 0xFF,
            hm1 & 0xFF,
            (hm1 >> 8) & 0xFF,
            (hm1 >> 16) & 0xFF,
        )
    )
    chunk = b"VP8X" + (10).to_bytes(4, "little") + b"\x00\x00\x00\x00" + dims
    body = b"WEBP" + chunk
    return b"RIFF" + len(body).to_bytes(4, "little") + body


def make_webp_base64(width, height):
    return base64.b64encode(make_webp(width, height))


class TestImageWebp(TransactionCase):
    """The 17.0 WebP tests on the patched 14.0 tools, the 14.0 contract
    (base64 in, base64 out) and the regressions of the other formats."""

    def setUp(self):
        super().setUp()
        self.base64_svg = base64.b64encode(b"<svg></svg>")
        self.base64_1920x1080_jpeg = tools.image_to_base64(
            Image.new("RGB", (1920, 1080)), "JPEG"
        )
        self.base64_2000x1000_png = tools.image_to_base64(
            Image.new("RGB", (2000, 1000)), "PNG"
        )
        self.base64_webp_2000x2000 = make_webp_base64(2000, 2000)

    def test_patch_applied(self):
        """A missing manifest key would be a silent no-op: assert every rebinding."""
        self.assertIs(tools.image.ImageProcess.__init__, image_webp.image_process_init)
        self.assertIs(tools.image.get_webp_size, image_webp.get_webp_size)
        self.assertIs(tools.get_webp_size, image_webp.get_webp_size)
        self.assertIs(tools.image.is_image_size_above, image_webp.is_image_size_above)
        self.assertIs(tools.is_image_size_above, image_webp.is_image_size_above)
        self.assertEqual(tools.image.FILETYPE_BASE64_MAGICWORD[b"U"], "webp")

    def test_17_get_webp_size(self):
        # Using 32 bytes image headers as data.
        # Lossy webp: 550x368
        webp_lossy = (
            b"RIFFhv\x00\x00WEBPVP8 \\v\x00\x00\xd2\xbe\x01\x9d\x01*&\x02p\x01>\xd5"
        )
        size = tools.get_webp_size(webp_lossy)
        self.assertEqual((550, 368), size, "Wrong resolution for lossy webp")
        # Lossless webp: 421x163
        webp_lossless = (
            b"RIFF\xba\x84\x00\x00WEBPVP8L"
            b"\xad\x84\x00\x00/\xa4\x81(\x10MHr\x1bI\x92\xa4"
        )
        size = tools.get_webp_size(webp_lossless)
        self.assertEqual((421, 163), size, "Wrong resolution for lossless webp")
        # Extended webp: 800x600
        webp_extended = (
            b"RIFF\x80\xce\x00\x00WEBPVP8X"
            b"\n\x00\x00\x00\x10\x00\x00\x00\x1f\x03\x00W\x02\x00AL"
        )
        size = tools.get_webp_size(webp_extended)
        self.assertEqual((800, 600), size, "Wrong resolution for extended webp")
        with self.assertRaises(UserError, msg="not a webp"):
            tools.get_webp_size(base64.b64decode(self.base64_1920x1080_jpeg))

    def test_12_image_process_verify_resolution(self):
        """The WebP half of the 17.0 test, on base64 input."""
        # Oversized webp images shouldn't be uploaded without any limit.
        res = tools.image_process(make_webp_base64(2000, 2000), verify_resolution=True)
        self.assertNotEqual(res, False, "webp size ok")
        with self.assertRaises(UserError, msg="webp size excessive"):
            tools.image_process(make_webp_base64(8000, 8000), verify_resolution=True)

    def test_webp_pass_through(self):
        """A WebP is stored as received: no operation touches it (as 17.0)."""
        webp = self.base64_webp_2000x2000
        self.assertIs(tools.image.ImageProcess(webp).image, False)
        self.assertEqual(tools.image_process(webp, size=(1920, 1920)), webp)
        self.assertEqual(
            tools.image_process(webp, size=(128, 128), crop="center"), webp
        )
        self.assertEqual(tools.image_process(webp, quality=95), webp)
        self.assertEqual(tools.image_process(webp, output_format="PNG"), webp)
        self.assertEqual(tools.image_process(webp, colorize=True), webp)
        self.assertEqual(tools.image_process(webp, verify_resolution=True), webp)
        webp_str = webp.decode("ascii")
        self.assertEqual(tools.image_process(webp_str, size=(128, 128)), webp_str)

    def test_is_image_size_above_webp(self):
        big, small = make_webp_base64(800, 600), make_webp_base64(400, 300)
        self.assertTrue(tools.is_image_size_above(big, small))
        self.assertFalse(tools.is_image_size_above(small, big))
        self.assertFalse(tools.is_image_size_above(big, big))
        self.assertTrue(tools.is_image_size_above(self.base64_1920x1080_jpeg, big))
        self.assertFalse(tools.is_image_size_above(big, self.base64_1920x1080_jpeg))
        self.assertFalse(tools.is_image_size_above(big, self.base64_svg))
        self.assertFalse(tools.is_image_size_above(big, False))

    def test_image_data_uri_webp(self):
        webp = self.base64_webp_2000x2000
        self.assertEqual(
            tools.image_data_uri(webp), "data:image/webp;base64," + webp.decode("ascii")
        )

    def test_other_formats_unchanged(self):
        """The patched constructor keeps the 14.0 behaviour for every other input."""
        self.assertFalse(tools.image_process(False, size=(10, 10)))
        self.assertEqual(
            tools.image_process(self.base64_svg, size=(10, 10)), self.base64_svg
        )
        self.assertEqual(
            tools.image.ImageProcess(self.base64_1920x1080_jpeg).original_format, "JPEG"
        )
        image = tools.base64_to_image(
            tools.image_process(self.base64_2000x1000_png, size=(1920, 1920))
        )
        self.assertEqual(image.size, (1920, 960))
        image = tools.base64_to_image(
            tools.image_process(self.base64_1920x1080_jpeg, size=(192, 108))
        )
        self.assertEqual(image.size, (192, 108))
        image = tools.base64_to_image(
            tools.image_process(self.base64_1920x1080_jpeg, output_format="PNG")
        )
        self.assertEqual(image.format, "PNG")
        self.assertTrue(
            tools.is_image_size_above(
                self.base64_1920x1080_jpeg, self.base64_2000x1000_png
            )
        )
        # in the following tests, pass `quality` to force the processing
        with self.assertRaises(UserError, msg="not an image"):
            tools.image_process(b"oazdazpodazdpokd", quality=95)
        with self.assertRaises(UserError, msg="not base64"):
            tools.image_process(b"oazdazpodazdpok", quality=95)
        base64_image_excessive = tools.image_to_base64(
            Image.new("RGB", (50001, 1000)), "PNG"
        )
        with self.assertRaises(UserError, msg="size excessive"):
            tools.image_process(base64_image_excessive, verify_resolution=True)
