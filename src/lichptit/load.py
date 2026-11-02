"""Đọc và kiểm tra 4 file YAML trong data/. Lỗi báo dạng: file:dòng: mục N (id=...) trường 'x': lý do."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml
from pydantic import BaseModel, ValidationError

from .models import ClassRule, Course, Exam, Task

FILES: dict[str, type[BaseModel]] = {
    "courses": Course,
    "classes": ClassRule,
    "exams": Exam,
    "tasks": Task,
}


class DataError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("\n".join(errors))


@dataclass
class Data:
    courses: dict[str, Course] = field(default_factory=dict)
    classes: list[ClassRule] = field(default_factory=list)
    exams: list[Exam] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)


_MSG = {
    "missing": "thiếu trường bắt buộc",
    "extra_forbidden": "trường không được phép (gõ sai tên?)",
}


def _msg(err: dict) -> str:
    if err["type"] in _MSG:
        return _MSG[err["type"]]
    msg = err["msg"]
    return msg.removeprefix("Value error, ")


def _field_line(item_node, field_name, default: int) -> int:
    if isinstance(item_node, yaml.MappingNode):
        for k, v in item_node.value:
            if k.value == field_name:
                return v.start_mark.line + 1
    return default


def _load_file(path: Path, model: type[BaseModel], errors: list[str]) -> list:
    text = path.read_text(encoding="utf-8")
    name = path.name
    try:
        raw = yaml.safe_load(text)
        root = yaml.compose(text)
    except yaml.YAMLError as e:
        mark = getattr(e, "problem_mark", None)
        line = f":{mark.line + 1}" if mark else ""
        errors.append(f"{name}{line}: YAML sai cú pháp: {getattr(e, 'problem', e)}")
        return []
    if raw is None:
        return []
    if not isinstance(raw, list):
        errors.append(f"{name}:1: file phải là một danh sách (mỗi mục bắt đầu bằng '- ')")
        return []
    out = []
    for i, (item, node) in enumerate(zip(raw, root.value), start=1):
        line = node.start_mark.line + 1
        if not isinstance(item, dict):
            errors.append(f"{name}:{line}: mục {i}: phải là một bảng khóa: giá trị")
            continue
        ident = item.get("id", item.get("code", "?"))
        try:
            out.append(model.model_validate(item))
        except ValidationError as e:
            for err in e.errors():
                fld = str(err["loc"][0]) if err["loc"] else None
                fline = _field_line(node, fld, line) if fld else line
                where = f" trường '{fld}'" if fld else ""
                errors.append(f"{name}:{fline}: mục {i} (id={ident}){where}: {_msg(err)}")
    return out


def load_data(data_dir: str | Path = "data") -> Data:
    """Đọc data/*.yaml, kiểm tra schema, id trùng và mã môn không tồn tại. Lỗi → DataError."""
    data_dir = Path(data_dir)
    errors: list[str] = []
    loaded: dict[str, list] = {}
    for key, model in FILES.items():
        path = data_dir / f"{key}.yaml"
        if not path.exists():
            if key == "courses":
                errors.append(f"{path}: không tìm thấy file (bắt buộc)")
            loaded[key] = []
            continue
        loaded[key] = _load_file(path, model, errors)

    data = Data()
    for c in loaded["courses"]:
        if c.code in data.courses:
            errors.append(f"courses.yaml: mã môn {c.code} bị trùng")
        data.courses[c.code] = c
    data.classes, data.exams, data.tasks = loaded["classes"], loaded["exams"], loaded["tasks"]

    seen: dict[str, str] = {}
    for fname, items in (("classes.yaml", data.classes), ("exams.yaml", data.exams), ("tasks.yaml", data.tasks)):
        for i, it in enumerate(items, start=1):
            if it.id in seen:
                errors.append(f"{fname}: mục {i} (id={it.id}): id trùng với một mục trong {seen[it.id]}")
            seen[it.id] = fname
            if it.course is not None and data.courses and it.course not in data.courses:
                errors.append(f"{fname}: mục {i} (id={it.id}) trường 'course': môn {it.course} không có trong courses.yaml")

    if errors:
        raise DataError(errors)
    return data
