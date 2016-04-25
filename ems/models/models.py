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


from openerp import models, fields, api, _
from openerp.exceptions import AccessError, Warning, ValidationError

from openerp.tools.misc import detect_server_timezone

import re

import hashlib

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


DAYS_OF_WEEK = [(1, _('Monday')), (2, _('Tuesday')), (3, _('Wednesday')),
                                      (4, _('Thursday')), (5, _('Friday')), (6, _('Saturday')),
                                      (7, _('Sunday'))]

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

    name = fields.Char(string='Session Number', required=False,
        readonly=False)

    description = fields.Text(string='Description', #translate=True,
        readonly=False)

    weight = fields.Float(string='Weight', digits=(5,2),
        readonly=False)


    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        default=lambda self: self.env['res.company']._company_default_get('ems.session'),
        ondelete='restrict',
        required=False, readonly=False)

    center_id = fields.Many2one('ems.center', string='Center', default=lambda self: self.env.user.center_id,
                                ondelete='restrict',
                                required=True, readonly=False)

    responsible_id = fields.Many2one('ems.responsible', string='Responsible',
                                     ondelete='restrict',
                                     required=False, readonly=False)

    partner_ids = fields.One2many(comodel_name='ems.partner', inverse_name='session_id', copy=True)

    partner_text = fields.Char(string='Attendees', compute='_compute_auxiliar_text', readonly=True, store=False, translate=False,
                               search='_search_partner_text')

    service_id = fields.Many2one('ems.service', string='Service',
                                 ondelete='restrict',
                                 required=True, readonly=False)

    color_rel = fields.Selection(related="service_id.color", store=False)

    ubication_id = fields.Many2one('ems.ubication', string='Ubication',
                                   ondelete='restrict',
                                   required=True, readonly=False)

    is_all_center = fields.Boolean(related='ubication_id.is_all_center', store=False)

    resource_ids = fields.Many2many('ems.resource', string='Resources',
        required=False, readonly=False)

    duration = fields.Integer(string='Duration', required=True)


    date_begin = fields.Datetime(string='Start Date', required=True, default=fields.datetime.now().replace(second=0, microsecond=0),
        readonly=False)
    date_end = fields.Datetime(string='End Date', required=True,
        readonly=False)

    reason = fields.Char(string='Reason', required=False, readonly=True)

    source_session_id = fields.Many2one('ems.session', string="Source session", readonly=True, ondelete='restrict',)

    target_session_id = fields.Many2one('ems.session', string="Target session", readonly=True, ondelete='restrict',)

    session_text = fields.Char(compute='_compute_auxiliar_text', readonly=True, translate=False)

    state = fields.Selection([
            ('draft', 'Draft'),
            ('cancelled', 'Cancelled'),
            ('rescheduled', 'Rescheduled'),
            ('confirmed', 'Confirmed'),
        ], string='Status', default='draft', readonly=True, required=True, copy=False,
        help="If session is created, the status is 'Draft'. If session is confirmed for the particular dates the status is set to 'Confirmed'. If the session is over, the status is set to 'Done'. If session is cancelled the status is set to 'Cancelled'.")



    @api.multi
    def button_print(self):
        #return self.env['report'].get_action(self, 'ems.report_emssessionsummary', data={'pp': self})

        #set the data
        #ids is the list of ids, so have to pass <model>._ids
        #model is the model name  <model>._name or string literal
        #form is the field list, I use <model>.read() to get all fields, read() can have parameter to only read specific fields

        datas = {
            'ids': self._ids,
            'model': self._name,
            #'kk': self.partner_ids,
            #'pp': [self.partner_ids],
            #'form': self.read(),
            #'context':self._context
        }
        #call the report
        return {
                   'type': 'ir.actions.report.xml',
                   'report_name': 'ems.report_emssessionsummary',
                   'datas': datas
               }


        '''
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('ems.report_sessionsummary')
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render('ems.report_sessionsummary', docargs)
        '''

    def accept(self):
        ## enca carreguem la sesio replanificada
        if self.target_session_id.state!='draft':
            raise ValidationError(_("The target session has to be in draft state to be deleted."))

        self.target_session_id.unlink(force=True)
        self.target_session_id = False

        self.state = 'draft'


    @api.multi
    def button_draft(self):
        if self.state == 'rescheduled':
            if self.target_session_id:
                wizard_id = self.env['ems.message.wizard'].create({
                    'message': _("The associated target session '%s' will be deleted. Continue?") % self.target_session_id.name_get()[0][1],
                    'model_name': 'ems.session',
                })

                return {
                    'type': 'ir.actions.act_window',
                    'name':_("Display Name"),#Name You want to display on wizard
                    'res_model': 'ems.message.wizard',
                    'view_type': 'form',
                    'view_mode': 'form',
                    #'views': [(view.id, 'form')],
                    #'view_id': view.id,
                    'res_id': wizard_id.id,
                    'target': 'new',
                    #'context': context,
                }

        self.state = 'draft'

    @api.multi
    def button_cancel(self):
        if self.state == 'confirmed':
            wizard_id = self.env['ems.session.cancel.wizard'].create({
                'reason': self.reason,
            })

            return {
                'type': 'ir.actions.act_window',
                'name':_("Display Name"),#Name You want to display on wizard
                'res_model': 'ems.session.cancel.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                #'views': [(view.id, 'form')],
                #'view_id': view.id,
                'res_id': wizard_id.id,
                'target': 'new',
                #'context': context,
            }

        self.state = 'cancelled'

    @api.multi
    def button_reschedule(self):
        sessions0 = self.env['ems.session'].search([ #('id', '!=', self.id),
                                            ('state', '=', 'confirmed'),
                                            ('center_id', '=', self.center_id.id),
                                            #('service_id', '=', self.service_id.id),
                                            ('date_begin', '>=', self.date_begin)
                                           ]).filtered(lambda x: x.service_id.is_ems and
                                                                 len(set(x.partner_ids.mapped('partner_id.id')) &
                                                                     set(self.partner_ids.mapped('partner_id.id')))!=0
                                                     )

        last_session = sessions0.sorted(lambda x: x.date_begin)[-1]

        def get_new_date(datestr_s, datestr_l, days=7):
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

        wizard_id = self.env['ems.session.reschedule.wizard'].create({
            'session_id': self.id,
            'duration': self.duration,
            'date_begin': get_new_date(self.date_begin, last_session.date_begin, days=7),
            'date_end': get_new_date(self.date_end, last_session.date_end, days=7),
            'reason': self.reason,
        })

        return {
            'type': 'ir.actions.act_window',
            'name':_("Display Name"),#Name You want to display on wizard
            'res_model': 'ems.session.reschedule.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            #'views': [(view.id, 'form')],
            #'view_id': view.id,
            'res_id': wizard_id.id,
            'target': 'new',
            #'context': context,
        }




    @api.multi
    def button_confirm(self):
        """ Confirm Event and send confirmation email to all register peoples """
        self.state = 'confirmed'



    @api.depends('partner_ids', 'responsible_id','partner_ids.partner_id', 'partner_ids.partner_id.name')
    def _compute_auxiliar_text(selfs):
        for self in selfs:
            self.session_text = False
            self.partner_text = False

            if self.is_all_center:
                self.session_text = self.service_id.name
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


    def _check_all(self):
        # check dates
        if self.date_end < self.date_begin:
            raise ValidationError(_('Closing Date cannot be set before Beginning Date'))

        ####
        if self.state == 'draft':
            return

        # check number of atendees
        if self.service_id.max_attendees>=0 and len(self.partner_ids)>self.service_id.max_attendees:
            raise ValidationError(_('Too many attendees, maximum of %i') % self.service_id.max_attendees)

        if self.service_id.min_attendees>len(self.partner_ids):
            raise ValidationError(_('It requieres %i attendees minimum') % self.service_id.min_attendees)

        # comprovem que la sessio no te cap forces session anteriro
        for ep in self.partner_ids:
            if ep.force_session:
                sessions_ant = self.env['ems.partner'].search([('partner_id','=', ep.partner_id.id)]).\
                    filtered(lambda x: x.session_id.center_id==self.center_id and
                                       x.session_id.state in ('cancelled', 'confirmed') and
                                       x.session_id.service_id.is_ems and
                                       x.session_id.date_begin<self.date_begin
                                    )
                if len(sessions_ant)!=0:
                    raise ValidationError(_("Only the first session can have a forced session."))

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
                raise ValidationError(_("There's another session in selected ubication"))

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
            raise ValidationError(_("There's another session in selected ubication"))


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
           raise ValidationError(_("There's another session using the same resources"))

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
            raise ValidationError(_("There's another session with selected responsible"))

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
           raise ValidationError(_("There's another session with selected customer"))


    @api.constrains('state')
    def check_state(self):
        self._check_all()


    @api.constrains('date_begin', 'date_end', 'center_id',
                    'ubication_id', 'resource_ids',
                    'responsible_id', 'partner_ids')
    def _check_session(self):
        #check state
        if self.state!='draft':
            raise ValidationError(_('You can only change a draft session'))

        self._check_all()

    @api.multi
    def unlink(self, force=False):
        for rec in self:
            #Call the parent method to eliminate the records.
            if rec.state == 'draft':
                if rec.source_session_id:
                    if rec.source_session_id.state=='rescheduled' and force:
                         super(ems_session, rec).unlink()
                    else:
                        raise ValidationError(_("This session is linked to session '%s', delete that before.") % rec.source_session_id.name_get()[0][1])
                else:
                    super(ems_session, rec).unlink()
            else:
                raise ValidationError(_('You can only delete a draft session'))

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, rec.session_text))

        return res



