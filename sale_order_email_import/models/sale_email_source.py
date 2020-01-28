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

import psycopg2
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
    port = fields.Integer(string='Port', default=139, required=True)

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

    def execute(self):
        self.ensure_one()

        # get connection
        conn = smbconn.SMBConnection(self.user, self.password, 'odoo', self.host, use_ntlm_v2=True)
        ok = conn.connect(self.ip, port=self.port)
        if not ok:
            raise UserError(_("Cannot connect to ip %s") % self.ip)

        errors = {}

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
                msg = None
                try:
                    msg = extract_msg.Message(file_content, attachmentClass=AttachmentMod)
                except:
                    errors.setdefault('wrong_format_file', []).append(f.filename)

                locale.setlocale(locale.LC_ALL, loc)

                if msg:
                    number = None
                    m = re.match(r'^.*gnx *([0-9]+)[^.]*\..+$', f.filename.lower())
                    if not m:
                        errors.setdefault('filename_format_error', []).append(f.filename)
                    else:
                        number = m.group(1)

                    if number:
                        sale_order_email_number = self.env['sale.order.email'].search([
                            ('source_id', '=', self.id),
                            ('number', '=', number),
                        ])
                        if sale_order_email_number:
                            errors.setdefault('duplicated_numbers', {}) \
                                .setdefault(number, []).append(f.filename)

                    if not msg.message_id:
                        errors.setdefault('message_id_not_found', []).append(f.filename)
                    else:
                        message_id = msg.message_id.strip()

                        sale_order_email_message = self.env['sale.order.email'].search([
                            ('message_id', '=', message_id),
                        ])
                        if sale_order_email_message:
                            errors.setdefault('duplicated_files', {}) \
                                .setdefault(sale_order_email_message.datas_fname, []) \
                                .append(f.filename)

                        if not sale_order_email_message and number and not sale_order_email_number:
                            sender = email.header.make_header(
                                email.header.decode_header(msg.sender)).__str__()
                            sender = sender.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')

                            sender_name, sender_email = None, None
                            m = re.match(r'^ *(.*?) *<([.@]+)> *$', sender)
                            if m:
                                sender_name, sender_email = m.groups()
                            else:
                                m = re.match(r'^ *([^@]+@.+) *$', sender)
                                if not m:
                                    errors.setdefault('email_wrong_format', []).append(f.filename)
                                else:
                                    sender_email = m.group(1)

                            if sender_email:
                                self.env['sale.order.email'].create({
                                    'number': number,
                                    'name': msg.subject and msg.subject.strip() or None,
                                    'email_name': sender_name,
                                    'email_from': sender_email.lower(),
                                    'date': email.utils.parsedate_to_datetime(msg.date) \
                                        .astimezone(pytz.UTC) \
                                        .replace(tzinfo=None),
                                    'body': msg.body and msg.body.strip() or None,
                                    'datas': base64.b64encode(file_content),
                                    'datas_fname': f.filename,
                                    'message_id': message_id,
                                    'source_id': self.id,
                                })

                _logger.info("%s/%s (%i/%i)" % (self.name, f.filename, i, N))

        conn.close()

        return errors

    @api.multi
    def get_data(self):
        if not self.active:
            raise UserError("The source is archived, re-enable it to use it.")

        return self.with_context(active_id=self.id).get_all_data()

    @api.model
    def get_all_data(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            sources = self.env['sale.order.email.source'].browse(active_id)
        else:
            sources = self.env['sale.order.email.source'].search([])
        if not sources:
            raise UserError("There's no sources defined or they're not enabled.")

        source_errors = {}
        for s in sources.sorted(lambda x: x.sequence):
            source_error = s.execute()
            if source_error:
                source_errors[s.name] = source_error

        # generate error message
        error_message = []
        filenames = set()
        for source_name, errors in source_errors.items():
            error_message.append("%s\n%s\n" % (source_name, '=' * 40))
            if 'duplicated_files' in errors:
                error_message.append(_("Duplicated files\n%s\n") % ('-' * 20,))
                error_duplicated_files = dict(sorted(errors['duplicated_files'].items(), key=lambda x: x[0]))
                for fok, frest in error_duplicated_files.items():
                    error_message.append("%s = %s" % (fok, ', '.join(sorted(frest))))
                    filenames |= set(frest)
                error_message.append("\n")

            if 'filename_format_error' in errors:
                error_message.append(_("Filename format error\n%s\n") % ('-' * 20,))
                for f in sorted(errors['filename_format_error']):
                    error_message.append(f)
                    filenames |= set([f])
                error_message.append("\n")

            if 'duplicated_numbers' in errors:
                error_message.append(_("Duplicated numbers\n%s\n") % ('-' * 20,))
                error_duplicated_numbers = dict(sorted(errors['duplicated_numbers'].items(), key=lambda x: x[0]))
                for fok, frest in error_duplicated_numbers.items():
                    error_message.append("%s ~ %s" % (fok, ', '.join(sorted(frest))))
                    filenames |= set(frest)
                error_message.append("\n")

            if 'wrong_format_file' in errors:
                error_message.append(_("Wrong format\n%s\n") % ('-' * 20,))
                for f in sorted(errors['wrong_format_file']):
                    error_message.append(f)
                    filenames |= set([f])
                error_message.append("\n")

            if 'message_id_not_found' in errors:
                error_message.append(_("Message-Id not found\n%s\n") % ('-' * 20,))
                for f in sorted(errors['message_id_not_found']):
                    error_message.append(f)
                    filenames |= set([f])
                error_message.append("\n")

            if 'email_wrong_format' in errors:
                error_message.append(_("Wrong e-mail format\n%s\n") % ('-' * 20,))
                for f in sorted(errors['email_wrong_format']):
                    error_message.append(f)
                    filenames |= set([f])
                error_message.append("\n")

            error_message.append("\n\nTotal files with errors: %i" % len(filenames))

        result_wizard = self.env['sale.order.email.import.result'].create({
            'errors': '%s' % (error_message and '\n'.join(error_message) or _('No errors nor warnings!'),),
        })

        return {
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'sale.order.email.import.result',
            'res_id': result_wizard.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {},
                       name=_('%s (copy)') % self.name,
                       )

        return super().copy(default)
