# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import traceback
from datetime import date, datetime
from unittest import mock

import pymssql
from pymssql import _mssql

from odoo.exceptions import UserError
from odoo.tests.common import tagged

from odoo.addons.connector_sage.components.adapter import GenericAdapter
from odoo.addons.queue_job.controllers.main import RunJobController
from odoo.addons.queue_job.delay import chain
from odoo.addons.queue_job.job import Job
from odoo.addons.queue_job.tests.common import trap_jobs

from .common import (
    ADAPTER_EXEC_SQL,
    ADAPTER_READ,
    ADAPTER_SEARCH,
    AGREEMENT_CODE,
    AGREEMENT_DATE,
    CHECK,
    CODE,
    CONCEPT,
    PAYROLL_LINE,
    PROCESS,
    SAGE_COMPANY,
    TRANSFER_LINE,
    SagePayslipCase,
)

# the adapter's own search, which the test case replaces with the fake Sage
REAL_SEARCH = GenericAdapter.search

MARIA = 603

MARIA_WORKER = {
    "CodigoEmpresa": SAGE_COMPANY,
    "CodigoEmpleado": MARIA,
    "SiglaNacion": "XX",
    "Dni": "WORKER03B",
    "NombreEmpleado": "MARIA",
    "PrimerApellidoEmpleado": "SOLER",
    "SegundoApellidoEmpleado": "VIDAL",
    "NumeroHijos": 0,
    "FechaNacimiento": False,
    "Email1": "maria@test.example.com",
    "Email2": "maria@test.example.com",
}

JOAN_JANUARY_PAYROLL_LINE = {
    "CodigoEmpresa": SAGE_COMPANY,
    "Año": 2026,
    "MesD": 1,
    "TipoProceso": PROCESS,
    "CodigoEmpleado": CODE,
    "CodigoConceptoNom": CONCEPT,
    "CodigoConvenio": AGREEMENT_CODE,
    "FechaRegistroCV": AGREEMENT_DATE,
    "ConceptoLargo": "SALARIO BASE",
    "ImporteNom": 1000.0,
}

JOAN_FEBRUARY_PAYROLL_LINE = {
    "CodigoEmpresa": SAGE_COMPANY,
    "Año": 2026,
    "MesD": 2,
    "TipoProceso": PROCESS,
    "CodigoEmpleado": CODE,
    "CodigoConceptoNom": CONCEPT,
    "CodigoConvenio": AGREEMENT_CODE,
    "FechaRegistroCV": AGREEMENT_DATE,
    "ConceptoLargo": "SALARIO BASE",
    "ImporteNom": 1100.0,
}

JOAN_JANUARY_LINE = {
    "CodigoEmpresa": SAGE_COMPANY,
    "Año": 2026,
    "MesD": 1,
    "TipoProceso": PROCESS,
    "CodigoEmpleado": CODE,
    "CodigoConceptoNom": CONCEPT,
    "CodigoConvenio": AGREEMENT_CODE,
    "FechaRegistroCV": AGREEMENT_DATE,
    "FechaCobro": datetime(2026, 1, 31),
    "ConceptoLargo": "SALARIO BASE",
    "ImporteNom": 1000.0,
}

JOAN_FEBRUARY_LINE = {
    "CodigoEmpresa": SAGE_COMPANY,
    "Año": 2026,
    "MesD": 2,
    "TipoProceso": PROCESS,
    "CodigoEmpleado": CODE,
    "CodigoConceptoNom": CONCEPT,
    "CodigoConvenio": AGREEMENT_CODE,
    "FechaRegistroCV": AGREEMENT_DATE,
    "FechaCobro": datetime(2026, 2, 28),
    "ConceptoLargo": "SALARIO BASE",
    "ImporteNom": 1100.0,
}

MARIA_JANUARY_LINE = {
    "CodigoEmpresa": SAGE_COMPANY,
    "Año": 2026,
    "MesD": 1,
    "TipoProceso": PROCESS,
    "CodigoEmpleado": MARIA,
    "CodigoConceptoNom": CONCEPT,
    "CodigoConvenio": AGREEMENT_CODE,
    "FechaRegistroCV": AGREEMENT_DATE,
    "FechaCobro": datetime(2026, 1, 15),
    "ConceptoLargo": "SALARIO BASE",
    "ImporteNom": 800.0,
}

JOAN_JANUARY_CHECK = {
    "CodigoEmpresa": SAGE_COMPANY,
    "CodigoEmpleado": CODE,
    "Año": 2026,
    "MesD": 1,
    "TipoProceso": PROCESS,
    "IdEmpleado": "WORKER-602",
    "OrdenNom": 1,
    "Importe": 900.0,
    "FechaBaja": datetime(3000, 12, 31),
}

JOAN_FEBRUARY_CHECK = {
    "CodigoEmpresa": SAGE_COMPANY,
    "CodigoEmpleado": CODE,
    "Año": 2026,
    "MesD": 2,
    "TipoProceso": PROCESS,
    "IdEmpleado": "WORKER-602",
    "OrdenNom": 1,
    "Importe": 950.0,
    "FechaBaja": datetime(3000, 12, 31),
}

