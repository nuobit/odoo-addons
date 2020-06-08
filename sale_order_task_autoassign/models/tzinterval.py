# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import datetime
import pytz


class TzInterval:
    def __init__(self, date_start, date_end, tz=None, base_tz=None, to_tz=None):
        """ if tz is none it means that the date_start and date_end are in naive utc-> no need to convert to utc
            if tz is not none mens date_start and date_end are in naive tz -> convert to naive utc
        """
        ## date start
        self.date_start = date_start or datetime.datetime(1900, 1, 1, 0, 0, 0)
        if type(date_start) is datetime.date:
            self.date_start = datetime.datetime.combine(self.date_start, datetime.datetime.min.time())
            if not tz:
                if base_tz:
                    self.date_start = self._tz_local_to_utc(self.date_start, base_tz)
        if tz:
            self.date_start = self._tz_local_to_utc(self.date_start, tz)

        if base_tz and to_tz:
            self.date_start = self._tz_utc_swap(self.date_start, base_tz, to_tz)

        ## date end
        if isinstance(date_end, datetime.timedelta):
            self.date_end = self.date_start + date_end
        else:
            self.date_end = date_end or datetime.datetime(3000, 1, 1, 0, 0, 0)
            if type(date_end) is datetime.date:
                self.date_end = datetime.datetime.combine(
                    self.date_end + datetime.timedelta(days=1), datetime.datetime.min.time())
                if not tz:
                    if base_tz:
                        self.date_end = self._tz_local_to_utc(self.date_end, base_tz)
            if tz:
                self.date_end = self._tz_local_to_utc(self.date_end, tz)

        if base_tz and to_tz:
            self.date_end = self._tz_utc_swap(self.date_end, base_tz, to_tz)

        ## duration
        self.duration = self.date_end - self.date_start

    def is_included(self, other):
        """ returns if current interval (self) is fully included on interval (other)"""
        return self.date_end <= other.date_end and \
               self.date_start >= other.date_start

    def is_overlaped(self, other):
        """ returnsw if interval (other) and current one (self) are overlapped """
        return self.date_end > other.date_start and \
               other.date_end > self.date_start

    def update_start(self, date_start):
        self.date_start = date_start
        self.date_end = date_start + self.duration

    def _date_tz(self, date, tz):
        return date.replace(tzinfo=pytz.utc) \
            .astimezone(pytz.timezone(tz)).replace(tzinfo=None)

    def date_start_tz(self, tz):
        return self._date_tz(self.date_start, tz)

    def weekday(self, tz):
        return self.date_start_tz(tz).weekday()

    def copy(self, date_start=None):
        nint = TzInterval(self.date_start, self.date_end)
        if date_start:
            nint.update_start(date_start)
        return nint

    def starts_before(self, other):
        return self.date_start < other.date_start

    def _tz_local_to_utc(self, dt, tz):
        t = pytz.timezone(tz).localize(dt)
        t = t.astimezone(pytz.utc)
        t = t.replace(tzinfo=None)
        return t

    def _tz_utc_swap(self, dt, base_tz, to_tz):
        '''
        :param dt: naive datetime in UTC
        :param base_tz: timezone base from which dt was calculated
        :param to_tz: timezone to convert
        :return: naive datetime in UTC
        '''
        t = pytz.utc.localize(dt)
        t = t.astimezone(pytz.timezone(base_tz))
        t = t.replace(tzinfo=None)
        return self._tz_local_to_utc(t, to_tz)

    def __str__(self):
        return "[%s, %s)" % (self.date_start, self.date_end)

    def __repr__(self):
        return self.__str__()
