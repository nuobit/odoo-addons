# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dev1@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def uninstall_hook(cr, _registry):
    """Schedule an update of the OCA module whose action this module overrides.
    Odoo runs it right after the uninstall, and the update loads that action
    again as the OCA module ships it."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    # the module name is unique (name_uniq); none is found when the OCA module
    # is being uninstalled too
    module = env["ir.module.module"].search(
        [
            ("name", "=", "document_page_environmental_aspect"),
            ("state", "=", "installed"),
        ]
    )
    if module:
        module.button_upgrade()
