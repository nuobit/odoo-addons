# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    fields = [
        'input_current',
        'output_current',
    ]

    set_tmpl = "%(field)s = p.%(field)s_moved0"

    env.cr.execute(
        "UPDATE lighting_product p "
        "SET %s" % ', '.join([set_tmpl % dict(field=f) for f in fields])
    )
