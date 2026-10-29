# ai-public-housing-analysis

한국의 공공임대, 공공지원민간임대, 공공분양 모집공고를 내 조건에 맞춰 분석해 주는 Claude Code 플러그인입니다.
공고 찾기부터 자격 판정, 주택 비교, 신청 일정 등록, 신청 현황 관리까지 다룹니다. 같은 skill을 Codex에서도 쓸 수 있습니다.

> **참고용 도구입니다.** 최종 자격, 순위, 당첨 여부는 모집공고 원문과 LH, SH 등 시행 기관의 심사로 정해집니다. 신청 전에는 반드시 공고 원문과 기관 안내를 확인하세요.

## 구성

| skill | 하는 일 |
|---|---|
| `housing-notice-analysis` | 진입점. 공고 하나를 원문 확보부터 신청 일정까지 분석 |
| `housing-scout` | 접수 중이거나 곧 접수할 공고를 찾아 1차 선별 |
| `housing-research` | 공식 원문, 정정 공고, 첨부 자료 확보와 일정 대조 |
| `housing-eligibility` | 공급유형별 자격과 순위 판정, 소득 산정 자료와 시점 확인 |
| `housing-unit-pick` | 당첨 구조, 실질 비용, 면적, 출퇴근 비교와 가중치 기반 추천 |
| `housing-apply` | 캘린더 일정 2개 등록, 신청 메모, 기관 문의 문구 |
| `housing-tracker` | 신청 현황 기록, 중복신청과 재당첨 제한 충돌 검사 |

## 설치

```bash
git clone git@github.com:jhwanchoi/ai-public-housing-analysis.git ~/Documents/git/ai-public-housing-analysis
claude plugin marketplace add ~/Documents/git/ai-public-housing-analysis
claude plugin install ai-public-housing-analysis@ai-public-housing-analysis --scope user
```

이미 열려 있는 Claude Code 세션에서는 `/reload-plugins`를 실행하면 바로 쓸 수 있습니다.

Codex에서는 skill 폴더를 하나씩 링크합니다.

```bash
for s in ~/Documents/git/ai-public-housing-analysis/skills/*; do
  ln -sfn "$s" ~/.agents/skills/"$(basename "$s")"
done
```

## 개인 데이터

소득, 자산, 현재 집 같은 개인정보는 저장소에 넣지 않습니다. 기본 위치는 `~/.config/ai-public-housing-analysis/`이고, `HOUSING_DATA_DIR` 환경변수로 바꿀 수 있습니다.

| 파일 | 내용 |
|---|---|
| `profile.md` | 내 프로필. 양식은 `profile.example.md` |
| `applications.md` | 신청 현황. `housing-tracker`가 관리 |
| `private-patterns.txt` | 커밋을 막을 개인 값(금액, 주소 등) 정규식. 한 줄에 하나 |

## 커밋 전 개인정보 검사

```bash
git config core.hooksPath hooks
```

`hooks/pre-commit`이 `scripts/check-private.sh`를 실행하고, 아래 경우 커밋을 막습니다.

- 프로필이나 신청 현황 파일, 공고 원문(PDF, HWPX, XLSX), 이미지가 스테이징된 경우
- 새로 추가한 줄에 이메일, 휴대전화 번호, 주민등록번호 형식이 있는 경우
- 새로 추가한 줄이 `private-patterns.txt`의 패턴과 일치하는 경우

## 라이선스

개인 프로젝트이며 별도 라이선스를 정하지 않았습니다. 공유받은 분은 개인 용도로 참고해 주세요.
