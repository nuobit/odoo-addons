# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, models
from odoo.exceptions import UserError

from odoo.addons.base.models.report_paperformat import PAPER_SIZES

PAPER_SIZES_D = {x["key"]: x for x in PAPER_SIZES if x["key"] != "custom"}


class report_paperformat(models.Model):
    _inherit = "report.paperformat"

    def get_paperformat_data(self):
        if self.format not in PAPER_SIZES_D:
            raise UserError(
                _("The format '%(paper_format)s' has no data defined")
                % {"paper_format": self.format}
            )
        return PAPER_SIZES_D[self.format]
