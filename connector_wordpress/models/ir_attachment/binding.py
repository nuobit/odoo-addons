# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


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
