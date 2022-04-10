# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sap_bind_ids = fields.One2many(
        comodel_name='sap.res.partner',
        inverse_name='odoo_id',
        string='SAPb1 Bindings',
    )


class ResPartnerBinding(models.Model):
    _name = 'sap.res.partner'
    _inherit = 'sap.binding'
    _inherits = {'res.partner': 'odoo_id'}

    odoo_id = fields.Many2one(comodel_name='res.partner',
                              string='Partner',
                              required=True,
                              ondelete='cascade')

    sap_cardcode = fields.Char(strin="SAP Cardcode")
    sap_rownum = fields.Char(string="SAP Rpwnum")
    sap_addressname = fields.Char(string="SAP Addressname")

    _sql_constraints = [
        (
            "lengow_partner_external_uniq",
            "unique(backend_id, sap_cardcode,sap_rownum,sap_addressname)",
            "A binding already exists with the same External (Lengow) ID.",
        ),

    ]
