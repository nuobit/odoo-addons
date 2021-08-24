# Copyright 2021 ForgeFlow S.L. <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["res.partner"].with_context(active_test=False).search(
        []
    )._compute_display_name()
