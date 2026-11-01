# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT 2025 - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.constrains("default_code", "company_id")
    def _check_default_code(self):
        for record in self:
            if record.default_code:
                # all products with the same default_code
                products_all = (
                    self.env["product.product"]
                    .sudo()
                    .with_context(active_test=False)
                    .search(
                        [
                            ("default_code", "=", record.default_code),
                        ]
                    )
                )
                # products inside the same template
                products_inside = products_all.filtered(
                    lambda p, record=record: p.product_tmpl_id == record
                )
                # products outside the same template
                products_outside = products_all - products_inside
                if record.company_id:
                    products_outside = products_outside.filtered(
                        lambda p, record=record: not p.product_tmpl_id.company_id
                        or p.product_tmpl_id.company_id == record.company_id
                    )
                # check if the default code is used in other templates
                if len(products_inside) > 1 or products_outside:
                    raise ValidationError(
                        _(
                            "Error! The Default Code {} already exists. "
                            "Check also the archived ones."
                        ).format(record.default_code)
                    )
