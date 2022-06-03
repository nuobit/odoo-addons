# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component



class VeloconnectProductTemplateTypeAdapter(Component):
    _name = "veloconnect.product.brand.adapter"
    _inherit = "veloconnect.adapter"

    _apply_on = "veloconnect.product.brand"

