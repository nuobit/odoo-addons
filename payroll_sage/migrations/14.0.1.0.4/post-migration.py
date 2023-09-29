# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
# pylint: disable=C7902
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env.cr.execute(
        """
        select p.id, p.process
        from payroll_sage_payslip p
        """
    )

    payslips = env.cr.fetchall()
    process_types_map = {}
    for _, process in payslips:
        if process not in process_types_map:
            ppt = env["payroll.sage.payslip.process"].create(
                {
                    "name": process,
                }
            )
            process_types_map[process] = ppt.id

    for payslip_id, process in payslips:
        env["payroll.sage.payslip"].browse(payslip_id).write(
            {"process_id": process_types_map[process]}
        )
