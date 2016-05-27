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



import datetime

import pytz

import math

from collections import namedtuple


from openerp import models, fields, api, _
from openerp.exceptions import AccessError, Warning, ValidationError, except_orm

from openerp.tools.misc import detect_server_timezone

import re

import babel

import hashlib

import logging

_logger = logging.getLogger(__name__)


def _reopen(self):
    return {
        'type': 'ir.actions.act_window',
        'view_mode': 'form',
        'view_type': 'form',
        'res_id': self.id,
        'res_model': self._name,
        'target': 'new',
        # save original model in context,
        # because selecting the list of available
        # templates requires a model in context
        'context': {
            'default_model': self._name,
        },
    }

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

def int2tuple(tint):
    t = tint/100.0
    hour = int(t)
    min = tint-hour*100

    return (hour, min)

def tuple2timestr(t):
    return "%02d:%02d" % t

def int2timestr(tint):
    hour, min = int2tuple(tint)

    return "%02d:%02d" % (hour, min)

def timestr2tuple(tstr):
    return int2tuple(timestr2int(tstr))


def timestr_loc2utc(timestr, tzloc):
    hour_loc, min_loc = timestr2tuple(timestr)
    now_utc = pytz.utc.localize(datetime.datetime.utcnow())
    now_loc = now_utc.astimezone(pytz.timezone(tzloc))
    datetime_loc=now_loc.replace(hour=hour_loc, minute=min_loc, second=0, microsecond=0)
    datetime_utc=datetime_loc.astimezone(pytz.utc)

    return tuple2timestr((datetime_utc.hour, datetime_utc.minute))


def timestr_utc2loc(timestr, tzloc):
    hour_utc, min_utc = timestr2tuple(timestr)
    now_utc = pytz.utc.localize(datetime.datetime.utcnow())
    datetime_utc=now_utc.replace(hour=hour_utc, minute=min_utc, second=0, microsecond=0)
    datetime_loc=datetime_utc.astimezone(pytz.timezone(tzloc))

    return tuple2timestr((datetime_loc.hour, datetime_loc.minute))


def timestrday2datetime(day, timestr_utc, tz):
    # timestr: string HH:MM (utc)
    # day: monday:1,, sunday:7 (local)
    # return: datetime (utc)
    now_utc = pytz.utc.localize(datetime.datetime.utcnow())
    now_loc = now_utc.astimezone(pytz.timezone(tz))
    wd_loc = now_loc.isoweekday()
    dt_mon_utc = now_utc - datetime.timedelta(days=wd_loc-1)

    datetime_utc0 = dt_mon_utc + datetime.timedelta(days=day-1)

    hour_utc, min_utc = timestr2tuple(timestr_utc)
    datetime_utc = datetime_utc0.replace(hour=hour_utc, minute=min_utc, second=0, microsecond=0)

    return datetime_utc


def daytime_loc2datetime_utc(day, t, tz):
    now_utc = pytz.utc.localize(datetime.datetime.utcnow())
    now_loc = now_utc.astimezone(pytz.timezone(tz))

    hour_loc, min_loc = timestr2tuple(t)
    datetime_loc=now_loc.replace(hour=hour_loc, minute=min_loc, second=0, microsecond=0)
    wd_loc = datetime_loc.isoweekday()

    datetime_utc0=datetime_loc.astimezone(pytz.utc)
    datetime_utc_mon = datetime_utc0 - datetime.timedelta(days=wd_loc-1)
    datetime_utc = datetime_utc_mon + datetime.timedelta(days=day-1)

    return datetime_utc

def datetime_utc2daytime_loc(dt, tz):

    dt_loc = dt.astimezone(pytz.timezone(tz))

    return dt_loc.isoweekday(), tuple2timestr((dt_loc.hour, dt_loc.minute))




'''
def tzuser2custom(dt, tzu, tzc):
    # dt: user datetime in utc
    # tzu: user tz
    # tzc: new timezone
    # return: dt in utc representing tzc local time instead of tzu local time
    dt_utc_user = pytz.utc.localize(fields.Datetime.from_string(dt))
    dt_loc_user = dt_utc_user.astimezone(pytz.timezone(tzu))
    dt_loc_custom = dt_loc_user.replace(tzinfo=pytz.timezone(tzc))

    return dt_loc_custom.astimezone(pytz.utc)

def tzcustom2user(dt, tzc, tzu):
    # dt: custom datetime in utc
    # tzc: custom tz
    # tzu: new timezone
    # return: dt in utc representing tzu local time instead of tzc local time
    dt_utc_custom = pytz.utc.localize(fields.Datetime.from_string(dt))
    dt_loc_custom = dt_utc_custom.astimezone(pytz.timezone(tzc))
    dt_loc_user = dt_loc_custom.replace(tzinfo=pytz.timezone(tzu))

    return dt_loc_user.astimezone(pytz.utc)
'''

'''
def datetime_tz_custom2user(dt, tzc, tzu):
    # inverse of _datetime_tz_user2custom
    dt_utc_custom = dt #pytz.utc.localize(fields.Datetime.from_string(dt))
    dt_tz_custom = dt_utc_custom.astimezone(pytz.timezone(tzc))
    dt_tz_user = pytz.timezone(tzu).localize(dt_tz_custom.replace(tzinfo=None))
    dt_utc_user = dt_tz_user.astimezone(pytz.utc)

    return dt_utc_user

def datetime_tz_user2custom(dt, tzu, tzc):
    # * convert dt to custom timezone (tzc) assuming dt is in utc
    # and it been informed with user timezne tzu in gui
    # * gui autoamtically converts the user input to utc assuming the user
    # is entering the dt in user tz (tzu) so the uutc genrated is not representing the custom tz informes
    # * this method converts that dt in utc entered using user tz, to dt in utc
    #   as if it was enterd with custom timezone (tzc)
    dt_utc_user = dt #pytz.utc.localize(fields.Datetime.from_string(dt))
    dt_tz_user = dt_utc_user.astimezone(pytz.timezone(tzu))
    dt_tz_custom = pytz.timezone(tzc).localize(dt_tz_user.replace(tzinfo=None))
    dt_utc_custom = dt_tz_custom.astimezone(pytz.utc)

    return dt_utc_custom
'''

#dt_loc_user = fields.Datetime.context_timestamp(rec, fields.Datetime.from_string(rec.date_begin_year))
                #dt_loc_center = dt_loc_user.replace(tzinfo=pytz.timezone(rec.tz))
                #rec.date_begin = dt_loc_center.astimezone(pytz.utc)

'''
    def calc_date2time(self, date1):
        dt = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(date1))
        return tuple2timestr((dt.hour, dt.minute))


    def calc_time2date(self, timestr):
        hour, min = timestr2tuple(timestr)
        dt = fields.Datetime.context_timestamp(self, fields.datetime.now()) #datetime.datetime(2016,1,17,23,0,0)
        d = datetime.date(dt.year, dt.month, dt.day)
        d_mon = d - datetime.timedelta(days=d.isoweekday()-1)
        da = d_mon + datetime.timedelta(days=self.day-1)
        de = datetime.datetime.combine(da, datetime.time(hour, min, 0))

        return de - dt.utcoffset()
'''

def datetime_naivestr_loc2utc(dt, tzloc):
    # convert date or datetime naive string of implicit timezone tzloc to naive strin of implicit timezone utc
    datetime_from_naive_loc = fields.Datetime.from_string(dt)
    datetime_from_loc = pytz.timezone(tzloc).localize(datetime_from_naive_loc)
    datetime_from_utc = datetime_from_loc.astimezone(pytz.utc)
    datetime_from_naive_utc = datetime_from_utc.replace(tzinfo=None)

    return fields.Datetime.to_string(datetime_from_naive_utc)




CALENDAR_COLORS = [ (1,  'Brown'),
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
                    ]


