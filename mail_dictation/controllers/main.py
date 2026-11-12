# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from werkzeug.datastructures import FileStorage

from odoo import _, http
from odoo.exceptions import UserError
from odoo.http import request

# The largest recording the route forwards, in bytes. A dictation stops at two
# minutes, which the browsers record in 1 to 2 MB: only a request that does not
# come from the composer reaches this bound. The transcription service's own
# limit is the service's to enforce.
MAX_AUDIO_SIZE = 25 * 1024 * 1024


class MailDictationController(http.Controller):
    @http.route(
        "/mail_dictation/transcribe", type="http", auth="user", methods=["POST"]
    )
    def mail_dictation_transcribe(self, audio=None, **kwargs):
        """Return the text of the recording ``audio`` as ``{"text": …}``, or
        ``{"error": …}`` with the message for the user."""
        if not request.env.user._is_internal():
            return request.make_json_response(
                {"error": _("Only internal users can dictate.")}, status=403
            )
        if not isinstance(audio, FileStorage):
            # The composer always sends the recording as a file.
            return request.make_json_response(
                {"error": _("The request carries no recording.")}, status=400
            )
        content = audio.read(MAX_AUDIO_SIZE + 1)
        if len(content) > MAX_AUDIO_SIZE:
            return request.make_json_response(
                {"error": _("The recording is too long to be transcribed.")},
                status=413,
            )
        try:
            text = request.env["mail.dictation"]._transcribe(
                content, audio.filename, audio.mimetype
            )
        except UserError as error:
            return request.make_json_response({"error": error.args[0]})
        return request.make_json_response({"text": text})
