# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceBaseSaleOrderImporter(Component):
    _inherit = "woocommerce.sale.order.record.direct.importer"

    def _get_order_vat(self, dir_type, value):
        """The VAT number of the NIF of the ``dir_type`` block of ``value``,
        with a country code: the block country's, else the one of the backend's
        company. It is worked out once per import and kept in the block, since
        each check may ask VIES."""
        block = value[dir_type]
        if "woocommerce_vat" not in block:
            block["woocommerce_vat"] = self.env["res.partner"]._woocommerce_vat_number(
                block["nif"],
                self.env["res.country"].search([("code", "=", block["country"])]),
                self.backend_record.company_id.country_id,
            )
        return block["woocommerce_vat"]

    def _get_partner_parent_key(self, dir_type, value):
        if value[dir_type].get("nif"):
            key = "vat", self._get_order_vat(dir_type, value)
        else:
            key = super()._get_partner_parent_key(dir_type, value)
        return key

    def _get_partner_parent_domain(self, dir_type, value):
        # A NIF belongs to a contact with no parent, whatever form its VAT
        # number was stored in: its children have it too, by Odoo's sync.
        # The forms are those of the NIF as the import codes it and as it is
        # with the code of the backend company's country: a NIF billed outside
        # Europe gets no code, but may have been stored with that one.
        # Without a NIF, the search is by name.
        if value[dir_type].get("nif"):
            partner = self.env["res.partner"]
            vat_forms = partner._woocommerce_vat_forms(
                self._get_order_vat(dir_type, value)
            ) + partner._woocommerce_vat_forms(
                partner.fix_eu_vat_number(
                    self.backend_record.company_id.country_id.id,
                    value[dir_type]["nif"],
                )
            )
            domain = [
                ("parent_id", "=", False),
                ("woocommerce_vat_compact", "in", vat_forms),
            ]
        else:
            domain = super()._get_partner_parent_domain(dir_type, value)
        return domain

    def _additional_partner_parent_fields(self, value, dir_type):
        return {
            **super()._additional_partner_parent_fields(value, dir_type),
            "vat": self._get_order_vat(dir_type, value)
            if value[dir_type].get("nif")
            else None,
        }
