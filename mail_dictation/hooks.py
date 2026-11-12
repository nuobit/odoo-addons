# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import SUPERUSER_ID, api

from .models.mail_dictation import PROVIDER_PARAM


def uninstall_hook(cr, registry):
    """Delete the choice of transcription service: the parameters of settings
    fields are not module data, so it would outlive the module."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["ir.config_parameter"].search([("key", "=", PROVIDER_PARAM)]).unlink()
