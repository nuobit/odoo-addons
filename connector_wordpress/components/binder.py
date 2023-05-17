# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import AbstractComponent


class WordPressBinder(AbstractComponent):
    _name = "wordpress.binder"
    _inherit = ["generic.binder", "base.wordpress.connector"]

    _default_binding_field = "wordpress_bind_ids"
