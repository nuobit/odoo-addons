# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class MailDictationFake(models.AbstractModel):
    """A transcription service, as a service's module adds one."""

    _name = "mail.dictation.fake"
    _description = "Fake dictation service"

    @api.model
    def _transcribe(self, audio, filename, mimetype):
        # Each test patches the answer it needs.
        raise NotImplementedError
