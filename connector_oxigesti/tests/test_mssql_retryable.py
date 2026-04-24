# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import pymssql

from odoo import _
from odoo.exceptions import UserError, ValidationError
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

    def _make_unreachable_backend(self):
        return self.env["oxigesti.backend"].create(
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

    # --- contract of the contextmanager itself -------------------------

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

    def test_programming_error_is_not_wrapped(self):
        """Programming errors (bad SQL, missing columns, etc.) must not
        be silently retried — they need fixing, not retrying."""
        with self.assertRaises(pymssql.ProgrammingError):
            with mssql_connection_retryable():
                raise pymssql.ProgrammingError("invalid column name")

    def test_database_error_base_class_is_not_wrapped(self):
        """The wrapper is deliberately narrow: it catches the concrete
        transient classes (``OperationalError``, ``InterfaceError``) and
        lets the ``DatabaseError`` base class flow through, so any future
        data-integrity / data-truncation error raised as bare
        ``DatabaseError`` is not accidentally converted to a retry."""
        with self.assertRaises(pymssql.DatabaseError):
            with mssql_connection_retryable():
                raise pymssql.DatabaseError("ambiguous error")

    def test_unrelated_exception_passthrough(self):
        """Non-pymssql errors flow through the wrapper untouched."""
        with self.assertRaises(ValueError):
            with mssql_connection_retryable():
                raise ValueError("unrelated")

    def test_no_exception_no_side_effects(self):
        """Happy path: the contextmanager must be transparent when no
        exception is raised."""
        marker = []
        with mssql_connection_retryable():
            marker.append("ok")
        self.assertEqual(marker, ["ok"])

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

    # --- production-observed error variants (task #2548, 2026-04-13) ---

    def test_error_variant_adaptive_server_unavailable(self):
        """66 of the 120 failed jobs had this exact variant."""
        with self.assertRaises(NetworkRetryableError):
            with mssql_connection_retryable():
                raise pymssql.OperationalError(
                    2,
                    b"Adaptive Server is unavailable or does not exist "
                    b"(SV-BCN-SC-SQ-0S) / Connection refused (111)",
                )

    def test_error_variant_general_sql_server_error(self):
        """50 of the 120 failed jobs had this exact variant."""
        with self.assertRaises(NetworkRetryableError):
            with mssql_connection_retryable():
                raise pymssql.OperationalError(
                    20003,
                    b"General SQL Server error: Check messages... "
                    b"Adaptive Server connection failed",
                )

    def test_error_variant_read_from_server_failed(self):
        """Unexpected EOF during an in-flight read."""
        with self.assertRaises(NetworkRetryableError):
            with mssql_connection_retryable():
                raise pymssql.OperationalError(20004, b"Read from the server failed")

    def test_error_variant_shutdown_in_progress(self):
        """The MSSQL SHUTDOWN window (2026-04-13 06:30)."""
        with self.assertRaises(NetworkRetryableError):
            with mssql_connection_retryable():
                raise pymssql.OperationalError(6005, b"SHUTDOWN is in progress")

    # --- interactive path (api_handle_errors) regressions --------------

    def test_operational_error_becomes_user_error_in_interactive_path(self):
        """When the adapter is called from the interactive path the outer
        ``api_handle_errors`` context must still surface a UserError
        (its first clause catches ``NetworkRetryableError`` and translates)."""
        with self.assertRaises(UserError):
            with api_handle_errors("Connection failed"):
                with mssql_connection_retryable():
                    raise pymssql.OperationalError(
                        "(20003) General SQL Server error: connection failed"
                    )

    def test_integrity_error_still_user_error_in_interactive_path(self):
        """Non-transient integrity errors must still surface a UserError
        on the interactive path (``api_handle_errors`` has a dedicated
        clause for them)."""
        with self.assertRaises(UserError):
            with api_handle_errors("Operation failed"):
                with mssql_connection_retryable():
                    raise pymssql.IntegrityError(2627, "PK violation")

    # --- end-to-end: real adapter path against unreachable host --------

    def test_unreachable_backend_get_version_raises_retryable(self):
        """An adapter pointed at an unreachable MSSQL host must surface
        ``NetworkRetryableError`` from ``get_version()`` — exercises
        ``_exec_query`` → ``_exec_sql`` → ``pymssql.connect`` → wrap."""
        backend = self._make_unreachable_backend()
        with backend.work_on("oxigesti.backend") as work:
            component = work.component_by_name(name="oxigesti.adapter.test")
            with self.assertRaises(NetworkRetryableError):
                component.get_version()

    def test_unreachable_backend_check_connection_raises_user_error(self):
        """``button_check_connection`` is an interactive path: an unreachable
        host must surface a ``UserError`` (``api_handle_errors`` wraps our
        ``NetworkRetryableError``)."""
        backend = self._make_unreachable_backend()
        with self.assertRaises(UserError):
            backend._check_connection()

    def test_unreachable_backend_write_raises_retryable(self):
        """``write`` starts by calling ``_exec_sql`` for the schema check,
        which goes through the wrapper — this proves the write call-path
        surfaces ``NetworkRetryableError`` instead of a raw pymssql
        exception when the host is unreachable."""
        backend = self._make_unreachable_backend()
        with backend.work_on("oxigesti.backend") as work:
            component = work.component_by_name(name="oxigesti.adapter.test")
            with self.assertRaises(NetworkRetryableError):
                component.write([1], {"some_field": "x"})

    def test_unreachable_backend_delete_raises_retryable(self):
        """Same as above for ``delete``: the schema-check ``_exec_sql``
        call at the top of ``delete`` surfaces ``NetworkRetryableError``
        when the host is unreachable."""
        backend = self._make_unreachable_backend()
        with backend.work_on("oxigesti.backend") as work:
            component = work.component_by_name(name="oxigesti.adapter.test")
            with self.assertRaises(NetworkRetryableError):
                component.delete([1])

    # --- guard on write/delete count mismatch paths --------------------
    #
    # The wrapping in write() and delete() must not swallow the
    # count-mismatch integrity checks. Both "count=0 => not found" and
    # "count>1 => duplicate" paths raise exceptions inside the
    # ``mssql_connection_retryable`` block; those exceptions are NOT
    # ``OperationalError`` / ``InterfaceError`` and must propagate.

    def test_count_zero_not_wrapped(self):
        """A generic Exception raised inside the wrapper must propagate
        as-is — covers the ``count == 0`` path in write/delete."""
        with self.assertRaises(Exception) as ctx:
            with mssql_connection_retryable():
                raise Exception("Impossible to update external record")
        # Must be the raw Exception, not NetworkRetryableError.
        self.assertNotIsInstance(ctx.exception, NetworkRetryableError)

    def test_count_above_one_integrity_error_not_wrapped(self):
        """A duplicate-row IntegrityError raised inside the wrapper
        must propagate as-is — covers the ``count > 1`` path in
        write/delete."""
        with self.assertRaises(pymssql.IntegrityError):
            with mssql_connection_retryable():
                raise pymssql.IntegrityError(
                    "Unexpected error: Returned more the one row with ID: ..."
                )

    # --- guard on create()'s IntegrityError 2627 workaround -------------
    #
    # create() has a specific ``except pymssql.IntegrityError`` that converts
    # error code 2627 (PK violation on varchar with trailing spaces) into a
    # ``ValidationError`` with a user-friendly message. My wrapping is on
    # ``_exec_sql`` (inside create), not on create itself, so this workaround
    # must keep working unchanged.

    def test_integrity_error_2627_still_raises_validation_error(self):
        """Replays the create() flow: IntegrityError(2627) from _exec_sql
        must still be caught by create() and re-raised as ValidationError."""
        try:
            try:
                with mssql_connection_retryable():
                    raise pymssql.IntegrityError(2627, "trailing-space PK")
            except pymssql.IntegrityError as e:
                if e.args[0] == 2627:
                    raise ValidationError(_("fake PK violation"))
                raise
        except ValidationError:
            pass
        else:
            self.fail("ValidationError was not raised")

    def test_integrity_error_non_2627_still_reraises(self):
        """A non-2627 IntegrityError inside _exec_sql must still reach
        create()'s bare ``raise`` branch unchanged — not silently retried."""
        try:
            try:
                with mssql_connection_retryable():
                    raise pymssql.IntegrityError(547, "FK violation")
            except pymssql.IntegrityError as e:
                if e.args[0] == 2627:
                    raise ValidationError(_("fake PK"))
                raise
        except pymssql.IntegrityError as err:
            self.assertEqual(err.args[0], 547)
        else:
            self.fail("IntegrityError was not re-raised")

    # --- paranoia: wrapper must NOT re-raise from its own cleanup -------

    def test_nested_wrapper_does_not_double_wrap(self):
        """Nesting the wrapper (defensive in case helper code uses it
        internally) must surface a single NetworkRetryableError, not a
        re-wrapped one — contextmanager catches only pymssql classes."""
        try:
            with mssql_connection_retryable():
                with mssql_connection_retryable():
                    raise pymssql.OperationalError("transient")
        except NetworkRetryableError as err:
            # The inner wrapper raised NetworkRetryableError, the outer
            # saw it, did NOT recognize it as pymssql.OperationalError
            # (it's not one), and let it bubble — not a double wrap.
            self.assertNotIsInstance(err.__cause__, NetworkRetryableError)
        else:
            self.fail("NetworkRetryableError was not raised")
