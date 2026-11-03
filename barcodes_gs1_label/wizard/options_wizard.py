# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

MMS_PER_DPI = 25.4


class BarcodesGS1PrintOptionsWizard(models.TransientModel):
    _name = "barcodes.gs1.label.options.wizard"
    _description = "Barcodes GS1 Print Options Wizard"

    @property
    def MAP_MODEL_REPORT(self):
        return {
            "product.product": "barcodes_gs1_label.action_report_product_gs1_barcodes",
            "stock.lot": "barcodes_gs1_label.action_report_lot_gs1_barcodes",
            "stock.picking": "barcodes_gs1_label.action_report_picking_gs1_barcodes",
            "stock.quant": "barcodes_gs1_label.action_report_quant_gs1_barcodes",
            "mrp.production": "barcodes_gs1_label_mrp."
            "action_report_mrp_production_gs1_barcodes",
        }

    # the records the wizard was opened on, kept from the action that opened it
    res_model = fields.Char(
        string="Model", default=lambda self: self.env.context.get("active_model")
    )
    res_ids = fields.Json(
        string="Records", default=lambda self: self.env.context.get("active_ids")
    )
    prints_products_or_lots = fields.Boolean(compute="_compute_prints_products_or_lots")

    @api.depends("res_model")
    def _compute_prints_products_or_lots(self):
        # products and lots print with their stock and the weight asked here;
        # the other records print the quantities they hold
        for wizard in self:
            wizard.prints_products_or_lots = wizard.res_model in (
                "product.product",
                "stock.lot",
            )

    start_row = fields.Integer(string="Start row", default=1)
    start_col = fields.Integer(string="Start column", default=1)
    with_stock = fields.Boolean(string="With stock only", default=True)

    weight = fields.Float(string="Weight (Kg)", digits=(6, 6))
    show_weight = fields.Boolean(string="Show weight", compute="_compute_show_weight")

    @api.depends("label_config_id.show_weight", "label_config_id.weight_available")
    def _compute_show_weight(self):
        for rec in self:
            rec.show_weight = (
                rec.label_config_id.show_weight and rec.label_config_id.weight_available
            )

    label_copies = fields.Integer(string="Copies", default=1, required=True)

    def all_location_ids(self):
        return self.env["stock.location"].search(
            [
                ("usage", "=", "internal"),
                ("company_id", "=", self.env.company.id),
            ]
        )

    stock_location_ids = fields.Many2many(
        string="Locations",
        comodel_name="stock.location",
        compute="_compute_stock_location_ids",
        store=True,
        readonly=False,
    )

    @api.depends("with_stock", "res_model", "res_ids")
    def _compute_stock_location_ids(self):
        all_locs = self.all_location_ids()
        for wizard in self:
            if wizard.with_stock:
                ids = wizard.res_ids
                model = wizard.res_model
                if model == "product.product":
                    locations = self.env["stock.location"]
                    for doc in (
                        self.env[model]
                        .browse(ids)
                        .sorted(lambda x: x.default_code or "")
                    ):
                        locations |= (
                            self.env["stock.quant"]
                            .search(
                                [
                                    ("product_id", "=", doc.id),
                                    ("location_id.usage", "=", "internal"),
                                    ("location_id", "in", all_locs.ids),
                                    ("quantity", ">", 0),
                                    ("company_id", "=", self.env.company.id),
                                ]
                            )
                            .mapped("location_id")
                        )
                    wizard.stock_location_ids = locations
                elif model == "stock.lot":
                    locations = self.env["stock.location"]
                    for doc in (
                        self.env[model]
                        .browse(ids)
                        .filtered(lambda x: x.product_id.tracking in ("lot", "serial"))
                        .sorted(lambda x: x.product_id.default_code or "")
                    ):
                        locations |= (
                            self.env["stock.quant"]
                            .search(
                                [
                                    ("product_id", "=", doc.product_id.id),
                                    ("location_id.usage", "=", "internal"),
                                    ("location_id", "in", all_locs.ids),
                                    ("lot_id", "=", doc.id),
                                    ("quantity", ">", 0),
                                    ("company_id", "=", self.env.company.id),
                                ]
                            )
                            .mapped("location_id")
                        )
                    wizard.stock_location_ids = locations
                else:
                    wizard.stock_location_ids = all_locs
            else:
                wizard.stock_location_ids = all_locs

    def _default_label_config_id(self):
        return self.env["barcodes.gs1.label.options.config"].search(
            [("default", "=", True), ("company_id", "=", self.env.company.id)]
        )

    label_config_id = fields.Many2one(
        comodel_name="barcodes.gs1.label.options.config",
        required=True,
        default=_default_label_config_id,
    )

    px_mm_rate_correction = fields.Float(
        string="px/mm rate correction", required=True, default=1.25
    )
    show_borders = fields.Boolean(string="Show borders", default=False)
    border_color = fields.Char(string="Border color", default="#e5e5e5")

    @api.constrains("with_stock", "stock_location_ids")
    def _check_stock_location_ids(self):
        for wizard in self:
            if (
                wizard.prints_products_or_lots
                and wizard.with_stock
                and not wizard.stock_location_ids
            ):
                raise ValidationError(
                    _(
                        "Choose the locations whose stock is printed, or untick "
                        '"With stock only".'
                    )
                )

    @api.constrains("show_borders", "border_color")
    def _check_border_color(self):
        for wizard in self:
            if wizard.show_borders and not wizard.border_color:
                raise ValidationError(
                    _("Choose the color of the borders, or do not show them.")
                )

    def print_product_barcodes(self):
        # checks
        self.label_config_id.format_id._check_paperformat_id()
        if (
            self.start_col < 1
            or self.start_col > self.label_config_id.format_id.page_cols_max
        ):
            raise UserError(
                _("Start column should be between %(min_col)i and %(max_col)i")
                % {
                    "min_col": 1,
                    "max_col": self.label_config_id.format_id.page_cols_max,
                }
            )
        if (
            self.start_row < 1
            or self.start_row > self.label_config_id.format_id.page_rows_max
        ):
            raise UserError(
                _("Start row should be between %(min_row)i and %(max_row)i")
                % {
                    "min_row": 1,
                    "max_row": self.label_config_id.format_id.page_rows_max,
                }
            )
        if self.label_copies < 1:
            raise UserError(_("The number of copies must be greater than 0"))

        model = self.res_model
        mm_px_rate = (
            self.label_config_id.format_id.paperformat_id.dpi
            / MMS_PER_DPI
            * self.px_mm_rate_correction
        )
        max_width_mm = (
            self.label_config_id.format_id.label_width
            * self.label_config_id.format_id.page_cols_max
        )
        widths_px = [
            int(self.label_config_id.format_id.label_width * mm_px_rate)
        ] * self.label_config_id.format_id.page_cols_max
        diff = int(max_width_mm * mm_px_rate - sum(widths_px))
        i = 0
        while diff:
            widths_px[i] += 1
            i = (i + 1) % self.label_config_id.format_id.page_cols_max
            diff -= 1
        padding_width_mm = self.label_config_id.format_id.sheet_width - max_width_mm
        max_height_mm = (
            self.label_config_id.format_id.label_height
            * self.label_config_id.format_id.page_rows_max
        )
        heights_px = [
            int(self.label_config_id.format_id.label_height * mm_px_rate)
        ] * self.label_config_id.format_id.page_rows_max
        diff = int(max_height_mm * mm_px_rate - sum(heights_px))
        i = 0
        while diff:
            heights_px[i] += 1
            i = (i + 1) % self.label_config_id.format_id.page_rows_max
            diff -= 1
        padding_height_mm = self.label_config_id.format_id.sheet_height - max_height_mm

        data = {
            "from_print_wizard": True,
            "ids": self.res_ids,
            "model": model,
            "lang_id": 1,
            "with_stock": self.with_stock,
            "stock_location_ids": self.stock_location_ids.ids,
            "show_price": self.label_config_id.show_price,
            "show_price_currency": (
                self.label_config_id.show_price_currency
                or not self.label_config_id.currency_optional
            ),
            "barcode_type": self.label_config_id.barcode_type,
            "show_weight": self.show_weight,
            "weight": self.weight,
            "layout": {
                "container_top": int(padding_height_mm * mm_px_rate / 2),
                "container_left": int(padding_width_mm * mm_px_rate / 2),
                "container_width": sum(widths_px),
                "container_height": sum(heights_px),
                "label_copies": self.label_copies,
                "labels_page_count": self.label_config_id.format_id.page_max_labels,
                "cols": self.label_config_id.format_id.page_cols_max,
                "start_cell": (self.start_row - 1)
                * self.label_config_id.format_id.page_cols_max
                + self.start_col,
                "label_widths": widths_px,
                "label_heights": heights_px,
                "label_landscape": self.label_config_id.format_id.label_width
                > self.label_config_id.format_id.label_height,
                "show_borders": self.show_borders,
                "border_color": self.border_color,
            },
        }
        return (
            self.env.ref(self.MAP_MODEL_REPORT[model])
            .with_context(
                no_paddings=True,
                paperformat_id=self.label_config_id.format_id.paperformat_id.id,
            )
            .report_action(self, data=data)
        )
