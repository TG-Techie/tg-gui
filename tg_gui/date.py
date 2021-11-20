from tg_gui_core import State, DerivedState
from tg_gui_platform.label import Label

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


class Date(Label):

    _prev_refresh: ClassVar[struct_time] = time.localtime()

    year, month, weekday = State(0000), State(00), State(0)
    monthday, yearday = State(00), State(000)
    hours, mins, secs = State(0), State(0), State(0)

    _date_components: ClassVar[dict[str, State]] = {
        # TODO: change the names of the date component dict keys to something a bit clearer
        "year": year,
        "month": month,
        "weekday": weekday,
        "monthday": monthday,
        "yearday": yearday,
        "hours": hours,
        "mins": mins,
        "secs": secs,
        "monthname": DerivedState(month, lambda m: _MONTHS[((m + 1) % 13) - 1]),
        "shortmonth": DerivedState(month, lambda m: _MONTHS[((m + 1) % 13) - 1][0:3]),
        "dayname": DerivedState(weekday, lambda w: _WEEKDAYS[w]),
        "shortyear": DerivedState(year, lambda y: y % 100),
    }

    def __init__(self, format: str, **kwargs) -> None:

        self._format_src = format

        # # find which date components this
        # self._components = comps = {
        #     name: cmp for name, cmp in self._date_components.items() if name in format
        # }
        deps = tuple(
            cmp for name, cmp in self._date_components.items() if name in format
        )

        self._inst_state = state = (
            DerivedState(deps, self._derive_new_str) if len(deps) else None
        )

        super().__init__(
            "" if state is None else state,
            **kwargs,
        )

    @classmethod
    def dateshort(cls: "Type[Date]") -> "Date":
        return cls("{monthday:02}{shortmonth:02}{year}")

    @classmethod
    def american_date(cls: "Type[Date]") -> "Date":
        return cls("{month:02}/{monthday:02}/{year}")

    @classmethod
    def international_date(cls: "Type[Date]") -> "Date":
        return cls("{monthday:02}/{month:02}/{year}")

    @classmethod
    def time(cls: "Type[Date]", secs=False) -> "Date":
        return cls("{hours}:{mins}:{secs}" if secs else "{hours}:{mins}")

    def _derive_new_str(self, *_) -> str:
        # takes any number of args b/c the order is not guaranteed
        format = self._format_src
        return format.format(
            **{
                name: state.value(self)
                for name, state in self._date_components.items()
                if name in format
            }
        )

    def _refresh_time(self, now: struct_time) -> None:

        # if is 24 hour time:
        self.hours = now.tm_hour
        self.mins = now.tm_min
        self.secs = now.tm_sec

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
