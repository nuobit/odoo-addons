# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models, tools


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    @api.model
    @tools.ormcache_context("self._uid", "debug", keys=("lang",))
    def load_menus(self, debug):
        # New dicts: the menus returned by super() are its cached result.
        return {
            key: self._with_flat_icon(menu)
            for key, menu in super().load_menus(debug).items()
        }

    def _with_flat_icon(self, menu):
        """Return ``menu`` with the image of the flat icon that replaces its
        web icon, or ``menu`` itself when no flat icon replaces it."""
        # The web icon "module,path" is the file served at "/module/path". The
        # root menu has no web icon, and a menu without icon has False.
        web_icon = menu.get("web_icon")
        icon_url = "/" + web_icon.replace(",", "/", 1) if web_icon else None
        flat_url = self.env["ir.module.module"]._get_flat_icon_urls().get(icon_url)
        if flat_url is None:
            return menu
        flat_web_icon = flat_url[1:].replace("/", ",", 1)
        return dict(menu, web_icon_data=self._compute_web_icon_data(flat_web_icon))
