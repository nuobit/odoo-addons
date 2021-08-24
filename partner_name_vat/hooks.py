# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import SUPERUSER_ID, api


def post_init_hook_vat_update(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["res.partner"].with_context(active_test=False).search(
        []
    )._compute_display_name()


def uninstall_hook_vat_remove(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["res.partner"].with_context(active_test=False).search(
        []
    )._compute_display_name()
