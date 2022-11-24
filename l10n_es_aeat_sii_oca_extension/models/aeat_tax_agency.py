# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models

from odoo.addons.l10n_es_aeat_sii_oca.models.aeat_tax_agency import (
    SII_PORT_NAME_MAPPING,
    SII_WDSL_MAPPING,
)


class AeatTaxAgency(models.Model):
    _inherit = "aeat.tax.agency"

    def _prepare_sii_wdsl_mapping(self):
        return SII_WDSL_MAPPING

    def _prepare_sii_port_name_mapping(self):
        return SII_PORT_NAME_MAPPING

    def _connect_params_sii(self, mapping_key, company):
        self.ensure_one()
        if SII_WDSL_MAPPING.get(mapping_key) and SII_PORT_NAME_MAPPING.get(mapping_key):
            return super()._connect_params_sii(mapping_key, company)
        sii_wdsl_mapping = self._prepare_sii_wdsl_mapping()
        sii_port_name_mapping = self._prepare_sii_port_name_mapping()

        wsdl_field = sii_wdsl_mapping[mapping_key]
        wsdl_test_field = wsdl_field + "_test_address"
        port_name = sii_port_name_mapping[mapping_key]
        address = getattr(self, wsdl_test_field) if company.sii_test else False
        if not address and company.sii_test:
            # If not test address is provides we try to get it using the port name.
            port_name += "Pruebas"
        return {
            "wsdl": getattr(self, wsdl_field),
            "address": address,
            "port_name": port_name,
        }
