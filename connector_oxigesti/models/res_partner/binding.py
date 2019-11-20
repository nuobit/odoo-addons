# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

from odoo.addons.component.core import Component
from odoo.addons.queue_job.job import job


class ResPartner(models.Model):
    _inherit = 'res.partner'

    oxigesti_bind_ids = fields.One2many(
        comodel_name='oxigesti.res.partner',
        inverse_name='odoo_id',
        string='Oxigesti Bindings',
    )


class ResPartnerBinding(models.Model):
    _name = 'oxigesti.res.partner'
    _inherit = 'oxigesti.binding'
    _inherits = {'res.partner': 'odoo_id'}

    odoo_id = fields.Many2one(comodel_name='res.partner',
                              string='Partner',
                              required=True,
                              ondelete='cascade')
    ## id
    oxigesti_codigo_mutua = fields.Integer(string="Codigo_Mutua on Oxigesti", required=True)

    _sql_constraints = [
        ('oxigesti_res_partner', 'unique(oxigesti_codigo_mutua)',
         'Partner with same ID on Oxigesti already exists.'),
    ]

    @job(default_channel='root.oxigesti')
    def import_customers_since(self, backend_record=None, since_date=None):
        """ Prepare the import of partners modified on Oxigesti """
        filters = {}
        now_fmt = fields.Datetime.now()
        self.env['oxigesti.res.partner'].import_batch(
            backend=backend_record, filters=filters)
        backend_record.import_customers_since_date = now_fmt

        return True
