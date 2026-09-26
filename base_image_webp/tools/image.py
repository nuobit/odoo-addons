# Backport of odoo/tools/image.py, Odoo 17.0 @ c98bc11e08d38cbc9f0e4bcfc552343ff9030583
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
"""WebP support of `odoo.tools.image` as Odoo 17.0 has it.

Odoo 17.0 never hands a WebP to PIL: `ImageProcess.__init__` recognises the
RIFF/WEBP header, keeps the bytes untouched and checks the resolution with a
header parser (`get_webp_size`); `is_image_size_above` reads the same header,
and the base64 magic-word map knows the `U` of `RIFF`. `apply()` binds those
four pieces into the running 14.0 `odoo.tools.image` (and `odoo.tools`, which
re-exports it).

Adapted to 14.0: `ImageProcess` receives the image base64 encoded, so the
constructor decodes it once before the 17.0 body; the error messages are the
14.0 ones so that the translations shipped by `base` still apply.
"""
import base64
import binascii
import io

from PIL import Image

from odoo import tools
from odoo.exceptions import UserError
from odoo.tools import image
from odoo.tools.misc import DotDict
from odoo.tools.translate import _


def image_process_init(self, base64_source, verify_resolution=True):
    """Initialize the `base64_source` image for processing.

    :param base64_source: the original image base64 encoded
        No processing will be done if the `base64_source` is falsy or if
        the image is SVG or WEBP.
    :type base64_source: string or bytes

    :param verify_resolution: if True, make sure the original image size is not
        excessive before starting to process it. The max allowed resolution is
        defined by `IMAGE_MAX_RESOLUTION`.
    :type verify_resolution: bool

    :return: self
    :rtype: ImageProcess

    :raise: ValueError if `verify_resolution` is True and the image is too large
    :raise: UserError if the base64 is incorrect or the image can't be identified by PIL
    """
    self.base64_source = base64_source or False
    self.operationsCount = 0

    if not base64_source or base64_source[:1] in (b"P", "P"):
        # don't process empty source or SVG
        self.image = False
    else:
        try:
            source = base64.b64decode(base64_source)
        except binascii.Error:
            raise UserError(
                _(
                    "This file could not be decoded as an image file. "
                    "Please try with a different file."
                )
            )

        if source[0:4] == b"RIFF" and source[8:15] == b"WEBPVP8":
            # don't process WEBP, but still verify its resolution like the
            # other formats.
            self.image = False
            if verify_resolution:
                size = get_webp_size(source)
                if size and size[0] * size[1] > image.IMAGE_MAX_RESOLUTION:
                    raise UserError(
                        _(
                            "Image size excessive, uploaded images must be smaller "
                            "than %s million pixels.",
                            str(image.IMAGE_MAX_RESOLUTION / 1e6),
                        )
                    )
        else:
            self.image = binary_to_image(source)

            # Original format has to be saved before fixing the orientation or
            # doing any other operations because the information will be lost on
            # the resulting image.
            self.original_format = (self.image.format or "").upper()

            self.image = image.image_fix_orientation(self.image)

            w, h = self.image.size
            if verify_resolution and w * h > image.IMAGE_MAX_RESOLUTION:
                raise UserError(
                    _(
                        "Image size excessive, uploaded images must be smaller "
                        "than %s million pixels.",
                        str(image.IMAGE_MAX_RESOLUTION / 1e6),
                    )
                )


def binary_to_image(source):
    try:
        return Image.open(io.BytesIO(source))
    except (OSError, binascii.Error):
        raise UserError(
            _(
                "This file could not be decoded as an image file. "
                "Please try with a different file."
            )
        )


def get_webp_size(source):
    """
    Returns the size of the provided webp binary source for VP8, VP8X and
    VP8L, otherwise returns None.
    See https://developers.google.com/speed/webp/docs/riff_container.

    :param source: binary source
    :return: (width, height) tuple, or None if not supported
    """
    if not (source[0:4] == b"RIFF" and source[8:15] == b"WEBPVP8"):
        raise UserError(_("This file is not a webp file."))

    vp8_type = source[15]
    if vp8_type == 0x20:  # 0x20 = ' '
        # Sizes on big-endian 16 bits at offset 26.
        width_low, width_high, height_low, height_high = source[26:30]
        width = (width_high << 8) + width_low
        height = (height_high << 8) + height_low
        return (width, height)
    elif vp8_type == 0x58:  # 0x48 = 'X'
        # Sizes (minus one) on big-endian 24 bits at offset 24.
        (
            width_low,
            width_medium,
            width_high,
            height_low,
            height_medium,
            height_high,
        ) = source[24:30]
        width = 1 + (width_high << 16) + (width_medium << 8) + width_low
        height = 1 + (height_high << 16) + (height_medium << 8) + height_low
        return (width, height)
    elif vp8_type == 0x4C and source[20] == 0x2F:  # 0x4C = 'L'
        # Sizes (minus one) on big-endian-ish 14 bits at offset 21.
        # E.g. [@20] 2F ab cd ef gh
        # - width = 1 + (c&0x3)d ab: ignore the two high bits of the second byte
        # - height= 1 + hef(c&0xC>>2): used them as the first two bits of the height
        ab, cd, ef, gh = source[21:25]
        width = 1 + ((cd & 0x3F) << 8) + ab
        height = 1 + ((gh & 0xF) << 10) + (ef << 2) + (cd >> 6)
        return (width, height)
    return None


def is_image_size_above(base64_source_1, base64_source_2):
    """Return whether or not the size of the given image `base64_source_1` is
    above the size of the given image `base64_source_2`.
    """
    if not base64_source_1 or not base64_source_2:
        return False
    if base64_source_1[:1] in (b"P", "P") or base64_source_2[:1] in (b"P", "P"):
        # False for SVG
        return False

    def get_image_size(base64_source):
        source = base64.b64decode(base64_source)
        if source[0:4] == b"RIFF" and source[8:15] == b"WEBPVP8":
            size = get_webp_size(source)
            if size:
                # Kept as upstream has it (the height reads size[0]).
                return DotDict({"width": size[0], "height": size[0]})
            else:
                # False for unknown WEBP format
                return False
        else:
            return image.image_fix_orientation(binary_to_image(source))

    image_source = get_image_size(base64_source_1)
    image_target = get_image_size(base64_source_2)
    return (
        image_source.width > image_target.width
        or image_source.height > image_target.height
    )


def apply():
    image.ImageProcess.__init__ = image_process_init
    image.get_webp_size = tools.get_webp_size = get_webp_size
    image.is_image_size_above = tools.is_image_size_above = is_image_size_above
    image.FILETYPE_BASE64_MAGICWORD[b"U"] = "webp"
