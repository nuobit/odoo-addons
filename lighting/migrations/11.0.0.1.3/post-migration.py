# Copyright 2018 NuoBiT Solutions, S.L. - Eric Antones
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    # copy info from type to product
    env['lighting.product'].search([]).filtered(lambda x: x.type_id.is_accessory).write({'is_accessory': True, 'type_id': False})

    # delete types with accessory checked
    env['lighting.product.type'].search([('is_accessory', '=', True)]).unlink()
