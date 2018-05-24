# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade

from odoo.exceptions import UserError, ValidationError

@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    env.cr.execute(
        "select product_id from lighting_product_auxiliaryequipmentmodel where brand_id is null"
    )

    nobrand = []
    for row in env.cr.fetchall():
        nobrand.append(row[0])

    if nobrand != []:
        env.cr.execute(
            "select reference from lighting_product where id in (%s) order by reference", nobrand
        )

        prods = [row[0] for row in env.cr.fetchall()]
        if prods != []:
            raise ValidationError("Upgrade aborted -> There are auxiliary equipment models without brand: %s" % prods)
