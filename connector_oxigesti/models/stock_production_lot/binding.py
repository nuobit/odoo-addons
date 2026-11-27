# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    oxigesti_bind_ids = fields.One2many(
        comodel_name="oxigesti.stock.production.lot",
        inverse_name="odoo_id",
        string="Oxigesti Bindings",
    )

    oxigesti_readonly = fields.Boolean(compute="_compute_oxigesti_readonly")

    @api.depends("oxigesti_bind_ids", "company_id")
    def _compute_oxigesti_readonly(self):
        for rec in self:
            rec.oxigesti_readonly = bool(
                rec.sudo().oxigesti_bind_ids.filtered(
                    lambda x: x.backend_id.company_id == rec.company_id
                )
            )

    oxigesti_write_date = fields.Datetime(
        compute="_compute_oxigesti_write_date",
        store=True,
        required=True,
        readonly=False,
        default=fields.Datetime.now,
    )

    @api.depends(
        "name",
        "product_id",
        "product_id.nos_enabled",
        "product_id.dn_enabled",
        "nos",
        "dn",
        "nos_unknown",
        "dn_unknown",
        "manufacturer_id",
        "weight",
        "manufacture_date",
        "retesting_date",
        "next_retesting_date",
        "removal_date",
    )
    def _compute_oxigesti_write_date(self):
        for rec in self:
            rec.oxigesti_write_date = fields.Datetime.now()

    @api.constrains("name", "product_id", "company_id")
    def _check_product_lot(self):
        for rec in self:
            if rec.oxigesti_readonly:
                raise ValidationError(
                    _(
                        "You can't modify name, product or company "
                        "because the lot is connected to Oxigesti"
                    )
                )


class StockProductionLotBinding(models.Model):
    _name = "oxigesti.stock.production.lot"
    _inherit = "oxigesti.binding"
    _inherits = {"stock.production.lot": "odoo_id"}
    _description = "Stock production lot binding"

    odoo_id = fields.Many2one(
        comodel_name="stock.production.lot",
        string="Stock Production Lot",
        required=True,
        ondelete="cascade",
    )

    @api.model
    def export_data(self, backend, since_date):
        def chunks(ls, n):
            """Yield successive n-sized chunks from lst."""
            for i in range(0, len(ls), n):
                yield ls[i : i + n]

        domain = [("company_id", "=", backend.company_id.id)]
        if since_date:
            domain += [("oxigesti_write_date", ">", since_date)]
        lot_ids = (
            self.env["stock.production.lot"]
            .with_context(active_test=False)
            .search(domain)
            .ids
        )
        for ck in chunks(lot_ids, 500):
            ck_domain = [("id", "in", ck)]
            self.with_delay().export_batch(backend, domain=ck_domain)

    @api.model
    def import_data(self, backend, since_date):
        filters = []
        if since_date:
            filters = [("write_date", ">", since_date)]
        self.with_delay().import_batch(backend, filters=filters)

    def resync(self):
        for record in self:
            func_exp = record.export_record
            func_imp = record.import_record
            if record.env.context.get("connector_delay"):
                func_exp = record.export_record.delay
                func_imp = record.import_record.delay
            with record.backend_id.work_on(record._name) as work:
                binder = work.component(usage="binder")
            relation = binder.unwrap_binding(self)
            func_exp(record.backend_id, relation)
            external_id = binder.to_external(self)
            func_imp(record.backend_id, external_id)
        return True
