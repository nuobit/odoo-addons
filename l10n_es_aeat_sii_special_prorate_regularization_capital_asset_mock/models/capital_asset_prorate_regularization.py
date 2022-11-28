# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class AssetProrateRegularization(models.Model):
    _inherit = "capital.asset.prorate.regularization"

    def _connect_sii(self, mapping_key):
        class SiiMock:
            _res = {
                "EstadoEnvio": "Correcto",
                "CSV": "CSVTEST",
                "RespuestaLinea": [{"CodigoErrorRegistro": False}],
            }

            def __init__(self, **kwargs):
                self.asset_line = kwargs.get("asset_line")

            def SuministroLRBienesInversion(self, header, asset_dict):
                _logger.info(
                    "SuministroLRBienesInversion:\nHeader: %s\nAsset Line: %s",
                    header,
                    asset_dict,
                )
                return self._res

            def AnulacionLRBienesInversion(self, header, asset_dict):
                _logger.info(
                    "AnulacionLRBienesInversion:\nHeader: %s\nAsset Line: %s",
                    header,
                    asset_dict,
                )
                if self.asset_line:
                    self.asset_line.sii_header_sent = False
                    self.asset_line.sii_content_sent = False
                return self._res

        return SiiMock(asset_line=self)
