import textwrap
from pathlib import Path

import pytest

COURSES = """
- code: ELE1433
  name: Kỹ thuật số
  group: "03"
  teacher: Vũ Anh Đào
- code: INT1358
  name: Toán rời rạc 1
"""

CLASSES = """
- id: ELE1433-tuan
  course: ELE1433
  weekday: T5
  from: 2026-10-26
  to: 2026-12-27
  start: "19:00"
  end: "21:50"
  skip_dates: [2026-11-19]
  link: https://example.invalid/lop
  room: "ID 123 456 789 MK BiMat42"
"""

EXAMS = """
- id: exam-ELE1433
  course: ELE1433
  date: 2027-01-09
  start: "07:30"
  duration_min: 90
  place: Trạm Hà Nội
  bring: [CCCD]
- id: exam-INT1358
  course: INT1358
  date: null
"""

TASKS = """
- id: task-a
  title: Nộp bài tập 1
  course: ELE1433
  due: 2026-11-10T23:59
- id: task-b
  title: Việc đã xong
  due: 2026-11-11
  status: done
"""


def write_data(root: Path, **files: str) -> Path:
    content = {"courses": COURSES, "classes": CLASSES, "exams": EXAMS, "tasks": TASKS}
    content.update(files)
    root.mkdir(parents=True, exist_ok=True)
    for name, text in content.items():
        (root / f"{name}.yaml").write_text(textwrap.dedent(text).lstrip("\n"), encoding="utf-8")
    return root


@pytest.fixture
def data_dir(tmp_path):
    return write_data(tmp_path / "data")
