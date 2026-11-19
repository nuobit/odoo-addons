# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, datetime
from unittest import mock

import pymssql

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.component.tests.common import TransactionComponentCase
from odoo.addons.queue_job.job import Job
from odoo.addons.queue_job.tests.common import trap_jobs

ADAPTER_SEARCH = "odoo.addons.connector_sage.components.adapter.GenericAdapter.search"
ADAPTER_READ = "odoo.addons.connector_sage.components.adapter.GenericAdapter.read"

SAGE_COMPANY = 99
CODE = 602
AGREEMENT_CODE = 91
AGREEMENT_DATE = datetime(2020, 1, 1)
PROCESS = "TEST-DEST"
CONCEPT = 901
NO_PAYSLIP = (
    "This job has no destination payslip, because it was queued without one "
    "or because its payslip was deleted. Cancel the job and, if the payslip "
    "still exists, import it again."
)

WORKER = {
    "CodigoEmpresa": SAGE_COMPANY,
    "CodigoEmpleado": CODE,
    "SiglaNacion": "XX",
    "Dni": "WORKER02A",
    "NombreEmpleado": "JOAN",
    "PrimerApellidoEmpleado": "PUIG",
    "SegundoApellidoEmpleado": "ROCA",
    "NumeroHijos": 0,
    "FechaNacimiento": None,
    "Email1": "joan@test.example.com",
    "Email2": "joan@test.example.com",
}

PAYROLL_LINES = [
    {
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
    },
    {
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
    },
]

TRANSFER_LINES = [
    {
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
    },
    {
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
    },
]

CHECKS = [
    {
        "CodigoEmpresa": SAGE_COMPANY,
        "CodigoEmpleado": CODE,
        "Año": 2026,
        "MesD": 1,
        "TipoProceso": PROCESS,
        "IdEmpleado": "WORKER-602",
        "OrdenNom": 1,
        "Importe": 900.0,
        "FechaBaja": datetime(3000, 12, 31),
    },
    {
        "CodigoEmpresa": SAGE_COMPANY,
        "CodigoEmpleado": CODE,
        "Año": 2026,
        "MesD": 2,
        "TipoProceso": PROCESS,
        "IdEmpleado": "WORKER-602",
        "OrdenNom": 1,
        "Importe": 950.0,
        "FechaBaja": datetime(3000, 12, 31),
    },
]

SAGE = {
    "sage.payroll.sage.payslip.line.payroll": PAYROLL_LINES,
    "sage.payroll.sage.payslip.line.transfer": TRANSFER_LINES,
    "sage.payroll.sage.payslip.check": CHECKS,
}


def sage_search(adapter, filters=None):
    # The payslips of these tests differ only in their months, so Sage
    # answers the month range of the filters.
    month_from, month_to = filters["MesD"][1]
    return [
        tuple(record[field] for field in adapter._id)
        for record in SAGE[adapter.model._name]
        if month_from <= record["MesD"] <= month_to
    ]


def sage_read(adapter, _id, attributes=None):
    records = {
        tuple(record[field] for field in adapter._id): record
        for record in SAGE[adapter.model._name]
    }
    return dict(records[tuple(_id)])


