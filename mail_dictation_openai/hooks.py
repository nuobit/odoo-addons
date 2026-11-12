# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import SUPERUSER_ID, api

from odoo.addons.mail_dictation.models.mail_dictation import PROVIDER_PARAM

from .models.mail_dictation_openai import SERVICE, SETTINGS_PARAMS


def uninstall_hook(cr, registry):
    """Delete this service's settings, and the choice of this service: the
    parameters of settings fields are not module data, so the service's key
    would outlive the module, and dictation would point to a service that is
    gone."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["ir.config_parameter"].search(
        [
            "|",
            ("key", "in", SETTINGS_PARAMS),
            "&",
            ("key", "=", PROVIDER_PARAM),
            ("value", "=", SERVICE),
        ]
    ).unlink()
