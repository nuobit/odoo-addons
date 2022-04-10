# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class SaleOrderLineBinder(Component):
    _name = 'sap.sale.order.line.binder'
    _inherit = 'sap.binder'

    _apply_on = 'sap.sale.order.line'

    _external_field = 'id'
    _internal_field = 'sap_id'
