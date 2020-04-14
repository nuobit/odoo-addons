# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import http

import base64

import werkzeug.exceptions

from odoo.addons.lighting_reporting.controllers.main import ProductDatasheetController


class ProductDatasheetAttachmentController(ProductDatasheetController):
    def generate_lighting_report(self, product_id, lang_id=None):
        default_lang = 'en_US'
        attachments_selected = product_id.attachment_ids \
            .filtered(lambda x: x.use_as_product_datasheet)

        if not attachments_selected:
            return super().generate_lighting_report(product_id, lang_id=lang_id)

        attachments = attachments_selected.filtered(
            lambda x: (
                    (not lang_id and (not x.lang_id or x.lang_id.code == default_lang)) or
                    (lang_id and lang_id.code == x.lang_id.code)
            ))

        if not attachments:
            return werkzeug.exceptions.NotFound(
                "The product %s has no datasheet in %s" % (
                    product_id.reference, lang_id and lang_id.code or default_lang))

        attachment = attachments.sorted(lambda x: (x.sequence, x.id))[0]
        pdf = base64.b64decode(attachment.datas)

        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
        ]
        return http.request.make_response(pdf, headers=pdfhttpheaders)
