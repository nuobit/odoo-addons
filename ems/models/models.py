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
from openerp.exceptions import AccessError, Warning, ValidationError

import re


import logging

_logger = logging.getLogger(__name__)




def timestr2int(tstr):
    m = re.match("^([0-9]{2}):([0-9]{2})", tstr)
    if m is None:
        raise ValidationError(_("Incorrect hour format"))

    hour, minu = m.groups()
    if int(hour)>23:
        raise ValidationError(_("The hour has to be between 0 and 23"))

    if int(minu)>59:
        raise ValidationError(_("Minutes has to be between 0 and 23"))

    return int(hour)*100+int(minu)

def int2timestr(tint):
    t = tint/100.0
    hour = int(t)
    min = (tint-t)*100

    return "%02d:%02d" % (hour, min)




class ems_center(models.Model):
    """Session"""
    _name = 'ems.center'
    _description = 'Center'

    name = fields.Char(string='Center name', required=True,
        readonly=False)

    description = fields.Text(string='Description',
        readonly=False)



class ems_session(models.Model):
    """Session"""
    _name = 'ems.session'
    _description = 'Session'
    _order = 'date_begin'

    name = fields.Char(string='Session Number', required=True,
        readonly=False, states={'done': [('readonly', True)]})

    description = fields.Text(string='Description', #translate=True,
        readonly=False, states={'done': [('readonly', True)]})

    weight = fields.Float(string='Weight', digits=(5,2),
        readonly=False, states={'done': [('readonly', True)]})


    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        default=lambda self: self.env['res.company']._company_default_get('ems.session'),
        required=False, readonly=False, states={'done': [('readonly', True)]})

    center_id = fields.Many2one('ems.center', string='Center', change_default=True,
        required=True, readonly=False)

    trainer_id = fields.Many2one('res.users', string='Trainer',
        #default=lambda self: self.env.user,
        readonly=False, states={'done': [('readonly', True)]})

    customer_id = fields.Many2one('res.partner', string='Customer',
        #default=lambda self: self.env.user.company_id.partner_id
        )

    service_id = fields.Many2one('ems.service', string='Service',
        required=True, readonly=False, states={'done': [('readonly', True)]})

    room_id = fields.Many2one('ems.room', string='Room',
        required=False, readonly=False, states={'done': [('readonly', True)]})

    resource_ids = fields.Many2many('ems.resource', string='Resources',
        required=False, readonly=False, states={'done': [('readonly', True)]})


    date_begin = fields.Datetime(string='Start Date', required=True,
        readonly=True, states={'draft': [('readonly', False)]})
    date_end = fields.Datetime(string='End Date', required=True,
        readonly=True, states={'draft': [('readonly', False)]})

    date_tz = fields.Selection('_tz_get', string='Timezone',
                        default=lambda self: self._context.get('tz', 'UTC'))

    date_begin_located = fields.Datetime(string='Start Date Located', compute='_compute_date_begin_tz')
    date_end_located = fields.Datetime(string='End Date Located', compute='_compute_date_end_tz')


    #order_id = fields.Many2one('pos.order',
    #    string="Order") #, required=True)

    state = fields.Selection([
            ('draft', 'Unconfirmed'),
            ('cancel', 'Cancelled'),
            ('confirm', 'Confirmed'),
            ('done', 'Done')
        ], string='Status', default='draft', readonly=True, required=True, copy=False,
        help="If session is created, the status is 'Draft'. If session is confirmed for the particular dates the status is set to 'Confirmed'. If the session is over, the status is set to 'Done'. If session is cancelled the status is set to 'Cancelled'.")

    @api.model
    def create(self, vals):
        session =  super(ems_session, self).create(vals)
        return session


    @api.model
    def _next_session(self):
        pass
        return "kk"
        #return [(x, x) for x in pytz.all_timezones]

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

    @api.onchange('center_id')
    def onchange_centre(self):
        service_ids = self.env['ems.room.service.rel'].search([('room_id.center_id','=',self.center_id.id)]).mapped('service_id.id')

        self.service_id = False
        self.room_id = False
        self.resource_ids = False

        res = dict(domain={'service_id': [('id', 'in', service_ids)]})

        return res


    @api.onchange('service_id', 'date_begin', 'date_end')
    def onchange_service(self):
        domains = {}
        ids = []
        ids2 = []
        ids22 = []
        for s in self.service_id.room_ids.filtered(lambda x: x.room_id.center_id==self.center_id).sorted(lambda x: x.sequence):
            sessions = self.env['ems.session'].search([
                ('center_id', '=', s.room_id.center_id.id),
                ('room_id', '=', s.room_id.id),
                ('date_begin','<',self.date_end),
                ('date_end','>',self.date_begin),

            ])
            if len(sessions)==0:
                ids.append(s.room_id.id)

            t = self.env['ems.session'].search([
                    ('center_id', '=', s.room_id.center_id.id),
                    ('date_begin','<',self.date_end),
                    ('date_end','>',self.date_begin),
                ])

            usats = False
            for r in s.resource_ids:
                for j in t:
                    if r in j.resource_ids:
                        usats=True
                        break
                if usats:
                    break
            if not usats:
                ids2.append(s.resource_ids)
                ids22+=s.resource_ids.mapped('id')

        domains.update({'room_id': [('id', 'in', ids)]})
        if ids!=[]:
            self.room_id = ids[0]
        else:
            self.room_id = False

        domains.update({'resource_ids': [('id', 'in', ids22)]})
        if ids2!=[]:
            self.resource_ids = ids2[0]
        else:
            self.resource_ids = False

        if len(domains)!=0:
            res = dict(domain=domains)

        return res


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


