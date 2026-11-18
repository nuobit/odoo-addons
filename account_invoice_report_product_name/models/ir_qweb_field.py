# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrQwebField(models.AbstractModel):
    _inherit = "ir.qweb.field"

    @api.model
    def record_to_html(self, record, field_name, options):
        # The invoice report sets this option on the span of a line's label, so
        # that a product line prints its product's name there, in the span's
        # widget. A view that makes that span print another field keeps the
        # option, so it applies to a line's label only.
        if (
            options.get("print_product_name")
            and record._name == "account.move.line"
            and field_name == "name"
            and record.product_id
        ):
            content = super().record_to_html(record.product_id, "name", options)
        else:
            content = super().record_to_html(record, field_name, options)
        return content
