import datetime as dt

from lichptit.expand import expand_all, find_conflicts
from lichptit.load import load_data

from conftest import write_data


def classes(events):
    return [e for e in events if e.kind == "class"]


def test_bung_dung_so_buoi_va_bo_ngay_nghi(data_dir):
    ev = classes(expand_all(load_data(data_dir)))
    dates = [e.start.date() for e in ev]
    # Thứ Năm từ 29/10 đến 24/12 = 9 buổi, bỏ 19/11 → 8
    assert len(ev) == 8
    assert dt.date(2026, 11, 19) not in dates
    assert all(d.isoweekday() == 4 for d in dates)


def test_gio_mui_vn(data_dir):
    e = classes(expand_all(load_data(data_dir)))[0]
    assert e.start.isoformat() == "2026-10-29T19:00:00+07:00"
    assert e.end.isoformat() == "2026-10-29T21:50:00+07:00"


def test_extra_dates(tmp_path):
    d = load_data(write_data(tmp_path / "d", classes="""
- id: c1
  course: ELE1433
  weekday: T5
  from: 2026-10-26
  to: 2026-11-08
  start: "19:00"
  end: "21:50"
  extra_dates: [2026-11-07]
  flags: [day_bu]
"""))
    ev = classes(expand_all(d))
    assert [e.start.date().day for e in ev] == [29, 5, 7]
    assert ev[0].title.startswith("[Dạy bù]")


def test_nhac_mac_dinh(data_dir):
    ev = expand_all(load_data(data_dir))
    by_kind = {e.kind: e for e in ev}
    assert by_kind["class"].alarms == [-dt.timedelta(minutes=30)]
    assert by_kind["task"].alarms == [-dt.timedelta(days=1), -dt.timedelta(hours=3)]
    exam = by_kind["exam"]
    # thi 07:30 ngày 09/01 → 20:00 ngày 08/01 là lệch -11h30
    assert exam.alarms == [-dt.timedelta(days=14), -dt.timedelta(days=3), -dt.timedelta(hours=11, minutes=30)]


def test_bo_viec_xong_va_thi_chua_co_ngay(data_dir):
    ev = expand_all(load_data(data_dir))
    refs = {e.ref_id for e in ev}
    assert "task-b" not in refs
    assert "exam-INT1358" not in refs
    assert "task-a" in refs and "exam-ELE1433" in refs


def test_nhac_tuy_chinh(tmp_path):
    d = load_data(write_data(tmp_path / "d", tasks="""
- id: t1
  title: x
  due: 2026-11-10T12:00
  remind: [3d, 2h, 30m]
"""))
    t = [e for e in expand_all(d) if e.kind == "task"][0]
    assert t.alarms == [-dt.timedelta(days=3), -dt.timedelta(hours=2), -dt.timedelta(minutes=30)]
    assert t.start.utcoffset() == dt.timedelta(hours=7)


def test_trung_lich(tmp_path):
    d = load_data(write_data(tmp_path / "d", exams="""
- id: e1
  course: INT1358
  date: 2026-10-29
  start: "20:00"
"""))
    ev = expand_all(d)
    pairs = find_conflicts(ev)
    assert len(pairs) == 1
    assert all("[Trùng lịch]" in e.title for e in pairs[0])
