# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceIrAttachmentBinder(Component):
    _name = "woocommerce.ir.attachment.binder"
    _inherit = "woocommerce.binder"

    _apply_on = "woocommerce.ir.attachment"

    external_id = "id"
    internal_id = "woocommerce_idattachment"
