# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    oxigesti_bind_ids = fields.One2many(
        comodel_name="oxigesti.product.product",
        inverse_name="odoo_id",
        string="Oxigesti Bindings",
    )

    @api.constrains("default_code")
    def _check_oxigesti_default_code(self):
        for rec in self:
            if rec.oxigesti_bind_ids.filtered("external_id_hash"):
                raise ValidationError(
                    _(
                        "You can't change the default code of a "
                        "product that has bindings to oxigesti"
                    )
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
    def export_data(self, backend, since_date):
        domain = [("company_id", "=", backend.company_id.id)]
        if since_date:
            domain += [
                "|",
                ("write_date", ">", since_date),
                ("product_tmpl_id.write_date", ">", since_date),
            ]
        self.with_delay().export_batch(backend, domain=domain)

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
