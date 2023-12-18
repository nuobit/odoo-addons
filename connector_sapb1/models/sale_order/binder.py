# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class SaleOrderBinder(Component):
    _name = "sapb1.sale.order.binder"
    _inherit = "sapb1.binder"

    _apply_on = "sapb1.sale.order"

    external_id = "DocEntry"
    internal_id = "sapb1_docentry"

    external_alt_id = ["CardCode", "NumAtCard"]
    internal_alt_id = ["partner_id", "client_order_ref"]
