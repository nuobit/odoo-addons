# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo_test_helper import FakeModelLoader

from odoo import Command

from odoo.addons.component.tests.common import TransactionComponentRegistryCase


class ConnectorExtensionBinderCase(TransactionComponentRegistryCase):
    """A test backend and a test binding of partners, loaded as fake models,
    and a component registry holding this module's components.
    Each test class adds the components its scenario needs."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .fake_models import (
            ConnectorExtensionTestBackend,
            ConnectorExtensionTestBinding,
        )

        fake_models = (ConnectorExtensionTestBackend, ConnectorExtensionTestBinding)
        cls.loader.update_registry(fake_models)
        # Odoo's TransactionCase.check_attrs (odoo/tests/common.py) fails each
        # test after which a model class has an attribute its attrs_before entry
        # does not list. TransactionCase.setUpClass fills attrs_before before
        # the fake models exist: their entries are the attributes they have once
        # loaded.
        for fake_model in fake_models:
            cls.attrs_before[fake_model._name] = cls.attrs_before["base"] | set(
                vars(cls.registry[fake_model._name])
            )
        cls._setup_registry(cls)
        cls.comp_registry.load_components("connector_extension")
        cls.backend = cls.env["connector.extension.test.backend"].create(
            {
                "name": "Test Backend",
                "lang_ids": [Command.set(cls.env.ref("base.lang_en").ids)],
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Partner Test",
                "email": "partner_test@example.com",
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls._teardown_registry(cls)
        cls.loader.restore_registry()
        super().tearDownClass()

    def binder(self, **work_attributes):
        """The binder of the test binding on the test backend. Its work
        context also carries ``work_attributes``."""
        with self.backend.work_on(
            "connector.extension.test.binding",
            components_registry=self.comp_registry,
            **work_attributes,
        ) as work:
            return work.component(usage="binder")
