# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, api, fields, models
from odoo.exceptions import UserError


class BarcodesGS1LabelOptionsConfig(models.Model):
    _name = "barcodes.gs1.label.options.format"
    _description = "Barcodes GS1 Label Options Format"

    name = fields.Char(required=True)

    def _default_paperformat(self):
        return self.env.ref("barcodes_gs1_label.paperformat_gs1_barcodes")

    paperformat_id = fields.Many2one(
        string="Paper format",
        comodel_name="report.paperformat",
        required=True,
        default=_default_paperformat,
    )
    sheet_width = fields.Integer(
        string="Sheet width (mm)",
        required=True,
        compute="_compute_sheet_sizes",
    )
    sheet_height = fields.Integer(
        string="Sheet height (mm)",
        required=True,
        compute="_compute_sheet_sizes",
    )

    @api.depends("paperformat_id")
    def _compute_sheet_sizes(self):
        for rec in self:
            if not rec.paperformat_id.format:
                raise UserError(
                    _("The paperformat '%(paper_format)s' has no format defined")
                    % {"paper_format": rec.paperformat_id.display_name}
                )
            if not rec.paperformat_id.orientation:
                raise UserError(
                    _("The paperformat '%(paper_format)s' has no orientation defined")
                    % {"paper_format": rec.paperformat_id.display_name}
                )

            if rec.paperformat_id.format == "custom":
                page_width = rec.paperformat_id.page_width
                page_height = rec.paperformat_id.page_height
                # TODO: put this check inside a report format models a contraint
                if any(
                    [
                        rec.paperformat_id.orientation == "Landscape"
                        and page_width < page_height,
                        rec.paperformat_id.orientation == "Portrait"
                        and page_width > page_height,
                    ]
                ):
                    raise UserError(
                        _(
                            "The paperformat '%(paper_format)s' has no coherent "
                            "height and width with the selected orientation. "
                            "Either change the orientation "
                            "or adjust the values of height and width."
                        )
                        % {"paper_format": rec.paperformat_id.display_name}
                    )
                rec.sheet_width = page_width
                rec.sheet_height = page_height
            else:
                paper_data = rec.paperformat_id.get_paperformat_data()
                page_width = paper_data["width"]
                page_height = paper_data["height"]
                if page_width > page_height:
                    long_side = page_width
                    short_side = page_height
                else:
                    long_side = page_height
                    short_side = page_width
                if rec.paperformat_id.orientation == "Landscape":
                    rec.sheet_width = long_side
                    rec.sheet_height = short_side
                elif rec.paperformat_id.orientation == "Portrait":
                    rec.sheet_width = short_side
                    rec.sheet_height = long_side
                else:
                    raise UserError(
                        _(
                            "The paperformat '%(paper_format)s' has an "
                            "invalid orientation '%(orientation)s'"
                        )
                        % {
                            "paper_format": rec.paperformat_id.display_name,
                            "orientation": rec.paperformat_id.orientation,
                        }
                    )

    label_width = fields.Float(
        string="Label width (mm)",
        required=True,
    )
    label_height = fields.Float(
        string="Label height (mm)",
        required=True,
    )
    page_rows_max = fields.Integer(
        string="Max rows per page",
        required=True,
        compute="_compute_page_label_count",
    )
    page_cols_max = fields.Integer(
        string="Max columns per page",
        required=True,
        compute="_compute_page_label_count",
    )
    page_max_labels = fields.Integer(
        string="Max labels per page",
        required=True,
        compute="_compute_page_label_count",
    )

    @api.depends("sheet_width", "sheet_height", "label_width", "label_height")
    def _compute_page_label_count(self):
        for rec in self:
            if rec.label_width and rec.label_height:
                page_cols_max = int(rec.sheet_width / rec.label_width)
                page_rows_max = int(rec.sheet_height / rec.label_height)
                if page_cols_max == 0 and page_rows_max != 0:
                    page_rows_max = 0
                if page_rows_max == 0 and page_cols_max != 0:
                    page_cols_max = 0
                rec.page_cols_max = page_cols_max
                rec.page_rows_max = page_rows_max
                rec.page_max_labels = page_cols_max * page_rows_max
            else:
                rec.page_cols_max = 0
                rec.page_rows_max = 0
                rec.page_max_labels = 0
