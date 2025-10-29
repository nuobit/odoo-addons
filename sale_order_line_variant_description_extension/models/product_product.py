# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    def get_product_multiline_description_sale(self):
        name = super().get_product_multiline_description_sale()
        if self.variant_description_sale:
            if self.description_sale:
                name = name.replace(
                    self.description_sale, self.variant_description_sale
                )
            else:
                m = re.match(
                    r"^(%s)(.*)$" % re.escape(self.display_name), name, re.DOTALL
                )
                if not m:
                    raise ValidationError(
                        _("Unexpected format in product name: %s") % name
                    )
                name = f"{m.group(1)}\n{self.variant_description_sale}{m.group(2)}"
        return name
