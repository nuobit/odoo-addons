# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _, fields, models, api
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class VeloconnectBackend(models.Model):
    _name = "veloconnect.backend"
    _inherit = "connector.backend"
    _description = "Veloconnect Backend"

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

    veloconnect_user = fields.Char(
        help="Buyer id to access",
        required=True,
        # to_delete
        default="28802"
    )
    veloconnect_password = fields.Char(
        help="WebService password",
        required=True,
        # to_delete
        default="b2fumo0910",
    )

    veloconnect_url = fields.Char(
        # to_delete
        default="http://fuchs-movesa.velocom.de/fr",
    )

    import_sale_orders_since_date = fields.Datetime('Import Services since')
    import_products_name = fields.Char('Import Products with Name')

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Veloconnect Partner",
        required=True,
    )

    def _check_connection(self):
        self.ensure_one()
        with self.work_on('veloconnect.backend') as work:
            token = work.component_by_name(name='veloconnect.adapter')._exec('get_token')

    def button_check_connection(self):
        for rec in self:
            rec._check_connection()
            rec.write({'state': 'checked'})

    def button_reset_to_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})

    def import_products(self):
        # if self.user_id:
        #     self = self.sudo(self.user_id)
        for rec in self:
            # since_date = fields.Datetime.from_string(rec.import_sale_orders_since_date)
            # rec.import_sale_orders_since_date = fields.Datetime.now()
            self.env['veloconnect.product.template'].with_delay(
            ).import_products(backend_record=rec)
            # backend_record=rec, since_date=since_date)

    # scheduler
    @api.model
    def _scheduler_import(self):
        for backend in self.env["veloconnect.backend"].search([]):
            backend.import_products()
