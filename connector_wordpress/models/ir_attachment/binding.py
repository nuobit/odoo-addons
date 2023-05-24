# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class WordPressIrAttachment(models.Model):
    _name = "wordpress.ir.attachment"
    _inherit = "wordpress.binding"
    _inherits = {"ir.attachment": "odoo_id"}
    _description = "WordPress Ir Attachment Binding"

    odoo_id = fields.Many2one(
        comodel_name="ir.attachment",
        string="Ir Attachment",
        required=True,
        ondelete="cascade",
    )
    wordpress_idattachment = fields.Integer(
        string="ID Attachment",
        readonly=True,
    )
    # # This field is for search
    # checksum= fields.Char()

    # TODO: eliminar esta constrain
    # _sql_constraints = [
    #     (
    #         "external_uniq",
    #         "unique(backend_id, wordpress_idattachment)",
    #         "A binding already exists with the same External (idAttachment) ID.",
    #     ),
    # ]

    @api.model
    def _get_base_domain(self):
        return []

    def export_ir_attachment_since(self, backend_record=None, since_date=None):
        domain = self._get_base_domain()
        if since_date:
            domain += [
                ("write_date", ">", fields.Datetime.to_string(since_date)),
            ]
        # TODO: refactor del domain
        domain += [
            ("res_id", "in", (62558, 62559)),
            ("res_field", "=", "image_variant_1920"),
            ("res_model", "=", "product.product"),
        ]
        self.export_batch(backend_record, domain=domain)
        return True


# self.env['ir.attachment'].sudo().search([
#                 ('name', '=', "image_variant_1920"),
#                 ('res_model', '=', "product.product"),
#                 ('res_id', '=', 62558),
#                 ('res_field','=', "image_variant_1920"),
#                 ('checksum','=', 'd55c9b6429534e8dcfd33cc1281e119d4715b6d4')
#         ], limit=1)
# El res field es imprescindible per fer la cerca al ir.attachment
