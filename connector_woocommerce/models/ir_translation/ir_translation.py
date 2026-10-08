# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


def _reaches_export_date(triggers):
    """Whether a WooCommerce export date is among the fields a trigger tree
    recomputes: on the same records, or on those reached through each
    relation."""
    return any(
        field.name == "woocommerce_write_date" for field in triggers.get(None, ())
    ) or any(
        _reaches_export_date(subtree)
        for relation, subtree in triggers.items()
        if relation is not None
    )


class IrTranslation(models.Model):
    _inherit = "ir.translation"

    def _modified(self):
        # Writing a field, from a form or from code, marks it as modified, and
        # that triggers every @api.depends on it. Saving only its translation,
        # from the translation dialog, writes the translation and not the
        # record, so no @api.depends is triggered: Odoo 14 marks the field in
        # this method only for the term translations of HTML and XML fields.
        # This override marks it for the translation of a whole field too,
        # when a WooCommerce export date depends on it, on its own record or
        # through a relation: a gallery image has no export date of its own,
        # but a module that sends the images' titles with their product makes
        # the product's date depend on them. Which export dates move is still
        # decided by the @api.depends of woocommerce_write_date.
        super()._modified()
        # One call carries every translation created, written or deleted
        # together: each translation of a whole field (type "model") that
        # belongs to a record is handled on its own.
        for translation in self.filtered(lambda x: x.type == "model" and x.res_id):
            # A whole field translation is named "<model>,<field>".
            model_name, field_name = translation.name.split(",")
            if model_name in self.env:
                model = self.env[model_name]
                if field_name in model._fields:
                    triggers = self.pool.field_triggers.get(
                        model._fields[field_name], {}
                    )
                    if _reaches_export_date(triggers):
                        model.browse(translation.res_id).modified([field_name])
                    # A field no export date depends on marks nothing.
                # A translation of a field no longer installed marks nothing.
            # A translation of a model no longer installed marks nothing.
