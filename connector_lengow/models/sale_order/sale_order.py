# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    lengow_bind_ids = fields.One2many(
        comodel_name="lengow.sale.order",
        inverse_name="odoo_id",
        string="Lengow Binding",
    )

    lengow_status = fields.Char(string="Lengow State", readonly=True, track_visibility='onchange')
    marketplace_status = fields.Char(string="Marketplace State", readonly=True, track_visibility='onchange')

    # TODO move this check to a standalone module and make the current module depends on it
    @api.constrains('partner_id', 'partner_invoice_id', 'partner_shipping_id')
    def _check_partner_parent_consistency(self):
        for rec in self:
            if rec.partner_invoice_id.parent_id:
                if rec.partner_invoice_id.parent_id != rec.partner_id:
                    raise ValidationError(_("The parent partner of the invoice address should be the same as "
                                            "the main partner in the order"))
            else:
                if rec.partner_invoice_id != rec.partner_id:
                    raise ValidationError(_("The invoice address has no parent so it should be the same as "
                                            "the main partner in the order"))
            if rec.partner_shipping_id.parent_id:
                if rec.partner_shipping_id.parent_id != rec.partner_id:
                    raise ValidationError(_("The parent partner of the shipping address should be the same as "
                                            "the main partner in the order"))
            else:
                if rec.partner_shipping_id != rec.partner_id:
                    raise ValidationError(_("The shipping address has no parent so it should be the same as "
                                            "the main partner in the order"))
