# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_column_renames = {
    "res_lang_wordpress_backend_rel": [
        ("wordpress_backend_id", "backend_id"),
        ("res_lang_id", "lang_id"),
    ]
}


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return
    openupgrade.rename_columns(env.cr, _column_renames)

    env.cr.execute(
        """
                ALTER TABLE res_lang_wordpress_backend_rel
                RENAME CONSTRAINT
                res_lang_wordpress_backend_rel_wordpress_backend_id_fkey
                TO res_lang_wordpress_backend_rel_backend_id_fkey;
            """
    )

    env.cr.execute(
        """
                    ALTER TABLE res_lang_wordpress_backend_rel
                    RENAME CONSTRAINT
                    res_lang_wordpress_backend_rel_res_lang_id_fkey
                    TO res_lang_wordpress_backend_rel_lang_id_fkey;
                """
    )
