# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class IrTranslation(models.Model):
    _inherit = "ir.translation"

    def _modified(self):
        # Odoo 14 tells a record that a translated field changed only for the
        # translation of its terms. The translation of a whole field, as the
        # translation dialog saves it, marks here the record it translates as
        # its model declares in `_woocommerce_translation_marking`: "depends"
        # when its export date depends on the translated fields, "write_date"
        # when its export selects by write date.
        super()._modified()
        for translation in self.filtered(lambda x: x.type == "model" and x.res_id):
            model_name, field_name = translation.name.split(",")
            if model_name in self.env:
                model = self.env[model_name]
                marking = getattr(model, "_woocommerce_translation_marking", None)
                if marking == "depends":
                    if field_name in model._fields:
                        model.browse(translation.res_id).modified([field_name])
                    # A translation of a field no longer installed marks nothing.
                elif marking == "write_date":
                    # An empty write stamps the write date. A translation can
                    # outlive the record it translates, and writing a deleted
                    # record fails when a record rule reads it.
                    model.browse(translation.res_id).exists().write({})
                elif marking is not None:
                    raise ValueError(
                        "%s: unknown _woocommerce_translation_marking %r"
                        % (model_name, marking)
                    )
                # A model that declares no marking is not marked.
            # A translation of a model no longer installed marks nothing.
