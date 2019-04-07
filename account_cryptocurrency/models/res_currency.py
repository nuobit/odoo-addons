# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
import json


class Currency(models.Model):
    _inherit = "res.currency"

    rate = fields.Float(digits=(15, 15))
    rounding = fields.Float(digits=(15, 9))


class CurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    rate = fields.Float(digits=(15, 15))
