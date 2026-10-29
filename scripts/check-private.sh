#!/usr/bin/env bash
# 커밋하려는 내용에 개인정보가 섞이지 않았는지 검사한다.
# 실제 개인 값(금액·주소 등)은 저장소 밖 패턴 파일에서 읽는다:
#   $HOUSING_DATA_DIR/private-patterns.txt (기본 ~/.config/ai-public-housing-analysis/private-patterns.txt)
#   한 줄에 하나, grep -E 정규식. 빈 줄과 # 주석은 무시.
set -euo pipefail

data_dir="${HOUSING_DATA_DIR:-$HOME/.config/ai-public-housing-analysis}"
patterns_file="$data_dir/private-patterns.txt"
fail=0

# 1) 개인 자료 파일 자체를 막는다
blocked_files=$(git diff --cached --name-only --diff-filter=ACMR \
  | grep -E '(^|/)(profile|applications)\.md$|\.(pdf|hwp|hwpx|xls|xlsx|png|jpe?g)$|(^|/)private/' \
  | grep -vxF '.claude-plugin/icon.png' || true)
if [ -n "$blocked_files" ]; then
  echo "[check-private] 개인 자료로 보이는 파일이 스테이징되어 있습니다:" >&2
  echo "$blocked_files" | sed 's/^/  - /' >&2
  fail=1
fi

# 2) 추가된 줄만 검사한다
added=$(git diff --cached -U0 --diff-filter=ACMR | grep -E '^\+' | grep -vE '^\+\+\+ ' || true)

check() {
  local label="$1" regex="$2" hits
  hits=$(printf '%s\n' "$added" | grep -nE -- "$regex" || true)
  if [ -n "$hits" ]; then
    echo "[check-private] $label 패턴 검출:" >&2
    printf '%s\n' "$hits" | head -5 | sed 's/^/  /' >&2
    fail=1
  fi
}

# git 사용자의 SSH 저장소 주소(git 다음 @호스트:경로)는 이메일로 보지 않는다
added_no_ssh=$(printf '%s\n' "$added" | sed -E 's/git@[A-Za-z0-9.-]+:[^ ]*//g')
hits=$(printf '%s\n' "$added_no_ssh" | grep -nE -- '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' || true)
if [ -n "$hits" ]; then
  echo "[check-private] 이메일 패턴 검출:" >&2
  printf '%s\n' "$hits" | head -5 | sed 's/^/  /' >&2
  fail=1
fi
check "휴대전화" '01[016789][- ]?[0-9]{3,4}[- ]?[0-9]{4}'
check "주민등록번호" '[0-9]{6}-[1-4][0-9]{6}'

if [ -f "$patterns_file" ]; then
  while IFS= read -r p || [ -n "$p" ]; do
    case "$p" in ''|'#'*) continue ;; esac
    check "개인 패턴" "$p"
  done < "$patterns_file"
else
  echo "[check-private] 경고: $patterns_file 없음. 개인 값 패턴 검사를 건너뜁니다." >&2
fi

if [ "$fail" -ne 0 ]; then
  echo "[check-private] 커밋을 중단했습니다. 의도한 내용이면 수정 후 다시 커밋하세요." >&2
  exit 1
fi
