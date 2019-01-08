import odoo.addons.web.controllers.main as main

from odoo import http
from odoo.http import Response, request


class Binary(main.Binary):
    @http.route(['/web/image',
                 '/web/image/<string:xmlid>',
                 '/web/image/<string:xmlid>/<string:filename>',
                 '/web/image/<string:xmlid>/<int:width>x<int:height>',
                 '/web/image/<string:xmlid>/<int:width>x<int:height>/<string:filename>',
                 '/web/image/<string:model>/<int:id>/<string:field>',
                 '/web/image/<string:model>/<int:id>/<string:field>/<string:filename>',
                 '/web/image/<string:model>/<int:id>/<string:field>/<int:width>x<int:height>',
                 '/web/image/<string:model>/<int:id>/<string:field>/<int:width>x<int:height>/<string:filename>',
                 '/web/image/<int:id>',
                 '/web/image/<int:id>/<string:filename>',
                 '/web/image/<int:id>/<int:width>x<int:height>',
                 '/web/image/<int:id>/<int:width>x<int:height>/<string:filename>',
                 '/web/image/<int:id>-<string:unique>',
                 '/web/image/<int:id>-<string:unique>/<string:filename>',
                 '/web/image/<int:id>-<string:unique>/<int:width>x<int:height>',
                 '/web/image/<int:id>-<string:unique>/<int:width>x<int:height>/<string:filename>',
                 '/web/image/h/<string:hash>/<string:filename>',
                 '/web/image/h/<string:hash>/<int:width>x<int:height>/<string:filename>',
                 ], type='http', auth="public")

    def content_image(self, hash=None, xmlid=None, model='ir.attachment', id=None, field='datas',
                      filename_field='datas_fname', unique=None, filename=None, mimetype=None,
                      download=None, width=0, height=0, crop=False, access_token=None):

        if hash:
            attachment_objs = request.env[model].search([
                ('id', '!=', False),
                ('res_model', '=', 'lighting.attachment'),
                ('public', '=', True),
                ('checksum', '=', hash)
            ]).sorted('write_date', reverse=True)

            attachment_id = None
            if attachment_objs:
                attachment_id = attachment_objs[0].id
            id = attachment_id

        res = super().content_image(xmlid=xmlid, model=model, id=id, field=field,
                                    filename_field=filename_field, unique=unique, filename=filename, mimetype=mimetype,
                                    download=download, width=width, height=height, crop=crop, access_token=access_token)
        return res
