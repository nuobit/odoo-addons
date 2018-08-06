# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade

@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    # move data to new color_consistency field
    env.cr.execute(
        "UPDATE lighting_product_source_line l "
        "SET color_consistency = p.color_consistency "
        "FROM lighting_product_source_type t, lighting_product_source s, "
        "     lighting_product p "
        "WHERE l.source_id = s.id and "
        "      l.type_id = t.id and "
	    "      s.product_id = p.id and "
	    "      t.is_led and "
        "      p.color_consistency != 0"
    )