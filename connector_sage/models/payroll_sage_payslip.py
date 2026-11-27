# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, exceptions, models
from odoo.exceptions import UserError

from odoo.addons.queue_job.job import (
    CANCELLED,
    ENQUEUED,
    FAILED,
    PENDING,
    STARTED,
    WAIT_DEPENDENCIES,
)

# The errors whose message Odoo shows to a person as it is: UserError and the
# errors of odoo.exceptions that inherit from it, named as queue_job stores the
# error of a failed job, "<module>.<class>"
USER_ERRORS = {
    "%s.%s" % (error.__module__, error.__name__)
    for error in vars(exceptions).values()
    if isinstance(error, type) and issubclass(error, UserError)
}


class Payslip(models.Model):
    _inherit = "payroll.sage.payslip"

    def action_paysplip_import(self):
        self._check_can_import()
        for rec in self:
            backend = self.env["sage.backend"].search(
                [("company_id", "=", rec.company_id.id)]
            )
            if len(backend) != 1:
                raise UserError(
                    _("Expected 1 backend for the current company, found %i")
                    % len(backend)
                )

            # import lines and checks
            if rec.type == "transfer":
                self.env[
                    "sage.payroll.sage.payslip.line.transfer"
                ].with_delay().import_payslip_lines_and_checks(rec, backend)
            elif rec.type == "payroll":
                self.env[
                    "sage.payroll.sage.payslip.line.payroll"
                ].with_delay().import_payslip_lines(rec, backend)
            else:
                raise UserError(_("Unexpected payslip type %s!") % rec.type)

        return True

    def action_paysplip_post(self):
        self._check_import_finished()
        return super().action_paysplip_post()

    def _check_can_import(self):
        posted = self.filtered(lambda payslip: payslip.state == "posted")
        if posted:
            raise UserError(
                _("A posted payslip cannot be imported (%s).")
                % ", ".join(posted.mapped("display_name"))
            )

    def _check_import_finished(self):
        # A record job that failed left its line or check out of the payslip
        jobs = (
            self.env["queue.job"]
            .sudo()
            .search(
                [
                    ("sage_payslip_id", "in", self.ids),
                    "|",
                    ("state", "in", (WAIT_DEPENDENCIES, PENDING, ENQUEUED, STARTED)),
                    "&",
                    ("method_name", "=", "import_record"),
                    ("state", "=", FAILED),
                ]
            )
        )
        if jobs:
            raise UserError(
                _(
                    "A payslip cannot be posted while its import has jobs queued, "
                    "running or failed (%s). Wait until they are done. A queue job "
                    "manager can requeue a failed job once its cause is fixed, or "
                    "cancel it to post the payslip as it is."
                )
                % ", ".join(jobs.sage_payslip_id.mapped("display_name"))
            )
        # A batch job that failed wrote nothing, so its payslip keeps what an
        # earlier import left, which Sage or the payslip's filter may no longer
        # have, until a later import succeeds or the failed job is cancelled.
        # A cancelled batch job imported nothing either, so the one before it
        # decides.
        batch_jobs = (
            self.env["queue.job"]
            .sudo()
            .search(
                [
                    ("sage_payslip_id", "in", self.ids),
                    ("method_name", "!=", "import_record"),
                    ("state", "!=", CANCELLED),
                ],
                order="id",
            )
        )
        # oldest first, so that each payslip keeps its newest batch job
        last_batch_jobs = {job.sage_payslip_id: job for job in batch_jobs}
        failed_jobs = [job for job in last_batch_jobs.values() if job.state == FAILED]
        if failed_jobs:
            raise UserError(
                _(
                    "A payslip cannot be posted while its last import has failed. "
                    "Fix the cause and import it again, or have a queue job "
                    "manager cancel the failed job to post the payslip as it is:"
                    "\n%s"
                )
                % "\n".join(self._failed_import_reason(job) for job in failed_jobs)
            )

    @api.model
    def _failed_import_reason(self, job):
        """Name the payslip of a failed import job, with the job's message when
        Odoo shows its error to a person as it is: any other error, such as
        Sage being unreachable, can carry a server's name or data"""
        if job.exc_name in USER_ERRORS and job.exc_message:
            reason = "%s: %s" % (job.sage_payslip_id.display_name, job.exc_message)
        else:
            reason = (
                _(
                    "%s: the import failed; a queue job manager can see why in "
                    "the failed job"
                )
                % job.sage_payslip_id.display_name
            )
        return reason
