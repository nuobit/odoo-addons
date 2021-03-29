# Copyright 2021 Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo.tests.common import SavepointCase, tagged

_logger = logging.getLogger(__name__)


@tagged("test_debug")
class TestProductServiceTime(SavepointCase):
    def test__product_variant_template_consinstency(self):
        _logger.info("XXXXXXXXXXXXXXX ------fffh-------------------1")
