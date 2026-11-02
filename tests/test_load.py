import pytest

from lichptit.load import DataError, load_data

from conftest import write_data


def errors_for(tmp_path, **files):
    with pytest.raises(DataError) as e:
        load_data(write_data(tmp_path / "d", **files))
    return e.value.errors


def test_load_ok(data_dir):
    d = load_data(data_dir)
    assert set(d.courses) == {"ELE1433", "INT1358"}
    assert len(d.classes) == 1 and len(d.exams) == 2 and len(d.tasks) == 2


def test_gio_25_bao_dung_dong(tmp_path):
    errs = errors_for(tmp_path, classes="""
- id: c1
  course: ELE1433
  date: 2026-11-05
  start: "25:00"
  end: "21:50"
""")
    assert len(errs) == 1
    assert errs[0].startswith("classes.yaml:4:")
    assert "start" in errs[0] and "25:00" in errs[0]


def test_gio_khong_ngoac_kep_van_doc_dung(tmp_path):
    d = load_data(write_data(tmp_path / "d", classes="""
- id: c1
  course: ELE1433
  date: 2026-11-05
  start: 19:00
  end: 21:50
"""))
    assert d.classes[0].start.hour == 19 and d.classes[0].end.minute == 50


def test_thieu_due(tmp_path):
    errs = errors_for(tmp_path, tasks="""
- id: t1
  title: OK
  due: 2026-11-10
- id: t2
  title: Thiếu hạn
""")
    assert len(errs) == 1
    assert errs[0].startswith("tasks.yaml:4:")
    assert "mục 2 (id=t2)" in errs[0] and "'due'" in errs[0] and "thiếu" in errs[0]


def test_mon_khong_ton_tai(tmp_path):
    errs = errors_for(tmp_path, exams="""
- id: e1
  course: XYZ999
""")
    assert any("XYZ999" in e and "exams.yaml" in e for e in errs)


def test_id_trung(tmp_path):
    errs = errors_for(tmp_path, exams="""
- id: task-a
  course: ELE1433
""")
    assert any("trùng" in e for e in errs)


def test_truong_la(tmp_path):
    errs = errors_for(tmp_path, tasks="""
- id: t1
  title: x
  due: 2026-11-10
  dua: sai
""")
    assert errs[0].startswith("tasks.yaml:4:") and "'dua'" in errs[0]


def test_thu_so_bi_tu_choi(tmp_path):
    errs = errors_for(tmp_path, classes="""
- id: c1
  course: ELE1433
  weekday: 5
  from: 2026-10-26
  to: 2026-12-27
  start: "19:00"
  end: "21:50"
""")
    assert "classes.yaml:3:" in errs[0] and "T2" in errs[0]


def test_du_lieu_that_trong_repo():
    d = load_data("data")
    assert len(d.courses) == 3
