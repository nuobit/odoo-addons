# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_field_renames = [
    (
        "wordpress.backend",
        "wordpress_backend",
        "language_ids",
        "lang_ids",
    )
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return
    openupgrade.rename_fields(env, _field_renames)
