# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WordPressIrAttachmentBatchDirectExporter(Component):
    """Export the WordPress Ir Attachment.

    For every Ir Attachment in the list, execute inmediately.
    """

    _name = "wordpress.ir.attachment.batch.direct.exporter"
    _inherit = "wordpress.batch.direct.exporter"

    _apply_on = "wordpress.ir.attachment"


class WordPressIrAttachmentBatchDelayedExporter(Component):
    """Export the WordPress Ir Attachment.

    For every Ir Attachment in the list, a delayed job is created.
    """

    _name = "wordpress.ir.attachment.batch.delayed.exporter"
    _inherit = "wordpress.batch.delayed.exporter"

    _apply_on = "wordpress.ir.attachment"


class WordPressIrAttachmentExporter(Component):
    _name = "wordpress.ir.attachment.record.direct.exporter"
    _inherit = "wordpress.record.direct.exporter"

    _apply_on = "wordpress.ir.attachment"
