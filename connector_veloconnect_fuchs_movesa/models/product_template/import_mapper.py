# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class VeloconnectProductTemplateImportMapper(Component):
    _inherit = "veloconnect.product.template.import.mapper"

    def _check_default_code(self, default_code, manufacturer_id):
        if default_code != manufacturer_id:
            if not self.backend_record.is_fuchs_movesa or not default_code.startswith(
                manufacturer_id.replace(" ", "")
            ):
                super()._check_default_code(default_code, manufacturer_id)
