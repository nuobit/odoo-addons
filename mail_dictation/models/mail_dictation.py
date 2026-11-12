# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, api, models
from odoo.exceptions import UserError

# The parameter that holds the transcription service chosen in Settings >
# Discuss: the settings write it, the dispatch reads it, and the uninstall hook
# deletes it.
PROVIDER_PARAM = "mail_dictation.provider"


class MailDictation(models.AbstractModel):
    _name = "mail.dictation"
    _description = "Dictation"

    @api.model
    def _transcribe(self, audio, filename, mimetype):
        """Return the text the chosen transcription service hears in ``audio``,
        without the whitespace around it: an answer of whitespace only is no
        words.

        The service is the model ``mail.dictation.<service>`` of the module
        that adds it to the choice in Settings > Discuss (as OCA's
        ``mail_gateway`` dispatches to ``mail.gateway.<type>``). Every failure
        raises a ``UserError`` whose message is meant for the user.

        Private, so that only the route, which refuses users who are not
        internal, can reach it: a public method could be called over RPC.
        """
        provider = self.env["ir.config_parameter"].sudo().get_param(PROVIDER_PARAM)
        service = self.env.get(f"mail.dictation.{provider}") if provider else None
        if service is None:
            # No service chosen, or the module of the chosen one is gone.
            raise UserError(
                _(
                    "Dictation is not configured: an administrator must choose "
                    "the transcription service in Settings > Discuss."
                )
            )
        return service._transcribe(audio, filename, mimetype).strip()
