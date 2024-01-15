# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

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

    # reglas de registro y buscas company
    @api.depends("paperformat_id")
    def _compute_sheet_sizes(self):
        for rec in self:
            if not rec.paperformat_id.format:
                raise UserError(
                    _("The paperformat '%s' has no format defined")
                    % rec.paperformat_id.display_name
                )

            if rec.paperformat_id.format == "custom":
                rec.sheet_width = int(rec.paperformat_id.page_width)
                rec.sheet_height = int(rec.paperformat_id.page_height)
            else:
                format_map = dict(
                    rec.paperformat_id.with_context(lang=None).fields_get(
                        "format", "selection"
                    )["format"]["selection"]
                )

                format_str = format_map[rec.paperformat_id.format]
                m = re.search("([0-9]+) +x +([0-9]+) +mm", format_str)
                if not m:
                    raise UserError(
                        _(
                            "Wrong paperformat definition '%s', "
                            "cannot extract sheet sizes from it"
                        )
                        % (rec.paperformat_id.display_name,)
                    )

                rec.sheet_width = int(m.group(1))
                rec.sheet_height = int(m.group(2))

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
                rec.page_cols_max = int(rec.sheet_width / rec.label_width)
                rec.page_rows_max = int(rec.sheet_height / rec.label_height)
                rec.page_max_labels = rec.page_cols_max * rec.page_rows_max
            else:
                rec.page_cols_max = 0
                rec.page_rows_max = 0
                rec.page_max_labels = 0
