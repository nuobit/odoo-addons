# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp import http
from openerp.http import request

class bypass_acme_challenge(http.Controller):
    @http.route('/.well-known/acme-challenge/<filename>', type='http', auth='none')
    def get_acme_challenge(self, filename, **kw):

        local_folder = request.env['ir.config_parameter'].get_param('acme.challenge.local.folder')
        if local_folder:
            try:
                with open(local_folder + '/' + filename, 'r') as f:
                    return f.read()
            except:
                pass

        return request.not_found()





