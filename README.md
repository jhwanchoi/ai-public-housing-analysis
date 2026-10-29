# ai-public-housing-analysis

한국 공공임대·공공지원민간임대·공공분양 모집공고를 개인 프로필 기준으로 분석하는 Claude Code 플러그인.
같은 skill을 Codex에서도 쓴다.

## Skills

| skill | 역할 |
|---|---|
| `housing-notice-analysis` | 진입점. 공고 하나를 원문 확보부터 신청 일정까지 분석 |
| `housing-scout` | 접수 중·예정 공고 탐색과 1차 선별 |
| `housing-research` | 공식 원문·정정공고·첨부 확보, 일정 대조 |
| `housing-eligibility` | 공급유형별 자격·순위 판정, 소득 산정 자료·시점 확인 |
| `housing-unit-pick` | 당첨 구조, 실질 비용, 면적, 출퇴근 비교와 가중치 추천 |
| `housing-apply` | 캘린더 2개 등록, 신청 메모, 기관 문의 스크립트 |
| `housing-tracker` | 신청 현황 기록, 중복신청·재당첨제한 충돌 검사 |

## 설치

```bash
git clone git@github.com:jhwanchoi/ai-public-housing-analysis.git ~/Documents/git/ai-public-housing-analysis
claude plugin marketplace add ~/Documents/git/ai-public-housing-analysis
claude plugin install ai-public-housing-analysis@ai-public-housing-analysis --scope user
```

Codex에서는 skill 폴더를 하나씩 링크한다.

```bash
for s in ~/Documents/git/ai-public-housing-analysis/skills/*; do ln -sfn "$s" ~/.agents/skills/"$(basename "$s")"; done
```

## 개인 데이터

개인정보는 저장소에 넣지 않는다. 기본 위치는 `~/.config/ai-public-housing-analysis/`이며 `HOUSING_DATA_DIR`로 바꿀 수 있다.

| 파일 | 내용 |
|---|---|
| `profile.md` | 프로필. 양식은 `profile.example.md` |
| `applications.md` | 신청 현황 (`housing-tracker`가 관리) |
| `private-patterns.txt` | 커밋 차단용 개인 값 정규식, 한 줄에 하나 |

## 커밋 전 개인정보 검사

```bash
git config core.hooksPath hooks
```

`hooks/pre-commit`이 `scripts/check-private.sh`를 실행한다. 아래 경우 커밋을 막는다.
- 프로필·신청 현황 파일, 공고 원문(PDF·HWPX·XLSX), 이미지가 스테이징됨
- 추가된 줄에 이메일·휴대전화·주민등록번호 형식이 있음
- 추가된 줄이 `private-patterns.txt`의 패턴과 일치함
