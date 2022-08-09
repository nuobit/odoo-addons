# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import AbstractComponent


class AnphitrionBinder(AbstractComponent):
    _name = "anphitrion.binder"
    _inherit = ["base.binder.composite", "base.anphitrion.connector"]
