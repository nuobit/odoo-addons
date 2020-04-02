# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import find_in_path
from odoo.tools import config

from math import ceil
import logging
import os
import tempfile
import subprocess
import re

from contextlib import closing
from distutils.version import LooseVersion

from PyPDF2 import PdfFileWriter, PdfFileReader

_logger = logging.getLogger(__name__)


def chunks(l, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def _get_ghostscript_bin():
    return find_in_path('gs')


# Check the presence of GhostScript and return its version at Odoo start-up
ghostscript_state = 'install'
try:
    process = subprocess.Popen(
        [_get_ghostscript_bin(), '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
except (OSError, IOError):
    _logger.info('You need GhostScript to print a pdf version of the reports.')
else:
    _logger.info('Will use the GhostScript binary at %s' % _get_ghostscript_bin())
    out, err = process.communicate()
    match = re.search(b'([0-9.]+)', out)
    if match:
        version = match.group(0).decode()
        if LooseVersion(version) < LooseVersion('9.26'):
            _logger.info('Upgrade GhostScript to (at least) 9.26')
            ghostscript_state = 'upgrade'
        else:
            ghostscript_state = 'ok'

        if config['workers'] == 1:
            _logger.info('You need to start Odoo with at least two workers to print a pdf version of the reports.')
            ghostscript_state = 'workers'
    else:
        _logger.info('GhostScript seems to be broken.')
        ghostscript_state = 'broken'


class Report(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def get_ghostscript_state(self):
        '''Get the current state of GhostScript: install, ok, upgrade, workers or broken.
        * install: Starting state.
        * upgrade: The binary is an older version (< 9.26).
        * ok: A binary was found with a recent version (>= 9.26).
        * workers: Not enough workers found to perform the pdf rendering process (< 2 workers).
        * broken: A binary was found but not responding.

        :return: ghostscript_state
        '''
        return ghostscript_state

    @api.model
    def _build_ghostscript_args(self):
        '''Build arguments understandable by ghostscript bin.

        :return: A list of string representing the wkhtmltopdf process command args.
        '''
        command_args = ['-dBATCH', '-dNOPAUSE', '-sDEVICE=pdfwrite']

        # Less verbose error messages
        command_args.extend(['-q'])

        return command_args

    @api.model
    def _run_wkhtmltopdf(self, bodies, header=None, footer=None,
                         landscape=False, specific_paperformat_args=None,
                         set_viewport_size=False):

        if len(bodies) < 50:
            return super(Report, self)._run_wkhtmltopdf(
                bodies, header=header, footer=footer, landscape=landscape,
                specific_paperformat_args=specific_paperformat_args,
                set_viewport_size=set_viewport_size)

        if self.get_ghostscript_state() == 'install':
            # ghostscript is not installed
            # check here to avoid the check been bypassed
            raise UserError(_("Unable to find ghostscript on this system. The PDF can not be created."))

        N = 10
        _logger.info("Many documents to print, splitting on %i chunks of %i documents max" % (ceil(len(bodies) / N), N))
        paths = []
        temporary_files = []
        for i, bodies_chunk in enumerate(chunks(bodies, N)):
            pdf_content_chunk = super(Report, self)._run_wkhtmltopdf(
                bodies_chunk, header=header, footer=footer, landscape=landscape,
                specific_paperformat_args=specific_paperformat_args,
                set_viewport_size=set_viewport_size)

            prefix = '%s%d.' % ('report.chunk.tmp.', i)
            chunk_file_fd, chunk_file_path = tempfile.mkstemp(suffix='.pdf', prefix=prefix)
            with closing(os.fdopen(chunk_file_fd, 'wb')) as chunk_file:
                chunk_file.write(pdf_content_chunk)
            paths.append(chunk_file_path)
            temporary_files.append(chunk_file_path)

        pdf_report_fd, pdf_report_path = tempfile.mkstemp(suffix='.pdf', prefix='report.tmp.')
        os.close(pdf_report_fd)
        temporary_files.append(pdf_report_path)

        command_args = self._build_ghostscript_args()
        output_command_args = ['-sOutputFile=%s' % pdf_report_path]
        try:
            ghostscript = [_get_ghostscript_bin()] + command_args + output_command_args + paths
            process = subprocess.Popen(ghostscript, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()
            if process.returncode not in (0,):
                message = _('GhostScript failed (error code: %s). Message: %s')
                raise UserError(message % (str(process.returncode), err[-1000:]))
        except:
            raise

        with open(pdf_report_path, 'rb') as pdf_document:
            pdf_content = pdf_document.read()

        # Manual cleanup of the temporary files
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except (OSError, IOError):
                _logger.error('Error when trying to remove file %s' % temporary_file)

        return pdf_content