DAYS_OF_WEEK = [(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'),
                (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'),
                (7, 'Sunday')]


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

    _inherit = 'mail.thread'

    number = fields.Char(string='Number', required=True, readonly=True,
                       default=lambda self: self.env['ir.sequence'].get('ems.session.sequence.type'),
                       copy=False)
    description = fields.Text(string='Description', #translate=True,
        readonly=False, track_visibility='onchange')

    has_description = fields.Boolean(string='Note?', compute='_compute_has_description')

    weight = fields.Float(string='Weight', digits=(5,2),
        readonly=False)


    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        default=lambda self: self.env['res.company']._company_default_get('ems.session'),
        ondelete='restrict',
        required=False, readonly=False)

    center_id = fields.Many2one('ems.center', string='Center', default=lambda self: self.env.user.center_id,
                                ondelete='restrict',
                                required=True, readonly=False, track_visibility='onchange')

    responsible_id = fields.Many2one('ems.responsible', string='Responsible',
                                     ondelete='restrict',
                                     required=False, readonly=False, track_visibility='onchange')

    partner_ids = fields.One2many(comodel_name='ems.partner', inverse_name='session_id', copy=True, track_visibility='onchange')

    partner_text = fields.Char(string='Attendees', compute='_compute_auxiliar_text', readonly=True, store=False, translate=False,
                               search='_search_partner_text')

    service_id = fields.Many2one('ems.service', string='Service',
                                 ondelete='restrict',
                                 required=True, readonly=False, track_visibility='onchange')
    is_meeting = fields.Boolean(related='service_id.is_meeting', store=False)


    color_rel = fields.Selection(related="service_id.color", store=False)

    ubication_id = fields.Many2one('ems.ubication', string='Ubication',
                                   ondelete='restrict',
                                   required=True, readonly=False, track_visibility='onchange')

    is_all_center = fields.Boolean(related='ubication_id.is_all_center', store=False)

    resource_ids = fields.Many2many('ems.resource', string='Resources',
        required=False, readonly=False, copy=True, track_visibility='onchange')

    duration = fields.Integer(string='Duration', required=True, track_visibility='onchange')


    date_begin = fields.Datetime(string='Start Date', required=True, default=fields.datetime.now().replace(second=0, microsecond=0),
        readonly=False, track_visibility='onchange')
    date_end = fields.Datetime(string='End Date', required=True,
        readonly=False, track_visibility='onchange')

    date_text = fields.Char(compute='_compute_timedate_text')
    time_text = fields.Char(compute='_compute_timedate_text')

    weekday_begin = fields.Char(string='Day of week', compute='_compute_weekdata_begin')
    weekyear_begin = fields.Integer(string='Week of year', compute="_compute_weekdata_begin")

    reason = fields.Char(string='Reason', required=False, readonly=False, copy=False, track_visibility='onchange')

    source_session_id = fields.Many2one('ems.session', string="Source session", readonly=True, copy=False) #, ondelete='restrict')
    source_session_ids = fields.Many2many('ems.session', relation="ems_source_session_rel",
                                          column1="session_id", column2="source_session_id",
                                          string="Source sessions", readonly=True, copy=False)

    source_numbers = fields.Char(compute='_compute_source_numbers', string="Sources")

    target_session_id = fields.Many2one('ems.session', string="Target session", readonly=True, copy=False) #, ondelete='restrict')
    target_session_ids = fields.Many2many('ems.session', relation="ems_target_session_rel",
                                          column1="session_id", column2="target_session_id",
                                          string="Target sessions", readonly=True, copy=False)

    session_text = fields.Char(compute='_compute_auxiliar_text', readonly=True, translate=False)

    num_pending_sessions = fields.Integer(string='Pending', compute='_compute_num_pending_sessions')


    out_of_time = fields.Boolean(string='Out of time', help='The attendee rescheduled a session out of time', default=False, copy=False, track_visibility='onchange')

    delayed_session = fields.Boolean(string='Delayed session', help='Indicates if the session has started with delay', default=False, copy=False, track_visibility='onchange')

    date_begin_actual = fields.Datetime(string='Actual start date', required=False, readonly=False, copy=False, track_visibility='onchange')

    delay_reason = fields.Char(string='Delay reason', required=False, readonly=False, copy=False, track_visibility='onchange')

    state = fields.Selection([
            ('draft', 'Draft'),
            ('cancelled', 'Cancelled'),
            ('rescheduled', 'Rescheduled'),
            ('reschedulepending', 'Reschedule pending'),
            ('schedulepending', 'Schedule pending'),
            ('confirmed', 'Confirmed'),
        ], string='Status', default='draft', readonly=True, required=True, copy=False, track_visibility='onchange')

    _sql_constraints = [('number_session_unique', 'unique(number)',_("Number duplicated"))]

    def split_session(self, g):
        a = []
        for i, p in enumerate(self.partner_ids, 1):
            a.append({'session_id': self.id,
                      'group': g,
                      'number': self.number,
                      'center_id': self.center_id.id,
                      'partner_id': p.partner_id.id,
                      'service_id': self.service_id,
                      'ubication_id': self.ubication_id,
                      'resource_ids': self.resource_ids,
                      'responsible_id': self.responsible_id,
                      'duration':  self.duration,
                      'date_begin': self.date_begin,
                    })
        return a

    def get_new_date(self, datestr_s, datestr_l, days=7):
        do = fields.Datetime.from_string(datestr_s)
        do_utc = pytz.utc.localize(do)
        do_loc = do_utc.astimezone(pytz.timezone('Europe/Madrid'))

        du = fields.Datetime.from_string(datestr_l)
        du_loc = fields.Datetime.context_timestamp(self, du)
        diff = do_loc.isoweekday()-du_loc.isoweekday()

        du2_loc = du_loc + datetime.timedelta(days=days+diff)
        du3_loc = du2_loc.replace(hour=do_loc.hour, minute=do_loc.minute, second=do_loc.second)
        du3_utc = du3_loc.astimezone(pytz.utc).replace(tzinfo=None)

        return du3_utc

    def _get_additional_message(self):
        msg = self.env.context.get('additional_message', False)
        if msg:
            return ' %s' % msg
        else:
            return ''

    @api.depends('state')
    def _compute_num_pending_sessions(selfs):
        for self in selfs:
            ps = self.env['ems.session'].search([ ('state', 'in', ('reschedulepending', 'schedulepending')),
                                                    ('center_id', '=', self.center_id.id),
                                            ]).filtered(lambda x: x.service_id.is_ems and
                                                                 len(set(x.partner_ids.mapped('partner_id.id')) &
                                                                     set(self.partner_ids.mapped('partner_id.id')))!=0
                                                     )
            self.num_pending_sessions = len(ps)

    @api.depends('description')
    def _compute_has_description(selfs):
        for self in selfs:
            if self.description:
                self.has_description = len(self.description.strip())!=0
            else:
                self.has_description = False

    @api.depends('date_begin')
    def _compute_weekdata_begin(selfs):
        for self in selfs:
            #dt = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(self.date_begin))
            #self.weekday_begin = dt.isoweekday()
            date_begin_dt_loc = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(self.date_begin))
            self.weekday_begin = babel.dates.format_date(date_begin_dt_loc, format='EEEE', locale=self.env.lang).capitalize()
            self.weekyear_begin = babel.dates.format_date(date_begin_dt_loc, format='w', locale=self.env.lang)

    @api.depends('date_begin', 'date_end')
    def _compute_timedate_text(selfs):
         for self in selfs:
            date_begin_dt_loc = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(self.date_begin))
            date_end_dt_loc = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(self.date_end))

            if date_begin_dt_loc.date()!=date_end_dt_loc.date():
                raise ValidationError(_("Session number '%s' has dates in different days"))

            date_dt = babel.dates.format_date(date_begin_dt_loc, format='full', locale=self.env.lang).capitalize()
            #self.date_text = "%s (%s - %s)" % (date_dt, date_begin_dt_loc.strftime('%H:%M'), date_end_dt_loc.strftime('%H:%M'))
            self.date_text = date_dt
            self.time_text = "%s - %s" % (date_begin_dt_loc.strftime('%H:%M'), date_end_dt_loc.strftime('%H:%M'))

    @api.depends('source_session_ids')
    def _compute_source_numbers(selfs):
        for self in selfs:
            self.source_numbers = ', '.join(self.source_session_ids.mapped('number'))

    @api.multi
    def button_print(self):
        pr = self.env['ems.partner'].search([('partner_id', 'in',
                                              self.partner_ids.mapped('partner_id.id'))])\
                .filtered(lambda x: x.session_id.center_id==self.center_id and
                                   x.session_id.state in ('cancelled', 'confirmed') and
                                   x.session_id.service_id.is_ems)\
                .mapped('num_session')

        wizard_id = self.env['ems.session.print.wizard'].create({
                    'session_from': min(pr),
                    'session_to': max(pr),
                })

        return {
                'type': 'ir.actions.act_window',
                'name': _("Print Sessions"),
                'res_model': 'ems.session.print.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                #'views': [(view.id, 'form')],
                #'view_id': view.id,
                'res_id': wizard_id.id,
                'target': 'new',
                #'context': context,
                }

    @api.multi
    def button_draft(self):
        if self.state == 'rescheduled':
            wizard_id = self.env['ems.message.wizard'].create({
                'message': _("The associated target sessions '%s' will be deleted. Continue?") % ', '.join(self.target_session_ids.mapped('number')),
                'model_name': 'ems.session',
            })

            return {
                'type': 'ir.actions.act_window',
                'name': _("Warning"),
                'res_model': 'ems.message.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                #'views': [(view.id, 'form')],
                #'view_id': view.id,
                'res_id': wizard_id.id,
                'target': 'new',
                #'context': context,
            }
        else:
            self.state = 'draft'

    @api.multi
    def button_cancel(self):
        wizard_id = self.env['ems.session.cancel.wizard'].create({
            'reason': self.reason,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _("Cancel Session"),
            'res_model': 'ems.session.cancel.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            #'views': [(view.id, 'form')],
            #'view_id': view.id,
            'res_id': wizard_id.id,
            'target': 'new',
            #'context': context,
        }




    @api.multi
    def button_reschedule(self):
        return {
            'type': 'ir.actions.act_window',
            'name':_("Reschedule Sessions"),
            'res_model': 'ems.session.reschedule.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            #'views': [(view.id, 'form')],
            #'view_id': view.id,
            #'res_id': wizard_id.id,
            'target': 'new',
            #'context': context,
        }

    @api.multi
    def button_reschedule_pending(self):
        wizard_id = self.env['ems.session.reschedule.pending.wizard'].create({
            'reason': self.reason,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _("Reschedule Pending"),
            'res_model': 'ems.session.reschedule.pending.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            #'views': [(view.id, 'form')],
            #'view_id': view.id,
            'res_id': wizard_id.id,
            'target': 'new',
            #'context': context,
        }

        self.state = 'reschedulepending'

    @api.multi
    def button_schedule_pending(self):
        self.state = 'schedulepending'

    @api.multi
    def button_confirm(self):
        self.state = 'confirmed'


    @api.multi
    def button_schedule(self):
        sessions0 = self.env['ems.session'].search([('state', '=', 'confirmed'),
                                                    ('center_id', '=', self.center_id.id),
                                                    ('date_begin', '>=', self.date_begin)
                                            ]).filtered(lambda x: x.service_id.is_ems and
                                                                 len(set(x.partner_ids.mapped('partner_id.id')) &
                                                                     set(self.partner_ids.mapped('partner_id.id')))!=0
                                                     )

        last_session = sessions0.sorted(lambda x: x.date_begin)[-1]

        default_days = 7
        default_num_sessions = 10

        wizard_id = self.env['ems.session.schedule.wizard'].create({
            'session_id': self.id,
            'num_sessions': default_num_sessions,
            'days': default_days,
            'date_begin': self.get_new_date(self.date_begin, last_session.date_begin, days=default_days)
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _("Schedule Sessions"),
            'res_model': 'ems.session.schedule.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            #'views': [(view.id, 'form')],
            #'view_id': view.id,
            'res_id': wizard_id.id,
            'target': 'new',
            #'context': context,
        }

    @api.depends('partner_ids', 'responsible_id','partner_ids.partner_id', 'partner_ids.partner_id.name')
    def _compute_auxiliar_text(selfs):
        for self in selfs:
            self.session_text = False
            self.partner_text = False

            if self.is_all_center:
                self.session_text = self.service_id.name
            else:
                if self.is_meeting:
                    self.session_text = '%s (%s)' % (self.service_id.name, self.ubication_id.name)
                else:
                    cust_text = []
                    for c in self.partner_ids:
                        num_sessio = ' (%i)' % c.num_session if self.service_id.is_ems else ''
                        cust_text.append('%s%s' % (c.partner_id.name, num_sessio ))

                    self.session_text = '%s [%s]' % (', '.join(cust_text), self.responsible_id.name_get()[0][1])
                    self.partner_text = '%s' % ', '.join(cust_text)

            if self.state not in ('confirmed'):
                self.session_text = '#%s# %s' % (self.state.upper(), self.session_text)

    def _search_partner_text(self, operator, value):
        return [('partner_ids.partner_id.name', operator, value)]

    @api.onchange('ubication_id')
    def _onchange_ubication(self):
        self.resource_ids = self.service_id.ubication_ids.filtered(lambda x: x.ubication_id==self.ubication_id).resource_ids

    @api.onchange('duration')
    def _onchange_duration(self):
        self.date_end = fields.Datetime.from_string(self.date_begin) + datetime.timedelta(minutes=self.duration)

    @api.onchange('date_begin')
    def _onchange_date_begin(self):
        self.date_end = fields.Datetime.from_string(self.date_begin) + datetime.timedelta(minutes=self.duration)

    @api.onchange('date_end')
    def _onchange_date_end(self):
        diff = fields.Datetime.from_string(self.date_end) - fields.Datetime.from_string(self.date_begin)
        self.duration = (diff.days*24*60*60 + diff.seconds) / 60

    @api.onchange('center_id')
    def onchange_centre(self):
        service_ids = self.env['ems.ubication.service.rel'].search([('ubication_id.center_id','=',self.center_id.id)]).mapped('service_id.id')
        #service_ids = self.env['ems.service'].filt

        self.service_id = False
        if len(service_ids)==1:
            self.service_id = service_ids[0]
        self.ubication_id = False
        self.responsible_id = False
        self.resource_ids = False
        self.partner_ids = False

        res = dict(domain={'service_id': [('id', 'in', service_ids)]})

        return res

    @api.model
    @api.onchange('service_id')
    def onchange_service(self):
        # actulitzem la data fi
        self.date_end = fields.Datetime.from_string(self.date_begin) + datetime.timedelta(minutes=self.service_id.duration)

        domains = {}
        ids = [] #self.ubication_id.id]
        ids2 = [] #self.resource_ids]
        ids22 = []
        for s in self.service_id.ubication_ids.filtered(lambda x: x.ubication_id.center_id==self.center_id).sorted(lambda x: x.sequence):
            ids.append(s.ubication_id.id)

            ids2.append(s.resource_ids)
            ids22+=s.resource_ids.mapped('id')

        domains.update({'ubication_id': [('id', 'in', ids)]})
        if ids!=[]:
            self.ubication_id = ids[0]
        else:
            self.ubication_id = False

        domains.update({'resource_ids': [('id', 'in', ids22)]})
        if ids2!=[]:
            self.resource_ids = ids2[0]
        else:
            self.resource_ids = False

        self.duration=self.service_id.duration

        if self.ubication_id.is_all_center:
            self.responsible_id = False
            self.resource_ids = False
            self.partner_ids = False

        res = {}
        if len(domains)!=0:
            res = dict(domain=domains)

        return res

    @api.onchange('delayed_session')
    def onchange_delayed_session(self):
        self.date_begin_actual = self.date_begin

    def _check_all(self):
        # check number of atendees
        if self.service_id.max_attendees>=0 and len(self.partner_ids)>self.service_id.max_attendees:
            raise ValidationError((_('Too many attendees, maximum of %i') % self.service_id.max_attendees)  + self._get_additional_message())

        if self.service_id.min_attendees>len(self.partner_ids):
            raise ValidationError((_('It requieres %i attendees minimum') % self.service_id.min_attendees) + self._get_additional_message() )

        # comprovem que la sessio no te cap forces session anteriro o posterior
        for ep in self.partner_ids:
            if ep.force_session:
                sessions_ant = self.env['ems.partner'].search([('partner_id','=', ep.partner_id.id)]).\
                    filtered(lambda x: x.session_id.center_id==self.center_id and
                                       x.session_id.state in ('cancelled', 'confirmed') and
                                       x.session_id.service_id.is_ems and
                                       x.session_id.date_begin<self.date_begin
                                    )
                if len(sessions_ant)!=0:
                    raise ValidationError(_("Only the first session can have a forced session.") + self._get_additional_message())
            else:
                sessions_ant = self.env['ems.partner'].search([('partner_id','=', ep.partner_id.id)]).\
                    filtered(lambda x: x.session_id.center_id==self.center_id and
                                       x.session_id.state in ('cancelled', 'confirmed') and
                                       x.session_id.service_id.is_ems and
                                       x.force_session and
                                       x.session_id.date_begin>self.date_begin
                                    )
                if len(sessions_ant)!=0:
                    raise ValidationError(_("It's not allowed to have a session before another one with forced session.") + self._get_additional_message())



        ### cerquem le sessions que se solapin amb l'actual (excepte lactual que segur que  solapa)
        # si la ubicacio actual es de tipus "tot el centre", qualsevol solapament temporal
        # en el mateix center no permet desar la nova ssessio
        if self.ubication_id.is_all_center:
            sessions = self.env['ems.session'].search([
                    ('id', '!=', self.id),
                    ('state', '=', 'confirmed'),
                    ('center_id', '=', self.center_id.id),
                    ('date_begin','<',self.date_end),
                    ('date_end','>',self.date_begin),
                ])


            if len(sessions)!=0: #hi ha solapaments
                raise ValidationError(_("There's another session in selected ubication") + self._get_additional_message())

            return

        ## que se solapin en la mateixa sala o en tot si es de tipus all center
        sessions = self.env['ems.session'].search([
                ('id', '!=', self.id),
                ('state', '=', 'confirmed'),
                ('center_id', '=', self.center_id.id),
                ('date_begin','<',self.date_end),
                ('date_end','>',self.date_begin)]).filtered(lambda x: x.ubication_id.is_all_center)
        if len(sessions)==0: #no hi ha solapaments amb una sessio que conte un servei de tipus all_center
             sessions = self.env['ems.session'].search([
                    ('id', '!=', self.id),
                    ('state', '=', 'confirmed'),
                    ('center_id', '=', self.center_id.id),
                    ('date_begin','<',self.date_end),
                    ('date_end','>',self.date_begin),
                    ('ubication_id', '=', self.ubication_id.id)
                ])
        if len(sessions)!=0: #hi ha solapaments
            raise ValidationError(_("There's another session in selected ubication") + self._get_additional_message())


        ## que se solapin amb algun dels recursos usats en la sessio en curs
        sessions = self.env['ems.session'].search([
                ('id', '!=', self.id),
                ('state', '=', 'confirmed'),
                ('center_id', '=', self.center_id.id),
                ('date_begin','<',self.date_end),
                ('date_end','>',self.date_begin),
            ])
        usats = False
        for r in self.resource_ids:
            for j in sessions:
                if r in j.resource_ids:
                    usats=True
                    break
            if usats:
                break
        if usats:
           raise ValidationError(_("There's another session using the same resources") + self._get_additional_message())

        ## que se solapin amb el mateix entrenador
        sessions = self.env['ems.session'].search([
                ('id', '!=', self.id),
                ('state', '=', 'confirmed'),
                ('center_id', '=', self.center_id.id),
                ('date_begin','<',self.date_end),
                ('date_end','>',self.date_begin),
                ('responsible_id', '=', self.responsible_id.id)
            ])
        if len(sessions)!=0: #hi ha solapaments
            raise ValidationError(_("There's another session with selected responsible") + self._get_additional_message())

        ## que se solapin amb el algun client
        sessions = self.env['ems.session'].search([
                ('id', '!=', self.id),
                ('state', '=', 'confirmed'),
                ('center_id', '=', self.center_id.id),
                ('date_begin','<',self.date_end),
                ('date_end','>',self.date_begin),
            ])
        usats = False
        for r in self.partner_ids.mapped('partner_id'):
            for j in sessions:
                if r in j.partner_ids.mapped('partner_id'):
                    usats=True
                    break
            if usats:
                break
        if usats:
           raise ValidationError(_("There's another session with selected customer") + self._get_additional_message())


    @api.constrains('state')
    def _check_state(self):
        if self.state == 'confirmed':
            self._check_all()

        #self.message_post(body='msg', subject='yy', type='notification', subtype="calendar.subtype_invitation")
        #self.message_post(type='notification')
        #def message_post(self, cr, uid, thread_id, body='', subject=None, type='notification', subtype=None, parent_id=False, attachments=None, context=None, **kwargs):
        #meeting_obj.message_post(cr, uid, attendee.event_id.id, body=_(("%s has accepted invitation") % (attendee.cn)),
        #self.message_post(cr, uid, event.id, body=_("An invitation email has been sent to attendee %s") % (partner.name,), subtype="calendar.subtype_invitation", context=context)
        #self.post.sudo(self.user_portal).message_post(body='Should crash', type='comment')
        #self.post.sudo(self.user_employee).message_post(body='Test0', type='notification')

    @api.constrains('date_begin', 'date_end')
    def _check_date_end(self):
        # check dates
        if self.date_end < self.date_begin:
            raise ValidationError(_('Closing Date cannot be set before Beginning Date')  + self._get_additional_message())

        self._onchange_date_end()

    @api.constrains('date_begin', 'date_end', 'center_id',
                    'ubication_id', 'resource_ids',
                    'responsible_id', 'partner_ids')
    def _check_session(self):
        #check state
        if self.state!='draft':
            raise ValidationError(_('You can only change a draft session')  + self._get_additional_message())


    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'draft':
                if rec.source_session_ids:
                    raise ValidationError(_("This session is linked to sessions '%s', deal with them before.") % rec.source_numbers)
                else:
                    super(ems_session, rec).unlink()
            else:
                raise ValidationError(_('You can only delete a draft session'))

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            #res.append((rec.id, rec.session_text))
            res.append((rec.id, '[%s] %s' % (rec.number, rec.partner_text)))

        return res



class ems_partner(models.Model):
    """ Ubication """
    _name = 'ems.partner'
    _description = 'Partner'

    partner_id = fields.Many2one('res.partner', string="Partner", ondelete='restrict', required=True)

    num_session = fields.Integer('Session', compute='_compute_session', inverse='_compute_session_inverse', readonly=True, default=-1, store=False)

    force_session = fields.Boolean(string='Force session', default=False)
    num_session_forced = fields.Integer('Session', required=False)

    phone = fields.Char(related='partner_id.phone', readonly=True)

    mobile = fields.Char(related='partner_id.mobile', readonly=True)

    email = fields.Char(related='partner_id.email', readonly=True)

    session_id = fields.Many2one('ems.session', ondelete='cascade',)

    date_begin_str = fields.Char(compute="_compute_date_begin_str", store=False)
    time_begin_str = fields.Char(compute="_compute_date_begin_str", store=False)

    _sql_constraints = [('attendee_session_unique', 'unique(session_id, partner_id)',_("Attendee duplicated"))]


    @api.one
    @api.depends('session_id.date_begin')
    def _compute_date_begin_str(self):
        if self.session_id:
            dt = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(self.session_id.date_begin))

            #lang_code = self.partner_id.lang or self.env.lang
            lang_code = self.env.lang
            #lang = self.env['res.lang'].search([('code', '=', lang_code)])

            self.date_begin_str = babel.dates.format_date(dt, format='full', locale=lang_code).capitalize()

            self.time_begin_str = dt.strftime('%H:%M')


    @api.one
    @api.depends('partner_id', 'force_session','session_id')
    def _compute_session(self):
        if self.session_id.service_id.is_ems:
            if self.force_session:
                self.num_session = self.num_session_forced
            else:
                sessions_ant = self.env['ems.partner'].search([('partner_id','=', self.partner_id.id)]).\
                    filtered(lambda x: x.session_id.center_id==self.session_id.center_id and
                                   x.session_id.state in ('cancelled', 'confirmed') and
                                   x.session_id.service_id.is_ems and
                                   x.session_id.date_begin<self.session_id.date_begin)

                self.num_session = len(sessions_ant) + 1
                tt = sessions_ant.filtered(lambda x: x.force_session)
                if tt:
                    self.num_session += tt.num_session_forced - 1
        else:
            self.num_session = -1

    @api.one
    def _compute_session_inverse(self):
        self.num_session_forced = self.num_session

    @api.constrains('force_session')
    def _check_force_session(self):
        if self.force_session:
            sessions_ant = self.env['ems.partner'].search([('partner_id','=', self.partner_id.id)]).\
                    filtered(lambda x: x.session_id.center_id==self.session_id.center_id and
                                       x.session_id.state=='confirmed' and
                                       x.session_id.service_id.is_ems and
                                       x.session_id.date_begin<self.session_id.date_begin
                                    )
            if len(sessions_ant)!=0:
                raise ValidationError(_("Only the first session can have a forced session."))

    @api.multi
    def view_sessions(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "ems.session",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [("partner_ids.partner_id.id", "=", self.partner_id.id)],
            #"context": {'search_default_partner_text': self.partner_id.name, 'default_partner_text' : self.partner_id.name },
            #"res_id": a_product_id,
            #"target": "new",
        }


    '''
    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            if not self.session_id.service_id.is_ems:
                self.num_session = -1
            else:
                ## obtenim les sessions quer contenen el aprnter actualitzat
                sessions = self.env['ems.session'].search([
                        ('state', '=', 'confirmed'),
                        ('center_id', '=', self.session_id.center_id.id),
                        ('date_end','<=',self.session_id.date_begin)])\
                    .filtered(lambda x: x.service_id.is_ems)\
                    .filtered(lambda x: self.partner_id in x.partner_ids.mapped('partner_id'))\
                    .sorted(lambda x: x.date_begin)
                if sessions:
                    self.num_session = sessions[-1].partner_ids.filtered(lambda x: x.partner_id.id == self.partner_id.id).session + 1
                else:
                    self.num_session = 0
    '''





class ems_ubication(models.Model):
    """ Ubication """
    _name = 'ems.ubication'
    _description = 'Ubication'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')

    is_all_center = fields.Boolean(string="All center", help="Indicates if this ubication represents the whole center", default=False)

    center_id = fields.Many2one('ems.center', string='Center',
                                ondelete='restrict',
                                required=True, readonly=False, default=lambda self: self.env.user.center_id)

    service_ids = fields.One2many('ems.ubication.service.rel', 'ubication_id', string="Services")


    @api.multi
    def name_get(self):
        result = []
        for ubi in self:
            result.append((ubi.id, '%s (%s)' % (ubi.name, ubi.center_id.name)))

        return result



class ems_service(models.Model):
    """ Session Type """
    _name = 'ems.service'
    _description = 'Service'

    name = fields.Char(string='Name', required=True, help="Minutes")
    description = fields.Text(string='Description')
    color = fields.Selection(selection=CALENDAR_COLORS, string="Color", required=True)

    ubication_ids = fields.One2many('ems.ubication.service.rel', 'service_id', string="Ubications")

    duration = fields.Integer(string='Duration', required=True)

    is_ems = fields.Boolean(string='EMS', default=False)

    is_meeting = fields.Boolean(string='Meeting', default=False)

    min_attendees = fields.Integer(string="Minimum attendees", help="Minimum number of attendees", required=True, default=0)
    max_attendees = fields.Integer(string="Maximum attendees", help="Maximum number of attendees (-1 for no restriction)", required=True, default=-1)

    _sql_constraints = [('service_color_unique', 'unique(color)',_("Color already used"))]

    @api.constrains('min_attendees', 'max_attendees')
    def check_attendees(self):
        if self.max_attendees<0 and self.max_attendees!=-1:
            self.max_attendees = -1

        if self.min_attendees<0:
            raise ValidationError(_('The minimum attendees cannot be less than 0.'))

        if self.max_attendees>0:
            if self.min_attendees>self.max_attendees:
                raise ValidationError(_('The minimum attendees cannot be greater than the maximum.'))



class ems_ubication_service(models.Model):
    """ Session Type """
    _name = 'ems.ubication.service.rel'
    _description = 'Ubication-Service relation'
    _order = 'sequence'

    service_id = fields.Many2one('ems.service', string="Service", ondelete='restrict')

    ubication_id = fields.Many2one('ems.ubication', string="Ubication", required=True, ondelete='restrict')

    resource_ids = fields.Many2many('ems.resource', string='Resources',
        required=False, readonly=False)

    sequence = fields.Integer('Sequence', default=1)

    '''
    _sql_constraints = [
        ('rel_uniq', 'unique(ubication_id, service_id)', 'Duplicated ubication'),
        ('seq_uniq', 'unique(service_id, sequence)', 'Duplicated sequence'),
    ]
    '''

    '''
    @api.model
    def create(self, vals):
        emssr =  super(ems_ubication_service, self).create(vals)

        #self.env['ems.service.resource.rel'].search([('service_id','=',emssr.service_id)])
        return emssr
    '''


class ems_resource(models.Model):
    """Resources"""
    _name = 'ems.resource'
    _description = 'Resource'

    name = fields.Char(string='Resource name', required=True,
        readonly=False)

    center_id = fields.Many2one('ems.center', string='Center', default=lambda self: self.env.user.center_id,
                                ondelete='restrict',
                                required=True, readonly=False)

    description = fields.Text(string='Description',
        readonly=False)

    @api.multi
    def name_get(self):
        result = []
        for res in self:
            result.append((res.id, '%s (%s)' % (res.name, res.center_id.name)))

        return result



class ems_timetable(models.Model):
    """Session"""
    _name = 'ems.timetable'
    _description = 'Timetable'
    _order = 'center_id,day,time_begin,time_end desc'

    center_id = fields.Many2one('ems.center', string='Center',
                                ondelete='restrict',
                                required=True, readonly=False, default=lambda self: self.env.user.center_id)

    type = fields.Selection(selection=[('weekday', _('Weekday')), ('yearday', _('Yearday'))], required=True, default='weekday')

    # weekday Local time ina a timezone tz
    day = fields.Selection(selection=DAYS_OF_WEEK, required=False, readonly=False, default=1)
    time_begin = fields.Char(string='Initial time', size=5, required=False, readonly=False, default='00:00')
    time_end = fields.Char(string='End time', size=5, required=False, readonly=False, default='01:00')

    # yearday UTC time
    date_begin_year = fields.Datetime(string="Date begin", default=fields.datetime.now().replace(second=0, microsecond=0))
    date_end_year = fields.Datetime(string="Date end", default=fields.datetime.now().replace(second=0, microsecond=0) + datetime.timedelta(hours=1))

    date_begin = fields.Datetime(compute='_compute_date_begin') #, inverse="_inverse_date_begin")
    date_end = fields.Datetime(compute='_compute_date_end') #, inverse="_inverse_date_end")

    responsible_id = fields.Many2one('ems.responsible', string='Responsible',
                                     ondelete='restrict', required=True, readonly=False)

    color_rel = fields.Selection(related="responsible_id.color", store=False)

    sequence = fields.Integer('Sequence', help="Sequence for the handle.")


    @api.depends('time_begin', 'date_begin_year')
    def _compute_date_begin(self):
        for rec in self:
            if rec.type == 'weekday':
                rec.date_begin = daytime_loc2datetime_utc(rec.day, rec.time_begin, rec._context.get('tz'))
            else:
                rec.date_begin = rec.date_begin_year

    '''
    def _inverse_date_begin(self):
        if self.date_begin:
            if self.type == 'weekday':
                date_begin = pytz.utc.localize(fields.Datetime.from_string(self.date_begin))
                self.day, self.time_begin = datetime_utc2daytime_loc(date_begin, self._context.get('tz'))
            else:
                self.date_begin_year = self.date_begin
    '''


    @api.depends('time_end', 'date_end_year')
    def _compute_date_end(self):
        for rec in self:
            if rec.type == 'weekday':
                rec.date_end = daytime_loc2datetime_utc(rec.day, rec.time_end, rec._context.get('tz'))
            else:
                rec.date_end = rec.date_end_year

    '''
    def _inverse_date_end(self):
        if self.date_end:
            if self.type == 'weekday':
                date_end = pytz.utc.localize(fields.Datetime.from_string(self.date_end))
                self.day, self.time_end = datetime_utc2daytime_loc(date_end, self._context.get('tz'))
            else:
                self.date_end_year = self.date_end
    '''


    @api.constrains('time_end', 'time_begin')
    def _check_times(self):
        if self.type=='weekday':
            self.env.time_update = False
            # check tie format
            timestr2int(self.time_begin)
            timestr2int(self.time_end)
            # check order
            if self.time_begin>=self.time_end:
                raise ValidationError(_("The initial time cannot be greater or equal than end time"))
        else:
            self.env.time_update = True



    @api.constrains('date_begin_year', 'date_end_year')
    def _check_dates(self):
        if self.type=='yearday':
            self.env.date_year_update = False
            # check tie format
            dt_begin_utc =  pytz.utc.localize(fields.Datetime.from_string(self.date_begin_year))
            dt_end_utc = pytz.utc.localize(fields.Datetime.from_string(self.date_end_year))
            if dt_end_utc<=dt_begin_utc:
                raise ValidationError(_("The initial date cannot be greater or equal than end date"))

            dt_begin_loc = dt_begin_utc.astimezone(pytz.timezone(self._context.get('tz')))
            dt_end_loc = dt_end_utc.astimezone(pytz.timezone(self._context.get('tz')))
            #if dt_begin_loc.day<dt_end_loc.day:
            #    self.date_begin_year = dt_begin_utc - datetime.timedelta(days=1)

            if dt_begin_loc.day!=dt_end_loc.day:
                raise ValidationError(_("The interval has to be of the same day"))
        else:
            self.env.date_year_update = True

    @api.constrains('type')
    def _clear_type_data(self):
        if self.type=='weekday':
            self.date_begin_year = False
            self.date_end_year = False
        else:
            self.day = False
            self.time_begin = False
            self.time_end = False




    @api.constrains('center_id', 'responsible_id', 'type', 'day', 'time_begin', 'time_end', 'date_begin_year', 'date_end_year')
    def _check_timetable(self):
        # serach for other timetables of the same day and same hours
        if self.type=='weekday':
            other_tts = self.env['ems.timetable'].search([  ('id', '!=', self.id),
                                                            ('center_id','=', self.center_id.id),
                                                            ('day','=', self.day),
                                                            ('time_end','>', self.time_begin),
                                                            ('time_begin','<', self.time_end),
                                                            ('responsible_id','=', self.responsible_id.id)
                                                            ])
        else:
            other_tts = self.env['ems.timetable'].search([  ('id', '!=', self.id),
                                                            ('center_id','=', self.center_id.id),
                                                            ('date_end_year','>', self.date_begin_year),
                                                            ('date_begin_year','<', self.date_end_year),
                                                            ('responsible_id','=', self.responsible_id.id)
                                                            ])

        msg = []
        for tt in other_tts:
            msg.append(tt.name_get()[0][1])

        if msg:
            raise ValidationError(_("Overlaps detected for responsible %s:\n%s") % (self.responsible_id.user_id.name, '\n'.join(msg)))




    @api.multi
    def name_get(self):
        res = []
        for tt in self:
            if tt.type=='weekday':
                name = "%s - %s (%s - %s)" % (tt.center_id.name, dict(DAYS_OF_WEEK)[tt.day], tt.time_begin, tt.time_end)
            else:
                name = "%s (%s - %s)" % (tt.center_id.name,
                                         fields.Datetime.context_timestamp(self, fields.Datetime.from_string(tt.date_begin_year)),
                                         fields.Datetime.context_timestamp(self, fields.Datetime.from_string(tt.date_end_year)))
            res.append((tt.id, name))

        return res


class ems_responsible(models.Model):
    """Session"""
    _name = 'ems.responsible'
    _description = 'Responsible'
    #_order = 'sequence'

    user_id = fields.Many2one('res.users', string='User', readonly=False, required=True, ondelete='restrict')

    name = fields.Char(string="Name")

    color = fields.Selection(selection=CALENDAR_COLORS, string="Color", required=True)

    is_staff = fields.Boolean(string="Staff", help='Indicates if responsible is staff or external', default=False)

    description = fields.Text(string='Description', required=False)

    timetable_ids = fields.One2many('ems.timetable', 'responsible_id', required=True,
        readonly=False,
        domain=['|', '&', ('type','=', 'yearday'),
                ('date_begin_year','>=', fields.Datetime.to_string(datetime.datetime.combine(fields.Datetime.from_string(fields.Datetime.now()), datetime.time(0,0,0)))),
                ('type', '=', 'weekday')
                ])


    absence_ids = fields.One2many('ems.responsible.absence', 'responsible_id', readonly=False)

    session_ids = fields.One2many('ems.session', 'responsible_id', readonly=False,
                                  domain=[('date_begin','>=', fields.Datetime.to_string(datetime.datetime.combine(fields.Datetime.from_string(fields.Datetime.now()), datetime.time(0,0,0))))])

    _sql_constraints = [('user_id_unique', 'unique(user_id)',_("Responsible already exists")),
                        ('service_color_unique', 'unique(color)',_("Color already used"))]

    @api.multi
    def name_get(self):
        res = []
        for tr in self:
            name = tr.name if tr.name else tr.user_id.name
            res.append((tr.id, name))
        return res

    @api.multi
    def button_print_sessions(self):
        # curretn month
        #date_from = fields.Date.from_string(fields.Date.context_today(self)).replace(day=1)
        #date_to = (date_from + datetime.timedelta(days=32)).replace(day=1) + datetime.timedelta(days=-1)

        #datetime.datetime.combine(context_today(), datetime.time(0,0,0)).replace(day=1))
        #datetime.datetime.combine(context_today()+datetime.timedelta(days=32), datetime.time(0,0,0)).replace(day=1))]"

        # previous month
        #datetime.datetime.combine((context_today().replace(day=1)+datetime.timedelta(days=-1)).replace(day=1), datetime.time(0,0,0))),
        #datetime.datetime.combine(context_today().replace(day=1), datetime.time(0,0,0)))]"

        '''
        wizard_id = self.env['ems.responsible.sessions.print.wizard'].create({
                    'responsible_id': self.id,
                    'date_from': date_from,
                    'date_to': date_to,
                })
        '''

        return {
                'type': 'ir.actions.act_window',
                'name': _("Print Responsible sessions"),
                'res_model': 'ems.responsible.sessions.print.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                #'views': [(view.id, 'form')],
                #'view_id': view.id,
                #'res_id': wizard_id.id,
                'target': 'new',
                #'context': context,
                }





class ems_responsible_absence(models.Model):
    """Session"""
    _name = 'ems.responsible.absence'
    _description = 'Responsible Absence'
    _order = 'responsible_id,center_id,ini_date'

    responsible_id = fields.Many2one('ems.responsible', string='Responsible', required=True, readonly=False, ondelete='restrict')

    center_id = fields.Many2one('ems.center', string='Center',
                                ondelete='restrict',
                                required=True, readonly=False, default=lambda self: self.env.user.center_id)

    ini_date = fields.Datetime(string='Initial Date', required=True)
    end_date = fields.Datetime(string='End Date', required=True)

    reason = fields.Text(string='Reason', required=False)

    '''
    @api.multi
    def name_get(self):
        res = []
        for tr in self:
            res.append((tr.id, tr.user_id.name))
        return res
    '''


class ems_source(models.Model):
    _name = 'ems.source'

    name = fields.Char(string='Origin', translate=True)
    is_detail = fields.Boolean('Detail field', default=False)




##### Inhrits ##########33


class res_users(models.Model):
    _inherit = 'res.users'

    center_id = fields.Many2one('ems.center', string='Center', ondelete='restrict',
        required=False, readonly=False)


class res_partner(models.Model):
    _inherit = 'res.partner'

    birth_date = fields.Date("Birth date")
    source_id = fields.Many2one('ems.source', string='Origin', ondelete='restrict')
    is_detail = fields.Boolean(related='source_id.is_detail')
    source_detail = fields.Char(string='Detail')
    health_survey = fields.Selection([('notoall', 'No to all'), ('yessevere', 'Yes, severe'),
                                      ('yesminor', 'Yes, minor')],
                                    help="Health survey")
    health_spec = fields.Text(string='Health specifications')
    medical_consent = fields.Boolean(string='Medical consent')



############ WIZARDS #############


class WizardSessionReschedule(models.TransientModel):
    _name = 'ems.session.reschedule.wizard'

    ### STEP 1
    session_id = fields.Many2one('ems.session', string="Session", domain=[('state', 'in', ('confirmed', 'reschedulepending'))])

    partner_ids = fields.One2many(comodel_name='ems.session.reschedule.partners.wizard', inverse_name='reschedule_id',
                               default=lambda self: self._default_partner_ids())

    ### STEP 2
    responsible_id = fields.Many2one(comodel_name='ems.responsible', string="New responsible", required=False, readonly=False)

    attendee_ids = fields.Many2many(comodel_name='res.partner', string="New attendees")

    session_ids = fields.One2many(comodel_name='ems.session.reschedule.sessions.wizard', inverse_name='reschedule_id')

    weekday_begin = fields.Selection(selection=DAYS_OF_WEEK, string="New weekday")


    reason = fields.Char(string='Reason', required=False, help="The reason why of the reschedule", default=lambda self: self._default_reason())

    out_of_time = fields.Boolean(string='Out of time', help='The attendee rescheduled a session out of time', default=False)


    ### COMMON
    state = fields.Selection(selection=[('step1', 'Step 1'), ('step2', 'Step 2'), ('step3', 'Step 3')],
                             string='Status', readonly=True, default='step1')



    def _default_partner_ids(self):
        session_ids = self.env['ems.session'].browse(self.env.context.get('active_ids'))

        a = []
        for g, s in enumerate(session_ids, 1):
            a += [(0, 0, x) for x in s.split_session(g)]

        return a

    def _default_reason(self):
        session_id = self.env['ems.session'].browse(self.env.context.get('active_ids'))

        if len(session_id)==1:
            return session_id.reason

    @api.multi
    def button_add_session(self):
        if len(self.partner_ids)==0:
            g = 1
        else:
            dup = self.partner_ids.filtered(lambda x: x.session_id.id==self.session_id.id)
            if len(dup)!=0:
                raise ValidationError(_("That session is already added"))
            g = max(self.partner_ids.mapped('group')) + 1

        self.partner_ids = [(0, 0, x) for x in self.session_id.split_session(g)]

        self.session_id = False

        return _reopen(self)

    @api.multi
    def button_remove_session(self):
        toremove = self.partner_ids.filtered(lambda x: x.session_id.id==self.session_id.id)
        self.partner_ids = [(2, x.id, 0) for x in toremove]

        self.session_id = False

        return _reopen(self)


    @api.multi
    def button_step1(self):
        self.state = 'step1'
        return _reopen(self)


    @api.multi
    def button_step2(self):
        self.state = 'step2'
        return _reopen(self)



    @api.multi
    def button_update(self):
        for s in self.session_ids:
            values = {}
            if self.responsible_id:
                values['responsible_id'] = self.responsible_id.id

            if self.attendee_ids:
                values['partner_ids'] = [(6, _, self.attendee_ids.mapped('id'))]

            if self.weekday_begin:
                # busquem si algun dels partners de cada sessio ja te una altra sessio en la mateixa setmana
                # en cas afirmatiu, donem error
                date_begin_dt_loc = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(s.date_begin))
                weekday_loc = date_begin_dt_loc.isoweekday()
                mon_dt_loc = date_begin_dt_loc - datetime.timedelta(days=weekday_loc-1)

                """
                # comprovrm que no hi hagi cap en la mateixa setmana ni pendent de canviar en la llista
                mon_dt_loc0 = mon_dt_loc.replace(hour=0, minute=0, second=0)
                sun_dt_loc0 = mon_dt_loc.replace(hour=23, minute=59, second=59) + datetime.timedelta(days=7-1)

                mon_str_utc0 = fields.Datetime.to_string((mon_dt_loc0.astimezone(pytz.utc)).replace(tzinfo=None))
                sun_str_utc0 = fields.Datetime.to_string((sun_dt_loc0.astimezone(pytz.utc)).replace(tzinfo=None))

                sessions0 = self.env['ems.partner'].search([('session_id.id', 'not in', self.session_ids.mapped('source_session_ids.id')),
                                                           ('session_id.state', '=', 'confirmed'),
                                                           ('session_id.center_id', '=', s.center_id.id),
                                                           ('session_id.service_id.is_ems', '=', True),
                                                           ('session_id.date_begin', '>=', mon_str_utc0),
                                                           ('session_id.date_begin', '<=', sun_str_utc0),
                                                           ('partner_id', 'in', s.partner_ids.mapped('id'))
                                                          ]).mapped('session_id')
                if len(sessions0)>0:
                    raise ValidationError(_("Group %i: There's more than one session in the same week not listed here.") % s.group)

                sessions1 = self.session_ids.filtered(lambda x: x.group!=s.group and
                                                                x.center_id.id==s.center_id.id and
                                                                x.service_id.is_ems==x.service_id.is_ems and
                                                                x.date_begin>=mon_str_utc0 and
                                                                x.date_begin<=sun_str_utc0 and
                                                                x.partner_ids.id in s.partner_ids.mapped('id')
                                                      )
                if len(sessions1)>0:
                    raise ValidationError(_("Group %i: There's more than one session in the same week listed here.") % s.group)
                """

                date_begin9_dt_loc = mon_dt_loc + datetime.timedelta(days=self.weekday_begin-1)
                date_begin9_dt_utc = (date_begin9_dt_loc.astimezone(pytz.utc)).replace(tzinfo=None)

                values['date_begin'] = date_begin9_dt_utc
                values['date_end'] = date_begin9_dt_utc + datetime.timedelta(minutes=s.duration)

            if values:
                s.write(values)

        self.responsible_id = False
        self.attendee_ids = False
        self.weekday_begin = False

        return _reopen(self)

    @api.multi
    def button_grouping(self):
        # agrupem els serveis per grup i fem comprovacions
        d = {}
        for p in self.partner_ids:
            if p.session_id.state not in ('confirmed', 'reschedulepending'):
                raise ValidationError(_("Only confirmed and reschedule pending sessions can be rescheduled"))

            if p.group not in d:
                d[p.group]=[]
            d[p.group].append(p.id)

        # esborrem tot lesxitent
        self.session_ids = [(2, x.id, 0) for x in self.session_ids ]

        # que en el cas que hi hagi mes d'un per data, les dades siguin iguals a tots
        a = []
        for k, v in d.items():
            ps = self.env['ems.session.reschedule.partners.wizard'].browse(v)
            if len(ps.mapped('id'))!=len(set(ps.mapped('partner_id.id'))):
                raise ValidationError(_("An attendee can only appears once in a group (%i)") % k)
            vals = {'group': k,
                    'partner_ids': [(4, x.partner_id.id, 0) for x in ps],
                    'center_id': ps[0].center_id.id,
                    'service_id': ps[0].service_id.id,
                    'ubication_id': ps[0].ubication_id.id,
                    'resource_ids': [(4, x.id, 0) for x in ps[0].resource_ids],
                    'responsible_id': ps[0].responsible_id.id,
                    'date_begin': ps[0].date_begin,
                    'duration': ps[0].duration,
                    'date_end': fields.Datetime.from_string(ps[0].date_begin) + datetime.timedelta(minutes=ps[0].duration),
                    'source_session_ids': list(set([(4, x.session_id.id, 0) for x in ps]))
                    }
            a.append((0, _, vals ))

        self.session_ids = a

        self.state = 'step3'

        return _reopen(self)



    @api.multi
    def button_reschedule(self):
        # mantenim una llista de les session source modificsades pel cas d'spelitar una sessio que les n resultants
        # tindriem la mateixa source i les dades n-aries (target session) ok, pero les unaries com el stat
        # podrien nduir a error
        ses = set()
        for s in self.session_ids:
            # comprovm que s'ha canviat alguna cosa
            fsr, fsp = set(), set()
            fsr.add(frozenset(s.resource_ids.mapped('id')))
            fsp.add(frozenset(s.partner_ids.mapped('id')))
            if set(s.source_session_ids.mapped('center_id.id')) == { s.center_id.id } and \
                    set(s.source_session_ids.mapped('service_id.id')) == { s.service_id.id } and \
                    set(s.source_session_ids.mapped('ubication_id.id')) == { s.ubication_id.id } and \
                    set([frozenset(x.resource_ids.mapped('id')) for x in s.source_session_ids]) == fsr and \
                    set(s.source_session_ids.mapped('responsible_id.id')) == { s.responsible_id.id } and \
                    set([frozenset(x.partner_ids.mapped('partner_id.id')) for x in s.source_session_ids]) == fsp and \
                    set(s.source_session_ids.mapped('duration')) == { s.duration } and \
                    set(s.source_session_ids.mapped('date_begin')) == { s.date_begin } and \
                    set(s.source_session_ids.mapped('date_end')) == { s.date_end }:
                raise ValidationError(_("Nothing to change"))

            # definim els vlaors de la nova sessio

            vals = {'center_id': s.center_id.id,
                    'service_id': s.service_id.id,
                    'ubication_id': s.ubication_id.id,
                    'resource_ids': [(4, r.id, _) for r in s.resource_ids],
                    'responsible_id': s.responsible_id.id,
                    'partner_ids': [(0, _, {'partner_id': x.id}) for x in s.partner_ids],
                    'duration': s.duration,
                    'date_begin': s.date_begin,
                    'date_end': s.date_end,

                    'source_session_ids': [(4, x.id, 0) for x in s.source_session_ids],

                }

            # tractem la descripcio en cass de multiples sources
            description_l = []
            for x in s.source_session_ids:
                if x.description and len(x.description.strip())!=0:
                    description_l.append('(%s) %s' % (x.number, x.description))
            if description_l!=[]:
                vals['description'] = '\n'.join(description_l)

            ## creem la sessio
            session9 = self.env['ems.session'].with_context(additional_message='[Group %i]' % s.group).create(vals)

            ## creem els vincles i les dades en les sessions source
            for s_src in s.source_session_ids:
                if s_src.id not in ses:
                    if s_src.state not in ('confirmed', 'reschedulepending'):
                        raise ValidationError(_("Only confirmed and reschedule pending sessions can be rescheduled"))

                    s_src.reason = self.reason
                    s_src.out_of_time = self.out_of_time
                    s_src.state = 'rescheduled'

                    ses.add(s_src.id)

                s_src.target_session_ids = [(4, session9.id, 0)]

            session9.button_confirm()



    '''
    @api.multi
    def reschedule_edit(self):
        session9 = self.reschedule()
        return {
            'type': 'ir.actions.act_window',
            #'name': _("Warning"),
            'res_model': 'ems.session',
            'view_type': 'form',
            'view_mode': 'form',
            #'views': [(view.id, 'form')],
            #'view_id': view.id,
            'res_id': session9.id,
            #'target': 'new',
            #'context': context,
        }
    '''







class WizardSessionReschedulePartners(models.TransientModel):
    _name = 'ems.session.reschedule.partners.wizard'

    reschedule_id = fields.Many2one(comodel_name='ems.session.reschedule.wizard', ondelete='cascade')

    group = fields.Integer('Group', required=True)

    session_id = fields.Many2one('ems.session', string="Session", required=True, domain=[('state', 'in', ('confirmed', 'reschedulepending'))])

    number = fields.Char(string="Session")

    center_id = fields.Many2one('ems.center', string='Center', required=True)
    partner_id = fields.Many2one('res.partner', string="Attendee", required=True)
    service_id = fields.Many2one('ems.service', string="Service", required=True)
    ubication_id = fields.Many2one('ems.ubication', string="Ubication", required=True)
    resource_ids = fields.Many2many('ems.resource', string="Resources", required=False)
    responsible_id = fields.Many2one('ems.responsible', string="Responsible", required=True)
    date_begin = fields.Datetime(string='Start date', required=True, readonly=False)
    duration = fields.Integer(string='Duration', required=True, readonly=False)



class WizardSessionRescheduleSessions(models.TransientModel):
    _name = 'ems.session.reschedule.sessions.wizard'

    reschedule_id = fields.Many2one(comodel_name='ems.session.reschedule.wizard', ondelete='cascade')

    group = fields.Integer('Group', required=True)

    center_id = fields.Many2one('ems.center', string="Center", required=True)
    partner_ids = fields.Many2many('res.partner', string="Attendees", required=True)
    service_id = fields.Many2one('ems.service', string="Service", required=True)
    ubication_id = fields.Many2one('ems.ubication', string="Ubication", required=True)
    resource_ids = fields.Many2many('ems.resource', string="Resources", required=False)
    responsible_id = fields.Many2one('ems.responsible', string="Responsible", required=True)

    date_helper = fields.Boolean(string='Date helper')
    date_begin_last = fields.Datetime(string='Last start date', help="Last session start date. If there's more than one attendees this date corresponds to the later session", required=False, readonly=True)
    weeks = fields.Integer(string='Weeks', help='Number of weeks after last session', required=True, readonly=False, default=1)
    allow_past_date = fields.Boolean(string='Allow past date', help='Allows reschedule sessions in the past', default=False)
    date_begin = fields.Datetime(string='Start date', required=True, readonly=False)
    weekday_begin = fields.Char(string='Day of week', compute="_compute_weekdata")
    weekyear_begin = fields.Integer(string='Week of year', compute="_compute_weekdata")
    date_end = fields.Datetime(string='End date', required=True, readonly=False)
    duration = fields.Integer(string='Duration', required=True, readonly=False)

    #state_new = fields.Datetime(string='New start date', required=False, readonly=False)

    source_session_ids = fields.Many2many('ems.session', relation='ems_wizard_reschedule_sessions_source_session_rel')
    source_session_numbers = fields.Char(string="Source sessions", compute="_compute_source_session_numbers")


    @api.depends('source_session_ids')
    def _compute_source_session_numbers(selfs):
        for self in selfs:
            self.source_session_numbers = ', '.join(self.source_session_ids.mapped('number'))

    @api.depends('date_begin')
    def _compute_weekdata(selfs):
        for self in selfs:
            date_begin_dt_loc = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(self.date_begin))
            self.weekday_begin = babel.dates.format_date(date_begin_dt_loc, format='EEEE', locale=self.env.lang).capitalize()
            self.weekyear_begin = babel.dates.format_date(date_begin_dt_loc, format='w', locale=self.env.lang)

    @api.onchange('service_id')
    def onchange_service(self):
        # actulitzem la data fi
        self.date_end = fields.Datetime.from_string(self.date_begin) + datetime.timedelta(minutes=self.service_id.duration)

        domains = {}
        ids = []
        ids2 = []
        ids22 = []
        for s in self.service_id.ubication_ids.filtered(lambda x: x.ubication_id.center_id==self.center_id).sorted(lambda x: x.sequence):
            ids.append(s.ubication_id.id)

            ids2.append(s.resource_ids)
            ids22+=s.resource_ids.mapped('id')

        domains.update({'ubication_id': [('id', 'in', ids)]})
        if ids!=[]:
            self.ubication_id = ids[0]
        else:
            self.ubication_id = False

        domains.update({'resource_ids': [('id', 'in', ids22)]})
        if ids2!=[]:
            self.resource_ids = ids2[0]
        else:
            self.resource_ids = False

        self.duration=self.service_id.duration

        res = {}
        if len(domains)!=0:
            res = dict(domain=domains)

        return res

    @api.onchange('duration')
    def _onchange_duration(self):
        self.date_end = fields.Datetime.from_string(self.date_begin) + datetime.timedelta(minutes=self.duration)

    @api.onchange('date_begin')
    def _onchange_date_begin(self):
        self.date_end = fields.Datetime.from_string(self.date_begin) + datetime.timedelta(minutes=self.duration)

    @api.onchange('date_end')
    def _onchange_date_end(self):
        diff = fields.Datetime.from_string(self.date_end) - fields.Datetime.from_string(self.date_begin)
        self.duration = (diff.days*24*60*60 + diff.seconds) / 60


    @api.onchange('partner_ids', 'date_helper', 'weeks', 'allow_past_date')
    def _onchange_partner(self):
        if self.date_helper:
            ### cerquem la ultima sessio del partner
            # totes les sessions ems dels partners
            sessions0 = self.env['ems.partner'].search([('session_id.state', '=', 'confirmed'),
                                                        ('session_id.center_id', '=', self.center_id.id),
                                                        ('session_id.service_id.is_ems', '=', True),
                                                        ('partner_id', 'in', self.partner_ids.mapped('id') )
                                                        ]).mapped('session_id')

            now = fields.Datetime.from_string(fields.Datetime.now()).replace(second=0)
            if sessions0:   # si hi ha sessions
                date_begin_last0 = sessions0.sorted(lambda x: x.date_begin)[-1].date_begin
                self.date_begin_last = date_begin_last0
            else:   # si no hi ha cap sessio, (aixo vol dir que el customer ha canviat per un de nou)
                date_begin_last0 = fields.Datetime.to_string(now)
                self.date_begin_last = False

            if not self.allow_past_date: # si no permetem que hi hagi replanmificacions anteorir a la data actual
                if fields.Datetime.from_string(date_begin_last0)<now:
                    date_begin_last0 = fields.Datetime.to_string(now)

            self.date_begin = fields.Datetime.from_string(date_begin_last0) + datetime.timedelta(days=self.weeks*7)

        '''
        else:
            pass
            self.date_begin_last = False
            self.date_begin = self.env.context['old']['date_begin']
            self.duration = self.env.context['old']['duration']
            self.date_end = self.date_begin +  datetime.timedelta(minutes=self.duration)
            del self.env.context['old']
        '''



    @api.constrains('date_begin', 'date_end')
    def _check_date_end(self):
        if self.date_end < self.date_begin:
            raise ValidationError(_('Closing Date cannot be set before Beginning Date'))


