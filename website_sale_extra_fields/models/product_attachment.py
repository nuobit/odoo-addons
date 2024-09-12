# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


# This model is used to store attachments from product images and documents.
# TODO: It's defined as group users in security. It's ok?.
class AttachmentGrouped(models.TransientModel):
    _name = "attachment.grouped"
    _order = "sequence, id"

    sequence = fields.Integer(
        string="Sequence",
    )
    attachment_id = fields.Many2one(
        comodel_name="ir.attachment",
        string="Attachment",
        required=True,
    )
