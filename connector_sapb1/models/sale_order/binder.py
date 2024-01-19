# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class SaleOrderBinder(Component):
    _name = "sapb1.sale.order.binder"
    _inherit = "sapb1.binder"

    _apply_on = "sapb1.sale.order"

    _external_field = "DocEntry"
    _internal_field = "sapb1_docentry"

    _external_alt_field = ["CardCode", "NumAtCard"]
    _internal_alt_field = ["partner_id", "client_order_ref"]
