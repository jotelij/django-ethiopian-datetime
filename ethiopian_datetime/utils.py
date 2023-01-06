from django.utils import timezone
from django.utils.dateparse import date_re, time_re, datetime_re
from ethiocalendar import (
    date as ethdate,
    datetime as ethdatetime,
    time as ethtime,
)


def parse_date(value):
    match = date_re.match(value)
    if match:
        kw = {k: int(v) for k, v in match.groupdict().items()}
        return ethdate(**kw)


def parse_time(value):

    try:
        return ethtime.fromisoformat(value).replace(tzinfo=None)
    except ValueError:
        if match := time_re.match(value):
            kw = match.groupdict()
            kw["microsecond"] = kw["microsecond"] and kw["microsecond"].ljust(6, "0")
            kw = {k: int(v) for k, v in kw.items() if v is not None}
            return ethdatetime.time(**kw)


def parse_datetime(value):
    match = datetime_re.match(value)
    if match:
        kw = match.groupdict()
        kw["microsecond"] = kw["microsecond"] and kw["microsecond"].ljust(6, "0")
        tzinfo = kw.pop("tzinfo")
        if tzinfo == "Z":
            tzinfo = ethdatetime.timezone.utc
        elif tzinfo is not None:
            offset_mins = int(tzinfo[-2:]) if len(tzinfo) > 3 else 0
            offset = 60 * int(tzinfo[1:3]) + offset_mins
            if tzinfo[0] == "-":
                offset = -offset
            tzinfo = timezone.get_fixed_timezone(offset)
        kw = {k: int(v) for k, v in kw.items() if v is not None}
        return ethdatetime(**kw, tzinfo=tzinfo)
