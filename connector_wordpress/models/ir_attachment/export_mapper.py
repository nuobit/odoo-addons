# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import os

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class WordPressIrAttachmentExportMapper(Component):
    _name = "wordpress.ir.attachment.export.mapper"
    _inherit = "wordpress.export.mapper"

    _apply_on = "wordpress.ir.attachment"

    @mapping
    def name(self, record):
        img_path = record._full_path(record.store_fname)
        file_type = record.mimetype.split("/")[1]
        # We need to concatenate the filename with the extension
        # because odoo does not store the extension
        # and wordpress needs it to recognize the file type
        if file_type == "octet-stream":
            file_type = "jpeg"
        filename = os.path.basename(img_path) + "." + file_type
        headers = {
            "content-disposition": "attachment; filename=%s" % filename,
            "content-type": record.mimetype,
        }
        data = open(img_path, "rb").read()
        return {
            "id": record.id,
            "headers": headers,
            "data": data,
        }
