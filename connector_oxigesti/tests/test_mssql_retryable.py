# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import pymssql

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.connector.exception import NetworkRetryableError

from ..components.adapter import api_handle_errors, mssql_connection_retryable


@tagged("post_install", "-at_install")
class TestMssqlConnectionRetryable(TransactionCase):
    """MSSQL connection errors must be retryable by queue_job.

    Reproduces the incident #2 from task #2548: during an MSSQL outage the
    adapter used to leak raw ``pymssql.OperationalError`` / ``InterfaceError``
    through the queue_job worker, which does not recognize them as
    retryable, so every in-flight export job went straight to ``failed``
    on its first attempt and the per-backend ``since_date`` cursor had
    already advanced past them.
    """

    def test_operational_error_is_wrapped_as_retryable(self):
        with self.assertRaises(NetworkRetryableError):
            with mssql_connection_retryable():
                raise pymssql.OperationalError(
                    "(6005) Adaptive Server is unavailable or does not exist"
                )

    def test_interface_error_is_wrapped_as_retryable(self):
        with self.assertRaises(NetworkRetryableError):
            with mssql_connection_retryable():
                raise pymssql.InterfaceError("Cannot connect to server")

    def test_integrity_error_is_not_wrapped(self):
        """Data-integrity errors must stay as-is — they are not transient
        and queue_job should not retry them."""
        with self.assertRaises(pymssql.IntegrityError):
            with mssql_connection_retryable():
                raise pymssql.IntegrityError(2627, "PK violation")

    def test_internal_error_is_not_wrapped(self):
        """Internal errors (programming/data contract) are not transient."""
        with self.assertRaises(pymssql.InternalError):
            with mssql_connection_retryable():
                raise pymssql.InternalError("bad internal state")

    def test_unrelated_exception_passthrough(self):
        """Non-pymssql errors flow through the wrapper untouched."""
        with self.assertRaises(ValueError):
            with mssql_connection_retryable():
                raise ValueError("unrelated")

    def test_operational_error_becomes_user_error_in_interactive_path(self):
        """When the adapter is called from the interactive path the outer
        ``api_handle_errors`` context must still surface a UserError
        (first clause catches ``NetworkRetryableError`` and translates)."""
        with self.assertRaises(UserError):
            with api_handle_errors("Connection failed"):
                with mssql_connection_retryable():
                    raise pymssql.OperationalError(
                        "(20003) General SQL Server error: connection failed"
                    )

    def test_cause_chain_preserved(self):
        """The original pymssql error must be preserved in ``__cause__``
        so the queue_job exc_info keeps the forensic trail."""
        try:
            with mssql_connection_retryable():
                raise pymssql.OperationalError("(6005) SHUTDOWN is in progress")
        except NetworkRetryableError as err:
            self.assertIsInstance(err.__cause__, pymssql.OperationalError)
        else:
            self.fail("NetworkRetryableError was not raised")

    def test_unreachable_backend_raises_retryable_via_adapter(self):
        """End-to-end: an adapter pointed at an unreachable MSSQL host must
        surface ``NetworkRetryableError``, not a raw pymssql exception — so
        the queue_job worker applies the configured ``retry_pattern``
        instead of failing on the first attempt."""
        backend = self.env["oxigesti.backend"].create(
            {
                "name": "Test unreachable",
                "server": "127.0.0.1",
                "port": 1,
                "database": "irrelevant",
                "schema": "dbo",
                "username": "irrelevant",
                "password": "irrelevant",
                "lang_id": self.env.ref("base.lang_en").id,
                "tz": "UTC",
                "chunk_size": 0,
            }
        )
        with backend.work_on("oxigesti.backend") as work:
            component = work.component_by_name(name="oxigesti.adapter.test")
            with self.assertRaises(NetworkRetryableError):
                component.get_version()
