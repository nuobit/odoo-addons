# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, models
from odoo.exceptions import UserError

from odoo.addons.base.models.report_paperformat import PAPER_SIZES

PAPER_SIZES_D = {x["key"]: x for x in PAPER_SIZES if x["key"] != "custom"}


class report_paperformat(models.Model):
    _inherit = "report.paperformat"

    @api.constrains("page_height", "page_width", "format")
    def _check_page_size(self):
        for rec in self:
            if rec.format == "custom":
                if rec.page_height < rec.page_width:
                    raise UserError(
                        _(
                            "The page height (%(height)s) must be greater than "
                            "the page width (%(width)s). Orientation will decide"
                            " ultimately which will be the large and short side."
                        )
                        % {
                            "height": rec.page_height,
                            "width": rec.page_width,
                        }
                    )

    def get_paperformat_data(self):
        if self.format not in PAPER_SIZES_D:
            raise UserError(
                _("The format '%(paper_format)s' has no data defined")
                % {"paper_format": self.format}
            )
        return PAPER_SIZES_D[self.format]

    def _compute_print_page_size(self):
        # return super()._compute_print_page_size()
        for rec in self:
            if rec.format == "custom":
                page_width = rec.page_width
                page_height = rec.page_height
            else:
                # paper_data = next(ps for ps in PAPER_SIZES if ps['key'] == rec.format)
                paper_data = rec.get_paperformat_data()
                page_width = paper_data["width"]
                page_height = paper_data["height"]

            if page_width > page_height:
                long_side = page_width
                short_side = page_height
            else:
                long_side = page_height
                short_side = page_width

            if rec.orientation == "Landscape":
                rec.print_page_width = long_side
                rec.print_page_height = short_side
            elif rec.orientation == "Portrait":
                rec.print_page_width = short_side
                rec.print_page_height = long_side
            else:
                raise UserError(
                    _(
                        "The paperformat '%(paper_format)s' has an "
                        "invalid orientation '%(orientation)s'"
                    )
                    % {
                        "paper_format": rec.display_name,
                        "orientation": rec.orientation,
                    }
                )
