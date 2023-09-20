# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class MrpProductionListener(Component):
    _name = "oxigesti.mrp.production.listener"
    _inherit = "oxigesti.listener"

    _apply_on = "oxigesti.mrp.production"
