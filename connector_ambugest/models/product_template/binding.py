# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

from odoo.addons.component.core import Component
from odoo.addons.queue_job.job import job
from odoo import exceptions


class ProductProduct(models.Model):
    _inherit = 'product.template'

    ambugest_bind_ids = fields.One2many(
        comodel_name='ambugest.product.template',
        inverse_name='odoo_id',
        string='Ambugest Bindings',
    )


class ProductProductBinding(models.Model):
    _name = 'ambugest.product.template'
    _inherit = 'ambugest.binding'
    _inherits = {'product.template': 'odoo_id'}

    odoo_id = fields.Many2one(comodel_name='product.template',
                              string='Product',
                              required=True,
                              ondelete='cascade')

    ## id
    ambugest_empresa = fields.Integer(string="Empresa on Ambugest", required=True)
    ambugest_id = fields.Integer(string="Id on Ambugest", required=True)

    _sql_constraints = [
        ('uniq', 'unique(odoo_id, ambugest_id, ambugest_empresa)',
         'Product with same ID on Ambugest already exists.'),
    ]

    @job(default_channel='root.ambugest')
    def import_products_since(self, backend_record=None, since_date=None):
        """ Prepare the import of products modified on Ambugest """
        filters = {
            'Empresa': backend_record.ambugest_company_id,
        }
        now_fmt = fields.Datetime.now()
        self.env['ambugest.product.template'].import_batch(
            backend=backend_record, filters=filters)
        backend_record.import_products_since_date = now_fmt

        return True
