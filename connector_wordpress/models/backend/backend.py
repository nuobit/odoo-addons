# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class WordPressBackend(models.Model):
    _name = "wordpress.backend"
    _inherit = "connector.backend.extension"
    _description = "WordPress Backend"

    name = fields.Char(
        required=True,
    )
    url = fields.Char(
        help="WordPress URL",
        required=True,
    )
    wp_user = fields.Char(
        help="WordPress User",
        required=True,
    )
    wp_pass = fields.Char(
        help="WordPress Password",
        required=True,
    )
    consumer_key = fields.Char(
        help="WordPress Consumer Key",
        required=True,
    )
    consumer_secret = fields.Char(
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company,
        ondelete="restrict",
    )
    export_ir_attachment_since_date = fields.Datetime(
        string="Export Products Since",
    )

    def export_ir_attachment_since(self):
        self.env.user.company_id = self.company_id
        for rec in self:
            since_date = fields.Datetime.from_string(
                rec.export_ir_attachment_since_date
            )
            rec.export_ir_attachment_since_date = fields.Datetime.now()
            self.env["wordpress.ir.attachment"].export_ir_attachment_since(
                backend_record=rec, since_date=since_date
            )

    # scheduler
    @api.model
    def _scheduler_export_ir_attachment(self):
        for backend in self.env[self._name].search([]):
            backend.export_ir_attachment_since()
