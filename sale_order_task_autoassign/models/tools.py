import datetime

import pytz


class TzInterval:
    def __init__(self, date_start, date_end, tz=None, base_tz=None, to_tz=None):
        """if tz is none it means that the date_start and date_end are
        in naive utc-> no need to convert to utc
         if tz is not none means date_start and
         date_end are in naive tz -> convert to naive utc
        """
        # date start
        self.date_start = date_start or datetime.datetime(1900, 1, 1, 0, 0, 0)
        if type(date_start) is datetime.date:
            self.date_start = datetime.datetime.combine(
                self.date_start, datetime.datetime.min.time()
            )
            if not tz:
                if base_tz:
                    self.date_start = self._tz_local_to_utc(self.date_start, base_tz)
        if tz:
            self.date_start = self._tz_local_to_utc(self.date_start, tz)

        if base_tz and to_tz:
            self.date_start = self._tz_utc_swap(self.date_start, base_tz, to_tz)

        # date end
        if isinstance(date_end, datetime.timedelta):
            self.date_end = self.date_start + date_end
        else:
            self.date_end = date_end or datetime.datetime(3000, 1, 1, 0, 0, 0)
            if type(date_end) is datetime.date:
                self.date_end = datetime.datetime.combine(
                    self.date_end + datetime.timedelta(days=1),
                    datetime.datetime.min.time(),
                )
                if not tz:
                    if base_tz:
                        self.date_end = self._tz_local_to_utc(self.date_end, base_tz)
            if tz:
                self.date_end = self._tz_local_to_utc(self.date_end, tz)

        if base_tz and to_tz:
            self.date_end = self._tz_utc_swap(self.date_end, base_tz, to_tz)

        # duration
        self.duration = self.date_end - self.date_start

    def is_included(self, other):
        """returns if current interval (self) is fully included on interval (other)"""
        return self.date_end <= other.date_end and self.date_start >= other.date_start

    def is_overlaped(self, other):
        """returns if interval (other) and current one (self) are overlapped"""
        return self.date_end > other.date_start and other.date_end > self.date_start

    def update_start(self, date_start):
        self.date_start = date_start
        self.date_end = date_start + self.duration

    def update_duration(self, duration, delta="minutes"):
        self.duration = datetime.timedelta(**{delta: duration})
        self.date_end = self.date_start + self.duration

    def _date_tz(self, date, tz):
        return (
            date.replace(tzinfo=pytz.utc)
            .astimezone(pytz.timezone(tz))
            .replace(tzinfo=None)
        )

    def date_start_tz(self, tz):
        return self._date_tz(self.date_start, tz)

    def weekday(self, tz):
        return self.date_start_tz(tz).weekday()

    # pylint: disable=W8106
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
        """
        :param dt: naive datetime in UTC
        :param base_tz: timezone base from which dt was calculated
        :param to_tz: timezone to convert
        :return: naive datetime in UTC
        """
        t = pytz.utc.localize(dt)
        t = t.astimezone(pytz.timezone(base_tz))
        t = t.replace(tzinfo=None)
        return self._tz_local_to_utc(t, to_tz)

    def __str__(self):
        return "[{}, {})".format(self.date_start, self.date_end)

    def __repr__(self):
        return self.__str__()


class Task:
    def __init__(self, obj, start, end=None, duration=None, delta="minutes"):
        self.obj = obj
        if not end:
            if duration:
                if not delta:
                    raise Exception("Delta must be defined along with duration")
                end = start + datetime.timedelta(**{delta: duration})
            else:
                raise Exception("End not defined")

        self.interval = TzInterval(start, end)

        if self.interval.duration.seconds <= 0:
            raise Exception("The task must have duration greater than 0")

    @property
    def start(self):
        return self.interval.date_start

    @property
    def end(self):
        return self.interval.date_end

    @property
    def duration(self):
        return self.interval.duration

    def is_included(self, other):
        """returns if current task (self) is fully included on task (other)"""
        return self.end <= other.end and self.start >= other.start

    def is_overlaped(self, other):
        """returns if task (other) and current one (self) are overlapped"""
        return self.end > other.start and other.end > self.start

    def update_start(self, start):
        self.interval.update_start(start)

    def starts_before(self, other):
        return self.interval.starts_before(other.interval)

    def get_duration_float(self, magnitude):
        res = float(int(self.interval.duration.seconds))
        if magnitude == "seconds":
            pass
        elif magnitude == "minutes":
            res /= 60
        elif magnitude == "hours":
            res /= 60 * 60
        else:
            raise Exception("Magnitude %s not implemented" % magnitude)

        return res

    def update_duration(self, duration, delta="minutes", is_rate=False):
        if not is_rate:
            self.interval.update_duration(duration, delta=delta)
        else:
            if duration != 1:
                self.interval.update_duration(
                    int(round(self.interval.duration.seconds / duration)),
                    delta="seconds",
                )

    # pylint: disable=W8106
    def copy(self, start=None, duration=None):
        nint = Task(self.obj, self.start, self.end)
        if start:
            nint.update_start(start)
        if duration:
            nint.update_duration(duration)
        return nint

    def __str__(self):
        return "%s:[%s, %s)|%i" % (
            self.obj,
            self.start,
            self.end,
            self.duration.seconds / 60,
        )

    def __repr__(self):
        return self.__str__()


