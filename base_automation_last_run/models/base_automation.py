# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class BaseAutomation(models.Model):
    _inherit = "base.automation"

    last_run = fields.Datetime(readonly=False, copy=False)
