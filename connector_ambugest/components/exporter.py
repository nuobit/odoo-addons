# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
from contextlib import closing, contextmanager
from odoo.addons.connector.exception import IDMissingInBackend
from odoo.addons.queue_job.exception import NothingToDoJob

import odoo
from odoo import _

from odoo.addons.queue_job.exception import (
    RetryableJobError,
    FailedJobError,
)

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class AmbugestExporter(AbstractComponent):
    """ Base importer for Ambugest """
    _name = 'ambugest.exporter'
    _inherit = ['base.exporter', 'base.ambugest.connector']
    _usage = 'record.exporter'
