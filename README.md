# ne-claude-plugins

NE능률 사내 Claude 플러그인 마켓플레이스.

Claude Code / Cowork에서 쓰는 사내 스킬 묶음을 한 곳에서 배포하고 버전 관리한다.

## 설치

```
/plugin marketplace add neneungyul2/ne-claude-plugins
/plugin install work-toolkit@ne-claude-plugins
/plugin install report-maker@ne-claude-plugins
/plugin install knowledge-notes@ne-claude-plugins
```

이미 추가한 마켓플레이스를 최신으로 당길 때:

```
/plugin marketplace update ne-claude-plugins
```

설치된 플러그인 확인·해제는 `/plugin` 메뉴에서 한다.

## 수록 플러그인

| 플러그인 | 하는 일 | 상태 |
|---|---|---|
| [`work-toolkit`](plugins/work-toolkit) | 조사·기획·보고·카피·이미지·데이터·자동화 7개 영역 52개 실무 상황 대응 | v0.2.0 |
| [`report-maker`](plugins/report-maker) | 컨설팅 펌 수준의 대시보드·보고서 제작 (질문 설계 → 데이터 → 스펙 → HTML/문서) | v0.3.0 |
| [`knowledge-notes`](plugins/knowledge-notes) | 새 지식을 atomic 노트로 분해해 Obsidian vault에 축적 | v0.1.0 (파일럿) |

## 저장소 구조

```
ne-claude-plugins/
├── .claude-plugin/
│   └── marketplace.json      마켓플레이스 정의. 플러그인을 추가하면 여기 등록한다
├── docs/
│   ├── design-decisions.md   왜 이렇게 만들었는지
│   └── open-issues.md        미확정 항목. 확인되면 여기와 플러그인 문서를 함께 고친다
└── plugins/
    ├── work-toolkit/
    ├── report-maker/
    └── knowledge-notes/
```

각 플러그인 디렉터리는 아래 규칙을 따른다.

- `.claude-plugin/plugin.json` — 플러그인 매니페스트 (필수)
- `skills/<스킬명>/SKILL.md` — 스킬. 디렉터리 하나가 스킬 하나
- `commands/<커맨드명>.md` — 슬래시 커맨드
- `references/` — 스킬들이 공유하는 참조 문서
- 플러그인 내부 파일을 가리킬 때는 항상 `${CLAUDE_PLUGIN_ROOT}/...` 를 쓴다

## 플러그인을 추가하려면

1. `plugins/<이름>/` 디렉터리를 만들고 `.claude-plugin/plugin.json`을 작성한다.
2. `.claude-plugin/marketplace.json`의 `plugins` 배열에 항목을 추가한다. `source`는 `"./plugins/<이름>"`.
3. 로컬에서 검증한다.
   ```
   claude plugin validate ./plugins/<이름>
   claude --plugin-dir ./plugins/<이름>
   ```
4. 커밋·푸시한다. 사용자는 `/plugin marketplace update ne-claude-plugins`로 받는다.

### 버전 정책

`plugin.json`과 `marketplace.json`의 `version`을 함께 올린다. 두 곳이 어긋나면 사용자가 업데이트를 못 받는다.

- 패치: 문구·오탈자 수정
- 마이너: 스킬 추가, 동작 변경
- 메이저: 기존 사용법이 깨지는 변경

## 문서

| 파일 | 내용 |
|---|---|
| [`docs/design-decisions.md`](docs/design-decisions.md) | 설계 근거. 결정을 바꾸려면 여기부터 고치고 구현을 따라오게 한다 |
| [`docs/open-issues.md`](docs/open-issues.md) | 미결 사항. 지표 정의·임계값처럼 확인이 필요한 항목을 모아둔다 |

## 사내 사용 시 주의

- 이 저장소의 내용은 사내 용도로만 사용한다.
- 지표 정의·기준처럼 부서마다 다를 수 있는 값은 플러그인에 박지 않고 참조 문서에서 관리한다. 확인되지 않은 값은 추정으로 채우지 말고 TODO로 남긴다.
- Metabase 등 사내망 전용 리소스에 의존하는 기능은 접근 불가한 사용자를 위한 대체 경로를 반드시 둔다.
