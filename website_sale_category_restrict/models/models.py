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

from openerp import models, fields


import logging

_logger = logging.getLogger(__name__)

class product_public_category(models.Model):
    _inherit = 'product.public.category'

    access_type = fields.Selection(string="Access type", selection=[("allow", "Allow all users except:"),
                                                                    ("deny", "Deny all user except:")], default='allow')

    except_users = fields.Many2many(comodel_name="res.users")

    def get_access(self, user=None):
        if not user:
            user = self.env.user

        if user in self.except_users:
            if self.access_type == 'allow':
                return False
        else:
            if self.access_type == 'deny':
                return False

        return True
