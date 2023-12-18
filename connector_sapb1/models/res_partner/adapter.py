# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class SapB1ResPartnerAdapter(Component):
    _name = "sapb1.res.partner.adapter"
    _inherit = "connector.sapb1.adapter"

    _apply_on = "sapb1.res.partner"

    def search_read(self, domain):
        domain = self._format_partner_domain(domain)
        filters_values = ["CardCode"]
        real_domain, common_domain = self._extract_domain_clauses(
            domain, filters_values
        )
        kw_base_params = self._domain_to_normalized_dict(real_domain)
        res = self._exec(
            "get_partner",
            **self._prepare_parameters(kw_base_params, [], filters_values)
        )
        res = self._reorg_partner_data(res)
        filtered_res = self._filter(res, common_domain)
        return filtered_res

    def _format_partner_values(self, values):
        conv_mapper = {
            "/Block": lambda x: x or None,
            "/Street": lambda x: x or None,
            "/ZipCode": lambda x: x or None,
            "/City": lambda x: x or None,
            "/AddressName3": lambda x: x or None,
        }
        self._convert_format(values, conv_mapper)

    def _format_partner_domain(self, domain):
        conv_mapper = {
            "Block": lambda x: x or None,
            "Street": lambda x: x or None,
            "ZipCode": lambda x: x or None,
            "City": lambda x: x or None,
            "AddressName3": lambda x: x or None,
        }
        return self._convert_format_domain(domain, conv_mapper)

    def _reorg_partner_data(self, values):
        for address in values["BPAddresses"]:
            address["CardCode"] = address.pop("BPCode")
        return values["BPAddresses"]

    def create(self, values):  # pylint: disable=W8106
        external_id = values.pop("CardCode")
        self._format_partner_values(values)
        with self._retry_concurrent_write_operation():
            res = self._exec("create_address", external_id=external_id, values=values)
        return res

    def write(self, external_id, values):  # pylint: disable=W8106
        """Update records on the external system"""
        values.pop("CardCode")
        values.pop("AddressName")
        res = self._exec("update_address", external_id=external_id, values=values)
        return res
