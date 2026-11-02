"""Bung dữ liệu thành danh sách sự kiện cụ thể (buổi học, buổi thi, hạn việc) kèm lời nhắc."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Literal

from .load import Data
from .models import VN, REMIND_RE, ClassRule, Course, Exam, Task

DEFAULT_REMIND = {
    "class": ["30m"],
    "task": ["1d", "3h"],
    "exam": ["14d", "3d", "1d@20:00"],
}


@dataclass
class Event:
    uid: str
    kind: Literal["class", "exam", "task"]
    ref_id: str
    course: str | None
    title: str
    start: dt.datetime  # có múi giờ VN
    end: dt.datetime
    all_day: bool = False
    alarms: list[dt.timedelta] = field(default_factory=list)  # lệch so với start (âm = trước)
    location: str | None = None
    url: str | None = None
    description: str = ""
    room: str | None = None  # bí mật – chỉ export_ics được dùng
    flags: list[str] = field(default_factory=list)


def remind_offset(spec: str, start: dt.datetime) -> dt.timedelta:
    """'30m' → -30 phút; '1d@20:00' → 20:00 của 1 ngày trước, tính theo lệch so với start."""
    m = REMIND_RE.fullmatch(spec)
    if m is None:
        raise ValueError(spec)
    if m[1] is not None:
        n, unit = int(m[1]), m[2]
        return -{"m": dt.timedelta(minutes=n), "h": dt.timedelta(hours=n), "d": dt.timedelta(days=n)}[unit]
    day = start.date() - dt.timedelta(days=int(m[3]))
    at = dt.datetime.combine(day, dt.time(int(m[4]), int(m[5])), tzinfo=VN)
    return at - start


def _alarms(kind: str, custom: list[str] | None, start: dt.datetime) -> list[dt.timedelta]:
    specs = custom if custom is not None else DEFAULT_REMIND[kind]
    offs = {remind_offset(s, start) for s in specs}
    return sorted(o for o in offs if o <= dt.timedelta(0))


def class_dates(rule: ClassRule) -> list[dt.date]:
    if rule.date is not None:
        dates = {rule.date}
    else:
        dates = set()
        d = rule.from_
        while d <= rule.to:
            if d.isoweekday() == rule.weekday:
                dates.add(d)
            d += dt.timedelta(days=1)
    dates -= set(rule.skip_dates)
    dates |= set(rule.extra_dates)
    return sorted(dates)


def _course_label(courses: dict[str, Course], code: str | None) -> str:
    if code is None:
        return ""
    c = courses.get(code)
    return f"{c.name} ({code})" if c else code


def expand_class(rule: ClassRule, courses: dict[str, Course]) -> list[Event]:
    c = courses.get(rule.course)
    desc = [f"Môn: {_course_label(courses, rule.course)}"]
    if c and c.group:
        desc.append(f"Nhóm: {c.group}")
    if c and c.teacher:
        desc.append(f"Giảng viên: {c.teacher}")
    if rule.periods:
        desc.append("Tiết: " + "–".join(str(p) for p in rule.periods))
    if rule.link:
        desc.append(f"Link học online: {rule.link}")
    if rule.note:
        desc.append(f"Ghi chú: {rule.note}")
    out = []
    for d in class_dates(rule):
        start = dt.datetime.combine(d, rule.start, tzinfo=VN)
        end = dt.datetime.combine(d, rule.end, tzinfo=VN)
        out.append(Event(
            uid=f"{rule.id}-{d.isoformat()}@lich-ptit",
            kind="class", ref_id=rule.id, course=rule.course,
            title=_course_label(courses, rule.course),
            start=start, end=end,
            alarms=_alarms("class", rule.remind, start),
            location="Học online" if rule.online else None,
            url=rule.link, description="\n".join(desc), room=rule.room,
            flags=list(rule.flags),
        ))
    return out


def expand_exam(exam: Exam, courses: dict[str, Course]) -> Event | None:
    if exam.date is None:
        return None
    all_day = exam.start is None
    start = dt.datetime.combine(exam.date, exam.start or dt.time(0, 0), tzinfo=VN)
    end = start + (dt.timedelta(days=1) if all_day else dt.timedelta(minutes=exam.duration_min or 90))
    desc = [f"Môn: {_course_label(courses, exam.course)}"]
    for label, val in (("Số báo danh", exam.seat_no), ("Hình thức", exam.form), ("Địa điểm", exam.place)):
        if val:
            desc.append(f"{label}: {val}")
    if exam.bring:
        desc.append("Mang theo: " + ", ".join(exam.bring))
    if exam.note:
        desc.append(f"Ghi chú: {exam.note}")
    return Event(
        uid=f"{exam.id}-{exam.date.isoformat()}@lich-ptit",
        kind="exam", ref_id=exam.id, course=exam.course,
        title=f"🎓 Thi: {_course_label(courses, exam.course)}",
        start=start, end=end, all_day=all_day,
        alarms=_alarms("exam", exam.remind, start),
        location=exam.place, description="\n".join(desc),
    )


def expand_task(task: Task, courses: dict[str, Course]) -> Event | None:
    if task.status == "done":
        return None
    desc = []
    if task.course:
        desc.append(f"Môn: {_course_label(courses, task.course)}")
    desc.append(f"Ưu tiên: {task.priority} · Trạng thái: {task.status} · Nguồn: {task.source}")
    if task.note:
        desc.append(f"Ghi chú: {task.note}")
    return Event(
        uid=f"{task.id}-{task.due.date().isoformat()}@lich-ptit",
        kind="task", ref_id=task.id, course=task.course,
        title=f"📝 Hạn: {task.title}",
        start=task.due, end=task.due,
        alarms=_alarms("task", task.remind, task.due),
        description="\n".join(desc),
    )


def find_conflicts(events: list[Event]) -> list[tuple[Event, Event]]:
    """Buổi học/buổi thi chồng giờ nhau (bỏ qua hạn việc)."""
    timed = sorted((e for e in events if e.kind != "task"), key=lambda e: e.start)
    out = []
    for i, a in enumerate(timed):
        for b in timed[i + 1:]:
            if b.start >= a.end:
                break
            out.append((a, b))
    return out


def expand_all(data: Data) -> list[Event]:
    events: list[Event] = []
    for rule in data.classes:
        events.extend(expand_class(rule, data.courses))
    for exam in data.exams:
        if (ev := expand_exam(exam, data.courses)) is not None:
            events.append(ev)
    for task in data.tasks:
        if (ev := expand_task(task, data.courses)) is not None:
            events.append(ev)
    for a, b in find_conflicts(events):
        for e in (a, b):
            if "trung_lich" not in e.flags:
                e.flags.append("trung_lich")
    for e in events:
        prefix = ("[Dạy bù] " if "day_bu" in e.flags else "") + ("[Trùng lịch] " if "trung_lich" in e.flags else "")
        e.title = prefix + e.title
    events.sort(key=lambda e: (e.start, e.uid))
    return events
