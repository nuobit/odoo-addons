# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


def insert_after(lst, item, new_item):
    for i, e in enumerate(lst):
        if e == item:
            lst.insert(i + 1, new_item)
            break


class AccountAsset(models.Model):
    _inherit = "account.asset"

    @api.model
    def _xls_acquisition_fields(self):
        fields = super()._xls_acquisition_fields()
        insert_after(fields, "name", "category")
        return fields

    @api.model
    def _xls_active_fields(self):
        fields = super()._xls_active_fields()
        insert_after(fields, "name", "category")
        return fields

    @api.model
    def _xls_removal_fields(self):
        fields = super()._xls_removal_fields()
        insert_after(fields, "name", "category")
        return fields

    @api.model
    def _xls_asset_template(self):
        asset_template = super()._xls_asset_template()
        AssetReport = self.env["report.account_asset_management.asset_report_xls"]
        return {
            "category": {
                "header": {"type": "string", "value": AssetReport._("Category")},
                "asset": {
                    "type": "string",
                    "value": AssetReport._render("asset.profile_id.display_name or ''"),
                },
                "width": 20,
            },
            **asset_template,
        }
