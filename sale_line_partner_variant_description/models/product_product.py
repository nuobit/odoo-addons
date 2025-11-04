# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _extract_part(self, part, name):
        m = re.match(r"^(.*)\n(%s)(.*)$" % re.escape(part), name, re.DOTALL)
        if m:
            desc = m.group(2)
            rest = m.group(1) + m.group(3)
        else:
            raise ValidationError(_("Unexpected format in product name: %s") % name)
        return desc, rest

    def get_product_multiline_description_sale(self):
        name = super().get_product_multiline_description_sale()
        if name:
            # extract description parts
            m = re.match(r"^(\[[^]]+\]) ([^\n]+)(\n.*)?$", name)
            if m:
                code, desc, rest = m.groups()
            else:
                m = re.match(r"^([^\n]+)(\n.*)?$", name)
                if m:
                    code, desc, rest = (None, *m.groups())
                else:
                    raise ValidationError(
                        _("Unexpected format in product name: %s") % name
                    )

            # build the new description line
            name_l = []
            ref_part_l = []
            if code:
                ref_part_l.append(code)

            cand_desc = None
            if rest:
                if self.variant_description_sale:
                    cand_desc, rest = self._extract_part(
                        self.variant_description_sale, rest
                    )
                else:
                    if self.description_sale:
                        cand_desc, rest = self._extract_part(
                            self.description_sale, rest
                        )

            buyer = self._get_buyer_data().get(self.id)
            if not buyer or not buyer.name:
                if cand_desc:
                    ref_part_l.append(cand_desc)
                else:
                    ref_part_l.append(desc)
            else:
                ref_part_l.append(desc)

            if ref_part_l:
                name_l.append(" ".join(ref_part_l))

            if rest:
                name_l.append(rest)

            if name_l:
                name = "".join(name_l)

        return name
