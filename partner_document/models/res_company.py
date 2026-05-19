# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    partner_document_request_data_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Request Data Email Template",
        domain=[("model", "=", "res.partner")],
    )
