# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo import SUPERUSER_ID


def post_init_hook_vat_update(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['res.partner'].search([])._compute_display_name()

def uninstall_hook_vat_remove(cr, registry):
    cr.execute(
        "update res_partner p "
        "set display_name = (case when p.vat is null then p.display_name "
        "     else replace(p.display_name, ' (' || p.vat || ')', '') end)"
    )

    # TODO: do it with api
    # env = api.Environment(cr, SUPERUSER_ID, {})
    # if 'res.partner' in env:
    #     env['res.partner'].search([])._compute_display_name()
