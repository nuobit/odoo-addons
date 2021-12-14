# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, fields, models

from odoo.addons.queue_job.job import job


class ProductCategoryBinding(models.Model):
    _name = "oxigesti.product.category"
    _inherit = "oxigesti.binding"
    _inherits = {"product.category": "odoo_id"}

    odoo_id = fields.Many2one(
        comodel_name="product.category",
        string="Product Category",
        required=True,
        ondelete="cascade",
    )

    @job(default_channel="root.oxigesti")
    @api.model
    def export_product_categories_since(self, backend_record=None, since_date=None):
        """ Prepare the batch export of product categories modified on Odoo """
        domain = []
        if since_date:
            domain += [("write_date", ">", since_date)]
        now_fmt = fields.Datetime.now()
        self.export_batch(backend=backend_record, domain=domain)
        backend_record.export_product_categories_since_date = now_fmt

        return True

    @api.multi
    def resync(self):
        for record in self:
            with record.backend_id.work_on(record._name) as work:
                binder = work.component(usage="binder")
                relation = binder.unwrap_binding(self)

            func = record.export_record
            if record.env.context.get("connector_delay"):
                func = record.export_record.delay

            func(record.backend_id, relation)

        return True
