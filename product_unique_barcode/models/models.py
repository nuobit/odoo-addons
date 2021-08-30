# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.constrains("barcode")
    def _check_barcode(self):
        for record in self:
            if record.barcode:
                barcode = self.search(
                    [
                        (
                            "product_tmpl_id.company_id",
                            "=",
                            record.product_tmpl_id.company_id.id,
                        ),
                        ("barcode", "=", record.barcode),
                        ("id", "!=", record.id),
                    ],
                    limit=1,
                )

                if barcode:
                    raise ValidationError(
                        _("Error! The Barcode %s already exists" % record.barcode)
                    )

    # replace current sql_constraint with a dummy one
    _sql_constraints = [
        (
            "barcode_uniq",
            "unique(barcode, id)",
            "A barcode can only be assigned to one product !",
        ),
    ]