class ems_partner(models.Model):
    """ Ubication """
    _name = 'ems.partner'
    _description = 'Partner'

    partner_id = fields.Many2one('res.partner', string="Partner", ondelete='restrict', required=True)

    session = fields.Integer(string='Session OLD', readonly=False, default=-1)

    num_session = fields.Integer('Session', compute='_compute_session', inverse='_compute_session_inverse', readonly=True, default=-1, store=False)

    force_session = fields.Boolean(string='Force session', default=False)
    num_session_forced = fields.Integer('Session', required=False)

    phone = fields.Char(related='partner_id.phone', readonly=True)

    mobile = fields.Char(related='partner_id.mobile', readonly=True)

    email = fields.Char(related='partner_id.email', readonly=True)

    session_id = fields.Many2one('ems.session', ondelete='cascade',)

    date_begin_str = fields.Char(compute="_compute_date_begin_str", store=False)
    time_begin_str = fields.Char(compute="_compute_date_begin_str", store=False)

    _sql_constraints = [('partner_session_unique', 'unique(session_id, partner_id)',_("Partner duplicated"))]


    @api.one
    @api.depends('session_id.date_begin')
    def _compute_date_begin_str(self):
        if self.session_id:
            dt = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(self.session_id.date_begin))

            lang = self.env['res.lang'].search([('code', '=', self.env.lang)])

            time_format = '%H:%M' #lang.time_format

            self.date_begin_str = dt.strftime(lang.date_format)
            self.time_begin_str = dt.strftime(time_format)



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

    sequence = fields.Integer('Sequence', help="Sequence for the handle.", default=1)

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

    session_id = fields.Many2one('ems.session', required=True)
    duration = fields.Integer(string='Duration', required=True, readonly=True)

    date_begin = fields.Datetime(string='Start Date', required=True, readonly=False)
    date_end = fields.Datetime(string='End Date', required=True, readonly=False)

    reason = fields.Char(string='Reason', required=False)

    confirm = fields.Boolean(string='Confirm', help='Confirm new session after created', default=True)

    @api.onchange('date_begin')
    def _onchange_date_begin(self):
        self.date_end = fields.Datetime.from_string(self.date_begin) + datetime.timedelta(minutes=self.duration)

    @api.onchange('date_end')
    def _onchange_date_end(self):
        self.date_begin = fields.Datetime.from_string(self.date_end) + datetime.timedelta(minutes=-self.duration)

    @api.multi
    def reschedule(self):
        # creem la nova sessio
        session9 = self.env['ems.session'].create({
            'center_id': self.session_id.center_id.id,
            'service_id': self.session_id.service_id.id,
            'ubication_id': self.session_id.ubication_id.id,
            'duration': self.duration,
            'date_begin': self.date_begin,
            'date_end': self.date_end,
            'responsible_id': self.session_id.responsible_id.id,
            'resource_ids': [(4, p.id, _) for p in self.session_id.resource_ids],
            'description': self.session_id.description,
            'source_session_id': self.session_id.id,
            'partner_ids': [(0, _, {'partner_id': p.partner_id.id}) for p in self.session_id.partner_ids],
        })

        self.session_id.reason = self.reason
        self.session_id.target_session_id = session9

        if self.confirm:
            session9.button_confirm()

        self.session_id.state = 'rescheduled'

