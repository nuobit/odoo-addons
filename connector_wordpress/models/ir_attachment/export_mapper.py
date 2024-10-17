# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import os

from odoo.tools import mimetypes

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class WordPressIrAttachmentExportMapper(Component):
    _name = "wordpress.ir.attachment.export.mapper"
    _inherit = "wordpress.export.mapper"

    _apply_on = "wordpress.ir.attachment"

    # TODO: create header in adapter, sending mimetype and file name
    @mapping
    def name(self, record):
        attachment_path = record._full_path(record.store_fname)
        file_name = os.path.basename(attachment_path)
        # We need to concatenate the filename with the extension
        # because odoo does not store the extension
        # and wordpress needs it to recognize the file type
        file_extension = mimetypes.guess_extension(record.mimetype)
        headers = {
            "content-disposition": "attachment; filename=%s"
            % (file_name + file_extension),
            "content-type": record.mimetype,
        }
        data = open(attachment_path, "rb").read()
        return {
            # "id": record.id,
            # "filename": file_name,
            # "mimetype": record.mimetype,
            "headers": headers,
            "data": data,
        }

    @mapping
    def seo_meta_data(self, record):
        return record._get_seo_meta_data()
