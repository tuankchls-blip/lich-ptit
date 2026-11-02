"""Dòng lệnh lichptit."""
import argparse


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="lichptit", description="Lịch PTIT – lịch học, lịch thi, việc cần làm")
    p.add_subparsers(dest="cmd")
    p.parse_args(argv)
    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
