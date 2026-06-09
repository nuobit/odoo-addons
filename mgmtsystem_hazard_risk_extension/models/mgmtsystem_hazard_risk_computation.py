# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MgmtsystemHazardRiskComputation(models.Model):
    _inherit = "mgmtsystem.hazard.risk.computation"

    # The OCA base module (mgmtsystem_hazard_risk) defines ``description`` as a
    # plain, non-translatable Text field, so the risk-formula descriptions can
    # only ever be shown in English. Redeclaring the field as translatable lets
    # those descriptions be presented in the user's language; the Spanish and
    # Catalan values ship in this module's i18n/ files.
    description = fields.Text(translate=True)
