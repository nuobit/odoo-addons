# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models

from .mail_dictation import PROVIDER_PARAM


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Each service's module adds itself with selection_add.
    mail_dictation_provider = fields.Selection(
        [],
        string="Transcription Service",
        config_parameter=PROVIDER_PARAM,
        help="Service that turns the dictated voice into text.",
    )
