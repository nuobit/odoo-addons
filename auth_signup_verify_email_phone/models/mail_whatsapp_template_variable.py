# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MailWhatsAppTemplateVariable(models.Model):
    _inherit = "mail.whatsapp.template.variable"

    signup_auth = fields.Boolean(related="template_id.signup_auth")
    signup_model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Signup Model",
        domain=[("model", "=", "res.users")],
        default=lambda self: self.env["ir.model"]
        .search([("model", "=", "res.users")])
        .id,
        readonly=True,
        help="The model used for signup authentication (automatically set to res.users).",
    )
    signup_field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Signup Field",
        domain="[('model_id', '=', signup_model_id)]",
        help="Select a field from res.users to use for authentication.",
    )
