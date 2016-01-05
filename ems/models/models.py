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



from datetime import timedelta

import pytz

from openerp import models, fields, api, _
from openerp.exceptions import AccessError, Warning



import logging

_logger = logging.getLogger(__name__)




class ems_session_type(models.Model):
    """ Session Type """
    _name = 'ems.session.type'
    _description = 'Session Type'

    name = fields.Char(string='Session Type', required=True)
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



class ems_session(models.Model):
    """Session"""
    _name = 'ems.session'
    _description = 'Session'
    _order = 'date_begin'

    name = fields.Char(string='Session Name', translate=True, required=True,
        readonly=False, states={'done': [('readonly', True)]})
    description = fields.Text(string='Description', #translate=True,
        readonly=False, states={'done': [('readonly', True)]})

    weight = fields.Float(string='Weight', digits=(5,2),
        readonly=False, states={'done': [('readonly', True)]})


    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        default=lambda self: self.env['res.company']._company_default_get('ems.session'),
        required=False, readonly=False, states={'done': [('readonly', True)]})
    trainer_id = fields.Many2one('res.users', string='Trainer',
        #default=lambda self: self.env.user,
        readonly=False, states={'done': [('readonly', True)]})

    customer_id = fields.Many2one('res.partner', string='Customer',
        #default=lambda self: self.env.user.company_id.partner_id
        )

    type = fields.Many2one('ems.session.type', string='Type of Session',
        required=True, readonly=False, states={'done': [('readonly', True)]})

    date_begin = fields.Datetime(string='Start Date', required=True,
        readonly=True, states={'draft': [('readonly', False)]})
    date_end = fields.Datetime(string='End Date', required=True,
        readonly=True, states={'draft': [('readonly', False)]})

    date_tz = fields.Selection('_tz_get', string='Timezone',
                        default=lambda self: self._context.get('tz', 'UTC'))

    date_begin_located = fields.Datetime(string='Start Date Located', compute='_compute_date_begin_tz')
    date_end_located = fields.Datetime(string='End Date Located', compute='_compute_date_end_tz')


    order_id = fields.Many2one('pos.order',
        string="Order") #, required=True)

    state = fields.Selection([
            ('draft', 'Unconfirmed'),
            ('cancel', 'Cancelled'),
            ('confirm', 'Confirmed'),
            ('done', 'Done')
        ], string='Status', default='draft', readonly=True, required=True, copy=False,
        help="If session is created, the status is 'Draft'. If session is confirmed for the particular dates the status is set to 'Confirmed'. If the session is over, the status is set to 'Done'. If session is cancelled the status is set to 'Cancelled'.")


    @api.model
    def _tz_get(self):
        return [(x, x) for x in pytz.all_timezones]

    @api.one
    @api.depends('date_tz', 'date_begin')
    def _compute_date_begin_tz(self):
        if self.date_begin:
            self_in_tz = self.with_context(tz=(self.date_tz or 'UTC'))
            date_begin = fields.Datetime.from_string(self.date_begin)
            self.date_begin_located = fields.Datetime.to_string(fields.Datetime.context_timestamp(self_in_tz, date_begin))


    @api.one
    @api.depends('date_tz', 'date_end')
    def _compute_date_end_tz(self):
        if self.date_end:
            self_in_tz = self.with_context(tz=(self.date_tz or 'UTC'))
            date_end = fields.Datetime.from_string(self.date_end)
            self.date_end_located = fields.Datetime.to_string(fields.Datetime.context_timestamp(self_in_tz, date_end))
        else:
            self.date_end_located = False


    @api.onchange('date_begin')
    def _onchange_date_begin(self):
        if self.date_begin and not self.date_end:
            date_begin = fields.Datetime.from_string(self.date_begin)
            self.date_end = fields.Datetime.to_string(date_begin + timedelta(hours=1))



    @api.multi
    @api.depends('name', 'date_begin', 'date_end')
    def name_get(self):
        result = []
        for event in self:
            date_begin = fields.Datetime.from_string(event.date_begin)
            date_end = fields.Datetime.from_string(event.date_end)
            dates = [fields.Date.to_string(fields.Datetime.context_timestamp(event, dt)) for dt in [date_begin, date_end] if dt]
            dates = sorted(set(dates))
            result.append((event.id, '%s (%s)' % (event.name, ' - '.join(dates))))
        return result


    @api.one
    @api.constrains('date_begin', 'date_end')
    def _check_closing_date(self):
        if self.date_end < self.date_begin:
            raise Warning(_('Closing Date cannot be set before Beginning Date.'))

    @api.one
    def button_draft(self):
        self.state = 'draft'

    @api.one
    def button_cancel(self):
        self.state = 'cancel'

    @api.one
    def button_done(self):
        self.state = 'done'

    @api.one
    def confirm_event(self):
        self.state = 'confirm'

    @api.one
    def button_confirm(self):
        """ Confirm Event and send confirmation email to all register peoples """
        self.confirm_event()



class res_users(models.Model):
    _inherit = 'res.users'

    trainer = fields.Boolean(help="Check this box if this user is a trainer.")

class res_partner(models.Model):
    _inherit = 'res.partner'

    ems_type = fields.Selection(selection=[('customer', 'Customer'), ('prospect', 'Prospect')],
                                help="Select customer type")



############ WIZARD #############

class Wizard(models.TransientModel):
    _name = 'ems.wizard'

    def _default_session(self):
        return self.env['ems.session'].browse(self._context.get('active_id'))

    session_id = fields.Many2one('ems.session',
        string="Session", required=True, default=_default_session)
    #attendee_ids = fields.Many2many('res.partner', string="Attendees")

    count = fields.Integer(string='Number of sessions', default=10, required=True)

    @api.multi
    def subscribe(self):
        s = self.session_id
        date_begin = fields.Datetime.from_string(s.date_begin)
        date_end = fields.Datetime.from_string(s.date_end)
        for i in range(self.count):


            days = 7*(i+1)
            date_begin9 = date_begin + timedelta(days=days)
            date_end9 = date_end + timedelta(days=days)

            g = self.env['ems.session'].search_count([('date_begin','<=',fields.Date.to_string(date_begin9)),
                                                      ('date_end','>=', fields.Date.to_string(date_end9))])
            raise Warning(g)

            self.env['ems.session'].create({'name': '%s%i' % (s.name, days), 'type': s.type.id,
                                                'date_begin': fields.Datetime.to_string(date_begin9),
                                                'date_end': fields.Datetime.to_string(date_end9)})


