# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api

_MODULE = "mgmtsystem_hazard_risk_extension"
_OWNER_MODULE = "mgmtsystem_hazard_risk"
_DESCRIPTION_NAME = "mgmtsystem.hazard.risk.computation,description"
_TRANSLATION_LANGS = ("ca_ES", "es_ES")
_FORMULA_XMLIDS = (
    "mgmtsystem_hazard_risk.risk_computation_a_times_b_times_c",
    "mgmtsystem_hazard_risk.risk_computation_a_times_b",
    "mgmtsystem_hazard_risk.risk_computation_a_plus_b",
    "mgmtsystem_hazard_risk.risk_computation_a_times_b_plus_c",
    "mgmtsystem_hazard_risk.risk_computation_a_plus_b_times_c",
    "mgmtsystem_hazard_risk.risk_computation_a_plus_b_plus_c",
)


def _formula_ids(env):
    return [
        record.id
        for record in (
            env.ref(xmlid, raise_if_not_found=False) for xmlid in _FORMULA_XMLIDS
        )
        if record
    ]


def _delete_formula_translations(env):
    formula_ids = _formula_ids(env)
    if formula_ids:
        env["ir.translation"].search(
            [
                ("type", "=", "model"),
                ("name", "=", _DESCRIPTION_NAME),
                ("res_id", "in", formula_ids),
                ("lang", "in", _TRANSLATION_LANGS),
            ]
        ).unlink()


def post_init_hook(cr, _registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _delete_formula_translations(env)
    module = env["ir.module.module"].search(
        [("name", "=", _MODULE)],
        limit=1,
    )
    module._update_translations(overwrite=True)


def uninstall_hook(cr, _registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _delete_formula_translations(env)
    owner = env["ir.module.module"].search(
        [("name", "=", _OWNER_MODULE), ("state", "=", "installed")],
        limit=1,
    )
    owner._update_translations(overwrite=True)
