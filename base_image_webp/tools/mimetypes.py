# Backport of odoo/tools/mimetypes.py, Odoo 17.0 @ c98bc11e08d38cbc9f0e4bcfc552343ff9030583
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
"""The WebP entry of the `guess_mimetype` signature table as Odoo 17.0 has it.

The table only answers when `python-magic` is not installed: with it, 14.0's
`guess_mimetype` asks libmagic, which already knows WebP. `apply()` inserts the
17.0 entry once, after `image/x-icon`, into the running `odoo.tools.mimetypes`.
"""
from odoo.tools import mimetypes


def _check_webp(data):
    """This checks the presence of the WEBP and VP8 in the RIFF"""
    if data[8:15] == b"WEBPVP8":
        return "image/webp"


def apply():
    mappings = list(mimetypes._mime_mappings)
    types = [entry.mimetype for entry in mappings]
    if "image/webp" in types:
        return
    entry = mimetypes._Entry("image/webp", [b"RIFF"], [_check_webp])
    mappings.insert(types.index("image/x-icon") + 1, entry)
    mimetypes._mime_mappings = tuple(mappings)
