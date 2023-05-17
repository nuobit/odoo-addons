# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WordPressIrAttachmentBinder(Component):
    _name = "wordpress.ir.attachment.binder"
    _inherit = "wordpress.binder"

    _apply_on = "wordpress.ir.attachment"

    external_id = "id"
    internal_id = "wordpress_idattachment"
