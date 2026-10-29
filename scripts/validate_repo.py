#!/usr/bin/env python3
"""PR과 main push마다 CI에서 실행하는 저장소 검사.

1. plugin.json과 marketplace.json이 올바른 JSON이고, 등록된 skill 폴더와 아이콘이 실제로 있는지
2. 각 SKILL.md의 frontmatter에 name과 description이 있고, name이 폴더 이름과 같은지
3. 추적 중인 파일에 개인 자료 파일이나 이메일, 휴대전화 번호, 주민등록번호 형식이 없는지

표준 라이브러리만 사용한다.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors: list[str] = []

BLOCKED_FILE = re.compile(
    r"(^|/)(profile|applications)\.md$|\.(pdf|hwp|hwpx|xls|xlsx|png|jpe?g)$|(^|/)private/"
)
ALLOWED_FILES = {".claude-plugin/icon.png"}
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
ALLOWED_EMAIL = re.compile(r"@users\.noreply\.github\.com$|^noreply@anthropic\.com$")
SSH_REMOTE = re.compile(r"git@[A-Za-z0-9.-]+:[^\s)]*")
PHONE = re.compile(r"\b01[016789][- ]?\d{3,4}[- ]?\d{4}\b")
RRN = re.compile(r"\b\d{6}-[1-4]\d{6}\b")


def check_manifests() -> None:
    plugin_path = ROOT / ".claude-plugin" / "plugin.json"
    try:
        plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
        json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"manifest를 읽을 수 없음: {e}")
        return

    for skill in plugin.get("skills", []):
        skill_md = ROOT / skill / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"plugin.json에 등록된 skill에 SKILL.md가 없음: {skill}")
            continue
        check_frontmatter(skill_md)

    icon = plugin.get("icon")
    if icon and not (ROOT / icon).is_file():
        errors.append(f"plugin.json의 icon 파일이 없음: {icon}")

    registered = {Path(s).name for s in plugin.get("skills", [])}
    for folder in sorted((ROOT / "skills").iterdir()):
        if folder.is_dir() and folder.name not in registered:
            errors.append(f"plugin.json에 등록되지 않은 skill 폴더: skills/{folder.name}")


def check_frontmatter(skill_md: Path) -> None:
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    rel = skill_md.relative_to(ROOT)
    if not match:
        errors.append(f"frontmatter가 없음: {rel}")
        return
    fields = dict(
        line.split(":", 1) for line in match.group(1).splitlines() if ":" in line
    )
    name = fields.get("name", "").strip()
    if not name:
        errors.append(f"frontmatter에 name이 없음: {rel}")
    elif name != skill_md.parent.name:
        errors.append(f"name({name})이 폴더 이름({skill_md.parent.name})과 다름: {rel}")
    if not fields.get("description", "").strip():
        errors.append(f"frontmatter에 description이 없음: {rel}")


def check_private_data() -> None:
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.splitlines()

    for rel in tracked:
        if rel in ALLOWED_FILES:
            continue
        if BLOCKED_FILE.search(rel):
            errors.append(f"개인 자료로 보이는 파일이 저장소에 있음: {rel}")
            continue
        try:
            lines = (ROOT / rel).read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for no, line in enumerate(lines, 1):
            scrubbed = SSH_REMOTE.sub("", line)
            for email in EMAIL.findall(scrubbed):
                if not ALLOWED_EMAIL.search(email):
                    errors.append(f"{rel}:{no}: 이메일 형식 발견")
            if PHONE.search(line):
                errors.append(f"{rel}:{no}: 휴대전화 번호 형식 발견")
            if RRN.search(line):
                errors.append(f"{rel}:{no}: 주민등록번호 형식 발견")


def main() -> int:
    check_manifests()
    check_private_data()
    if errors:
        print("검사 실패:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("검사 통과")
    return 0


if __name__ == "__main__":
    sys.exit(main())
