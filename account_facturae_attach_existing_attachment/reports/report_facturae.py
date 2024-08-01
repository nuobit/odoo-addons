# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class ReportFacturae(models.AbstractModel):
    _inherit = "report.l10n_es_facturae.facturae_signed"

    @api.model
    def generate_report(self, ir_report, docids, data=None):
        ir_report = ir_report.with_context(facturae_signed=True)
        return super(ReportFacturae, self).generate_report(ir_report, docids, data)
