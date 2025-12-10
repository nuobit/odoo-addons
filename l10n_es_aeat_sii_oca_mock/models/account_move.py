# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _connect_aeat(self, mapping_key):
        class SiiMock:
            _res = {
                "EstadoEnvio": "Correcto",
                "CSV": "CSVTEST",
                "RespuestaLinea": [{"CodigoErrorRegistro": False}],
            }

            def __init__(self, *args, **kwargs):
                self.invoice = kwargs.get("invoice")

            def SuministroLRFacturasEmitidas(self, header, inv_dict):
                _logger.info(
                    "SuministroLRFacturasEmitidas:\nHeader: %s\nInvoice: %s",
                    header,
                    inv_dict,
                )
                return self._res

            def SuministroLRFacturasRecibidas(self, header, inv_dict):
                _logger.info(
                    "SuministroLRFacturasRecibidas:\nHeader: %s\nInvoice: %s",
                    header,
                    inv_dict,
                )
                return self._res

            def AnulacionLRFacturasEmitidas(self, header, inv_dict):
                _logger.info(
                    "AnulacionLRFacturasEmitidas:\nHeader: %s\nInvoice: %s",
                    header,
                    inv_dict,
                )
                if self.invoice:
                    self.invoice.aeat_header_sent = False
                    self.invoice.aeat_content_sent = False
                return self._res

            def AnulacionLRFacturasRecibidas(self, header, inv_dict):
                _logger.info(
                    "AnulacionLRFacturasRecibidas:\nHeader: %s\nInvoice: %s",
                    header,
                    inv_dict,
                )
                if self.invoice:
                    self.invoice.aeat_header_sent = False
                    self.invoice.aeat_content_sent = False
                return self._res

        return SiiMock(invoice=self)
