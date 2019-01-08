import odoo.addons.web.controllers.main as main

from odoo import http
from odoo.http import Response, request


class Binary(main.Binary):
    @http.route(['/web/image/h/<string:hash>/<string:filename>',
                 '/web/image/h/<string:hash>/<int:width>x<int:height>/<string:filename>',
                 ])
    def content_image(self, hash=None, xmlid=None, model='ir.attachment', id=None, field='datas',
                      filename_field='datas_fname', unique=None, filename=None, mimetype=None,
                      download=None, width=0, height=0, crop=False, access_token=None):
        attachment_objs = request.env[model].search([
            ('id', '!=', False),
            ('res_model', '=', 'lighting.attachment'),
            ('public', '=', True),
            ('checksum', '=', hash)
        ]).sorted('write_date', reverse=True)

        attachment_id = None
        if attachment_objs:
            attachment_id = attachment_objs[0].id

        res = super().content_image(xmlid=xmlid, model=model, id=attachment_id, field=field,
                                    filename_field=filename_field, unique=unique, filename=filename, mimetype=mimetype,
                                    download=download, width=width, height=height, crop=crop, access_token=access_token)
        return res
