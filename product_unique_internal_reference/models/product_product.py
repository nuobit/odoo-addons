# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT 2025 - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.constrains("default_code")
    def _check_default_code(self):
        for record in self:
            if record.default_code:
                domain = [
                    ("default_code", "=", record.default_code),
                    ("id", "!=", record.id),
                ]
                if record.product_tmpl_id.company_id:
                    domain += [
                        "|",
                        (
                            "product_tmpl_id.company_id",
                            "=",
                            record.product_tmpl_id.company_id.id,
                        ),
                        ("product_tmpl_id.company_id", "=", False),
                    ]
                product = (
                    self.sudo()
                    .with_context(active_test=False)
                    .search(
                        domain,
                        limit=1,
                    )
                )
                if product:
                    raise ValidationError(
                        _(
                            "Error! The Default Code {} already exists. "
                            "Check also the archived ones."
                        ).format(record.default_code)
                    )
