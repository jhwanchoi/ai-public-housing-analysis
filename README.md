# ai-housing-analysis

한국 임대주택·공공분양 모집공고를 개인 프로필 기준으로 분석하는 AI 에이전트용 skill.
Claude Code와 Codex에서 같은 skill을 쓴다.

## 구성

```
skills/housing-notice-analysis/
├── SKILL.md                  분석 순서와 판단 원칙
└── references/
    ├── income-rules.md       소득 산정 자료·시점 확인 규칙과 사례
    └── cost-formulas.md      실질 주거비, 전환율, 분양 비용, 당첨 구조 계산
profile.example.md            개인 프로필 양식 (실제 값 없음)
```

## 설치

```bash
git clone git@github.com:jhwanchoi/ai-housing-analysis.git ~/Documents/git/ai-housing-analysis
ln -s ~/Documents/git/ai-housing-analysis/skills/housing-notice-analysis ~/.claude/skills/housing-notice-analysis
ln -s ~/Documents/git/ai-housing-analysis/skills/housing-notice-analysis ~/.agents/skills/housing-notice-analysis
```

## 프로필

개인정보(소득, 주소, 보증금 등)는 저장소에 넣지 않는다.

- `profile.example.md`를 `profile.md`로 복사해 채우거나,
- 다른 위치에 두고 `HOUSING_PROFILE` 환경변수로 경로를 지정한다.

`profile.md`, `*.pdf`, `*.hwpx`, `*.xlsx` 등 공고 원문과 개인 자료는 `.gitignore`로 제외된다.
