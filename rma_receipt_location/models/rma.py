# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, fields, models


class Rma(models.Model):
    _inherit = "rma"

    receipt_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Receipt Location",
        compute="_compute_receipt_location_id",
        store=True,
        readonly=False,
    )

    @api.depends("partner_id")
    def _compute_receipt_location_id(self):
        for rec in self:
            rec.receipt_location_id = rec.partner_id.property_stock_customer

    def _prepare_picking(self, picking_form):
        super()._prepare_picking(picking_form)
        if self.receipt_location_id:
            picking_form.location_id = self.receipt_location_id
