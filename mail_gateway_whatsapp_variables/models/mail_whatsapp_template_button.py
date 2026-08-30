# Copyright 2025 NuoBiT - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailWhatsAppTemplateButton(models.Model):
    _name = "mail.whatsapp.template.button"
    _description = "Mail WhatsApp template button"

    template_id = fields.Many2one(comodel_name="mail.whatsapp.template")
    template_state = fields.Selection(related="template_id.state", readonly=True)
    text = fields.Char()
    url = fields.Char()
    url_type = fields.Selection(
        selection=[("static", "Static"), ("dynamic", "Dynamic")],
        string="URL Type",
    )
