# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from datetime import datetime
from unittest import mock

from odoo.tools import config

from odoo.addons.component.core import Component
from odoo.addons.queue_job.exception import RetryableJobError

from .common import ConnectorExtensionBinderCase

BINDING_MODEL = "connector.extension.test.binding"


class ConnectorExtensionTestBinder(Component):
    """A remote record is keyed by its "id", kept in the binding's "external_id"."""

    _name = "connector.extension.test.binder"
    _inherit = "connector.extension.binder"
    _apply_on = BINDING_MODEL

    external_id = "id"
    internal_id = "external_id"


class ConnectorExtensionTestEmailBinder(Component):
    """The same keys, and the e-mail as the remote alternative id."""

    _name = "connector.extension.test.email.binder"
    _inherit = "connector.extension.binder"
    _apply_on = BINDING_MODEL

    external_id = "id"
    internal_id = "external_id"
    external_alt_id = "email"


class ConnectorExtensionTestExportMapper(Component):
    _name = "connector.extension.test.export.mapper"
    _inherit = "connector.extension.export.mapper"
    _apply_on = BINDING_MODEL

    direct = [("email", "email")]


class ConnectorExtensionTestAdapter(Component):
    """Searches the remote records carried by the work context."""

    _name = "connector.extension.test.adapter"
    _inherit = "connector.extension.adapter.crud"
    _apply_on = BINDING_MODEL

    def search_read(self, domain):
        return self._filter(self.work.remote_records, domain)


class TestBinder(ConnectorExtensionBinderCase):
    """A binder with no alternative id. The registry holds no export mapper,
    no import mapper and no adapter for the test binding."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._build_components(cls, ConnectorExtensionTestBinder)

    def test_bind_import_completes_the_values_without_committing(self):
        values = {}
        sync_date = datetime(2026, 3, 2, 9, 30)
        binder = self.binder()
        # test_enable off, as on a server: a commit guarded by it would run
        with (
            mock.patch.dict(config.options, {"test_enable": False}),
            mock.patch.object(self.env.cr, "commit") as commit,
        ):
            binder.bind_import({"id": 7}, values, sync_date, for_create=True)
        commit.assert_not_called()
        self.assertEqual(
            values,
            {
                "sync_date": sync_date,
                "backend_id": self.backend.id,
                "external_id": 7,
            },
        )

    def test_bind_import_of_an_update_adds_only_the_sync_date(self):
        values = {"name": "Partner Test"}
        sync_date = datetime(2026, 3, 2, 9, 30)
        self.binder().bind_import({"id": 7}, values, sync_date)
        self.assertEqual(values, {"name": "Partner Test", "sync_date": sync_date})

    def test_relink_without_alternative_id_needs_no_export_mapper(self):
        binding = self.binder().to_binding_from_internal_key(self.partner)
        self.assertEqual(binding, self.env[BINDING_MODEL])
        self.assertFalse(
            self.env[BINDING_MODEL].search([("odoo_id", "=", self.partner.id)])
        )

    def test_external_ids_of_a_bound_record_are_its_remote_keys(self):
        self.env[BINDING_MODEL].create(
            {
                "backend_id": self.backend.id,
                "odoo_id": self.partner.id,
                "external_id": 7,
            }
        )
        external_ids = self.binder().get_external_dict_ids(self.partner)
        self.assertEqual(external_ids, {"id": 7})

    def test_external_ids_of_an_unbound_record_fail_naming_model_and_step(self):
        binder = self.binder()
        with self.assertRaises(AssertionError) as error:
            binder.get_external_dict_ids(self.partner)
        self.assertEqual(
            str(error.exception),
            "Error on res.partner: The external id cannot be obtained. "
            "At this stage, the external record should have been already "
            "linked via ._export_dependencies.",
        )


class TestBinderEmailRelink(ConnectorExtensionBinderCase):
    """A binder whose alternative id is the e-mail, which the export mapper
    sends: a partner with no binding is linked to the remote record that
    has its e-mail, and the import mapper is missing, so the binder binds
    it itself."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._build_components(
            cls,
            ConnectorExtensionTestEmailBinder,
            ConnectorExtensionTestExportMapper,
            ConnectorExtensionTestAdapter,
        )

    def test_relink_binds_the_remote_record_with_the_same_email(self):
        binder = self.binder(
            remote_records=[
                {"id": 7, "email": "partner_test@example.com"},
                {"id": 8, "email": "other_test@example.com"},
            ]
        )
        binding = binder.to_binding_from_internal_key(self.partner)
        self.assertEqual(binding.odoo_id, self.partner)
        self.assertEqual(binding.backend_id, self.backend)
        self.assertEqual(binding.external_id, 7)

    def test_relink_when_the_remote_fails_binds_nothing(self):
        binder = self.binder(remote_records=[])
        with mock.patch.object(
            ConnectorExtensionTestAdapter,
            "search_read",
            autospec=True,
            side_effect=RetryableJobError("The remote system is not reachable"),
        ):
            # assertRaisesRegex opens no savepoint, so a binding made before
            # the error would stay for the check below
            with self.assertRaisesRegex(RetryableJobError, "not reachable"):
                binder.to_binding_from_internal_key(self.partner)
        self.assertFalse(
            self.env[BINDING_MODEL].search([("odoo_id", "=", self.partner.id)])
        )

    def test_relink_without_a_remote_match_binds_nothing(self):
        binder = self.binder(
            remote_records=[{"id": 8, "email": "other_test@example.com"}]
        )
        binding = binder.to_binding_from_internal_key(self.partner)
        self.assertEqual(binding, self.env[BINDING_MODEL])
        self.assertFalse(
            self.env[BINDING_MODEL].search([("odoo_id", "=", self.partner.id)])
        )
