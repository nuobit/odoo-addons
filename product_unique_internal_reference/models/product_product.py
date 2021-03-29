# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.constrains("default_code")
    def _check_default_code(self, template_default_code=None):
        for record in self:
            default_code = template_default_code or record.default_code
            if default_code:
                domain = [
                    ("default_code", "=", default_code),
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
                            "Error! The Default Code %s already exists. "
                            "Check also the archived ones." % product.default_code
                        )
                    )