@tagged("post_install", "-at_install")
class TestPayslipDestination(TransactionComponentCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env["res.company"].create({"name": "Sage Test Company"})
        cls.account_payable = (
            cls.env["account.account"]
            .with_company(cls.company)
            .create(
                {
                    "name": "Test Account Payable",
                    "code": "TESTPAY01",
                    "account_type": "liability_payable",
                    "reconcile": True,
                    "company_ids": [(6, 0, cls.company.ids)],
                }
            )
        )
        cls.backend = cls.env["sage.backend"].create(
            {
                "name": "Test Sage Backend",
                "server": "localhost",
                "port": 1433,
                "database": "test",
                "schema": "dbo",
                "username": "test",
                "password": "test",
                "company_id": cls.company.id,
                "sage_company_id": SAGE_COMPANY,
                "import_employees_default_account_payable_id": cls.account_payable.id,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Test Payroll Journal",
                "code": "TPAY",
                "type": "general",
                "company_id": cls.company.id,
            }
        )
        cls.process = cls.env["payroll.sage.payslip.process"].create({"name": PROCESS})
        cls.agreement = cls.env["sage.payroll.sage.labour.agreement"].create(
            {
                "backend_id": cls.backend.id,
                "name": "TEST AGREEMENT",
                "code": AGREEMENT_CODE,
                "registration_date_cv": AGREEMENT_DATE,
                "company_id": cls.company.id,
                "sage_codigo_empresa": SAGE_COMPANY,
                "sage_codigo_convenio": AGREEMENT_CODE,
                "sage_fecha_registro_cv": AGREEMENT_DATE,
            }
        )
        cls.env["sage.payroll.sage.labour.agreement.wage.type.line"].create(
            {
                "sage_labour_agreement_id": cls.agreement.id,
                "name": "SALARIO BASE",
                "short_name": "SALARIO",
                "code": CONCEPT,
                "positive": True,
                "total_historical_record": "accrural",
                "sage_codigo_empresa": SAGE_COMPANY,
                "sage_codigo_convenio": AGREEMENT_CODE,
                "sage_fecha_registro_cv": AGREEMENT_DATE,
                "sage_codigo_concepto_nom": CONCEPT,
            }
        )
        with mock.patch(ADAPTER_READ, return_value=dict(WORKER)):
            cls.env["sage.hr.employee"].import_record(cls.backend, (SAGE_COMPANY, CODE))

    def setUp(self):
        super().setUp()
        search = mock.patch(ADAPTER_SEARCH, autospec=True, side_effect=sage_search)
        read = mock.patch(ADAPTER_READ, autospec=True, side_effect=sage_read)
        search.start()
        read.start()
        self.addCleanup(search.stop)
        self.addCleanup(read.stop)

    def _create_payslip(self, payslip_type, month_from, month_to):
        payslip = self.env["payroll.sage.payslip"].create(
            {
                "name": "Test Payslip",
                "entry_date": date(2026, 3, 1),
                "year": 2026,
                "month_from": month_from,
                "month_to": month_to,
                "labour_agreement_id": self.agreement.odoo_id.id,
                "company_id": self.company.id,
                "journal_id": self.journal.id,
                "type": payslip_type,
                "process_id": self.process.id,
            }
        )
        payslip.action_paysplip_validate()
        return payslip

    def _run_jobs(self, trap):
        """Run the queued batch jobs, then the record jobs they queue."""
        trap.perform_enqueued_jobs()
        trap.perform_enqueued_jobs()

    def test_overlapping_imports_keep_their_payslips(self):
        """January is imported and, before its jobs run, February too: each
        line lands in the payslip of its own import."""
        january = self._create_payslip("payroll", 1, 1)
        february = self._create_payslip("payroll", 2, 2)
        with trap_jobs() as trap:
            january.action_paysplip_import()
            february.action_paysplip_import()
            self._run_jobs(trap)
        self.assertEqual(
            january.payslip_line_ids.sage_payroll_bind_ids.mapped("sage_mesd"), [1]
        )
        self.assertEqual(
            february.payslip_line_ids.sage_payroll_bind_ids.mapped("sage_mesd"), [2]
        )

    def test_late_job_keeps_its_payslip(self):
        """The record job of January's line is still queued when February is
        imported and its jobs run, as after a retry or a requeue: it creates
        its line in January."""
        january = self._create_payslip("payroll", 1, 1)
        february = self._create_payslip("payroll", 2, 2)
        with trap_jobs() as january_trap:
            january.action_paysplip_import()
            # only the batch job: the job of January's line stays queued
            january_trap.perform_enqueued_jobs()
            with trap_jobs() as february_trap:
                february.action_paysplip_import()
                self._run_jobs(february_trap)
            january_trap.perform_enqueued_jobs()
        self.assertEqual(
            january.payslip_line_ids.sage_payroll_bind_ids.mapped("sage_mesd"), [1]
        )
        self.assertEqual(
            february.payslip_line_ids.sage_payroll_bind_ids.mapped("sage_mesd"), [2]
        )

    def test_job_without_payslip_fails(self):
        """A record job queued by an older version of the connector carries
        no payslip: it fails asking to cancel it and import the payslip again,
        and does not take the payslip selected on the backend."""
        january = self._create_payslip("payroll", 1, 1)
        self.backend.import_payslip_line_id = january
        with self.assertRaisesRegex(UserError, NO_PAYSLIP):
            self.env["sage.payroll.sage.payslip.line.payroll"].import_record(
                self.backend,
                (
                    SAGE_COMPANY,
                    2026,
                    1,
                    PROCESS,
                    CODE,
                    CONCEPT,
                    AGREEMENT_CODE,
                    AGREEMENT_DATE,
                ),
            )
        self.assertFalse(
            self.env["sage.payroll.sage.payslip.line.payroll"].search(
                [("backend_id", "=", self.backend.id)]
            )
        )

    def test_job_of_deleted_payslip_fails(self):
        """The payslip is deleted while the job of its line is queued: the job
        fails asking to cancel it, and creates nothing."""
        january = self._create_payslip("payroll", 1, 1)
        with trap_jobs() as trap:
            january.action_paysplip_import()
            # only the batch job: the job of January's line stays queued
            trap.perform_enqueued_jobs()
            january.action_paysplip_set_to_draft()
            january.unlink()
            with self.assertRaisesRegex(UserError, NO_PAYSLIP):
                trap.perform_enqueued_jobs()
        self.assertFalse(
            self.env["sage.payroll.sage.payslip.line.payroll"].search(
                [("backend_id", "=", self.backend.id)]
            )
        )

    def test_import_leaves_backend_selection(self):
        """The payslip's Import button no longer writes the payslip on the
        backend."""
        january = self._create_payslip("transfer", 1, 1)
        with trap_jobs():
            january.action_paysplip_import()
        self.assertFalse(self.backend.import_payslip_line_id)
        self.assertFalse(self.backend.import_payslip_check_id)

    def test_backend_line_import_keeps_selected_payslip(self):
        """The backend's Import Payslip Lines button imports the payslip
        selected there, and its lines land in it even if the selection
        changes before their jobs run."""
        january = self._create_payslip("payroll", 1, 1)
        february = self._create_payslip("payroll", 2, 2)
        self.backend.import_payslip_line_id = january
        with trap_jobs() as trap:
            self.backend.import_payslip_lines()
            self.backend.import_payslip_line_id = february
            self._run_jobs(trap)
        self.assertEqual(
            january.payslip_line_ids.sage_payroll_bind_ids.mapped("sage_mesd"), [1]
        )
        self.assertFalse(february.payslip_line_ids)

    def test_backend_check_import_keeps_selected_payslip(self):
        """The backend's Import Payslip Checks button imports the checks of
        the payslip selected there, and they land in it even if the selection
        changes before their jobs run."""
        january = self._create_payslip("transfer", 1, 1)
        february = self._create_payslip("transfer", 2, 2)
        self.backend.import_payslip_check_id = january
        with trap_jobs() as trap:
            self.backend.import_payslip_checks()
            self.backend.import_payslip_check_id = february
            self._run_jobs(trap)
        self.assertEqual(
            january.payslip_check_ids.sage_bind_ids.mapped("sage_mesd"), [1]
        )
        self.assertFalse(february.payslip_check_ids)

    def test_existing_line_keeps_its_payslip(self):
        """January's line is read again by the import of a payslip of January
        and February: it is written in place and stays in January, and only
        February's line is new."""
        january = self._create_payslip("payroll", 1, 1)
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        january_line = january.payslip_line_ids
        winter = self._create_payslip("payroll", 1, 2)
        with trap_jobs() as trap:
            winter.action_paysplip_import()
            self._run_jobs(trap)
        self.assertEqual(january.payslip_line_ids, january_line)
        self.assertEqual(
            winter.payslip_line_ids.sage_payroll_bind_ids.mapped("sage_mesd"), [2]
        )

    def test_overlapping_transfer_imports_keep_their_payslips(self):
        """Two transfers are imported one after the other, before their jobs
        run: each one gets its own transfer lines and checks."""
        january = self._create_payslip("transfer", 1, 1)
        february = self._create_payslip("transfer", 2, 2)
        with trap_jobs() as trap:
            january.action_paysplip_import()
            february.action_paysplip_import()
            self._run_jobs(trap)
        self.assertEqual(
            january.payslip_line_ids.sage_transfer_bind_ids.mapped("sage_mesd"), [1]
        )
        self.assertEqual(
            february.payslip_line_ids.sage_transfer_bind_ids.mapped("sage_mesd"), [2]
        )
        self.assertEqual(
            january.payslip_check_ids.sage_bind_ids.mapped("sage_mesd"), [1]
        )
        self.assertEqual(
            february.payslip_check_ids.sage_bind_ids.mapped("sage_mesd"), [2]
        )

    def test_check_job_without_payslip_fails(self):
        """A check job queued by an older version of the connector carries no
        payslip: it fails asking to cancel it and import the payslip again,
        and does not take the payslip selected on the backend."""
        january = self._create_payslip("transfer", 1, 1)
        self.backend.import_payslip_check_id = january
        with self.assertRaisesRegex(UserError, NO_PAYSLIP):
            self.env["sage.payroll.sage.payslip.check"].import_record(
                self.backend, (SAGE_COMPANY, CODE, 2026, 1, PROCESS, "WORKER-602", 1)
            )
        self.assertFalse(
            self.env["sage.payroll.sage.payslip.check"].search(
                [("backend_id", "=", self.backend.id)]
            )
        )

    def test_check_job_of_deleted_payslip_fails(self):
        """The transfer is deleted while the job of its check is queued: the
        job fails asking to cancel it, and creates nothing."""
        january = self._create_payslip("transfer", 1, 1)
        self.backend.import_payslip_check_id = january
        with trap_jobs() as trap:
            self.backend.import_payslip_checks()
            # only the batch job: the job of January's check stays queued
            trap.perform_enqueued_jobs()
            january.action_paysplip_set_to_draft()
            january.unlink()
            with self.assertRaisesRegex(UserError, NO_PAYSLIP):
                trap.perform_enqueued_jobs()
        self.assertFalse(
            self.env["sage.payroll.sage.payslip.check"].search(
                [("backend_id", "=", self.backend.id)]
            )
        )

    def test_existing_check_keeps_its_payslip(self):
        """January's check is read again by the import of a transfer of
        January and February: it is written in place and stays in January, and
        only February's check is new."""
        january = self._create_payslip("transfer", 1, 1)
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        january_check = january.payslip_check_ids
        winter = self._create_payslip("transfer", 1, 2)
        with trap_jobs() as trap:
            winter.action_paysplip_import()
            self._run_jobs(trap)
        self.assertEqual(january.payslip_check_ids, january_check)
        self.assertEqual(
            winter.payslip_check_ids.sage_bind_ids.mapped("sage_mesd"), [2]
        )

    def test_existing_line_updated_without_payslip(self):
        """A job without a payslip, as an older version queued it or as the
        Resynchronize button runs it, writes an existing line in place: its
        new amount is stored and it stays in its payslip."""
        january = self._create_payslip("payroll", 1, 1)
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        january_line = january.payslip_line_ids
        with mock.patch.dict(PAYROLL_LINES[0], {"ImporteNom": 1500.0}):
            self.env["sage.payroll.sage.payslip.line.payroll"].import_record(
                self.backend,
                (
                    SAGE_COMPANY,
                    2026,
                    1,
                    PROCESS,
                    CODE,
                    CONCEPT,
                    AGREEMENT_CODE,
                    AGREEMENT_DATE,
                ),
            )
        self.assertEqual(january.payslip_line_ids, january_line)
        self.assertEqual(january_line.amount, 1500.0)

    def test_existing_check_updated_without_payslip(self):
        """A check job without a payslip, as an older version queued it or as
        the Resynchronize button runs it, writes an existing check in place:
        its new amount is stored and it stays in its payslip."""
        january = self._create_payslip("transfer", 1, 1)
        with trap_jobs() as trap:
            january.action_paysplip_import()
            self._run_jobs(trap)
        january_check = january.payslip_check_ids
        with mock.patch.dict(CHECKS[0], {"Importe": 1250.0}):
            self.env["sage.payroll.sage.payslip.check"].import_record(
                self.backend, (SAGE_COMPANY, CODE, 2026, 1, PROCESS, "WORKER-602", 1)
            )
        self.assertEqual(january.payslip_check_ids, january_check)
        self.assertEqual(january_check.amount, 1250.0)

    def test_requeued_job_keeps_its_payslip(self):
        """January's line job waits in the queue while February is imported,
        then runs as a requeue runs it, read back from the database: it
        creates its line in January."""
        january = self._create_payslip("payroll", 1, 1)
        february = self._create_payslip("payroll", 2, 2)
        queue = self.env["queue.job"]
        last_id = queue.search([], order="id desc", limit=1).id or 0
        january.action_paysplip_import()
        batch_job = queue.search([("id", ">", last_id)])
        self.assertEqual(len(batch_job), 1)
        Job.load(self.env, batch_job.uuid).perform()
        line_job = queue.search([("id", ">", batch_job.id)])
        self.assertEqual(len(line_job), 1)
        with trap_jobs() as trap:
            february.action_paysplip_import()
            self._run_jobs(trap)
        Job.load(self.env, line_job.uuid).perform()
        self.assertEqual(
            january.payslip_line_ids.sage_payroll_bind_ids.mapped("sage_mesd"), [1]
        )
        self.assertEqual(
            february.payslip_line_ids.sage_payroll_bind_ids.mapped("sage_mesd"), [2]
        )

    def test_retry_after_sage_error_keeps_its_payslip(self):
        """Sage cannot be read when January's line job runs: the job stops
        with the database error and January gets no line. February is
        imported, and the retry of January's job creates its line in
        January."""
        january = self._create_payslip("payroll", 1, 1)
        february = self._create_payslip("payroll", 2, 2)
        with trap_jobs() as trap:
            january.action_paysplip_import()
            # only the batch job: the job of January's line stays queued
            trap.perform_enqueued_jobs()
            (line_job,) = trap.enqueued_jobs
            with mock.patch(
                ADAPTER_READ,
                side_effect=pymssql.OperationalError("Unable to connect to Sage"),
            ):
                with self.assertRaisesRegex(
                    pymssql.OperationalError, "Unable to connect to Sage"
                ):
                    trap.perform_enqueued_jobs()
            self.assertFalse(january.payslip_line_ids)
            with trap_jobs() as february_trap:
                february.action_paysplip_import()
                self._run_jobs(february_trap)
            line_job.perform()
        self.assertEqual(
            january.payslip_line_ids.sage_payroll_bind_ids.mapped("sage_mesd"), [1]
        )
        self.assertEqual(
            february.payslip_line_ids.sage_payroll_bind_ids.mapped("sage_mesd"), [2]
        )