class WizardMessage(models.TransientModel):
    _name = 'ems.message.wizard'

    message = fields.Char(string="Message", readonly=True)

    model_name = fields.Char()

    @api.multi
    def accept(self):
        active_id = self.env[self.model_name].browse(self._context.get('active_id'))

        active_id.accept()


class WizardSessionCancel(models.TransientModel):
    _name = 'ems.session.cancel.wizard'

    reason = fields.Char(string='Reason', required=False)

    @api.multi
    def accept(self):
        session_id = self.env['ems.session'].browse(self._context.get('active_id'))
        session_id.reason = self.reason
        session_id.state = 'cancelled'





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


class WizardCheckSessionNumber(models.TransientModel):
    _name = 'ems.check.session.number.wizard'

    line_ids = fields.One2many(comodel_name='ems.check.session.number.line.wizard', inverse_name='check_id')

    @api.model
    def default_get(self, fields):
        res = super(WizardCheckSessionNumber, self).default_get(fields)
        if 'line_ids' in fields:
            res['line_ids'] = self.find()
        return res

    @api.multi
    def find(self):
        sids=[]
        for x in self.env['ems.partner'].search([]):
            if x.session_id.service_id.is_ems and x.session!=-1 and x.num_session!=x.session:
                sids.append(x.session_id.id)

        sids=list(set(sids))

        sessions = self.env['ems.session'].browse(sids).sorted(lambda x: x.date_begin)

        y = []
        for s in sessions:
            y.append((0,0, {'session_id': s.id}))


        return y





class WizardCheckSessionNumberLine(models.TransientModel):
    _name = 'ems.check.session.number.line.wizard'

    check_id = fields.Many2one('ems.check.session.number.wizard', ondelete='cascade')

    session_id = fields.Many2one('ems.session')





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
        if len(session_obj)==1:
            # separem per patner i pagines classificades
            for p in session_obj.partner_ids.mapped('partner_id').sorted(lambda x: x.name):
                ses_p = self.env['ems.partner'].search([('partner_id','=', p.id)]).\
                            filtered(lambda x: x.session_id.center_id==session_obj.center_id and
                                               x.session_id.state in ('confirmed') and
                                               x.session_id.service_id.is_ems
                             ).sorted(lambda x: x.session_id.date_begin)

                # separem per pagina, una pagina 2 taules de 5 elements, 10 en total per pagina
                sl = self.classify_data(ses_p, items_per_block=5, blocks_per_pag=2)

                ps.append((p, sl))
        else:
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
