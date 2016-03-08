# -*- coding: utf-8 -*-
#/#############################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2015 NuoBiT Solutions, S.L. (<http://www.nuobit.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#/#############################################################################

from openerp import models, fields, api


import logging

_logger = logging.getLogger(__name__)

class survey_user_input(models.Model):
    _inherit = 'survey.user_input'

    @api.multi
    def name_get(self):
        l = []
        for rec in self:
            l.append((rec.id, '%s%s' % (rec.date_create, (' - %s [%s]' % (rec.partner_id.name, rec.email)) if rec.partner_id else '')))

        return l
