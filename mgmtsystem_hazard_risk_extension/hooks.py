# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api

_MODULE = "mgmtsystem_hazard_risk_extension"


def _stock_formulas(env):
    """The formulas mgmtsystem_hazard_risk ships, found by their external ids."""
    external_ids = env["ir.model.data"].search(
        [
            ("module", "=", "mgmtsystem_hazard_risk"),
            ("model", "=", "mgmtsystem.hazard.risk.computation"),
        ]
    )
    return env["mgmtsystem.hazard.risk.computation"].browse(
        external_ids.mapped("res_id")
    )


def post_init_hook(cr, _registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _stock_formulas(env)._reload_description_translations(_MODULE)


def uninstall_hook(cr, _registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _stock_formulas(env)._delete_description_translations(_MODULE)
