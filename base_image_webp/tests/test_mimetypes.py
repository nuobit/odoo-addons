# Backport of odoo/addons/base/tests/test_mimetypes.py, Odoo 17.0
# @ c98bc11e08d38cbc9f0e4bcfc552343ff9030583
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
import base64

from odoo.tests.common import BaseCase
from odoo.tools import mimetypes
from odoo.tools.mimetypes import guess_mimetype

from odoo.addons.base_image_webp.tools import mimetypes as mimetypes_webp

# single pixel webp image
WEBP = b"""UklGRjoAAABXRUJQVlA4IC4AAAAwAQCdASoBAAEAAUAmJaAAA3AA/u/uY//8s//2W/7LeM///5Bj
/dl/pJxGAAAA"""


class TestGuessMimetypeWebp(BaseCase):
    def test_mimetype_webp(self):
        content = base64.b64decode(WEBP)
        mimetype = guess_mimetype(content, default="test")
        self.assertEqual(mimetype, "image/webp")

    def test_patch_applied(self):
        """The 17.0 entry sits once in the table, right after image/x-icon."""
        types = [entry.mimetype for entry in mimetypes._mime_mappings]
        self.assertEqual(types.count("image/webp"), 1)
        self.assertEqual(types.index("image/webp"), types.index("image/x-icon") + 1)
        entry = mimetypes._mime_mappings[types.index("image/webp")]
        self.assertEqual(entry.signatures, [b"RIFF"])
        self.assertEqual(entry.discriminants, [mimetypes_webp._check_webp])
        self.assertEqual(
            mimetypes_webp._check_webp(base64.b64decode(WEBP)), "image/webp"
        )
        self.assertIsNone(mimetypes_webp._check_webp(b"RIFF\x00\x00\x00\x00WAVEfmt "))
        mimetypes_webp.apply()
        self.assertEqual(len(mimetypes._mime_mappings), len(types), "applied once")
