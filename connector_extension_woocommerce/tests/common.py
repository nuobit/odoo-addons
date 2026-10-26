# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from unittest.mock import Mock

from odoo.addons.component.core import WorkContext
from odoo.addons.component.tests.common import TransactionComponentRegistryCase


class WooCommerceAdapterCase(TransactionComponentRegistryCase):
    """The WooCommerce adapter on a stand-in backend, without any HTTP call."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_registry(cls)
        cls.comp_registry.load_components("connector_extension_woocommerce")

    @classmethod
    def tearDownClass(cls):
        cls._teardown_registry(cls)
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        # The module has no backend model: the adapter reads only these two
        # fields of the backend it works for, here with their defaults
        self.backend_record = Mock(page_size=10, enable_call_logging=False)
        self.backend_record.env = self.env
        work = WorkContext(
            model_name="res.partner",
            collection=self.backend_record,
            components_registry=self.comp_registry,
        )
        self.adapter = self.comp_registry[
            "connector.extension.woocommerce.adapter.crud"
        ](work)
