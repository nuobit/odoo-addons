# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def comment_to_note(cr):
    cr.execute(
        """
        UPDATE account_asset
        SET note = NULLIF(COALESCE(note, '') || COALESCE(comment, ''), '')"""
    )
    cr.execute(
        """
        ALTER TABLE account_asset
        DROP COLUMN comment
        """
    )


def migrate(cr, version):
    comment_to_note(cr)
