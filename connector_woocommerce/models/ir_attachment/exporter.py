# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceIrAttachmentBatchDirectExporter(Component):
    """Export the WooCommerce Ir Attachment.

    For every Ir Attachment in the list, execute inmediately.
    """

    _name = "woocommerce.ir.attachment.batch.direct.exporter"
    _inherit = "woocommerce.batch.direct.exporter"

    _apply_on = "woocommerce.ir.attachment"


class WooCommerceIrAttachmentBatchDelayedExporter(Component):
    """Export the WooCommerce Ir Attachment.

    For every Ir Attachment in the list, a delayed job is created.
    """

    _name = "woocommerce.ir.attachment.batch.delayed.exporter"
    _inherit = "woocommerce.batch.delayed.exporter"

    _apply_on = "woocommerce.ir.attachment"


class WooCommerceIrAttachmentExporter(Component):
    _name = "woocommerce.ir.attachment.record.direct.exporter"
    _inherit = "woocommerce.record.direct.exporter"

    _apply_on = "woocommerce.ir.attachment"
