# Copyright 2025 NuoBiT - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailWhatsAppTemplateVariable(models.Model):
    _name = "mail.whatsapp.template.variable"
    _description = "Mail WhatsApp template variable"
    _order = "name"

    template_id = fields.Many2one(comodel_name="mail.whatsapp.template")
    template_state = fields.Selection(related="template_id.state", readonly=True)
    section = fields.Selection(
        selection=[("body", "Body")],
    )
    name = fields.Char()
    parameter_type = fields.Selection(
        selection=[("text", "Text")],
    )
    default_value = fields.Char()
