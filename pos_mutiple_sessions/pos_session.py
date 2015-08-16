# -*- coding: utf-8 -*-
#/#############################################################################
#
#   NuoBiT
#   Copyright (C) 2015 NuoNiT(<http://www.nuobit.com>).
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

from openerp import models


import logging

_logger = logging.getLogger(__name__)


class pos_session(models.Model):
    _inherit = 'pos.session'

    def create(self, *args, **kwargs):
        for i, (f, msg, l) in enumerate(self._constraints):
            if f.__name__ == '_check_unicity':
                del self._constraints[i]
                break

        return super(pos_session, self).create(*args, **kwargs)

    def name_get(self, cr, uid, ids, context=None):
        result = []
        for record in self.browse(cr, uid, ids, context=context):
            result.append((record.id, '%s (%s)' % (record.name,
                                                   record.config_id.name)))
        return result
