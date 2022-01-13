# The MIT License (MIT)
#
# Copyright (c) 2021 Jonah Yolles-Murphy (TG-Techie)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import annotations

from tg_gui_core import State, DerivedState, uid, themedwidget, _Screen_
from .label import Label

from tg_gui_core import isoncircuitpython

import time
from time import struct_time

__all__ = (
    "Date",
    "refresh_time",
    "refresh_date",
)

try:
    from typing import ClassVar, Type
except:
    pass

# TODO: maybe make the _MONTH, const, etc usable by drivers w/out importing all tg-gui (ie put it somehwere else)
_MONTHS = (
    "<INVALID MONTH>",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "Novemer",
    "December",
)

_WEEKDAYS = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)
_SHORTWEEKDAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
# fmt: off
_24TO12HOUR =  (
    (12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
)
# fmt: on


@themedwidget
class Date(Label):

    # _default_styling_ = {}
    # _default_styling_.update(Label._default_styling_)
    # _default_styling_.update(fit_to_text=True)

    # for internal use when updating the state objects
    _prev_refresh: ClassVar[struct_time] = time.localtime()

    # publicly exposed state
    year, month, weekday = State(0000), State(00), State(0)
    monthday, yearday = State(00), State(000)
    hour24, min, sec = State(0), State(0), State(0)

    hour12 = DerivedState(hour24, lambda h: _24TO12HOUR[h])

    # TODO: # FUTURE: make hour depend on the system to dispatch to hour12 or hour 24
    is_24_hour = State(True)
    hour = hour24
    # is_24_hour = State("<hooked into system or platform>")
    # hour = DeriourvedState((is_24hour, hour24, hour12))

    _date_components: ClassVar[dict[str, State]] = {
        # TODO: change the names of the date component dict keys to something a bit clearer
        "year": year,
        "month": month,
        "weekday": weekday,
        "day": monthday,
        "monthday": monthday,
        "yearday": yearday,
        "hour": hour,
        "hour12": hour12,
        "hour24": hour24,
        "min": min,
        "sec": sec,
        "monthname": DerivedState(month, lambda m: _MONTHS[((m + 1) % 13) - 1]),
        "monthshort": DerivedState(month, lambda m: _MONTHS[((m + 1) % 13) - 1][0:3]),
        "dayname": DerivedState(weekday, lambda w: _WEEKDAYS[w]),
        "dayshort": DerivedState(weekday, lambda w: _SHORTWEEKDAYS[w]),
        "yearshort": DerivedState(year, lambda y: y % 100),
    }

    shared_replacements = (
        ("{year}", "{year:04}"),
        ("{min}", "{min:02}"),
        ("{sec}", "{sec:02}"),
        ("{yearshort}", "{yearshort:02}"),
        ("{hour24}", "{hour24:02}"),
        ("{hour12}", "{hour12: 2}"),
        ("{hourdelim}", ":"),
    )

    replacements_hour24 = (
        ("{hour}", "{hour24:02}"),
        ("{monthday}", "{monthday:02}"),
        ("{hourdelim}", "h"),
    )

    replacements_12hour = (
        ("{hour}", "{hour12: 2}"),
        ("{monthday}", "{monthday: 2}"),
        ("{hourdelim}", ":"),
    )

    def __init__(self, format: str, **kwargs) -> None:

        self._format_src = format

        dependencies = tuple(
            cmp for name, cmp in self._date_components.items() if name in format
        )

        self._inst_state = state = (
            DerivedState(dependencies, self._derive_new_str)
            if len(dependencies)
            else None
        )

        if format == "":
            self._id_ = uid()  # hack in identiable for setting purposes
        else:
            super().__init__(
                format if state is None else state,
                **kwargs,
            )

    @classmethod
    def dateshort(cls: "Type[Date]", **kwargs) -> "Date":
        return cls("{monthday:02}{monthshort}{year}", **kwargs)

    @classmethod
    def american_date(cls: "Type[Date]", **kwargs) -> "Date":
        return cls("{month:02}/{monthday:02}/{year}", **kwargs)

    @classmethod
    def international_date(cls: "Type[Date]", **kwargs) -> "Date":
        return cls("{monthday:02}/{month:02}/{year}", **kwargs)

    @classmethod
    def time(cls: "Type[Date]", secs=False, **kwargs) -> "Date":
        return cls(
            "{hour:02}:{min:02}:{sec:02}" if secs else "{hour:02}:{min:02}",
            **kwargs,
        )

    def _derive_new_str(self, *_) -> str:
        # takes any number of args b/c the order is not guaranteed
        format = self._format_src

        # add default formatting when no :_x fromatters are supplied
        for patrn, repl in (
            self.replacements_hour24 if self.is_24_hour else self.replacements_12hour
        ):
            format = format.replace(patrn, repl)

        for patrn, repl in self.shared_replacements:
            format = format.replace(patrn, repl)

        values = {
            name: state.value(self)
            for name, state in self._date_components.items()
            if name in format
        }

        return format.format(**values)

    def _refresh_time(self, now: struct_time) -> None:

        # if is 24 hour time:
        self.hour24 = now.tm_hour
        self.min = now.tm_min
        self.sec = now.tm_sec

        if type(self)._prev_refresh.tm_hour > now.tm_hour:
            self._refresh_date(now)

    def _refresh_date(self, now: struct_time) -> None:

        self.year = now.tm_year
        self.month = now.tm_mon
        self.monthday = now.tm_mday
        self.weekday = now.tm_wday
        self.yearday = now.tm_yday

        type(self)._prev_refresh = now


_date_inst = Date("")
_date_inst._refresh_date(time.localtime())
_date_inst._refresh_time(time.localtime())

# --- interface ---
# these should be registed into the event loop for the gui
refresh_time = _date_inst._refresh_time
refresh_date = _date_inst._refresh_date

_Screen_._register_recurring_update_(
    _date_inst,
    lambda: refresh_time(time.localtime()),
    1.0,
)
