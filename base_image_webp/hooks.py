# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
from .tools import image, mimetypes


def post_load():
    image.apply()
    mimetypes.apply()
