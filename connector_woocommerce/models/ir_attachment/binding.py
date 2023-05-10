# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class WooCommerceIrAttachment(models.Model):
    _name = "woocommerce.ir.attachment"
    _inherit = "woocommerce.binding"
    _inherits = {"ir.attachment": "odoo_id"}
    _description = "WooCommerce Ir Attachment Binding"

    odoo_id = fields.Many2one(
        comodel_name="ir.attachment",
        string="Ir Attachment",
        required=True,
        ondelete="cascade",
    )
    woocommerce_idattachment = fields.Integer(
        string="ID Attachment",
        readonly=True,
    )

    # TODO: eliminar esta constrain
    _sql_constraints = [
        (
            "external_uniq",
            "unique(backend_id, woocommerce_idattachment)",
            "A binding already exists with the same External (idAttachment) ID.",
        ),
    ]

    @api.model
    def _get_base_domain(self):
        return []

    def export_ir_attachment_since(self, backend_record=None, since_date=None):
        domain = self._get_base_domain()
        # TODO: descomentar
        if since_date:
            domain += [
                ("write_date", ">", fields.Datetime.to_string(since_date)),
            ]
        self.export_batch(backend_record, domain=domain)
        return True
