# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResPartnerBinding(models.Model):
    _name = "sapb1.res.partner"
    _inherit = "sapb1.binding"
    _inherits = {"res.partner": "odoo_id"}
    _description = "SAP B1 Partner Binding"

    odoo_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        ondelete="cascade",
    )
    sapb1_cardcode = fields.Char(
        string="SAP B1 Cardcode",
        required=True,
    )
    sapb1_addressname = fields.Char(
        string="SAP B1 Addressname",
        required=True,
    )

    _sql_constraints = [
        (
            "sapb1_partner_external_uniq",
            "unique(backend_id, sapb1_cardcode,sapb1_addressname)",
            "A binding already exists with the same External (SAP B1) ID.",
        ),
    ]