class WizardMessage(models.TransientModel):
    _name = 'ems.message.wizard'

    message = fields.Char(string="Message", readonly=True)

    model_name = fields.Char()

    @api.multi
    def accept(self):
        session_id = self.env[self.model_name].browse(self._context.get('active_id'))

        ## enca carreguem la sesio replanificada
        if len(session_id.target_session_ids.filtered(lambda x: x.state!='draft'))!=0:
            raise ValidationError(_("The target sessions have to be in draft state to be deleted."))

        '''
        obj_tmp = session_id.target_session_id

        session_id.target_session_id = False
        obj_tmp.source_session_id = False

        obj_tmp.unlink()

        session_id.state = 'draft'
        '''

        ids_tmp = session_id.target_session_ids.mapped('id')

        session_id.target_session_ids = [(5, 0, 0)]

        for t in self.env['ems.session'].browse(ids_tmp):
            t.source_session_ids = [(5, 0, 0)]
            t.unlink()

        session_id.state = 'draft'


class WizardSessionCancel(models.TransientModel):
    _name = 'ems.session.cancel.wizard'

    reason = fields.Char(string='Reason', required=False)

    @api.multi
    def accept(self):
        session_id = self.env['ems.session'].browse(self._context.get('active_id'))
        session_id.reason = self.reason
        session_id.state = 'cancelled'


