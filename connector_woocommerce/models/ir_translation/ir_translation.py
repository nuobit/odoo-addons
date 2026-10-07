# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class IrTranslation(models.Model):
    _inherit = "ir.translation"

    def _modified(self):
        # Odoo 14 tells a record that a translated field changed only for the
        # translation of its terms. The translation of a whole field, as the
        # translation dialog saves it, would leave the products that export
        # the field unmarked, and the attribute values, attributes and
        # categories out of their next export by date.
        super()._modified()
        for translation in self.filtered(lambda x: x.type == "model" and x.res_id):
            model_name, field_name = translation.name.split(",")
            if model_name in ("product.template", "product.product"):
                if field_name in self.env[model_name]._fields:
                    self.env[model_name].browse(translation.res_id).modified(
                        [field_name]
                    )
                # A translation of a field no longer installed marks nothing.
            elif model_name in (
                "product.attribute",
                "product.attribute.value",
                "product.public.category",
            ):
                # Their exports select by write date, which an empty write
                # stamps. A translation can outlive the record it translates,
                # and writing a deleted record fails when a record rule reads it.
                self.env[model_name].browse(translation.res_id).exists().write({})
            # A translation of any other model marks nothing here.
