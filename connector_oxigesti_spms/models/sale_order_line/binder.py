# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class SaleOrderBinderLine(Component):
    _name = "oxigesti.spms.sale.order.line.binder"
    _inherit = "oxigesti.spms.binder"

    _apply_on = "oxigesti.spms.sale.order.line"

    external_id = "Id"
    internal_id = "oxigesti_spms_id"
