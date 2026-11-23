#!/usr/bin/env python3
"""신청 현황 파일(applications.md)의 표를 안전하게 고친다.

데이터 위치: $HOUSING_DATA_DIR/applications.md, 없으면 ~/.config/ai-public-housing-analysis/applications.md
개인 데이터이므로 이 스크립트는 저장소 안에는 아무것도 쓰지 않는다.

사용법:
  tracker.py list [--active]
  tracker.py add --notice 공고 [--org ..] [--unit ..] [--rank ..] [--status ..] [--next ..] [--memo ..]
  tracker.py set 공고명일부 [--org ..] [--unit ..] [--rank ..] [--status ..] [--next ..] [--memo ..]

표준 라이브러리만 사용한다.
"""
import argparse
import datetime
import os
import sys
from pathlib import Path

COLUMNS = ["notice", "org", "unit", "rank", "status", "next", "memo"]
HEADERS = ["공고", "기관과 유형", "신청 단위", "순위", "상태", "다음 일정", "메모"]
ACTIVE = ("신청예정", "신청완료", "서류대상", "당첨", "예비", "계약")
TEMPLATE = (
    "# 신청 현황\n\n"
    "| " + " | ".join(HEADERS) + " |\n"
    "|" + "---|" * len(HEADERS) + "\n"
)


def data_path() -> Path:
    base = os.environ.get("HOUSING_DATA_DIR") or "~/.config/ai-public-housing-analysis"
    return Path(base).expanduser() / "applications.md"


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_table_row(line: str) -> bool:
    return line.startswith("|") and not set(line.replace("|", "").strip()) <= set("-: ")


def load(path: Path) -> list[str]:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(TEMPLATE, encoding="utf-8")
    return path.read_text(encoding="utf-8").splitlines()


def data_rows(lines: list[str]) -> list[int]:
    """헤더 행을 뺀 데이터 행의 줄 번호."""
    rows = [i for i, l in enumerate(lines) if is_table_row(l)]
    return rows[1:]


def clean(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ").strip()


def render(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def touch_date(lines: list[str]) -> None:
    today = datetime.date.today().isoformat()
    for i, l in enumerate(lines):
        if l.startswith("최종 갱신:"):
            rest = l[len("최종 갱신:"):].strip()
            parts = rest.split(" ", 1)
            suffix = f" {parts[1]}" if len(parts) > 1 and len(parts[0]) == 10 else ""
            lines[i] = f"최종 갱신: {today}{suffix}"
            return


def cmd_list(lines: list[str], active: bool) -> int:
    for i in data_rows(lines):
        cells = split_row(lines[i])
        status = cells[4] if len(cells) > 4 else ""
        if active and not status.startswith(ACTIVE):
            continue
        print(f"{status:<16} {cells[0]}  →  {cells[5] if len(cells) > 5 else ''}")
    return 0


def cmd_add(lines: list[str], args: argparse.Namespace) -> int:
    cells = [clean(getattr(args, c) or "-") for c in COLUMNS]
    rows = data_rows(lines)
    if any(split_row(lines[i])[0] == cells[0] for i in rows):
        print(f"이미 같은 공고 행이 있습니다: {cells[0]} (set으로 수정하세요)", file=sys.stderr)
        return 1
    header = [i for i, l in enumerate(lines) if is_table_row(l)]
    insert_at = (rows[-1] if rows else header[0] + 1) + 1
    lines.insert(insert_at, render(cells))
    touch_date(lines)
    return 0


def cmd_set(lines: list[str], args: argparse.Namespace) -> int:
    matches = [i for i in data_rows(lines) if args.match in split_row(lines[i])[0]]
    if len(matches) != 1:
        print(f"'{args.match}'와 일치하는 행이 {len(matches)}개입니다. 더 구체적으로 지정하세요.", file=sys.stderr)
        for i in matches:
            print("  - " + split_row(lines[i])[0], file=sys.stderr)
        return 1
    i = matches[0]
    cells = split_row(lines[i])
    cells += [""] * (len(COLUMNS) - len(cells))
    changed = False
    for k, col in enumerate(COLUMNS):
        value = getattr(args, col, None)
        if value is not None:
            cells[k] = clean(value)
            changed = True
    if not changed:
        print("바꿀 칸을 하나 이상 지정하세요.", file=sys.stderr)
        return 1
    lines[i] = render(cells)
    touch_date(lines)
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="신청 현황 표 관리")
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("list")
    pl.add_argument("--active", action="store_true", help="신청예정~계약 상태만")

    for name in ("add", "set"):
        sp = sub.add_parser(name)
        if name == "set":
            sp.add_argument("match", help="공고명 일부")
            sp.add_argument("--notice")
        else:
            sp.add_argument("--notice", required=True)
        for col in COLUMNS[1:]:
            sp.add_argument(f"--{col}")

    args = p.parse_args()
    path = data_path()
    lines = load(path)

    if args.cmd == "list":
        return cmd_list(lines, args.active)
    code = cmd_add(lines, args) if args.cmd == "add" else cmd_set(lines, args)
    if code == 0:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"갱신함: {path}")
    return code


if __name__ == "__main__":
    sys.exit(main())