class ems_room(models.Model):
    """ Room """
    _name = 'ems.room'
    _description = 'Room'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')

    center_id = fields.Many2one('ems.center', string='Center',
        required=True, readonly=False)

    service_ids = fields.One2many('ems.room.service.rel', 'room_id', string="Services")



class ems_service(models.Model):
    """ Session Type """
    _name = 'ems.service'
    _description = 'Service'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
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

    #resource_ids = fields.Many2many('ems.resource', 'ems_service_resource_rel', 'resource_id', 'service_id', string="Resources")
    #resource_ids = fields.One2many('ems.service.resource.rel', 'service_id')
    room_ids = fields.One2many('ems.room.service.rel', 'service_id', string="Rooms")

    @api.multi
    def name_get(self):
        result = []
        for service in self:
            result.append((service.id, '%s%s' % (service.name, ' [%s]' % service.color if service.color else '')))

        return result


class ems_room_service(models.Model):
    """ Session Type """
    _name = 'ems.room.service.rel'
    _description = 'Room-Service relation'
    _order = 'sequence'

    room_id = fields.Many2one('ems.room', string="Room")
    service_id = fields.Many2one('ems.service', string="Service")

    resource_ids = fields.Many2many('ems.resource', string='Resources',
        required=True, readonly=False)

    sequence = fields.Integer('sequence', help="Sequence for the handle.", default=1)

    '''
    _sql_constraints = [
        ('rel_uniq', 'unique(room_id, service_id)', 'Duplicated room'),
        ('seq_uniq', 'unique(service_id, sequence)', 'Duplicated sequence'),
    ]
    '''


    @api.model
    def create(self, vals):
        emssr =  super(ems_room_service, self).create(vals)

        #self.env['ems.service.resource.rel'].search([('service_id','=',emssr.service_id)])
        return emssr


class ems_resource(models.Model):
    """Resources"""
    _name = 'ems.resource'
    _description = 'Resource'

    name = fields.Char(string='Resource name', required=True,
        readonly=False)

    center_id = fields.Many2one('ems.center', string='Center', change_default=True,
        required=True, readonly=False)

    description = fields.Text(string='Description',
        readonly=False)



