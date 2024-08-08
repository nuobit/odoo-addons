# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class WooCommerceBinding(models.AbstractModel):
    _inherit = "woocommerce.binding"

    def _prepare_relation(self, relation, record):
        super()._prepare_relation(relation, record)
        context = relation.env.context.copy()
        iso_lang = self.env["res.lang"]._get_iso_code_from_wpml_code(
            record.woocommerce_lang
        )
        if iso_lang:
            context.update({"lang": iso_lang, "resync_export": True})
        relation.env.context = context