MARIA_JANUARY_CHECK = {
    "CodigoEmpresa": SAGE_COMPANY,
    "CodigoEmpleado": MARIA,
    "Año": 2026,
    "MesD": 1,
    "TipoProceso": PROCESS,
    "IdEmpleado": "WORKER-603",
    "OrdenNom": 1,
    "Importe": 700.0,
    "FechaBaja": datetime(3000, 12, 31),
}

SAGE = {
    PAYROLL_LINE: [JOAN_JANUARY_PAYROLL_LINE, JOAN_FEBRUARY_PAYROLL_LINE],
    TRANSFER_LINE: [JOAN_JANUARY_LINE, JOAN_FEBRUARY_LINE, MARIA_JANUARY_LINE],
    CHECK: [JOAN_JANUARY_CHECK, JOAN_FEBRUARY_CHECK, MARIA_JANUARY_CHECK],
}

POSTED_IMPORT = r"A posted payslip cannot be imported \(January\)\."
FILTER_CHANGED = (
    r"Payslip January holds lines or checks that Sage still has but that its "
    r"filter no longer selects"
)
FILTER_CHANGED_PAYROLL = FILTER_CHANGED + (
    r"\. Its year, months, labour agreement or process may have changed since "
    r"it was imported\. Nothing has been imported\."
)
FILTER_CHANGED_TRANSFER = FILTER_CHANGED + (
    r"\. Its year, months, labour agreement, process or payment date may have "
    r"changed since it was imported, or Sage may have moved a line to another "
    r"payment date\. Nothing has been imported\."
)
POST_WAITS = (
    r"A payslip cannot be posted while its import has jobs queued, running or "
    r"failed \(January\)\."
)
LAST_IMPORT_FAILED = (
    r"A payslip cannot be posted while its last import has failed\. Fix the "
    r"cause and import it again, or have a queue job manager cancel the "
    r"failed job to post the payslip as it is:\n"
)
FAILED_WITHOUT_DETAIL = (
    r"January: the import failed; a queue job manager can see why in the "
    r"failed job\Z"
)
# what pymssql 2.2.11 raises when Sage cannot be reached: the error's number
# and its text, which names the server
SAGE_UNREACHABLE = (
    20009,
    b"DB-Lib error message 20009, severity 9:\nUnable to connect: Adaptive "
    b"Server is unavailable or does not exist (sage.test)\n",
)
LOCKED = (
    r"Lines and checks of a posted payslip cannot be created, changed or "
    r"deleted \(January\)\."
)
NOT_IN_SAGE = (
    r"This line or check is no longer in Sage\. Import its payslip again and "
    r"cancel this job\."
)


