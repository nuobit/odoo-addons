# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    oxigesti_bind_ids = fields.One2many(
        comodel_name="oxigesti.product.product",
        inverse_name="odoo_id",
        string="Oxigesti Bindings",
    )

    def unlink(self):
        to_remove = {}
        for record in self:
            to_remove[record.id] = [
                (binding.backend_id.id, binding._name, binding.external_id)
                for binding in record.oxigesti_bind_ids
            ]
        result = super(ProductProduct, self).unlink()
        for bindings_data in to_remove.values():
            self._event("on_record_post_unlink").notify(bindings_data)
        return result


class ProductProductBinding(models.Model):
    _name = "oxigesti.product.product"
    _inherit = "oxigesti.binding"
    _inherits = {"product.product": "odoo_id"}
    _description = "Product product binding"

    odoo_id = fields.Many2one(
        comodel_name="product.product",
        string="Odoo Product",
        required=True,
        ondelete="cascade",
    )

    @api.model
    def export_products_since(self, backend_record=None, since_date=None):
        """ Prepare the batch export of products modified on Odoo """
        domain = [("company_id", "in", (backend_record.company_id.id, False))]
        if since_date:
            domain += [
                "|",
                ("write_date", ">", since_date),
                ("product_tmpl_id.write_date", ">", since_date),
            ]
        now_fmt = fields.Datetime.now()
        self.export_batch(backend=backend_record, domain=domain)
        backend_record.export_products_since_date = now_fmt

        return True

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
