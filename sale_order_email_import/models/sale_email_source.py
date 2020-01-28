# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields, _
from odoo.exceptions import UserError

import tempfile
import email.utils
import email.header
import pytz
import locale

import re

import base64

import logging

_logger = logging.getLogger(__name__)

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

    name = fields.Char(string='Name', required=True)
    host = fields.Char(string='Host', required=True)
    ip = fields.Char(string='IP address', required=True)

    resource = fields.Char(string='Resource', required=True)
    folder = fields.Char(string='Folder', required=True)

    domain = fields.Char(string='Domain', required=True)
    user = fields.Char(string='User', required=True)
    password = fields.Char(string='Password', required=True)

    sequence = fields.Integer()

    active = fields.Boolean(default=True,
                            help="The active field allows you to hide the source without removing it.")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name must be unique!'),
    ]

    @api.multi
    def get_data(self):
        if not self.active:
            raise UserError("The source is archived, re-enable it to use it.")

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
            new_filenames = sorted(list(set(all_filenames) - set(existing_filenames)))

            pending_files = {}
            N = len(new_filenames)
            _logger.info("Found %i new files on source '%s'" % (N, self.name))
            for i, filename in enumerate(new_filenames, 1):
                f = files_ndx[filename]
                file_path = '%s/%s' % (self.folder, f.filename)

                file_obj = tempfile.NamedTemporaryFile()
                conn.retrieveFile(self.resource, file_path, file_obj)
                file_obj.seek(0)
                file_content = file_obj.read()
                file_obj.close()

                loc = locale.getlocale()
                locale.setlocale(locale.LC_ALL, 'C')
                try:
                    msg = extract_msg.Message(file_content, attachmentClass=AttachmentMod)
                except:
                    raise
                locale.setlocale(locale.LC_ALL, loc)

                sale_order_email_count = self.env['sale.order.email'].search_count([
                    ('message_id', '=', msg.message_id),
                ])
                if not sale_order_email_count:
                    m = re.match(r'^.*gnx *([0-9]+)[^.]*\..+$', f.filename.lower())
                    if not m:
                        if msg.message_id not in pending_files:
                            pending_files[msg.message_id] = []
                        pending_files[msg.message_id].append(f.filename)
                        _logger.info("%s/%s filename format error, "
                                     "postponing process (%i/%i)" % (self.name, f.filename, i, N))
                    else:
                        if msg.message_id in pending_files:
                            del pending_files[msg.message_id]
                        number = m.group(1)

                        sender = email.header.make_header(
                            email.header.decode_header(msg.sender)).__str__()
                        sender = sender.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
                        m = re.match(r'^ *(.*?) *<(.+)> *$', sender)
                        if m:
                            sender_name, sender_email = m.groups()
                        else:
                            m = re.match(r'^ *([^@]+@.+) *$', sender)
                            if not m:
                                raise UserError("Incorrect e-mail format '%s' in file '%s'" % (msg.sender, f.filename))
                            sender_name, sender_email = None, m.group(1)

                        self.env['sale.order.email'].create({
                            'number': number,
                            'name': msg.subject,
                            'email_name': sender_name,
                            'email_from': sender_email.lower(),
                            'date': email.utils.parsedate_to_datetime(msg.date) \
                                .astimezone(pytz.UTC) \
                                .replace(tzinfo=None),
                            'body': msg.body and msg.body.strip() or None,
                            'datas': base64.b64encode(file_content),
                            'datas_fname': f.filename,
                            'message_id': msg.message_id,
                            'source_id': self.id,
                        })
                        _logger.info("%s/%s imported successfully (%i/%i)" % (self.name, f.filename, i, N))
                else:
                    sale_order_email = self.env['sale.order.email'].search([
                        ('message_id', '=', msg.message_id),
                    ])
                    _logger.info("%s/%s already exists with another filename '%s' "
                                 "but the same message_id '%s' (%i/%i)" % (
                                     self.name, f.filename, sorted(sale_order_email.mapped('datas_fname')),
                                     msg.message_id, i, N))

            if pending_files:
                pending_files1 = {i: sorted(v) for i, (k, v) in enumerate(pending_files.items())}
                raise UserError("Filenames with incorrect format: %s" % pending_files1)

        conn.close()

    @api.model
    def get_all_data(self):
        sources = self.env['sale.order.email.source'].search([])
        if not sources:
            raise UserError("There's no sources defined or they're not enabled.")
        for s in sources:
            s.get_data()

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {},
                       name=_('%s (copy)') % self.name,
                       )

        return super().copy(default)
