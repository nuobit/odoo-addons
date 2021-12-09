# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    oxigesti_bind_ids = fields.One2many(
        comodel_name="oxigesti.stock.production.lot",
        inverse_name="odoo_id",
        string="Oxigesti Bindings",
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
    def export_stock_production_lot_since(self, backend_record=None, since_date=None):
        """ Prepare the batch export of Lots on Odoo """

        def chunks(ls, n):
            """Yield successive n-sized chunks from lst."""
            for i in range(0, len(ls), n):
                yield ls[i : i + n]

        domain = [("company_id", "=", backend_record.company_id.id)]
        if since_date:
            domain += [("write_date", ">", since_date)]

        lot_ids = self.env["stock.production.lot"].search(domain).ids
        now_fmt = fields.Datetime.now()
        for ck in chunks(lot_ids, 500):
            ck_domain = [("id", "in", ck)]
            self.with_delay().export_batch(backend=backend_record, domain=ck_domain)
        backend_record.export_stock_production_lot_since_date = now_fmt

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