@tagged("post_install", "-at_install")
class TestPayslipImportConsistency(SagePayslipCase):
    sage = SAGE

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # posting needs accounts on the wage type: a tag to the debit and
        # another to the credit, for each type of payslip
        account = cls.env["account.account"].create(
            {
                "name": "Test Salaries",
                "code": "TESTSAL02",
                "user_type_id": cls.env.ref("account.data_account_type_expenses").id,
                "company_id": cls.company.id,
            }
        )
        tags = cls.env["payroll.sage.wage.tag"]
        for payslip_type in ("payroll", "transfer"):
            for credit_debit in ("debit", "credit"):
                tags |= cls.env["payroll.sage.wage.tag"].create(
                    {
                        "type": payslip_type,
                        "account_id": account.id,
                        "credit_debit": credit_debit,
                        "aggregate": True,
                        "company_id": cls.company.id,
                    }
                )
        cls.wage_type_line.wage_tag_ids = tags
        with mock.patch(ADAPTER_READ, return_value=dict(MARIA_WORKER)):
            cls.env["sage.hr.employee"].import_record(
                cls.backend, (SAGE_COMPANY, MARIA)
            )

    def _store_as_failed(self, queue_job, error):
        """Store the job as failed with the error it raised and write it to the
        database, with the values the job runner stores after the job raised."""
        job = Job.load(self.env, queue_job.uuid)
        traceback_txt = "".join(
            traceback.format_exception(type(error), error, error.__traceback__)
        )
        job.set_failed(
            **RunJobController()._get_failure_values(job, traceback_txt, error)
        )
        job.store()
        self.env["queue.job"].flush()

    def _import_failing(self, payslip, error):
        """Import the payslip while reading Sage raises the error: its batch
        job fails before writing anything, and is stored as failed."""
        queue = self.env["queue.job"]
        last_id = queue.search([], order="id desc", limit=1).id or 0
        payslip.action_paysplip_import()
        batch_job = queue.search([("id", ">", last_id)])
        with mock.patch(ADAPTER_SEARCH, side_effect=error):
            with self.assertRaises(type(error)):
                Job.load(self.env, batch_job.uuid).perform()
        self._store_as_failed(batch_job, error)
        return batch_job

    def test_posted_payslip_is_not_imported(self):
        """The import of a posted payslip is refused before Sage is read, and
        no job is queued."""
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        january.action_paysplip_post()
        with trap_jobs() as trap:
            with self.assertRaisesRegex(UserError, POSTED_IMPORT):
                january.action_paysplip_import()
            trap.assert_jobs_count(0)

    def test_backend_line_import_refuses_posted_payslip(self):
        """The backend's Import Payslip Lines button refuses the posted
        payslip selected there, and queues no job."""
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        january.action_paysplip_post()
        self.backend.import_payslip_line_id = january
        with trap_jobs() as trap:
            with self.assertRaisesRegex(UserError, POSTED_IMPORT):
                self.backend.import_payslip_lines()
            trap.assert_jobs_count(0)

    def test_backend_check_import_refuses_posted_payslip(self):
        """The backend's Import Payslip Checks button refuses the posted
        payslip selected there, and queues no job."""
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        january.action_paysplip_post()
        self.backend.import_payslip_check_id = january
        with trap_jobs() as trap:
            with self.assertRaisesRegex(UserError, POSTED_IMPORT):
                self.backend.import_payslip_checks()
            trap.assert_jobs_count(0)

    def test_import_queued_before_posting_is_refused(self):
        """An import queued before its payslip is posted, as one queued by an
        older version of the connector, refuses the posted payslip when it
        runs, before it reads Sage, and queues no job."""
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        with trap_jobs() as trap:
            january.action_paysplip_import()
            january.action_paysplip_post()
            with self.assertRaisesRegex(UserError, POSTED_IMPORT):
                trap.perform_enqueued_jobs()
            trap.assert_jobs_count(0)

    def test_line_and_check_removed_from_sage_are_deleted(self):
        """Sage removes Joan's line and check of January between two imports
        of the same transfer: the second import deletes them, with their
        bindings."""
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        line_binding = january.payslip_line_ids.sage_transfer_bind_ids
        check_binding = january.payslip_check_ids.sage_bind_ids
        with mock.patch.dict(
            SAGE,
            {
                TRANSFER_LINE: [JOAN_FEBRUARY_LINE, MARIA_JANUARY_LINE],
                CHECK: [JOAN_FEBRUARY_CHECK, MARIA_JANUARY_CHECK],
            },
        ):
            with trap_jobs() as trap:
                january.action_paysplip_import()
                self._run_jobs(trap)
        self.assertFalse(january.payslip_line_ids)
        self.assertFalse(january.payslip_check_ids)
        self.assertFalse(line_binding.exists())
        self.assertFalse(check_binding.exists())

    def test_payroll_line_removed_from_sage_is_deleted(self):
        """Sage removes Joan's payroll line of January between two imports of
        the same payslip: the second import deletes it, with its binding."""
        january = self._create_payslip("payroll", 1, 1, name="January")
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        binding = january.payslip_line_ids.sage_payroll_bind_ids
        with mock.patch.dict(SAGE, {PAYROLL_LINE: [JOAN_FEBRUARY_PAYROLL_LINE]}):
            with trap_jobs() as trap:
                january.action_paysplip_import()
                self._run_jobs(trap)
        self.assertFalse(january.payslip_line_ids)
        self.assertFalse(binding.exists())

    def test_only_the_lines_removed_from_sage_are_deleted(self):
        """A transfer of January without payment date holds Joan's lines of
        31/01 and of 15/01 and Maria's of 15/01. Sage removes Joan's of 31/01
        and Maria's: the import deletes those two and keeps Joan's of 15/01,
        which Sage still has, without taking it for a line its filter no
        longer selects."""
        joan_january_15_line = {
            "CodigoEmpresa": SAGE_COMPANY,
            "Año": 2026,
            "MesD": 1,
            "TipoProceso": PROCESS,
            "CodigoEmpleado": CODE,
            "CodigoConceptoNom": CONCEPT,
            "CodigoConvenio": AGREEMENT_CODE,
            "FechaRegistroCV": AGREEMENT_DATE,
            "FechaCobro": datetime(2026, 1, 15),
            "ConceptoLargo": "SALARIO BASE",
            "ImporteNom": 200.0,
        }
        january = self._create_payslip("transfer", 1, 1, name="January")
        with mock.patch.dict(
            SAGE,
            {
                TRANSFER_LINE: [
                    JOAN_JANUARY_LINE,
                    MARIA_JANUARY_LINE,
                    joan_january_15_line,
                ],
                CHECK: [],
            },
        ):
            with trap_jobs() as trap:
                january.action_paysplip_import()
                self._run_jobs(trap)
        self.assertEqual(
            january.payslip_line_ids.mapped("amount"), [1000.0, 800.0, 200.0]
        )
        with mock.patch.dict(SAGE, {TRANSFER_LINE: [joan_january_15_line], CHECK: []}):
            with trap_jobs() as trap:
                january.action_paysplip_import()
                self._run_jobs(trap)
        self.assertEqual(january.payslip_line_ids.mapped("amount"), [200.0])

    def test_import_after_months_moved_to_empty_month_is_refused(self):
        """January is imported, then its months are moved to March, which
        Sage has nothing for: the import is refused, because Sage still has
        the line and the check the payslip holds, and it writes nothing."""
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        january.action_paysplip_set_to_draft()
        january.write({"month_from": 3, "month_to": 3})
        january.action_paysplip_validate()
        with trap_jobs() as trap:
            january.action_paysplip_import()
            with self.assertRaisesRegex(UserError, FILTER_CHANGED):
                trap.perform_enqueued_jobs()
            trap.assert_jobs_count(0)
        self.assertEqual(
            january.payslip_line_ids.sage_transfer_bind_ids.mapped("sage_mesd"), [1]
        )
        self.assertEqual(
            january.payslip_check_ids.sage_bind_ids.mapped("sage_mesd"), [1]
        )

    def test_import_after_months_narrowed_is_refused(self):
        """A payslip of January and February is imported, then narrowed to
        February: the import reads February's line, but Sage still has the
        January line the payslip holds, so it is refused and writes nothing,
        not even February's new amount."""
        winter = self._create_payslip("payroll", 1, 2, name="Winter")
        with trap_jobs() as trap:
            winter.action_paysplip_import()
            self._run_jobs(trap)
        winter.action_paysplip_set_to_draft()
        winter.month_from = 2
        winter.action_paysplip_validate()
        with mock.patch.dict(JOAN_FEBRUARY_PAYROLL_LINE, {"ImporteNom": 1500.0}):
            with trap_jobs() as trap:
                winter.action_paysplip_import()
                with self.assertRaisesRegex(
                    UserError,
                    r"Payslip Winter holds lines or checks that Sage still has but "
                    r"that its filter no longer selects",
                ):
                    trap.perform_enqueued_jobs()
                trap.assert_jobs_count(0)
        self.assertEqual(
            winter.payslip_line_ids.sage_payroll_bind_ids.mapped("sage_mesd"), [1, 2]
        )
        self.assertEqual(winter.payslip_line_ids.mapped("amount"), [1000.0, 1100.0])

    def test_import_after_payment_date_changed_is_refused(self):
        """January is imported with the payment date 31/01, then the date is
        changed to 15/01: the import reads Maria's line and check of that
        date, but Sage still has Joan's line and check the payslip holds, so
        it is refused and writes nothing."""
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        january.action_paysplip_set_to_draft()
        january.payment_date = date(2026, 1, 15)
        january.action_paysplip_validate()
        with trap_jobs() as trap:
            january.action_paysplip_import()
            with self.assertRaisesRegex(UserError, FILTER_CHANGED_TRANSFER):
                trap.perform_enqueued_jobs()
            trap.assert_jobs_count(0)
        self.assertEqual(
            january.payslip_line_ids.sage_transfer_bind_ids.mapped(
                "sage_codigo_empleado"
            ),
            [CODE],
        )
        self.assertEqual(
            january.payslip_check_ids.sage_bind_ids.mapped("sage_codigo_empleado"),
            [CODE],
        )

    def test_import_after_agreement_changed_is_refused(self):
        """January is imported, then its labour agreement is changed to one
        that Sage has nothing for: the import is refused, because Sage still
        has the line the payslip holds, and it writes nothing."""
        other_agreement = self.env["payroll.sage.labour.agreement"].create(
            {
                "name": "OTHER AGREEMENT",
                "code": 92,
                "registration_date_cv": date(2020, 1, 1),
                "company_id": self.company.id,
            }
        )
        january = self._create_payslip("payroll", 1, 1, name="January")
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        january.action_paysplip_set_to_draft()
        january.labour_agreement_id = other_agreement
        january.action_paysplip_validate()
        with trap_jobs() as trap:
            january.action_paysplip_import()
            with self.assertRaisesRegex(UserError, FILTER_CHANGED_PAYROLL):
                trap.perform_enqueued_jobs()
            trap.assert_jobs_count(0)
        self.assertEqual(
            january.payslip_line_ids.sage_payroll_bind_ids.mapped(
                "sage_codigo_convenio"
            ),
            [AGREEMENT_CODE],
        )

    def test_import_after_process_changed_is_refused(self):
        """January is imported, then its process is changed to one that Sage
        has nothing for: the import is refused, because Sage still has the
        line and the check the payslip holds, and it writes nothing."""
        other_process = self.env["payroll.sage.payslip.process"].create(
            {"name": "OTHER-DEST"}
        )
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        january.action_paysplip_set_to_draft()
        january.process_id = other_process
        january.action_paysplip_validate()
        with trap_jobs() as trap:
            january.action_paysplip_import()
            with self.assertRaisesRegex(UserError, FILTER_CHANGED):
                trap.perform_enqueued_jobs()
            trap.assert_jobs_count(0)
        self.assertEqual(
            january.payslip_line_ids.sage_transfer_bind_ids.mapped("sage_tipo_proceso"),
            [PROCESS],
        )
        self.assertEqual(
            january.payslip_check_ids.sage_bind_ids.mapped("sage_tipo_proceso"),
            [PROCESS],
        )

    def test_import_after_months_widened_adds_new_lines(self):
        """January is imported, then widened to January and February: the
        filter still selects January's line, so the import goes on and adds
        February's."""
        january = self._create_payslip("payroll", 1, 1, name="January")
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        january.action_paysplip_set_to_draft()
        january.month_to = 2
        january.action_paysplip_validate()
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        self.assertEqual(
            january.payslip_line_ids.sage_payroll_bind_ids.mapped("sage_mesd"), [1, 2]
        )

    def test_query_in_sage_selects_the_checks_by_the_transfer_lines(self):
        """January, a transfer paid on 31/01, imports its checks from the
        backend. The query that asks Sage for them keeps the checks whose
        employee has a transfer line of the same company, year, month and
        process with January's agreement and payment date, and pymssql, which
        formats the query before sending it, puts each value of the filter in
        its place."""
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        queries = []

        def send_to_sage(adapter, sql, params, as_dict=False):
            # format the query as pymssql does before sending it; the schema
            # exists and Sage answers no record
            queries.append(_mssql.substitute_params(sql, params).decode())
            return [(1,)] if "sys.schemas" in sql else []

        self.backend.import_payslip_check_id = january
        with mock.patch(ADAPTER_SEARCH, REAL_SEARCH), mock.patch(
            ADAPTER_EXEC_SQL, autospec=True, side_effect=send_to_sage
        ):
            with trap_jobs() as trap:
                self.backend.import_payslip_checks()
                trap.perform_enqueued_jobs()
        self.assertIn(
            "select * from t where CodigoEmpresa = 99 and Año = 2026 and "
            "MesD between 1 and 1 and TipoProceso = N'TEST-DEST' and "
            "exists (select 1 from (",
            queries[-1],
        )
        self.assertIn(
            ") l where l.CodigoEmpresa = t.CodigoEmpresa and "
            "l.CodigoEmpleado = t.CodigoEmpleado and l.Año = t.Año and "
            "l.MesD = t.MesD and l.TipoProceso = t.TipoProceso and "
            "l.CodigoConvenio = 91 and l.FechaRegistroCV = '2020-01-01' and "
            "l.FechaCobro = '2026-01-31')",
            queries[-1],
        )

    def test_failed_sage_read_deletes_nothing(self):
        """Sage removes January's line, but the next import cannot read Sage:
        the import fails and the line stays."""
        january = self._create_payslip("payroll", 1, 1, name="January")
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        line = january.payslip_line_ids
        with mock.patch.dict(SAGE, {PAYROLL_LINE: [JOAN_FEBRUARY_PAYROLL_LINE]}):
            with trap_jobs() as trap:
                january.action_paysplip_import()
                with mock.patch(
                    ADAPTER_SEARCH,
                    side_effect=pymssql.OperationalError("Unable to connect to Sage"),
                ):
                    with self.assertRaisesRegex(
                        pymssql.OperationalError, "Unable to connect to Sage"
                    ):
                        trap.perform_enqueued_jobs()
                trap.assert_jobs_count(0)
        self.assertEqual(january.payslip_line_ids, line)

    def test_line_and_check_made_by_hand_are_kept(self):
        """A line and a check added by hand to January stay when its import
        deletes the line and the check that Sage removed."""
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        joan = january.payslip_line_ids.employee_id
        hand_line = self.env["payroll.sage.payslip.line"].create(
            {
                "name": "PLUS",
                "wage_type_line_id": self.wage_type_line.odoo_id.id,
                "employee_id": joan.id,
                "amount": 50.0,
                "payslip_id": january.id,
            }
        )
        hand_check = self.env["payroll.sage.payslip.check"].create(
            {"employee_id": joan.id, "amount": 40.0, "payslip_id": january.id}
        )
        with mock.patch.dict(
            SAGE,
            {
                TRANSFER_LINE: [JOAN_FEBRUARY_LINE, MARIA_JANUARY_LINE],
                CHECK: [JOAN_FEBRUARY_CHECK, MARIA_JANUARY_CHECK],
            },
        ):
            with trap_jobs() as trap:
                january.action_paysplip_import()
                self._run_jobs(trap)
        self.assertEqual(january.payslip_line_ids, hand_line)
        self.assertEqual(january.payslip_check_ids, hand_check)

    def test_post_waits_for_the_import(self):
        """Post is refused while the batch of the import waits in the queue,
        and then while the jobs of its line and its check do, and it is
        allowed once they are all done."""
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        queue = self.env["queue.job"]
        last_id = queue.search([], order="id desc", limit=1).id or 0
        january.action_paysplip_import()
        batch_job = queue.search([("id", ">", last_id)])
        self.assertEqual(len(batch_job), 1)
        with self.assertRaisesRegex(UserError, POST_WAITS):
            january.action_paysplip_post()
        Job.load(self.env, batch_job.uuid).perform()
        batch_job.button_done()
        record_jobs = queue.search([("id", ">", batch_job.id)])
        self.assertEqual(len(record_jobs), 2)
        with self.assertRaisesRegex(UserError, POST_WAITS):
            january.action_paysplip_post()
        for record_job in record_jobs:
            Job.load(self.env, record_job.uuid).perform()
        record_jobs.button_done()
        january.action_paysplip_post()
        self.assertEqual(january.state, "posted")

    def test_post_waits_while_the_import_is_enqueued_and_running(self):
        """The job runner hands the batch of January's import to a worker,
        which starts it: Post is refused while the job is enqueued and while
        it runs."""
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        queue = self.env["queue.job"]
        last_id = queue.search([], order="id desc", limit=1).id or 0
        january.action_paysplip_import()
        batch_job = queue.search([("id", ">", last_id)])
        job = Job.load(self.env, batch_job.uuid)
        job.set_enqueued()
        job.store()
        with self.assertRaisesRegex(UserError, POST_WAITS):
            january.action_paysplip_post()
        job.set_started()
        job.store()
        with self.assertRaisesRegex(UserError, POST_WAITS):
            january.action_paysplip_post()

    def test_post_waits_while_the_import_waits_for_another_job(self):
        """January's import is chained after an import of the employees, as
        another module can chain jobs: the batch of the import waits for that
        job, and Post is refused meanwhile."""
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        chain(
            self.env["sage.hr.employee"].delayable().import_batch(self.backend),
            self.env[TRANSFER_LINE]
            .delayable()
            .import_payslip_lines_and_checks(january, self.backend),
        ).delay()
        with self.assertRaisesRegex(UserError, POST_WAITS):
            january.action_paysplip_post()

    def test_post_by_a_payroll_user_waits_for_the_import(self):
        """A payroll user who cannot read the queue posts January: Post is
        refused while its import waits in the queue, and allowed once the
        import is done."""
        user = self.env["res.users"].create(
            {
                "name": "Payroll User",
                "login": "payroll_user",
                "company_id": self.company.id,
                "company_ids": [(6, 0, [self.company.id])],
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("payroll_sage.group_user").id,
                            self.env.ref("account.group_account_invoice").id,
                        ],
                    )
                ],
            }
        )
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        queue = self.env["queue.job"]
        last_id = queue.search([], order="id desc", limit=1).id or 0
        january.action_paysplip_import()
        batch_job = queue.search([("id", ">", last_id)])
        with self.assertRaisesRegex(UserError, POST_WAITS):
            january.with_user(user).action_paysplip_post()
        Job.load(self.env, batch_job.uuid).perform()
        batch_job.button_done()
        record_jobs = queue.search([("id", ">", batch_job.id)])
        for record_job in record_jobs:
            Job.load(self.env, record_job.uuid).perform()
        record_jobs.button_done()
        january.with_user(user).action_paysplip_post()
        self.assertEqual(january.state, "posted")

    def test_failed_check_job_blocks_post_until_cancelled(self):
        """The job of January's check fails, so the check is missing from the
        payslip: Post is refused until the job is cancelled."""
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        queue = self.env["queue.job"]
        last_id = queue.search([], order="id desc", limit=1).id or 0
        january.action_paysplip_import()
        batch_job = queue.search([("id", ">", last_id)])
        Job.load(self.env, batch_job.uuid).perform()
        batch_job.button_done()
        line_job = queue.search(
            [("id", ">", batch_job.id), ("model_name", "=", TRANSFER_LINE)]
        )
        check_job = queue.search(
            [("id", ">", batch_job.id), ("model_name", "=", CHECK)]
        )
        Job.load(self.env, line_job.uuid).perform()
        line_job.button_done()
        with mock.patch(
            ADAPTER_READ,
            side_effect=pymssql.OperationalError("Unable to connect to Sage"),
        ):
            with self.assertRaisesRegex(
                pymssql.OperationalError, "Unable to connect to Sage"
            ) as unreachable:
                Job.load(self.env, check_job.uuid).perform()
        self._store_as_failed(check_job, unreachable.exception)
        with self.assertRaisesRegex(UserError, POST_WAITS):
            january.action_paysplip_post()
        check_job.button_cancelled()
        january.action_paysplip_post()
        self.assertEqual(january.state, "posted")

    def test_failed_import_batch_blocks_post(self):
        """January's next import fails before writing anything, as Sage cannot
        be reached, so January keeps the lines of the one before, which Sage
        may no longer have: Post is refused, and says that the import failed
        without pymssql's text, which names the server."""
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        self._import_failing(january, pymssql.OperationalError(SAGE_UNREACHABLE))
        with self.assertRaisesRegex(
            UserError, LAST_IMPORT_FAILED + FAILED_WITHOUT_DETAIL
        ):
            january.action_paysplip_post()
        self.assertEqual(january.state, "validated")

    def test_refused_import_blocks_post_with_its_message(self):
        """January's next import is refused, as its payment date changed: Post
        is refused, and gives the refusal's own message."""
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        january.action_paysplip_set_to_draft()
        january.payment_date = date(2026, 1, 15)
        january.action_paysplip_validate()
        queue = self.env["queue.job"]
        last_id = queue.search([], order="id desc", limit=1).id or 0
        january.action_paysplip_import()
        batch_job = queue.search([("id", ">", last_id)])
        with self.assertRaisesRegex(UserError, FILTER_CHANGED) as refused:
            Job.load(self.env, batch_job.uuid).perform()
        self._store_as_failed(batch_job, refused.exception)
        with self.assertRaisesRegex(
            UserError, LAST_IMPORT_FAILED + "January: " + FILTER_CHANGED
        ):
            january.action_paysplip_post()
        self.assertEqual(january.state, "validated")

    def test_failed_import_batch_without_message_blocks_post(self):
        """January's next import fails with an error of ours that has no
        message: Post is refused, and says only that the import failed."""
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        self._import_failing(january, UserError(""))
        with self.assertRaisesRegex(
            UserError, LAST_IMPORT_FAILED + FAILED_WITHOUT_DETAIL
        ):
            january.action_paysplip_post()
        self.assertEqual(january.state, "validated")

    def test_import_after_a_failed_import_allows_post(self):
        """January's next import fails, and the one after it succeeds: Post
        is allowed again, with no queue job manager."""
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        failed_job = self._import_failing(
            january, pymssql.OperationalError(SAGE_UNREACHABLE)
        )
        january.action_paysplip_import()
        queue = self.env["queue.job"]
        batch_job = queue.search([("id", ">", failed_job.id)])
        Job.load(self.env, batch_job.uuid).perform()
        batch_job.button_done()
        record_jobs = queue.search([("id", ">", batch_job.id)])
        for record_job in record_jobs:
            Job.load(self.env, record_job.uuid).perform()
        record_jobs.button_done()
        january.action_paysplip_post()
        self.assertEqual(january.state, "posted")

    def test_cancelled_failed_import_allows_post(self):
        """January's next import fails, and a queue job manager cancels its
        job to post January as it is: Post is allowed."""
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        failed_job = self._import_failing(
            january, pymssql.OperationalError(SAGE_UNREACHABLE)
        )
        failed_job.button_cancelled()
        january.action_paysplip_post()
        self.assertEqual(january.state, "posted")

    def test_cancelled_later_import_keeps_post_refused(self):
        """January's next import fails, and a queue job manager cancels the
        import after it before it runs: the failed import is still the last
        that ran, so Post is refused."""
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        failed_job = self._import_failing(
            january, pymssql.OperationalError(SAGE_UNREACHABLE)
        )
        january.action_paysplip_import()
        later_job = self.env["queue.job"].search([("id", ">", failed_job.id)])
        later_job.button_cancelled()
        with self.assertRaisesRegex(
            UserError, LAST_IMPORT_FAILED + FAILED_WITHOUT_DETAIL
        ):
            january.action_paysplip_post()
        self.assertEqual(january.state, "validated")

    def test_job_of_deleted_payslip_is_stored_as_failed(self):
        """January is deleted while the job of its line waits in the queue:
        the job fails and is stored as failed."""
        january = self._create_payslip("payroll", 1, 1, name="January")
        queue = self.env["queue.job"]
        last_id = queue.search([], order="id desc", limit=1).id or 0
        january.action_paysplip_import()
        batch_job = queue.search([("id", ">", last_id)])
        Job.load(self.env, batch_job.uuid).perform()
        batch_job.button_done()
        line_job = queue.search([("id", ">", batch_job.id)])
        january.action_paysplip_set_to_draft()
        january.unlink()
        with self.assertRaisesRegex(
            UserError, "This job has no destination payslip"
        ) as failed:
            Job.load(self.env, line_job.uuid).perform()
        self._store_as_failed(line_job, failed.exception)
        self.assertEqual(line_job.state, "failed")

    def test_transfers_of_one_month_get_their_own_checks(self):
        """In January, Joan is paid on 31/01 and Maria on 15/01, each with a
        check. The transfers of January of each date are imported: each one
        gets the check of its employee, and neither import is refused because
        of the other."""
        end = self._create_payslip(
            "transfer", 1, 1, name="January 31", payment_date=date(2026, 1, 31)
        )
        middle = self._create_payslip(
            "transfer", 1, 1, name="January 15", payment_date=date(2026, 1, 15)
        )
        with trap_jobs() as trap:
            end.action_paysplip_import()
            middle.action_paysplip_import()
            self._run_jobs(trap)
        self.assertEqual(
            end.payslip_check_ids.sage_bind_ids.mapped("sage_codigo_empleado"), [CODE]
        )
        self.assertEqual(
            middle.payslip_check_ids.sage_bind_ids.mapped("sage_codigo_empleado"),
            [MARIA],
        )

    def test_line_job_of_payslip_posted_meanwhile_writes_nothing(self):
        """Sage changes the amount of January's line, and January is posted
        while the job that would write it waits in the queue, as a job queued
        by an older version of the connector: the job fails and the line
        keeps its amount."""
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        with mock.patch.dict(JOAN_JANUARY_LINE, {"ImporteNom": 1500.0}):
            with trap_jobs() as trap:
                january.action_paysplip_import()
                # only the batch job: the jobs of the line and the check stay
                # queued
                trap.perform_enqueued_jobs()
                january.action_paysplip_post()
                with self.assertRaisesRegex(UserError, LOCKED):
                    trap.perform_enqueued_jobs()
        self.assertEqual(january.payslip_line_ids.mapped("amount"), [1000.0])

    def test_line_job_of_line_now_in_another_payslip_writes_nothing(self):
        """Two imports race: the batches of January and of Winter both read
        January's line before its job creates it in January. Winter's job of
        that line then fails naming January, and the line keeps the amount
        January's job wrote."""
        january = self._create_payslip("payroll", 1, 1, name="January")
        winter = self._create_payslip("payroll", 1, 2, name="Winter")
        with trap_jobs() as january_trap:
            january.action_paysplip_import()
            # only the batch job: the job of January's line stays queued
            january_trap.perform_enqueued_jobs()
            with trap_jobs() as winter_trap:
                winter.action_paysplip_import()
                # only the batch job: the jobs of Winter's lines stay queued
                winter_trap.perform_enqueued_jobs()
                january_trap.perform_enqueued_jobs()
                with mock.patch.dict(JOAN_JANUARY_PAYROLL_LINE, {"ImporteNom": 1500.0}):
                    with self.assertRaisesRegex(
                        UserError,
                        r"This line or check already belongs to another payslip "
                        r"\(January\): it is not imported into Winter\. Check the "
                        r"filters of both payslips, then import Winter again and "
                        r"cancel this job\.",
                    ):
                        winter_trap.perform_enqueued_jobs()
        self.assertEqual(january.payslip_line_ids.mapped("amount"), [1000.0])

    def test_line_job_of_deleted_payslip_leaves_the_other_payslips_line(self):
        """As in the race above, Winter's job of January's line runs after
        January's job created it, but Winter was deleted meanwhile: the job
        fails saying so, and the line keeps the amount January's job wrote."""
        january = self._create_payslip("payroll", 1, 1, name="January")
        winter = self._create_payslip("payroll", 1, 2, name="Winter")
        with trap_jobs() as january_trap:
            january.action_paysplip_import()
            # only the batch job: the job of January's line stays queued
            january_trap.perform_enqueued_jobs()
            with trap_jobs() as winter_trap:
                winter.action_paysplip_import()
                # only the batch job: the jobs of Winter's lines stay queued
                winter_trap.perform_enqueued_jobs()
                january_trap.perform_enqueued_jobs()
                winter.action_paysplip_set_to_draft()
                winter.unlink()
                with mock.patch.dict(JOAN_JANUARY_PAYROLL_LINE, {"ImporteNom": 1500.0}):
                    with self.assertRaisesRegex(
                        UserError,
                        r"This line or check already belongs to another payslip "
                        r"\(January\), and the payslip of this job was deleted: "
                        r"it is not imported\. Cancel this job\.",
                    ):
                        winter_trap.perform_enqueued_jobs()
        self.assertEqual(january.payslip_line_ids.mapped("amount"), [1000.0])

    def test_line_job_of_line_removed_from_sage_fails(self):
        """Sage removes January's line while its job waits in the queue: the
        job fails saying so, and creates nothing."""
        january = self._create_payslip("payroll", 1, 1, name="January")
        with trap_jobs() as trap:
            january.action_paysplip_import()
            # only the batch job: the job of January's line stays queued
            trap.perform_enqueued_jobs()
            with mock.patch.dict(SAGE, {PAYROLL_LINE: [JOAN_FEBRUARY_PAYROLL_LINE]}):
                with self.assertRaisesRegex(UserError, NOT_IN_SAGE):
                    trap.perform_enqueued_jobs()
        self.assertFalse(january.payslip_line_ids)

    def test_refused_lines_leave_the_checks_out(self):
        """January holds Joan's line, imported alone from the backend. The
        import of a transfer of January and February is one job, which reads
        that line and is refused naming January, so none of the transfer's
        checks is imported either."""
        january = self._create_payslip(
            "transfer", 1, 1, name="January", payment_date=date(2026, 1, 31)
        )
        self.backend.import_payslip_line_id = january
        with trap_jobs() as trap:
            self.backend.import_payslip_lines()
            self._run_jobs(trap)
        winter = self._create_payslip("transfer", 1, 2, name="Winter")
        with trap_jobs() as trap:
            winter.action_paysplip_import()
            # a job of the checks alone would import them although the lines
            # are refused
            trap.assert_jobs_count(1)
            with self.assertRaisesRegex(
                UserError,
                r"The import of payslip Winter reads lines or checks that already "
                r"belong to another payslip \(January\)\.",
            ):
                trap.perform_enqueued_jobs()
            trap.assert_jobs_count(0)
        self.assertFalse(winter.payslip_check_ids)

    def test_refused_checks_leave_the_lines_out(self):
        """In January, Joan is also paid on 15/01, and his check belongs to the
        transfer of 31/01. The import of the transfer of 15/01 reads that
        check and is refused naming the other transfer, so none of its lines
        is imported either."""
        joan_january_15_line = {
            "CodigoEmpresa": SAGE_COMPANY,
            "Año": 2026,
            "MesD": 1,
            "TipoProceso": PROCESS,
            "CodigoEmpleado": CODE,
            "CodigoConceptoNom": CONCEPT,
            "CodigoConvenio": AGREEMENT_CODE,
            "FechaRegistroCV": AGREEMENT_DATE,
            "FechaCobro": datetime(2026, 1, 15),
            "ConceptoLargo": "SALARIO BASE",
            "ImporteNom": 200.0,
        }
        with mock.patch.dict(
            SAGE,
            {
                TRANSFER_LINE: [
                    JOAN_JANUARY_LINE,
                    JOAN_FEBRUARY_LINE,
                    MARIA_JANUARY_LINE,
                    joan_january_15_line,
                ]
            },
        ):
            end = self._create_payslip(
                "transfer", 1, 1, name="January 31", payment_date=date(2026, 1, 31)
            )
            with trap_jobs() as trap:
                end.action_paysplip_import()
                self._run_jobs(trap)
            middle = self._create_payslip(
                "transfer", 1, 1, name="January 15", payment_date=date(2026, 1, 15)
            )
            with trap_jobs() as trap:
                middle.action_paysplip_import()
                with self.assertRaisesRegex(
                    UserError,
                    r"The import of payslip January 15 reads lines or checks that "
                    r"already belong to another payslip \(January 31\)\.",
                ):
                    trap.perform_enqueued_jobs()
                trap.assert_jobs_count(0)
        self.assertFalse(middle.payslip_line_ids)
