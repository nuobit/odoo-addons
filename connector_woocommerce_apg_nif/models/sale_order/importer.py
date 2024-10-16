# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceBaseSaleOrderImporter(Component):
    _inherit = "woocommerce.wpml.sale.order.record.direct.importer"

    # TODO: ADD EMPTY COMPANY_TYPE AND OVERWRITE NAME IF NIF EXISTS
    def _get_partner_parent_domain(self, dir_type, value):
        domain = super()._get_partner_parent_domain(dir_type, value)
        if value[dir_type].get("nif"):
            domain.append(("vat", "=", value[dir_type]["nif"]))
        else:
            if (
                dir_type == "shipping"
                and value["shipping"]["name"] == value["billing"]["name"]
            ):
                domain.append(("id", "=", value["billing"]["parent"]))
        return domain

    def _additional_partner_parent_fields(self, value, dir_type):
        return {
            **super()._additional_partner_parent_fields(value, dir_type),
            "vat": value[dir_type].get("nif"),
        }