class TaskList:
    def __init__(self, tasks):
        if tasks:
            if not isinstance(tasks, list):
                tasks = [tasks]

        for tsk in tasks:
            self._check_task(tsk)

        self.tasks = tasks

    def rotate_split(self, i):
        return self.tasks[i], self.__class__(self.tasks[:i] + self.tasks[i + 1 :])

    @property
    def start(self):
        return sorted(self.tasks, key=lambda x: x.end)[0].end

    @property
    def end(self):
        return sorted(self.tasks, key=lambda x: x.end)[-1].end

    def _check_task(self, tsk):
        if not isinstance(tsk, Task):
            raise Exception("The tasks must be of task class")

    # pylint: disable=W8106
    def copy(self):
        return self.__class__(self.tasks[:])

    def add(self, tsk):
        self._check_task(tsk)
        self.tasks.append(tsk)

    def check_len(self, n):
        if len(self) != n:
            raise Exception("Different lengths!!!!! no pot ser: %s" % self)

    def __len__(self):
        return len(self.tasks)

    def __str__(self):
        dst = ""
        if self.tasks:
            clstr = [str(x) for x in sorted(self.tasks, key=lambda x: x.start)]
            dst = "[%s], #%i, <%s>" % (", ".join(clstr), len(self.tasks), self.end)

        return "TaskList(%s)" % dst

    def __repr__(self):
        return self.__str__()


class UserTasks:
    def __init__(self):
        self.tasks = {}
        self.resources = {}

    @property
    def end(self):
        end = None
        for v in self.tasks.values():
            if end is None:
                end = v.end
            else:
                if end != v.end:
                    raise Exception("Inconsistencies, all elements must be same end")
        return end

    def del_user(self, res, raise_not_exists=False):
        if res.id not in self.tasks:
            if raise_not_exists:
                raise Exception("User %s does not exist" % res)
        else:
            del self.tasks[res.id]

        if res.id not in self.resources:
            if raise_not_exists:
                raise Exception("User %s does not exist" % res)
        else:
            del self.resources[res.id]

    def get_resources(self):
        return self.resources.values()

    def exists(self, res):
        return res.id in self.tasks

    def add(self, res, tsk):
        if res.id not in self.tasks:
            self.tasks[res.id] = TaskList([])
            self.resources[res.id] = res

        self.tasks[res.id].add(tsk)

    def update(self, res, cl):
        if not isinstance(cl, TaskList):
            raise Exception("Expected candidate list")

        self.tasks[res.id] = cl
        self.resources[res.id] = res

    def get(self, res):
        if res.id not in self.tasks:
            # raise Exception("User %s not found" % user)
            return TaskList([])

        return self.tasks[res.id]

    def check_longs(self, n):
        for cl in self.tasks.values():
            cl.check_len(n)

    def get_quickest(self, check_len=None):
        d_gr = {}
        min_end = None
        for user, cl in self.tasks.items():
            if check_len is not None:
                cl.check_len(check_len)
            if min_end is None:
                min_end = cl.end
            else:
                if min_end < cl.end:
                    continue
                elif min_end > cl.end:
                    d_gr.pop(min_end)
                    min_end = cl.end

            d_gr.setdefault(min_end, self.__class__()).update(self.resources[user], cl)

        if d_gr:
            if len(d_gr) != 1:
                raise Exception("Unexpected 33")
            return d_gr[min_end]

        return None

    def merge(self, other):
        keys = set(other.tasks.keys()) - set(self.tasks.keys())
        c9 = self.copy()
        for user in keys:
            res = self.resources[user]
            if res.id in self.tasks:
                raise Exception("Unexpected 88")
            c9.update(res, other.get(res))

        return c9

    # pylint: disable=W8106
    def copy(self):
        d = {}
        for k, v in self.tasks.items():
            d[k] = v.copy()
        r = {}
        for k, v in self.resources.items():
            r[k] = v

        c9 = self.__class__()
        c9.tasks = d
        c9.resources = r
        return c9

    def _comp(self, op, other):
        if not isinstance(other, self.__class__):
            return NotImplemented

        if op == "=":
            return self.end == other.end
        elif op == "!=":
            return self.end != other.end
        elif op == ">":
            return self.end > other.end
        elif op == ">=":
            return self.end >= other.end
        elif op == "<":
            return self.end < other.end
        elif op == "<=":
            return self.end <= other.end
        else:
            raise Exception("op %s not expected" % op)

    def __len__(self):
        return len(self.tasks)

    def __eq__(self, other):
        return self._comp("=", other)

    def __ne__(self, other):
        return self._comp("!=", other)

    def __ge__(self, other):
        return self._comp(">=", other)

    def __gt__(self, other):
        return self._comp(">", other)

    def __le__(self, other):
        return self._comp("<=", other)

    def __lt__(self, other):
        return self._comp("<", other)

    def __str__(self):
        return str(self.tasks)

    def __repr__(self):
        return self.__str__()
