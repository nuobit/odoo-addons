# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _, fields, models, api
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class LengowBackend(models.Model):
    _name = "lengow.backend"
    _inherit = "connector.backend"
    _description = "Lengow Backend"

    @api.model
    def _select_state(self):
        return [('draft', 'Draft'),
                ('checked', 'Checked'),
                ('production', 'In Production')]

    name = fields.Char("Name", required=True)

    state = fields.Selection(
        selection='_select_state',
        string='State',
        default='draft'
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        ondelete="restrict",
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        ondelete="restrict",
    )

    access_token = fields.Char(
        help="WebService Access Token",
        required=True,
    )
    secret = fields.Char(
        help="Webservice password",
        required=True,
    )
    base_url = fields.Char(
        default="https://api.lengow.net",
    )

    import_sale_orders_since_date = fields.Datetime('Import Services since')

    @api.multi
    def _check_connection(self):
        self.ensure_one()
        with self.work_on('lengow.backend') as work:
            token = work.component_by_name(name='lengow.adapter')._exec('get_token')
        if not token:
            raise UserError('Invalid token')

    @api.multi
    def button_check_connection(self):
        for rec in self:
            rec._check_connection()
            rec.write({'state': 'checked'})

    @api.multi
    def button_reset_to_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})

    @api.multi
    def import_sale_orders_since(self):
        for rec in self:
            since_date = fields.Datetime.from_string(rec.import_sale_orders_since_date)
            rec.import_sale_orders_since_date = fields.Datetime.now()
            self.env['lengow.sale.order'].with_delay(
            ).import_sale_orders_since(
                backend_record=rec, since_date=since_date)
