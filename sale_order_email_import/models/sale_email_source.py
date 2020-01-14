# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields, _
from odoo.exceptions import UserError

from odoo.addons.queue_job.job import job

import tempfile
import email.utils
import pytz
import locale

import base64

try:
    import extract_msg


    # workaround for https://github.com/mattgwwalker/msg-extractor/blob/6fd92d74562425e79487fba56c5e1ae5caaf6681/extract_msg/attachment.py#L46
    class AttachmentMod(extract_msg.Attachment):
        def __init__(self, msg, dir_):
            try:
                super().__init__(msg, dir_)
            except NotImplementedError:
                pass
except ImportError:
    extract_msg = None

try:
    import smb.SMBConnection as smbconn
except ImportError:
    smbconn = None


class SaleOrderEmailSource(models.Model):
    _name = 'sale.order.email.source'
    _rec_name = 'folder'

    host = fields.Char(string='Host', required=True)
    ip = fields.Char(string='IP address', required=True)

    resource = fields.Char(string='Resource', required=True)
    folder = fields.Char(string='Folder', required=True)

    domain = fields.Char(string='Domain', required=True)
    user = fields.Char(string='User', required=True)
    password = fields.Char(string='Password', required=True)

    sequence = fields.Integer()

    @api.multi
    def get_data(self):
        # get connection
        conn = smbconn.SMBConnection(self.user, self.password, 'odoo', self.host, use_ntlm_v2=True)
        ok = conn.connect(self.ip)
        if not ok:
            raise UserError(_("Cannot connect to ip %s") % self.ip)

        # get file list
        files = conn.listPath(self.resource, self.folder)

        # find new files
        if files:
            files_ndx = {f.filename: f for f in files if not f.isDirectory}
            all_filenames = list(files_ndx.keys())
            existing_filenames = self.env['sale.order.email'].search([
                ('datas_fname', 'in', all_filenames),
            ]).mapped('datas_fname')
            new_filenames = set(all_filenames) - set(existing_filenames)

            for filename in new_filenames:
                f = files_ndx[filename]
                file_path = '%s/%s' % (self.folder, f.filename)

                file_obj = tempfile.NamedTemporaryFile()
                conn.retrieveFile(self.resource, file_path, file_obj)
                file_obj.seek(0)
                file_content = file_obj.read()
                file_obj.close()

                loc = locale.getlocale()
                locale.setlocale(locale.LC_ALL, 'C')
                msg = extract_msg.Message(file_content, attachmentClass=AttachmentMod)
                locale.setlocale(locale.LC_ALL, loc)

                sale_order_email = self.env['sale.order.email'].search_count([
                    ('message_id', '=', msg.message_id),
                ])
                if not sale_order_email:
                    self.env['sale.order.email'].create({
                        'name': msg.subject,
                        'email_from': msg.sender,
                        'date': email.utils.parsedate_to_datetime(msg.date) \
                            .astimezone(pytz.UTC) \
                            .replace(tzinfo=None),
                        'body': msg.body,
                        'datas': base64.b64encode(file_content),
                        'datas_fname': f.filename,
                        'message_id': msg.message_id,
                    })

        conn.close()

    @api.model
    def get_all_data(self):
        for s in self.env['sale.order.email.source'].search([]):
            s.get_data()