class ems_timetable(models.Model):
    """Session"""
    _name = 'ems.timetable'
    _description = 'Timetable'
    _order = 'center_id,day,itime'

    #name = fields.Char(string='Name', required=True,
    #    readonly=False)

    center_id = fields.Many2one('ems.center', string='Center',
        required=True, readonly=False)

    day = fields.Selection(selection=[('1', _('Monday')), ('2', _('Tuesday')), ('3', _('Wednesday')),
                                      ('4', _('Thursday')), ('5', _('Friday')), ('6', _('Saturday')),
                                      ('7', _('Sunday'))], required=True, readonly=False)
    ini_time = fields.Char(string='Initial time', size=5, required=True,
        #default=lambda self: self.env.user,
        readonly=False, default="00:00")

    end_time = fields.Char(string='End time', size=5, required=True,
        #default=lambda self: self.env.user,
        readonly=False, default="01:00")

    itime = fields.Integer(readonly=True)
    etime = fields.Integer(readonly=True)


    trainer_ids = fields.One2many('ems.timetable.trainer', 'timetable_id', required=True,
        #default=lambda self: self.env.user,
        readonly=False)


    @api.depends('ini_time', 'end_time')
    def _calc_inttime(self):
        self.itime = timestr2int(self.ini_time)
        self.etime = timestr2int(self.end_time)

    @api.constrains('ini_time', 'end_time')
    def _check_times(self):
        if self.itime>self.etime:
            raise ValidationError(_("The initial time cannot be greater than end time"))

    @api.onchange('ini_time', 'end_time')
    def onchange_times_ems(self):
        self._check_times()


    def _check_overlap(self, other):
        b = timestr2int(other.ini_time)<timestr2int(self.end_time) and \
                        timestr2int(other.end_time)>timestr2int(self.ini_time)

        return b


    @api.constrains('trainer_ids', 'center_id', 'day', 'ini_time', 'end_time')
    def _check_trainer_id_ems(self):
        # serach for other timetables of the same day and same hours
        other_tts = self.env['ems.timetable'].search([('id', '!=', self.id),
                                                      ('center_id','=', self.center_id.id),
                                                      ('day','=', self.day)
                                                    ])
        for tt in other_tts:
            if self._check_overlap(tt):
                for trainer in self.trainer_ids:
                    for tt_trainer in tt.trainer_ids:
                        if tt_trainer.trainer_id.id==trainer.trainer_id.id:
                            raise ValidationError(_("The trainer %s already has a timetable") % trainer.timetable_id)




class ems_timetable_trainer(models.Model):
    """Session"""
    _name = 'ems.timetable.trainer'
    _description = 'Timetable Trainer'
    _order = 'sequence'

    #name = fields.Char(string='Name', required=True,
    #    readonly=False)

    sequence = fields.Integer('sequence', help="Sequence for the handle.", default=1)

    trainer_id = fields.Many2one('res.users', string='Trainer', domain=[('trainer', '=', True)],
        readonly=False)

    timetable_id = fields.Many2one('ems.timetable', string='Timetable Trainer', readonly=False)





##### Inhrits ##########33


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
    def generate(self):
        s = self.session_id
        date_begin = fields.Datetime.from_string(s.date_begin)
        date_end = fields.Datetime.from_string(s.date_end)
        for i in range(self.count-1):
            days = 7*(i+1)
            date_begin9 = date_begin + timedelta(days=days)
            date_end9 = date_end + timedelta(days=days)

            #g = self.env['ems.session'].search_count([('date_begin','<=',fields.Date.to_string(date_begin9)),
            #                                          ('date_end','>=', fields.Date.to_string(date_end9))])
            #raise Warning(g)

            self.env['ems.session'].create({'name': '%s%i' % (s.name, days), 'service': s.service_id.id,
                                                'date_begin': fields.Datetime.to_string(date_begin9),
                                                'date_end': fields.Datetime.to_string(date_end9)})



