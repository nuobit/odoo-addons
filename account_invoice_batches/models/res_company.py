# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    invoice_batch_sending_email_template_id = fields.Many2one(
        string="Default Invoice batches e-mail template",
        comodel_name="mail.template",
        domain=[("model_id", "=", "account.move")],
    )
    invoice_batch_user_id = fields.Many2one(
        string="Invoice batch user",
        comodel_name="res.users",
        domain=[("share", "=", False)],
        help="Internal user the invoice batch jobs run as. The invoices "
        "generated from a batch and the e-mails sent from it belong to this "
        "user: it is their creator, their follower and the author of the sent "
        "messages, so the customer replies reach its mailbox.",
    )

    @api.constrains("invoice_batch_user_id")
    def _check_invoice_batch_user_id(self):
        # the field domain only guides the widget: the invariant lives here
        for company in self.filtered("invoice_batch_user_id.share"):
            raise ValidationError(
                _(
                    "The invoice batch user %(user)s of company %(company)s must "
                    "be an internal user, not a portal or public one.",
                    user=company.invoice_batch_user_id.display_name,
                    company=company.display_name,
                )
            )

    def _get_invoice_batch_user(self):
        """Return the user the invoice batch jobs of this company run as.

        Raise a UserError naming the company when no user is configured, the
        user is archived, is not internal, has no e-mail address or is not
        allowed on the company, so nothing is queued or executed with a wrong
        identity.
        """
        self.ensure_one()
        user = self.invoice_batch_user_id
        if not user:
            raise UserError(
                _(
                    "Company %(company)s has no invoice batch user. Set one in "
                    "Settings > Invoicing > Invoice batches.",
                    company=self.display_name,
                )
            )
        if not user.active:
            raise UserError(
                _(
                    "The invoice batch user %(user)s of company %(company)s is "
                    "archived.",
                    user=user.display_name,
                    company=self.display_name,
                )
            )
        if user.share:
            # the groups can change after the user was set on the company
            raise UserError(
                _(
                    "The invoice batch user %(user)s of company %(company)s is "
                    "not an internal user.",
                    user=user.display_name,
                    company=self.display_name,
                )
            )
        if not user.email:
            raise UserError(
                _(
                    "The invoice batch user %(user)s of company %(company)s has "
                    "no e-mail address.",
                    user=user.display_name,
                    company=self.display_name,
                )
            )
        if self not in user.company_ids:
            raise UserError(
                _(
                    "The invoice batch user %(user)s is not allowed on company "
                    "%(company)s.",
                    user=user.display_name,
                    company=self.display_name,
                )
            )
        return user
