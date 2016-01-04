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

from openerp import api, models, fields, SUPERUSER_ID
from openerp.api import Environment



import logging

_logger = logging.getLogger(__name__)



class event_type(models.Model):
    _inherit = 'event.type'

    color = fields.Selection(selection=[(1,  'Brown'),
                                        (2,  'Brown-Red'),
                                        (3,  'Red'),
                                        (4,  'Light Red'),
                                        (5,  'Orange'),
                                        (6,  'Light Orange'),
                                        (8,  'Green 1'),
                                        (7,  'Light Green 1'),
                                        (9,  'Green 2'),
                                        (10, 'Light Green 2'),
                                        (11, 'Yellow'),
                                        (12, 'Yellow-Orange'),
                                        (13, 'Light Blue-Green'),
                                        (14, 'Cyan'),
                                        (15, 'Light Blue'),
                                        (16, 'Blue'),
                                        (17, 'Blue-Purple'),
                                        (18, 'Light Purple'),
                                        (23, 'Purple'),
                                        (24, 'Dark Purple'),
                                        (22, 'Pink'),
                                        (19, 'Grey'),
                                        (20, 'Grey-Light Red'),
                                        (21, 'Grey-Red'),
                                        ], string="Color")

    @api.multi
    def name_get(self):
        result = []
        for etype in self:
            result.append((etype.id, '%s%s' % (etype.name, ' [%s]' % etype.color if etype.color else '')))

        return result



