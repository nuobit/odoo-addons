# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WordPressIrChecksumBinder(Component):
    _name = "wordpress.ir.checksum.binder"
    _inherit = "wordpress.binder"

    _apply_on = "wordpress.ir.checksum"

    @property
    def external_id(self):
        return ["id"]

    @property
    def internal_id(self):
        return ["wordpress_idchecksum"]

    @property
    def external_alt_id(self):
        return []

    def _additional_external_binding_fields(self, external_data):
        return {
            **super()._additional_external_binding_fields(external_data),
            "wordpress_source_url": external_data["source_url"],
        }
