# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.tests import common
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TestAccountTax(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountTax, cls).setUpClass()

    def test_tax_template(self):
       print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")