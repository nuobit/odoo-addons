# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    oxigesti_bind_ids = fields.One2many(
        comodel_name="oxigesti.mrp.production",
        inverse_name="odoo_id",
        string="Oxigesti Bindings",
    )

    def _get_valid_components(self):
        fields = ["cylinder", "valve"]
        moves = self.env["stock.move"]
        for mrp_type in fields:
            move_raw = self.move_raw_ids.filtered(
                lambda x: x.product_id.mrp_type == mrp_type
                and x.quantity_done > 0
                and x.move_line_ids
            )
            if len(move_raw.product_id) == 0:
                raise ValidationError(
                    _("Production of empty gas bottle type without %s product: %s")
                    % (mrp_type, self.name)
                )
            if len(move_raw) > 1 or sum(move_raw.mapped("quantity_done")) > 1:
                raise ValidationError(
                    _(
                        "The empty gas bottle (%s) has been created with"
                        " more than one %s"
                    )
                    % (self.name, mrp_type)
                )
            if len(move_raw.move_line_ids) > 1:
                raise ValidationError(
                    _(
                        "You have a component with more than one serial"
                        " number to generate: %s"
                    )
                    % self.name
                )
            if not move_raw.product_id.default_code:
                raise ValidationError(
                    _("Internal Reference not set in product: %s")
                    % move_raw.product_id.name
                )
            moves |= move_raw
        return moves


class MrpProductionBinding(models.Model):
    _name = "oxigesti.mrp.production"
    _inherit = "oxigesti.binding"
    _inherits = {"mrp.production": "odoo_id"}
    _description = "Product Mrp Production"

    odoo_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Production",
        required=True,
        ondelete="cascade",
    )

    @api.model
    def export_data(self, backend, since_date):
        domain = [
            ("company_id", "=", backend.company_id.id),
            ("product_id.mrp_type", "=", "empty_gas_bottle"),
            ("state", "=", "done"),
        ]
        if since_date:
            domain += [("write_date", ">", since_date)]
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
