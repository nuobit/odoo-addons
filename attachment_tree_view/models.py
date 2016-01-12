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

from openerp import api, models, fields

class account_invoice_attachment(models.Model):
    _inherit = 'account.invoice'

    attachment_count = fields.Integer(compute='_count_attachments')
    
    #@api.one
    def _count_attachments(self):
        obj_attachment = self.env['ir.attachment']
        for record in self:
            record.attachment_count = obj_attachment.search_count(
                [('res_model','=','account.invoice'),('res_id','=',record.id)])
    

    
