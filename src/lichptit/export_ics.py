"""Xuất calendar.ics (RFC 5545) có VALARM để đăng ký trên iPhone."""
from __future__ import annotations

import datetime as dt

from icalendar import Alarm, Calendar
from icalendar import Event as IEvent

from .expand import Event

UTC = dt.timezone.utc


def to_ics(events: list[Event], now: dt.datetime | None = None) -> bytes:
    now = (now or dt.datetime.now(UTC)).astimezone(UTC).replace(microsecond=0)
    cal = Calendar()
    cal.add("prodid", "-//lich-ptit//Lich PTIT//VI")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")
    cal.add("x-wr-calname", "Lịch PTIT")
    cal.add("x-wr-timezone", "Asia/Ho_Chi_Minh")
    cal.add("refresh-interval", dt.timedelta(hours=1), parameters={"VALUE": "DURATION"})
    cal.add("x-published-ttl", "PT1H")

    for ev in events:
        ie = IEvent()
        ie.add("uid", ev.uid)
        ie.add("dtstamp", now)
        ie.add("summary", ev.title)
        if ev.all_day:
            ie.add("dtstart", ev.start.date())
            ie.add("dtend", ev.end.date())
        else:
            ie.add("dtstart", ev.start.astimezone(UTC))
            ie.add("dtend", ev.end.astimezone(UTC))
        desc = ev.description
        if ev.room:  # ID/mật khẩu phòng: chỉ được nằm ở đây
            desc = (desc + "\n" if desc else "") + f"Phòng: {ev.room}"
        if desc:
            ie.add("description", desc)
        if ev.location:
            ie.add("location", ev.location)
        if ev.url:
            ie.add("url", ev.url)
        ie.add("categories", [{"class": "Học", "exam": "Thi", "task": "Việc"}[ev.kind]])
        for off in ev.alarms:
            a = Alarm()
            a.add("action", "DISPLAY")
            a.add("description", ev.title)
            a.add("trigger", off)
            ie.add_component(a)
        cal.add_component(ie)
    return cal.to_ical()
