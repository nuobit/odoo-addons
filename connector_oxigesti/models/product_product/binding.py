# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api

from odoo.addons.queue_job.job import job


class ProductProduct(models.Model):
    _inherit = 'product.product'

    oxigesti_bind_ids = fields.One2many(
        comodel_name='oxigesti.product.product',
        inverse_name='odoo_id',
        string='Oxigesti Bindings',
    )

    @api.multi
    def unlink(self):
        to_remove = {}
        for record in self:
            to_remove[record.id] = [
                (binding.backend_id.id, binding._name, binding.external_id) for binding in record.oxigesti_bind_ids
            ]
        result = super(ProductProduct, self).unlink()
        for bindings_data in to_remove.values():
            self._event('on_record_post_unlink').notify(bindings_data)
        return result


class ProductProductBinding(models.Model):
    _name = 'oxigesti.product.product'
    _inherit = 'oxigesti.binding'
    _inherits = {'product.product': 'odoo_id'}

    odoo_id = fields.Many2one(comodel_name='product.product',
                              string='Product',
                              required=True,
                              ondelete='cascade')

    @job(default_channel='root.oxigesti')
    @api.model
    def export_products_since(self, backend_record=None, since_date=None):
        """ Prepare the batch export of products modified on Odoo """
        domain = [
            ('company_id', '=', backend_record.company_id.id),
        ]
        if since_date:
            domain += [
                '|', ('write_date', '>', since_date),
                ('product_tmpl_id.write_date', '>', since_date)
            ]
        now_fmt = fields.Datetime.now()
        self.export_batch(backend=backend_record, domain=domain)
        backend_record.export_products_since_date = now_fmt

        return True

    @api.multi
    def resync(self):
        for record in self:
            with record.backend_id.work_on(record._name) as work:
                binder = work.component(usage='binder')
                relation = binder.unwrap_binding(self)

            func = record.export_record
            if record.env.context.get('connector_delay'):
                func = record.export_record.delay

            func(record.backend_id, relation)

        return True
