# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DocumentPageHistoryRecipientDownload(models.Model):
    """Real download evidence of a (version, partner) recipient line.

    A row only exists when a covered recipient actually accessed/downloaded the
    PDF of the version. It is always imputed to the version (``history_id``) the
    link belonged to, never to the page's current head.
    """

    _name = "document.page.history.recipient.download"
    _description = "Document Page Distribution Download"
    _order = "download_date desc, id desc"

    recipient_id = fields.Many2one(
        "document.page.history.recipient",
        required=True,
        ondelete="cascade",
        index=True,
    )
    history_id = fields.Many2one(
        "document.page.history",
        related="recipient_id.history_id",
        store=True,
        index=True,
    )
    document_page_id = fields.Many2one(
        "document.page",
        related="recipient_id.document_page_id",
        store=True,
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        related="recipient_id.company_id",
        store=True,
        index=True,
    )
    user_id = fields.Many2one("res.users")
    partner_id = fields.Many2one("res.partner")
    attachment_id = fields.Many2one("ir.attachment", ondelete="set null")
    download_date = fields.Datetime()
    ip_address = fields.Char(string="IP Address")
    user_agent = fields.Char()
