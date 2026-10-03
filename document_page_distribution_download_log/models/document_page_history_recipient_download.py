# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class DocumentPageHistoryRecipientDownload(models.Model):
    """Evidence that a user's browser asked for a file of a version of a
    document, to hand it to the user.

    A row is written each time a tracked link is asked for that way (a click, a
    new tab, a save), whoever the user is; never for an address that the
    browser declares as a part of another page (an image, a media file, a
    script) or as asked ahead of the user. It belongs to the version the link
    was saved in, never to the current version of the document.
    """

    _name = "document.page.history.recipient.download"
    _description = "Document Page Distribution Download"
    _order = "download_date desc, id desc"

    history_id = fields.Many2one(
        comodel_name="document.page.history",
        required=True,
        ondelete="restrict",
        index=True,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        required=True,
        ondelete="restrict",
        index=True,
    )
    # the recipient line of the version for the user, when there is one
    recipient_id = fields.Many2one(
        comodel_name="document.page.history.recipient",
        compute="_compute_recipient_id",
        store=True,
        ondelete="set null",
        index=True,
    )
    document_page_id = fields.Many2one(
        comodel_name="document.page",
        related="history_id.page_id",
        store=True,
        index=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="history_id.company_id",
        store=True,
        index=True,
    )
    # the file is evidence: it is not deleted while a row names it
    attachment_id = fields.Many2one(
        comodel_name="ir.attachment",
        required=True,
        ondelete="restrict",
        index=True,
    )
    download_date = fields.Datetime(required=True, default=fields.Datetime.now)

    @api.depends("history_id.recipient_ids.partner_id", "user_id.partner_id")
    def _compute_recipient_id(self):
        for download in self:
            # a version has one recipient per partner at most
            # (constraint history_partner_uniq of the recipients)
            download.recipient_id = download.history_id.recipient_ids.filtered(
                lambda recipient: recipient.partner_id == download.user_id.partner_id
            )
