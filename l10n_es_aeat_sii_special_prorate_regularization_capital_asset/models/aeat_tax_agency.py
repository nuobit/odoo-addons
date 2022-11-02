# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AeatTaxAgency(models.Model):
    _inherit = "aeat.tax.agency"

    def _prepare_sii_wdsl_mapping(self):
        return {**super()._prepare_sii_wdsl_mapping(), "capital_asset": "sii_wsdl_pi"}

    def _prepare_sii_port_name_mapping(self):
        return {
            **super()._prepare_sii_port_name_mapping(),
            "capital_asset": "SuministroBienesInversion",
        }
