# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models

from .mail_dictation_openai import (
    ADDRESS_PARAM,
    API_KEY_PARAM,
    DEFAULT_ADDRESS,
    DEFAULT_MODEL,
    MODEL_PARAM,
    SERVICE,
)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    mail_dictation_provider = fields.Selection(
        selection_add=[(SERVICE, "OpenAI-compatible service")],
        ondelete={SERVICE: "set null"},
    )
    mail_dictation_address = fields.Char(
        string="Dictation Service Address",
        config_parameter=ADDRESS_PARAM,
        default=DEFAULT_ADDRESS,
        help="Address of the OpenAI-compatible transcription API: the voice "
        "is sent to this address followed by /audio/transcriptions.",
    )
    mail_dictation_api_key = fields.Char(
        string="Dictation Service Key",
        config_parameter=API_KEY_PARAM,
        help="Key of the transcription service, sent as a bearer token.",
    )
    mail_dictation_model = fields.Char(
        string="Dictation Model",
        config_parameter=MODEL_PARAM,
        default=DEFAULT_MODEL,
        help="Transcription model of the service that turns the voice into text.",
    )