class WizardSessionReschedulePending(models.TransientModel):
    _name = 'ems.session.reschedule.pending.wizard'

    reason = fields.Char(string='Reason', required=False)

    @api.multi
    def accept(self):
        session_id = self.env['ems.session'].browse(self._context.get('active_id'))
        session_id.reason = self.reason
        session_id.state = 'reschedulepending'

class WizardSessionPrint(models.TransientModel):
    _name = 'ems.session.print.wizard'

    session_from = fields.Integer(string='From session', required=True)
    session_to = fields.Integer(string='To session', required=True)


    @api.constrains('session_from', 'session_to')
    def _check_session_num(self):
        if self.session_from<=0 or self.session_to<=0:
            raise ValidationError(_("The session number must be greater than 0"))
        else:
            if self.session_to<self.session_from:
                 raise ValidationError(_("The session number to must be greater or equal than session number from"))

    @api.multi
    def button_print(self):
        datas = {
            'ids': self.env.context.get('active_ids'),
            'model': self._name,
            'button': True,
            'session_from': self.session_from,
            'session_to': self.session_to,

        }
        #call the report
        return {
                   'type': 'ir.actions.report.xml',
                   'report_name': 'ems.report_emssessionsummary',
                   'datas': datas
               }


class WizardSessionSchedule(models.TransientModel):
    _name = 'ems.session.schedule.wizard'

    session_id = fields.Many2one('ems.session', required=False)

    num_sessions = fields.Integer(string='Number of sessions', help="Number of session to schedule", required=True)
    days = fields.Integer(string='Day interval', help="Days between sessions", required=True)
    action = fields.Selection(selection=[('draft', 'Draft'), ('confirm', 'Confirm'), ('schedulepending', 'Schedule pending')],
                              string='Action', help="Try to change state of sessions after created", default='draft')
    date_begin = fields.Datetime(String="From date", help="Date to the first new session and from the others will be calculated", required=True)

    @api.constrains('num_sessions')
    def _check_num_sessions(self):
        if self.num_sessions<1:
            raise ValidationError(_("The number of session to schedule must be greater than 0"))

    @api.constrains('days')
    def _check_days(self):
        if self.days<1:
            raise ValidationError(_("The day interval of session to schedule must be greater than 0"))


    @api.multi
    def schedule(self):
        d = []
        for n in range(self.num_sessions):
            date_begin9 = fields.Datetime.from_string(self.date_begin) + datetime.timedelta(days=self.days*n)
            date_end9 = date_begin9 + datetime.timedelta(minutes=self.session_id.duration)
            session9 = self.env['ems.session'].create({
                'center_id': self.session_id.center_id.id,
                'service_id': self.session_id.service_id.id,
                'ubication_id': self.session_id.ubication_id.id,
                'duration': self.session_id.duration,
                'date_begin': date_begin9,
                'date_end': date_end9,
                'responsible_id': self.session_id.responsible_id.id,
                'resource_ids': [(4, p.id, _) for p in self.session_id.resource_ids],
                'partner_ids': [(0, _, {'partner_id': p.partner_id.id}) for p in self.session_id.partner_ids],
            })

            if self.action=='confirm':
                try:
                    session9.button_confirm()
                except (ValidationError, except_orm) as e:
                    session9.button_draft()
                    d.append((session9, e.value))
            elif self.action=='schedulepending':
                session9.button_schedule_pending()


        if len(d)!=0:
            message = _("There's %i sessions with validation errors. You must confirm them manually.") % len(d)
        else:
            message = _("All sessions have been created successfully.")

        wizard_id = self.env['ems.message.info.wizard'].create({
            'message': message,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _("Info"),
            'res_model': 'ems.message.info.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            #'views': [(view.id, 'form')],
            #'view_id': view.id,
            'res_id': wizard_id.id,
            'target': 'new',
            #'context': context,
        }





class WizardInfo(models.TransientModel):
    _name = 'ems.message.info.wizard'

    message = fields.Char(readonly=True)




class WizardResponsibleSessionsPrint(models.TransientModel):
    _name = 'ems.responsible.sessions.print.wizard'

    responsible_id = fields.Many2one('ems.responsible', string="Responsible", required=True, default=lambda self: self._default_responsible())
    date_from = fields.Date(string='Date from', required=True, default=lambda self: self._default_date_from())
    date_to = fields.Date(string='Date to', required=True, default=lambda self: self._default_date_to())

    def _default_date_from(self):
        return fields.Date.from_string(fields.Date.context_today(self)).replace(day=1)

    def _default_date_to(self):
        date_from = fields.Date.from_string(fields.Date.context_today(self)).replace(day=1)
        return (date_from + datetime.timedelta(days=32)).replace(day=1) + datetime.timedelta(days=-1)\

    def _default_responsible(self):
        ids = self.env.context.get('active_ids')
        if ids is not None:
            if len(ids)==1:
                return self.env['ems.responsible'].browse(ids).id
            else:
                raise ValidationError(_("Not implemented yet"))

    @api.constrains('date_from', 'date_to')
    def _check_session_dates(self):
        if self.date_from>self.date_to:
            raise ValidationError(_("The date to must be greater or equal than date from"))


    @api.multi
    def button_print(self):
        datas = {
            'ids': self.responsible_id.ids, # self.env.context.get('active_ids'),
            'model': self._name,
            'button': True,
            'date_from': self.date_from,
            'date_to': self.date_to,

        }
        #call the report
        return {
                   'type': 'ir.actions.report.xml',
                   'report_name': 'ems.report_emsresponsiblesessions',
                   'datas': datas
               }


class WizardTimetable(models.TransientModel):
    _name = 'ems.timetable.wizard'

    def _overlapped_timetables(self):
        tt = self.env['ems.timetable'].browse(self._context.get('active_id'))

        other_tts = self.env['ems.timetable'].search([('center_id','=', tt.center_id.id),
                                                     ]).sorted(key=lambda x: x.sequence)

        tts=set()
        for tt1 in other_tts:
            if tt1.type == 'yearday':
                if tt1.date_begin_year < fields.Datetime.to_string(datetime.datetime.combine(fields.Datetime.from_string(fields.Datetime.now()), datetime.time(0,0,0))):
                    continue

            if pytz.utc.localize(fields.Datetime.from_string(tt.date_end)) > pytz.utc.localize(fields.Datetime.from_string(tt1.date_begin)) and \
                                pytz.utc.localize(fields.Datetime.from_string(tt.date_begin)) < pytz.utc.localize(fields.Datetime.from_string(tt1.date_end)):
                tts.add(tt1.id)


        return self.env['ems.timetable'].browse(list(tts)).sorted(key=lambda x: x.sequence)

    timetable_ids = fields.Many2many('ems.timetable',
        string="Timetable", required=True, default=_overlapped_timetables)



################# CUSTOM REPORTS

class ParticularEMSReportSessionSummary(models.AbstractModel):
    _name = 'report.ems.report_emssessionsummary'


    def classify_data(self, objs, items_per_block=5, blocks_per_pag=2):
        # reb una llist d'objectrs ja orddrenada
        ITEMS_PER_BLOCK = items_per_block
        BLOCKS_PER_PAG = blocks_per_pag
        ITEMS_PER_PAG = ITEMS_PER_BLOCK*BLOCKS_PER_PAG

        ### calssifiquem les dades
        data = {}
        bloc = 0
        pag = 1
        for i,t in enumerate(objs.ids,1):
            if pag not in data:
                data[pag]={}

            if bloc not in data[pag]:
                data[pag][bloc]=[]

            data[pag][bloc].append(t)

            # canvi de pagina
            if i%(ITEMS_PER_PAG)==0:
                pag += 1

            # canvi de bloc
            if i%ITEMS_PER_BLOCK==0:
                bloc = ((bloc + 1) % BLOCKS_PER_PAG)

        ## convertim les ddes en una llista sequencial i ho convertim aobjectes
        pags = []
        for p in sorted(data.keys()):
            pag = data[p]
            blocs = []
            for b in sorted(pag.keys()):
                bloc = pag[b]
                bloc_obj = self.env[objs._name].browse(bloc)
                blocs.append(bloc_obj)
            pags.append(blocs)


        return pags



    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        #report = report_obj._get_report_from_name('ems.report_emssessionsummary')
        session_obj = self.env['ems.session'].browse(self.ids)

        ps = []
        if len(session_obj)==1 and data is not None and data.get('button', False):
            # impresio llancada desde el buto de disn la sessio
            for p in session_obj.partner_ids.mapped('partner_id').sorted(lambda x: x.name):
                ses_p = self.env['ems.partner'].search([('partner_id','=', p.id)]).\
                            filtered(lambda x: x.session_id.center_id==session_obj.center_id and
                                               x.session_id.state in ('confirmed') and
                                               x.session_id.service_id.is_ems and
                                               x.num_session>=data.get('session_from') and
                                                    x.num_session<=data.get('session_to')
                             ).sorted(lambda x: x.session_id.date_begin)

                # separem per pagina, una pagina 2 taules de 5 elements, 10 en total per pagina
                sl = self.classify_data(ses_p, items_per_block=5, blocks_per_pag=2)

                ps.append((p, sl))
        else:
            # impresio llancada des de la vista tree
            for p in session_obj.mapped('partner_ids.partner_id').sorted(lambda x: x.name):
                ses_p = session_obj.mapped('partner_ids').\
                            filtered(lambda x: p.id == x.partner_id.id and
                                               x.session_id.state in ('confirmed') and
                                               x.session_id.service_id.is_ems
                            ).sorted(lambda x: x.session_id.date_begin)

                # separem per pagina, una pagina 2 taules de 5 elements, 10 en total per pagina
                sl = self.classify_data(ses_p, items_per_block=5, blocks_per_pag=2)

                ps.append((p, sl))

        docargs = {
            'docs': session_obj,
            'ps': ps,
            'c': self.env.user.company_id,
        }
        return report_obj.render('ems.report_emssessionsummary', docargs)




class ParticularEMSReportResponsibleSessions(models.AbstractModel):
    _name = 'report.ems.report_emsresponsiblesessions'

    @api.multi
    def render_html(self, data=None):
        responsible_obj = self.env['ems.responsible'].browse(self.ids)

        if len(responsible_obj)==1:
            datetime_from_naive_utc = datetime_naivestr_loc2utc(data['date_from'], self.env.context.get('tz'))
            datetime_to_naive_loc = fields.Datetime.to_string(fields.Datetime.from_string(data['date_to']).replace(hour=23, minute=59, second=59))
            datetime_to_naive_utc = datetime_naivestr_loc2utc(datetime_to_naive_loc, self.env.context.get('tz'))

            # obtenim les sessiond els mes del responsable
            # ('state', 'in', ('confirmed', 'cancelled')) OR ('state', 'in', ('rescheduled')) AND ('out_of_time', '=', True)
            sessions_obj = self.env['ems.session'].search([('responsible_id', '=', responsible_obj.id),
                                                           '|', ('state', 'in', ('confirmed', 'cancelled')),
                                                            '&', ('state', '=', 'rescheduled'), ('out_of_time', '=', True),
                                                            ('date_begin', '>=', datetime_from_naive_utc),
                                                            ('date_begin', '<=', datetime_to_naive_utc)],
                                                         order='date_begin, id')

            # de le sobtingudes busquem els solapaments i els classifiquem, aixo es fa tota lestona teninr en compte que
            # les sessions estan ordernades
            aux = set()
            overlaps = []
            for s in sessions_obj:
                if s.id not in aux:
                    ovl = sessions_obj.filtered(lambda x: x.date_begin<s.date_end and x.date_end>s.date_begin) #.sorted(lambda x:x.date_begin, x.id)
                    overlaps.append(ovl)
                    aux |= set(ovl.mapped('id'))

            # convertim a llista d'objectes, determnant les dates
            w = []
            t = {}
            for session_l in overlaps:
                date_begin_dt = fields.Datetime.from_string(session_l[0].date_begin)
                date_end_dt =fields.Datetime.from_string(session_l[-1].date_end)
                duration_td =  date_end_dt - date_begin_dt
                duration = duration_td.days*24*60 + duration_td.seconds/60
                if len(session_l)==1 and session_l[0].duration!=duration:
                    raise ValidationError(_("Session number '%s' has an incoherence duration: Materialized: %i vs Calculated: %i") % (session_l[0].number, session_l[0].duration, duration))

                date_begin_dt_loc = fields.Datetime.context_timestamp(self, date_begin_dt)
                date_end_dt_loc = fields.Datetime.context_timestamp(self, date_end_dt)

                if date_begin_dt_loc.date()!=date_end_dt_loc.date():
                    raise ValidationError(_("Session number '%s' has dates in different days"))

                date_dt = babel.dates.format_date(date_begin_dt_loc, format='full', locale=self.env.lang).capitalize()
                #datetime_str = "%s (%s - %s)" % (date_dt, date_begin_dt_loc.strftime('%H:%M'), date_end_dt_loc.strftime('%H:%M'))
                datetime_str = "%s - %s" % (date_begin_dt_loc.strftime('%H:%M'), date_end_dt_loc.strftime('%H:%M'))
                s = dict(datetime_str=datetime_str, duration=duration, sessions=session_l)

                date_k = date_begin_dt_loc.date()
                if date_k not in t:
                    t[date_k] = []
                t[date_k].append(s)

            # ordernem el diccionari
            for y in sorted(t):
                y1 = babel.dates.format_date(y, format='full', locale=self.env.lang).capitalize()
                w.append(dict(day=y1, data=t[y], day_duration=reduce(lambda x, y: x+y, [u['duration'] for u in t[y]])))

        else:
            raise ValidationError(_("Not implemented yet"))

        Params = namedtuple('Params', 'date_from date_to print_date_str')
        pars = Params(date_from=babel.dates.format_date(fields.Date.from_string(data['date_from']), format='medium', locale=self.env.lang),
                      date_to=babel.dates.format_date(fields.Date.from_string(data['date_to']), format='medium', locale=self.env.lang),
                      print_date_str=babel.dates.format_datetime(fields.Datetime.context_timestamp(self, fields.datetime.now()),
                                                                 format='medium', locale=self.env.lang).replace(".", ":")
                    )

        # incoquem al report
        report_obj = self.env['report']
        docargs = {
            'docs': responsible_obj,
            'params': pars,
            'w': w,
            'c': self.env.user.company_id,
        }
        return report_obj.render('ems.report_emsresponsiblesessions', docargs)

