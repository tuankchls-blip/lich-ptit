"""Mô hình dữ liệu (Pydantic) cho 4 file YAML trong data/ – xem docs/spec.md mục 5."""
from __future__ import annotations

import datetime as dt
import re
from typing import Annotated, Literal
from zoneinfo import ZoneInfo

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, Field, model_validator

VN = ZoneInfo("Asia/Ho_Chi_Minh")


# ---------- kiểu dùng chung ----------

def _parse_hhmm(v):
    """Nhận "19:00". YAML 1.1 đọc 19:00 (không ngoặc kép) thành số 1140 – đổi lại cho đúng."""
    if isinstance(v, dt.time):
        return v
    if isinstance(v, int) and not isinstance(v, bool):
        v = f"{v // 60:02d}:{v % 60:02d}"
    if isinstance(v, str):
        m = re.fullmatch(r"(\d{1,2}):(\d{2})", v.strip())
        if m:
            h, mi = int(m[1]), int(m[2])
            if h < 24 and mi < 60:
                return dt.time(h, mi)
        raise ValueError(f"giờ không hợp lệ {v!r}, cần dạng HH:MM trong khoảng 00:00–23:59")
    raise ValueError(f"giờ không hợp lệ {v!r}, cần dạng \"HH:MM\"")


HHMM = Annotated[dt.time, BeforeValidator(_parse_hhmm)]

REMIND_RE = re.compile(r"^(\d+)([mhd])$|^(\d+)d@(\d{2}):(\d{2})$")


def _check_remind(v: str) -> str:
    m = REMIND_RE.fullmatch(v)
    if not m or (m[4] is not None and (int(m[4]) > 23 or int(m[5]) > 59)):
        raise ValueError(f"lời nhắc {v!r} sai dạng; dùng 30m, 2h, 3d hoặc 1d@20:00")
    return v


Remind = Annotated[str, AfterValidator(_check_remind)]


def _check_id(v: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.\-]*", v):
        raise ValueError(f"id {v!r} chỉ được chứa chữ không dấu, số, '-', '_', '.'")
    return v


Id = Annotated[str, BeforeValidator(lambda v: str(v) if isinstance(v, int) else v), AfterValidator(_check_id)]

# Chuỗi tự do; YAML có thể đọc "03" hay 12 thành số nên ép về chuỗi.
Text = Annotated[str, BeforeValidator(lambda v: str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v)]

WEEKDAYS = {"T2": 1, "T3": 2, "T4": 3, "T5": 4, "T6": 5, "T7": 6, "CN": 7}
WEEKDAY_NAMES = {1: "Thứ Hai", 2: "Thứ Ba", 3: "Thứ Tư", 4: "Thứ Năm", 5: "Thứ Sáu", 6: "Thứ Bảy", 7: "Chủ nhật"}


def _parse_weekday(v):
    # Chỉ nhận T2..T7, CN để tránh nhầm "5" là Thứ Năm hay Thứ Sáu.
    if isinstance(v, str) and v.strip().upper() in WEEKDAYS:
        return WEEKDAYS[v.strip().upper()]
    raise ValueError(f"thứ {v!r} không hợp lệ; dùng một trong T2, T3, T4, T5, T6, T7, CN")


Weekday = Annotated[int, BeforeValidator(_parse_weekday)]


def _parse_due(v):
    if isinstance(v, dt.date) and not isinstance(v, dt.datetime):
        return dt.datetime.combine(v, dt.time(23, 59))
    return v


def _to_vn(v: dt.datetime) -> dt.datetime:
    return v.replace(tzinfo=VN) if v.tzinfo is None else v.astimezone(VN)


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


# ---------- các mô hình ----------

class Course(_Strict):
    code: Id
    name: str
    group: Text | None = None
    credits: int | None = None
    teacher: str | None = None
    lms_url: str | None = None
    color: str | None = None


class ClassRule(_Strict):
    """Buổi học: một buổi lẻ (date) hoặc lặp hằng tuần (weekday + from + to)."""

    id: Id
    course: Text
    date: dt.date | None = None
    weekday: Weekday | None = None
    from_: dt.date | None = Field(None, alias="from")
    to: dt.date | None = None
    start: HHMM
    end: HHMM
    periods: list[int] | None = None
    online: bool = True
    link: str | None = None
    room: str | None = None  # ID/mật khẩu phòng – chỉ đưa vào DESCRIPTION của ICS
    skip_dates: list[dt.date] = []
    extra_dates: list[dt.date] = []
    flags: list[Literal["day_bu", "trung_lich"]] = []
    remind: list[Remind] | None = None
    note: str | None = None

    @model_validator(mode="after")
    def _check(self):
        if self.end <= self.start:
            raise ValueError("giờ kết thúc (end) phải sau giờ bắt đầu (start)")
        weekly = (self.weekday, self.from_, self.to)
        if self.date is not None:
            if any(x is not None for x in weekly):
                raise ValueError("buổi lẻ có 'date' thì không ghi weekday/from/to")
        else:
            if any(x is None for x in weekly):
                raise ValueError("cần 'date' (buổi lẻ) hoặc đủ weekday + from + to (lặp hằng tuần)")
            if self.from_ > self.to:
                raise ValueError("'from' phải trước hoặc bằng 'to'")
        return self


class Exam(_Strict):
    id: Id
    course: Text
    date: dt.date | None = None  # null = trường chưa công bố
    start: HHMM | None = None
    duration_min: int | None = Field(None, gt=0)
    place: str | None = None
    seat_no: Text | None = None
    form: str | None = None
    bring: list[str] = []
    remind: list[Remind] | None = None
    note: str | None = None

    @model_validator(mode="after")
    def _check(self):
        if self.start is not None and self.date is None:
            raise ValueError("có 'start' thì phải có 'date'")
        return self


class Task(_Strict):
    id: Id
    title: str
    course: Text | None = None
    due: Annotated[dt.datetime, BeforeValidator(_parse_due), AfterValidator(_to_vn)]
    priority: Literal["high", "normal", "low"] = "normal"
    status: Literal["todo", "doing", "done"] = "todo"
    source: Literal["manual", "lms", "qldt"] = "manual"
    note: str | None = None
    remind: list[Remind] | None = None
