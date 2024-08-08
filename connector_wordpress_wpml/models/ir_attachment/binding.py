# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class WordPressIrAttachment(models.Model):
    _inherit = "wordpress.ir.attachment"

    wordpress_lang = fields.Char(
        string="Language",
        required=True,
        ondelete="cascade",
    )

    _sql_constraints = [
        (
            "internal_uniq",
            "unique(backend_id, wordpress_lang, odoo_id)",
            "A binding already exists with the same Internal (Odoo) ID.",
        ),
        (
            "external_uniq",
            "unique(backend_id, wordpress_ir_attachment,"
            "wordpress_irattachment, wordpress_lang)",
            "A binding already exists with the same External (irAttachment) ID.",
        ),
    ]

    def _prepare_relation(self, relation, record):
        super()._prepare_relation(relation, record)
        context = relation.env.context.copy()
        iso_lang = self.env["res.lang"]._get_iso_code_from_wpml_code(
            record.wordpress_lang
        )
        if iso_lang:
            context.update({"lang": iso_lang, "resync_export": True})
        relation.env.context = context
