"""Dòng lệnh lichptit: check | build."""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from .expand import expand_all, find_conflicts
from .export_ics import to_ics
from .load import DataError, load_data


def _load(data_dir: str):
    try:
        return load_data(data_dir)
    except DataError as e:
        print("LỖI DỮ LIỆU – không xuất lịch:", file=sys.stderr)
        for line in e.errors:
            print("  " + line, file=sys.stderr)
        return None


def _print_conflicts(events) -> None:
    for a, b in find_conflicts(events):
        print(f"⚠️  Trùng giờ: {a.start:%d/%m %H:%M} {a.title}  ↔  {b.start:%d/%m %H:%M} {b.title}")


def cmd_check(args) -> int:
    data = _load(args.data)
    if data is None:
        return 1
    events = expand_all(data)
    n_class = sum(e.kind == "class" for e in events)
    n_exam_dated = sum(e.date is not None for e in data.exams)
    n_open = sum(t.status != "done" for t in data.tasks)
    print(f"OK: {len(data.courses)} môn, {n_class} buổi học, "
          f"{len(data.exams)} kỳ thi ({n_exam_dated} đã có ngày), "
          f"{len(data.tasks)} việc ({n_open} chưa xong)")
    _print_conflicts(events)
    return 0


def cmd_build(args) -> int:
    token = args.token or os.environ.get("SITE_TOKEN", "")
    if not re.fullmatch(r"[A-Za-z0-9_\-]{1,128}", token):
        print("Thiếu hoặc sai --token / SITE_TOKEN (chỉ chữ, số, '-', '_').", file=sys.stderr)
        return 2
    data = _load(args.data)
    if data is None:
        return 1
    events = expand_all(data)
    outdir = Path(args.out) / token
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "calendar.ics").write_bytes(to_ics(events))
    # Không in token ra log (đường dẫn bí mật).
    print(f"Đã ghi {args.out}/***/calendar.ics ({len(events)} sự kiện)")
    _print_conflicts(events)
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="lichptit", description="Lịch PTIT – lịch học, lịch thi, việc cần làm")
    p.add_argument("--data", default="data", help="thư mục chứa các file YAML (mặc định: data)")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("check", help="kiểm tra dữ liệu YAML").set_defaults(func=cmd_check)
    b = sub.add_parser("build", help="xuất calendar.ics")
    b.add_argument("--out", default="_site", help="thư mục đầu ra (mặc định: _site)")
    b.add_argument("--token", help="tên thư mục bí mật; mặc định lấy biến SITE_TOKEN")
    b.set_defaults(func=cmd_build)
    args = p.parse_args(argv)
    if not getattr(args, "func", None):
        p.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
