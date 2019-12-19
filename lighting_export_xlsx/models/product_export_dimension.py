# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api


class LightingExportDimension():

    @api.multi
    def export_xlsx(self, template_id=None):
        if not self:
            return None

        res = {}
        for rec in self:
            res[rec.display_name] = rec.value

        return [res]
