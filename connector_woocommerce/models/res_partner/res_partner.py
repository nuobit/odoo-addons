# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models

from ....connector_extension.common.tools import list2hash


class Partner(models.Model):
    _inherit = "res.partner"

    woocommerce_bind_ids = fields.One2many(
        comodel_name="woocommerce.res.partner",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
    )

    address_hash = fields.Char(
        compute="_compute_address_hash", store=True, readonly=True
    )

    @api.model
    def _get_hash_fields(self):
        return ["name", "street", "street2", "city", "zip", "email", "mobile"]

    def _set_values_hash(self):
        for rec in self:
            values = [rec[x] or None for x in self._get_hash_fields()]
            values.append(rec.parent_id.name or None)
            values.append(rec.state_id.code or None)
            values.append(rec.country_id.code or None)
            return values

    @api.depends(
        "name",
        "parent_id",
        "street",
        "street2",
        "city",
        "state_id",
        "zip",
        "country_id",
        "email",
        "mobile",
    )
    def _compute_address_hash(self):
        for rec in self:
            values = rec._set_values_hash()
            rec.address_hash = list2hash(values)
