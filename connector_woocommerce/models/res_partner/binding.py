# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class WooCommerceResPartner(models.Model):
    _name = "woocommerce.res.partner"
    _inherit = "woocommerce.binding"
    _inherits = {"res.partner": "odoo_id"}
    _description = "WooCommerce Res Partner Binding"

    odoo_id = fields.Many2one(
        comodel_name="res.partner",
        string="Res Partner",
        required=True,
        ondelete="cascade",
    )
    woocommerce_idrespartner = fields.Integer(
        string="ID Res Partner",
        readonly=True,
    )
    woocommerce_address_type = fields.Char(
        string="WooCommerce Type",
        readonly=True,
    )
    woocommerce_address_hash = fields.Char(
        string="Address Hash",
        readonly=True,
    )

    _sql_constraints = [
        (
            "external_uniq",
            "unique(backend_id, woocommerce_idrespartner)",
            "A binding already exists with the same External (idResPartner) ID.",
        ),
    ]

    # @api.model
    # def _get_base_domain(self):
    #     return []

    # def import_res_partners_since(self, backend_record=None, since_date=None):
    #     domain = self._get_base_domain()
    #     # TODO: descomentar
    #     if since_date:
    #         domain += [("write_date", ">", since_date)]
    #
    #     self.import_batch(backend_record, domain=domain)
    #     return True
