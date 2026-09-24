# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        # The web client replaces with them the icon URLs it builds by itself,
        # such as those of the Settings sidebar.
        return dict(
            super().session_info(),
            flat_icon_urls=self.env["ir.module.module"]._get_flat_icon_urls(),
        )
