# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import AbstractComponent


class SapBinder(AbstractComponent):
    _name = "sap.binder"
    _inherit = ['base.binder.composite','base.sap.connector']

    _binding_field = 'sap_bind_ids'