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
        "UPDATE lighting_product_source_line l "
        "SET special_spectrum = coalesce(l.special_spectrum, p.color) "
        "FROM lighting_product_source_type t, lighting_product_source s, "
        "     lighting_product p "
        "WHERE l.source_id = s.id AND "
        "      l.type_id = t.id AND "
        "      s.product_id = p.id AND "
        "      t.is_led AND "
        "      ((l.special_spectrum is not null AND p.color is null) OR "
        "       (l.special_spectrum is null AND p.color is not null) OR "
        "       (l.special_spectrum is not null AND p.color is not null AND l.special_spectrum != p.color))"
    )