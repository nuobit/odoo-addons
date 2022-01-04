# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    def _default_sii_registration_key(self):
        sii_key_obj = self.env["aeat.sii.mapping.registration.keys"]
        contract_type = self.env.context.get("default_contract_type")
        key = sii_key_obj.search(
            [("code", "=", "01"), ("type", "=", contract_type)], limit=1
        )
        return key

    sii_registration_key = fields.Many2one(
        comodel_name="aeat.sii.mapping.registration.keys",
        string="SII registration key",
        default=_default_sii_registration_key,
    )
    sii_registration_key_additional1 = fields.Many2one(
        comodel_name="aeat.sii.mapping.registration.keys",
        string="Additional SII registration key",
    )
    sii_registration_key_additional2 = fields.Many2one(
        comodel_name="aeat.sii.mapping.registration.keys",
        string="Additional 2 SII registration key",
    )
    sii_registration_key_code = fields.Char(
        related="sii_registration_key.code",
        readonly=True,
    )
    sii_enabled = fields.Boolean(
        string="Enable SII",
        compute="_compute_sii_enabled",
    )
    sii_property_location = fields.Selection(
        string="Real property location",
        copy=False,
        selection=[
            (
                "1",
                "[1]-Real property with cadastral code located within "
                "the Spanish territory except Basque Country or Navarra",
            ),
            ("2", "[2]-Real property located in the " "Basque Country or Navarra"),
            (
                "3",
                "[3]-Real property in any of the above situations "
                "but without cadastral code",
            ),
            ("4", "[4]-Real property located in a foreign country"),
        ],
    )
    sii_property_cadastrial_code = fields.Char(
        string="Real property cadastrial code",
        size=25,
        copy=False,
    )

    @api.multi
    @api.depends("company_id", "company_id.sii_enabled")
    def _compute_sii_enabled(self):
        for rec in self:
            rec.sii_enabled = rec.company_id.sii_enabled

    @api.multi
    def _prepare_invoice(self):
        invoice = super()._prepare_invoice()

        values = {}
        if self.sii_registration_key:
            values["sii_registration_key"] = self.sii_registration_key.id
        if self.sii_registration_key_additional1:
            values[
                "sii_registration_key_additional1"
            ] = self.sii_registration_key_additional1.id
        if self.sii_registration_key_additional2:
            values[
                "sii_registration_key_additional2"
            ] = self.sii_registration_key_additional2.id

        if self.contract_type == "sale":
            if self.sii_property_location:
                values["sii_property_location"] = self.sii_property_location
            if self.sii_property_cadastrial_code:
                values[
                    "sii_property_cadastrial_code"
                ] = self.sii_property_cadastrial_code

        if values:
            invoice.update(values)

        return invoice
