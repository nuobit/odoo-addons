# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class IrTranslation(models.Model):
    _inherit = "ir.translation"

    def _modified(self):
        # Odoo 14 tells a record that a translated field changed only for the
        # translation of its terms. The translation of a whole field, as the
        # translation dialog saves it, would leave the products that export
        # the field unmarked.
        super()._modified()
        for translation in self.filtered(lambda x: x.type == "model" and x.res_id):
            model_name, field_name = translation.name.split(",")
            if (
                model_name in ("product.template", "product.product")
                and field_name in self.env[model_name]._fields
            ):
                self.env[model_name].browse(translation.res_id).modified([field_name])
