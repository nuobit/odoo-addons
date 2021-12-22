# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models

from .common import BATCH_SENDING_METHODS


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoice_batch_sending_method = fields.Selection(
        selection=BATCH_SENDING_METHODS,
        string="Invoice Batch Sending method",
        required=True,
        default="pdf",
        tracking=True,
    )
    invoice_batch_email_partner_id = fields.Many2one(
        comodel_name="res.partner",
        domain="[('id', 'child_of', active_id), ('email', '!=', False)]",
        ondelete="restrict",
        string="Invoice Batch Contact",
        tracking=True,
    )
