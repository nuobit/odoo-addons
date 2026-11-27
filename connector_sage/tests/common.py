# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, datetime, time
from unittest import mock

from odoo.tests.common import SavepointCase

ADAPTER_SEARCH = "odoo.addons.connector_sage.components.adapter.GenericAdapter.search"
ADAPTER_READ = "odoo.addons.connector_sage.components.adapter.GenericAdapter.read"
ADAPTER_EXEC_SQL = (
    "odoo.addons.connector_sage.components.adapter.GenericAdapter._exec_sql"
)

TRANSFER_LINE = "sage.payroll.sage.payslip.line.transfer"
PAYROLL_LINE = "sage.payroll.sage.payslip.line.payroll"
CHECK = "sage.payroll.sage.payslip.check"

SAGE_COMPANY = 99
CODE = 602
AGREEMENT_CODE = 91
AGREEMENT_DATE = datetime(2020, 1, 1)
PROCESS = "TEST-DEST"
CONCEPT = 901

WORKER = {
    "CodigoEmpresa": SAGE_COMPANY,
    "CodigoEmpleado": CODE,
    "SiglaNacion": "XX",
    "Dni": "WORKER02A",
    "NombreEmpleado": "JOAN",
    "PrimerApellidoEmpleado": "PUIG",
    "SegundoApellidoEmpleado": "ROCA",
    "NumeroHijos": 0,
    "FechaNacimiento": False,
    "Email1": "joan@test.example.com",
    "Email2": "joan@test.example.com",
}


def _sage_value(value):
    """A value as Sage compares it: a date against a datetime column is that
    day at midnight."""
    if type(value) is date:
        return datetime.combine(value, time())
    return value


def _meets(value, condition):
    """Whether a value of Sage meets one condition of the adapter's filters,
    written as the adapter writes them: a value, or an operator and its
    operand."""
    if isinstance(condition, (tuple, list)):
        operator, operand = condition
        if operator == "=":
            return _sage_value(value) == _sage_value(operand)
        elif operator == "in":
            return _sage_value(value) in {_sage_value(item) for item in operand}
        elif operator == "between":
            low, high = operand
            return _sage_value(low) <= _sage_value(value) <= _sage_value(high)
        raise NotImplementedError("Operator %s" % operator)
    return _sage_value(value) == _sage_value(condition)


class FakeSage:
    """Sage as the adapters reach it: it answers their search and their read
    from the records it holds for each binding model, as their queries do."""

    def __init__(self, records):
        self.records = records

    def answer_search(self, adapter, filters=None):
        return [
            tuple(record[field] for field in adapter._id)
            for record in self._select(adapter, filters or {})
        ]

    def answer_read(self, adapter, _id, attributes=None):
        records = self._select(adapter, dict(zip(adapter._id, _id)))
        if len(records) > 1:
            raise AssertionError("Sage holds the id %s more than once" % (_id,))
        return dict(records[0]) if records else []

    def _select(self, adapter, filters):
        model = adapter.model._name
        if model == CHECK:
            return [
                check for check in self.records[CHECK] if self._selects(check, filters)
            ]
        return [
            record
            for record in self.records[model]
            if all(_meets(record[column], filters[column]) for column in filters)
        ]

    def _selects(self, check, filters):
        """The checks follow the transfer lines: a filter on a column that
        the checks lack selects the checks of the employees with a transfer
        line that meets it in the same month and process."""
        line_columns = [column for column in filters if column not in check]
        return all(
            _meets(check[column], filters[column])
            for column in filters
            if column in check
        ) and (
            not line_columns
            or any(
                all(
                    line[column] == check[column]
                    for column in (
                        "CodigoEmpresa",
                        "CodigoEmpleado",
                        "Año",
                        "MesD",
                        "TipoProceso",
                    )
                )
                and all(
                    _meets(line[column], filters[column]) for column in line_columns
                )
                for line in self.records[TRANSFER_LINE]
            )
        )


class SagePayslipCase(SavepointCase):
    """A Sage backend with a labour agreement, its wage type and a worker
    imported from Sage. Sage answers from the records of the class attribute
    ``sage``: a list of Sage records per binding model."""

    sage = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env["res.company"].create({"name": "Sage Test Company"})
        cls.account_payable = cls.env["account.account"].create(
            {
                "name": "Test Account Payable",
                "code": "TESTPAY01",
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
                "reconcile": True,
                "company_id": cls.company.id,
            }
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
        cls.wage_type_line = cls.env[
            "sage.payroll.sage.labour.agreement.wage.type.line"
        ].create(
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
        sage = FakeSage(self.sage)
        search = mock.patch(
            ADAPTER_SEARCH, autospec=True, side_effect=sage.answer_search
        )
        read = mock.patch(ADAPTER_READ, autospec=True, side_effect=sage.answer_read)
        search.start()
        read.start()
        self.addCleanup(search.stop)
        self.addCleanup(read.stop)

    def _create_payslip(
        self,
        payslip_type,
        month_from,
        month_to,
        name="Test Payslip",
        payment_date=None,
    ):
        payslip = self.env["payroll.sage.payslip"].create(
            {
                "name": name,
                "entry_date": date(2026, 3, 1),
                "year": 2026,
                "month_from": month_from,
                "month_to": month_to,
                "labour_agreement_id": self.agreement.odoo_id.id,
                "company_id": self.company.id,
                "journal_id": self.journal.id,
                "type": payslip_type,
                "process_id": self.process.id,
                "payment_date": payment_date,
            }
        )
        payslip.action_paysplip_validate()
        return payslip

    def _run_jobs(self, trap):
        """Run the queued batch jobs, then the record jobs they queue."""
        trap.perform_enqueued_jobs()
        trap.perform_enqueued_jobs()
