# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import AbstractComponent


class WordPressAdapter(AbstractComponent):
    _name = "wordpress.adapter"
    _inherit = ["base.backend.wordpress.adapter.crud", "base.wordpress.connector"]

    _description = "WordPress Binding (abstract)"
