# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class OxigestiSPMSBackendAdapter(Component):
    _name = "oxigesti.spms.backend.adapter"
    _inherit = ["oxigesti.spms.adapter", "oxigesti.spms.connector"]
    _description = "Oxigesti SPMS Backend Adapter"

    _apply_on = "oxigesti.spms.backend"

    # def create_partner(self):
    #     vals = {
    #         "Id": 12345,
    #         "UnidadeLocalSalude": "Centro de Salud Madrid",
    #         "DataInicio": "2023-01-01",
    #         "DataFim": "2023-12-31",
    #         "Cidade": "Madrid",
    #         "CodigoPostal": "28001",
    #         "Domicilio": "Calle Gran Via, 10",
    #         "NIF": "12345678A",
    #         "Cliente_Odoo": True,
    #         "CodigoConvencao": "CONV2023",
    #     }
    #     return self.create(vals)
