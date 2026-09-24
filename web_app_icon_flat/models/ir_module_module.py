# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import base64
from pathlib import Path

from odoo import api, fields, models, modules, tools


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    display_icon = fields.Char(
        string="Displayed Icon URL",
        compute="_compute_display_icon",
        help="URL of the flat icon that replaces the module icon, if any; "
        "otherwise, the URL of the module icon.",
    )

    @api.model
    def _get_flat_icon_addons(self):
        """Return the names of the addons that ship flat icons, in order.

        An addon ships the file ``static/img/<module>/<file>`` to replace the
        icon ``<module>/static/description/<file>``. A module that brings the
        flat icon of another app extends this list with its own name; when two
        addons ship the same file, the last one wins.
        """
        return ["web_app_icon_flat"]

    @api.model
    @tools.ormcache()
    def _get_flat_icon_urls(self):
        """Return the URL of each icon that a flat icon replaces, mapped to the
        URL of the flat icon."""
        return {
            f"/{icon.parent.name}/static/description/{icon.name}": (
                f"/{addon}/static/img/{icon.parent.name}/{icon.name}"
            )
            for addon in self._get_flat_icon_addons()
            for icon in Path(modules.get_module_path(addon), "static/img").glob("*/*")
        }

    @api.depends("icon")
    def _compute_display_icon(self):
        flat_icon_urls = self._get_flat_icon_urls()
        for module in self:
            module.display_icon = flat_icon_urls.get(module.icon, module.icon)

    @api.depends("display_icon")
    def _get_icon_image(self):
        flat_modules = self.filtered(lambda module: module.display_icon != module.icon)
        for module in flat_modules:
            path = modules.get_module_resource(*module.display_icon.split("/")[1:])
            with tools.file_open(
                path, "rb", filter_ext=(".png", ".svg", ".gif", ".jpeg", ".jpg")
            ) as image_file:
                module.icon_image = base64.b64encode(image_file.read())
        return super(IrModuleModule, self - flat_modules)._get_icon_image()
