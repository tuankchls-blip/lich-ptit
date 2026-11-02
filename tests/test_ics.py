import datetime as dt

from icalendar import Calendar

from lichptit.expand import expand_all
from lichptit.export_ics import to_ics
from lichptit.load import load_data

ROOM = "BiMat42"


def build(data_dir, now):
    return to_ics(expand_all(load_data(data_dir)), now=now)


def test_ics_mo_lai_duoc_uid_on_dinh_valarm(data_dir):
    t1 = dt.datetime(2026, 11, 1, tzinfo=dt.timezone.utc)
    a, b = build(data_dir, t1), build(data_dir, t1 + dt.timedelta(hours=6))
    ca, cb = Calendar.from_ical(a), Calendar.from_ical(b)
    ua = [str(e["UID"]) for e in ca.walk("VEVENT")]
    ub = [str(e["UID"]) for e in cb.walk("VEVENT")]
    assert ua == ub and len(ua) == len(set(ua)) == 8 + 1 + 1
    assert "ELE1433-tuan-2026-10-29@lich-ptit" in ua

    alarms = {str(e["UID"]).split("-20")[0]: len(e.walk("VALARM")) for e in ca.walk("VEVENT")}
    assert alarms["ELE1433-tuan"] == 1
    assert alarms["task-a"] == 2
    assert alarms["exam-ELE1433"] == 3


def test_gio_doi_sang_utc(data_dir):
    cal = Calendar.from_ical(build(data_dir, None))
    first = next(e for e in cal.walk("VEVENT") if str(e["UID"]).startswith("ELE1433-tuan-2026-10-29"))
    start = first.decoded("DTSTART")
    assert start == dt.datetime(2026, 10, 29, 12, 0, tzinfo=dt.timezone.utc)
    assert b"DTSTART:20261029T120000Z" in build(data_dir, None)


def test_room_chi_nam_trong_description(data_dir, capsys):
    from lichptit.cli import main

    raw = build(data_dir, None)
    cal = Calendar.from_ical(raw)
    for e in cal.walk("VEVENT"):
        for key, val in e.items():
            if ROOM in str(val):
                assert key == "DESCRIPTION"
    assert any(ROOM in str(e.get("DESCRIPTION", "")) for e in cal.walk("VEVENT"))
    # Không lọt ra log của check/build
    main(["--data", str(data_dir), "check"])
    out = capsys.readouterr()
    assert ROOM not in out.out + out.err


def test_lich_co_refresh(data_dir):
    raw = build(data_dir, None)
    assert b"REFRESH-INTERVAL;VALUE=DURATION:PT1H" in raw
