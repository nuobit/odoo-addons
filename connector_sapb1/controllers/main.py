import re
import datetime
import time

from odoo import http

import werkzeug.exceptions

import logging

_logger = logging.getLogger(__name__)

try:
    import paramiko
    from hdbcli import dbapi
except ImportError as err:
    _logger.debug(err)


class SAPB1Controller(http.Controller):
    @http.route(['/sapb1/doc/<string:doctype>/r/C<int:cardcodenum>/<int:docnum>',
                 ], type='http', auth="user")
    def download_doc_refund(self, doctype=None, cardcodenum=None, docnum=None):
        if doctype == 'order':
            return werkzeug.exceptions.UnprocessableEntity('An order cannot be refundable')
        return self.download_doc(doctype=doctype, cardcodenum=cardcodenum, docnum=docnum, refund=True)

    @http.route(['/sapb1/doc/<string:doctype>/C<int:cardcodenum>/<int:docnum>',
                 ], type='http', auth="user")
    def download_doc(self, doctype=None, cardcodenum=None, docnum=None, refund=False):
        cardcode = "C%i" % cardcodenum
        backend = http.request.env['sapb1.backend'].sudo().search([
            ('active', '=', True),
        ], limit=1, order='sequence,id')
        if not backend:
            return werkzeug.exceptions.InternalServerError('No configuration found')

        ### prepare doctype parameters
        if doctype == 'invoice':
            if not refund:
                prefix = 'Factura\ de\ clientes'
                tablename = 'OINV'
            else:
                prefix = 'Abono\ de\ clientes'
                tablename = 'ORIN'
        elif doctype == 'delivery':
            if not refund:
                prefix = 'Entrega'
                tablename = 'ODLN'
            else:
                prefix = 'Devolución'
                tablename = 'ORDN'
        elif doctype == 'order':
            if not refund:
                prefix = 'Pedido\ de\ cliente'
                tablename = 'ORDR'
        else:
            return werkzeug.exceptions.NotAcceptable('Doctype not exists')

        sql = """SELECT i."CardCode", i."DocNum", i."CreateDate", i."CreateTS"
                 FROM "%(schema)s".%(tablename)s i
                 WHERE i."CANCELED" = 'N' AND
                       i."CardCode" = :cardcode AND
                       i."DocNum" = :docnum
                 ORDER BY i."DocDate" DESC
              """ % dict(schema=backend.db_schema, tablename=tablename)

        ##### check coherence between cardname and docnum
        conn = dbapi.connect(backend.db_host,
                             backend.db_port,
                             backend.db_username,
                             backend.db_password)

        cursor = conn.cursor()

        # check schema to avoid injections
        sql_schemas = "SELECT SCHEMA_NAME FROM SCHEMAS"
        cursor.execute(sql_schemas)
        result = cursor.fetchall()
        if backend.db_schema not in map(lambda x: x[0], result):
            return werkzeug.exceptions.SecurityError('The DB schema does not exist')

        # get document data
        cursor.execute(sql, {'cardcode': cardcode,
                             'docnum': docnum})

        header = [x[0] for x in cursor.description]
        db_docs = []
        for row in cursor:
            row_d = dict(zip(header, row))
            dt = row_d.pop('CreateDate')
            time_int = row_d.pop('CreateTS')
            t_time = time.strptime('{0:06d}'.format(time_int), '%H%M%S')
            dt = dt.replace(hour=t_time.tm_hour, minute=t_time.tm_min, second=t_time.tm_sec)
            row_d.update({'createdatetime': dt})
            db_docs.append(row_d)

        cursor.close()
        conn.close()

        if not db_docs:
            return werkzeug.exceptions.NotFound('This document for this partner is canceled or '
                                                'does not exist on DB')

        ##### get files
        # create ssh client
        client = paramiko.client.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # client.load_system_host_keys()
        client.connect(backend.fileserver_host,
                       port=backend.fileserver_port,
                       username=backend.fileserver_username,
                       password=backend.fileserver_password)

        # create sftp client
        sftp = paramiko.SFTPClient.from_transport(client.get_transport())

        # check if basepath exists to avoid injections
        try:
            sftp.stat(backend.fileserver_basepath)
        except FileNotFoundError:
            return werkzeug.exceptions.NotFound('Base path not found on server')

        baseprefix = '%s/%s' % (backend.fileserver_basepath, prefix)

        cmd = "/bin/ls -1 %s_%i_*.pdf" % (baseprefix, docnum)
        stdin, stdout, stderr = client.exec_command(cmd)
        stdout.channel.recv_exit_status()

        filematch = stdout.readlines()
        if not filematch:
            return werkzeug.exceptions.NotFound('Document %i not found. Administrator notified' % docnum)

        file_docs = []
        for f in filematch:
            m = re.match(r'(^.+_%i_([0-9]{8})_([0-9]{6}).pdf)' % docnum, f)
            if not m:
                return werkzeug.exceptions.UnprocessableEntity(
                    'Document %i found but unexpected filename structure' % docnum)

            dt_str = "%s %s" % (m.group(2), m.group(3))
            dt = datetime.datetime.strptime(dt_str, '%Y%m%d %H%M%S')
            file_docs.append({
                'filename': m.group(1),
                'createdatetime': dt
            })

        ### find coherence between teoric db_docs and actual file_docs
        ## find matching db register of file. The files should have been created
        #  after or at the same time than dataabse register
        file_docs_db = []
        for fd in file_docs:
            diffs = []
            for dd in db_docs:
                diff = (fd['createdatetime'] - dd['createdatetime']).total_seconds()
                if diff >= 0:
                    diffs.append((dd, diff))

            if diffs:
                if len(diffs) > 1:
                    _logger.warning("More than one document found on DB that matches the file. "
                                    "Assuming it corresponds to the closest one in the past")
                diffs.sort(key=lambda x: x[1])
                file_docs_db.append((fd, *diffs[0]))

        if not file_docs_db:
            return werkzeug.exceptions.NotFound(
                'Document found in DB and files but they cannot be associated because of timestamp incoherences')

        ### keep only the most recent one
        file_docs_db.sort(key=lambda x: x[0]['createdatetime'], reverse=True)
        filepath_def = file_docs_db[0][0]['filename']

        f = sftp.open(filepath_def, 'r')
        f.seek(0)
        doc = f.read()
        f.close()

        sftp.close()
        client.close()

        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(doc)),
        ]
        return http.request.make_response(doc, headers=pdfhttpheaders)
