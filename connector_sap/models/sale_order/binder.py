# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class SaleOrderBinder(Component):
    _name = 'sap.sale.order.binder'
    _inherit = 'sap.binder'

    _apply_on = 'sap.sale.order'

    _external_field = 'DocEntry'
    _internal_field = 'sapb1_docentry'
