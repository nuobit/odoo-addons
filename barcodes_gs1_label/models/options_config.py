# Copyright NuoBiT Solutions SL - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, api, fields, models
from odoo.exceptions import UserError


class BarcodesGS1LabelOptionsConfig(models.Model):
    _name = "barcodes.gs1.label.options.config"
    _description = "Barcodes GS1 Label Options Config"

    name = fields.Char(required=True)

    default = fields.Boolean()

    @api.model
    def _default_company_id(self):
        return self.env.company

    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        default=lambda self: self._default_company_id(),
        readonly=True,
    )

    @property
    def BARCODE_TYPE_SELECTION(self):
        return [
            ("gs1-128", "GS1-128"),
            ("gs1-datamatrix", "GS1-Datamatrix"),
            ("ean13-code128", "EAN13 + Code128"),
            ("ean13", "EAN13"),
        ]

    barcode_type = fields.Selection(
        string="Barcode type",
        selection=lambda self: self.BARCODE_TYPE_SELECTION,
        required=True,
    )

    @api.constrains("default")
    def _check_default(self):
        for rec in self:
            if rec.default:
                if (
                    self.search_count(
                        [("default", "=", True), ("company_id", "=", rec.company_id.id)]
                    )
                    > 1
                ):
                    raise UserError(
                        _("Only one label configuration can be set as default")
                    )

    format_id = fields.Many2one(
        string="Label format",
        comodel_name="barcodes.gs1.label.options.format",
        required=True,
    )

    show_price = fields.Boolean(string="Show price")
    show_price_currency = fields.Boolean(string="Show currency")

    @api.depends(
        "name",
        "barcode_type",
        "format_id.paperformat_id.name",
        "format_id.label_width",
        "format_id.label_height",
        "format_id.page_max_labels",
    )
    def _compute_display_name(self):
        barcode_type_labels = dict(
            self._fields["barcode_type"]._description_selection(self.env)
        )
        for rec in self:
            label_format = rec.format_id
            format_part = (
                f"{label_format.paperformat_id.name} "
                f"({label_format.label_width:g} x {label_format.label_height:g} mm) "
                f"[{label_format.page_max_labels}]"
                if label_format
                else None
            )
            barcode_type_part = (
                barcode_type_labels[rec.barcode_type] if rec.barcode_type else None
            )
            rec.display_name = " - ".join(
                part for part in (rec.name, format_part, barcode_type_part) if part
            )
