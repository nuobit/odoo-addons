# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade

@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    # move color from product to special_spectrum on source lina
    env.cr.execute(
        "UPDATE lighting_product_ledchip lc "
        "SET source_line_id = l.id "
        "FROM lighting_product_source_line l, "
        "     lighting_product_source_type t, lighting_product_source s "
        "WHERE l.source_id = s.id AND "
        "      l.type_id = t.id AND "
        " 	   s.product_id = lc.product_id AND "
        " 	   t.is_led"
    )