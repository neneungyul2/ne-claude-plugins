# ne-claude-plugins

NE능률 사내 Claude 플러그인 마켓플레이스.

Claude Code / Cowork에서 쓰는 사내 스킬 묶음을 한 곳에서 배포하고 버전 관리한다.

## 설치

```
/plugin marketplace add choiyh919/sales-strategy
/plugin install work-toolkit@ne-claude-plugins
/plugin install report-maker@ne-claude-plugins
/plugin install knowledge-notes@ne-claude-plugins
/plugin install print-quantity@ne-claude-plugins
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
| [`report-maker`](plugins/report-maker) | 컨설팅 펌 수준의 대시보드·보고서 제작 (결정·진단·점검·조망·탐색 다섯 종류, 질문 설계 → 데이터 → 스펙 → 스토리 검사 → HTML/문서, 화면 편집, NE 디자인 토큰) | v0.13.0 |
| [`knowledge-notes`](plugins/knowledge-notes) | 새 지식을 atomic 노트로 분해해 Obsidian vault에 축적 | v0.1.0 (파일럿) |
| [`print-quantity`](plugins/print-quantity) | 도서 제작 수량 산출. 신간은 시장에서 역산, 기간본은 재고 소진 시점에서 역산 | v0.2.0 |

### report-maker 한눈에

말로 요청하면 **결론을 누가 내는지**를 보고 다섯 종류 중 하나로 만든다. 종류 이름을 알 필요는 없다.

| 종류 | 이럴 때 | 이렇게 말하면 된다 |
|---|---|---|
| 결정형 | 무엇을 할지 승인받아야 할 때 | "개정 시점을 앞당길지 정해야 해" |
| 진단형 | 원인을 밝혀야 할 때 | "점유율이 왜 떨어졌는지 봐줘" |
| 점검형 | 정해둔 기준으로 매번 확인할 때 | "매주 이상 있으면 알 수 있게", 영업일보 |
| 조망형 | 판단 없이 전체 그림을 보여줄 때 | "시장 현황 한눈에", "의견 빼고 데이터만" |
| 탐색형 | 읽는 사람이 직접 골라 볼 때 | "기간·지역 바꿔가며 볼 수 있게" |

진행은 다섯 단계다 — ① 용도를 묻고 종류 확인(글자 스케치로) → ② 데이터 정리 → ③ 구성 확인 →
④ HTML·문서 만들기 → ⑤ 검수. 읽는 사람이 배경을 모르면 맨 위에 질문과 전체 그림을 먼저 둔다.
완성된 HTML은 화면에서 글·단락 순서·배치를 직접 고쳐 저장할 수 있다. 자세한 것은 [플러그인 README](plugins/report-maker).

## 저장소 구조

```
ne-claude-plugins/
├── AGENTS.md                 이 레포를 고칠 때 지켜야 할 규칙. 작업 전에 읽는다
├── CLAUDE.md                 AGENTS.md를 가리키는 포인터
├── .claude-plugin/
│   └── marketplace.json      마켓플레이스 정의. 플러그인을 추가하면 여기 등록한다
├── docs/
│   ├── design-decisions.md   왜 이렇게 만들었는지
│   └── open-issues.md        미확정 항목. 확인되면 여기와 플러그인 문서를 함께 고친다
└── plugins/
    ├── work-toolkit/
    ├── report-maker/
    ├── knowledge-notes/
    └── print-quantity/
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

판정 기준은 하나다. **설치한 사람이 하던 대로 했을 때 경험이 달라지는가.**

- **patch** — 하던 대로 하면 같은 결과. 문구·오탈자, 임계값 미세조정, 내부 리팩터링, 단순 튜닝
- **minor** — 하던 대로 해도 되지만 다르게 쓸 수 있게 된다. 스킬·커맨드 추가, 단계 추가, 폴백 신설
- **major** — 하던 대로 하면 깨진다. 이름 변경·삭제, 비호환 스키마 변경 (0.x 구간에서는 minor로 올리되 무엇이 깨지는지 명시)

애매하면 낮은 쪽으로 내린다. 올릴 때는 `plugin.json` · `marketplace.json` · 위 수록 플러그인 표
**세 곳을 함께** 올린다. 앞의 두 곳이 어긋나면 사용자가 업데이트를 못 받는다.

자세한 기준과 배포 절차는 [`AGENTS.md`](AGENTS.md)에 있다.

## 문서

| 파일 | 내용 |
|---|---|
| [`AGENTS.md`](AGENTS.md) | 작업 규칙. 환경 의존 폴백, 버전 정책, 배포 절차. 이 레포를 고치기 전에 읽는다 |
| [`docs/design-decisions.md`](docs/design-decisions.md) | 설계 근거. 결정을 바꾸려면 여기부터 고치고 구현을 따라오게 한다 |
| [`docs/open-issues.md`](docs/open-issues.md) | 미결 사항. 지표 정의·임계값처럼 확인이 필요한 항목을 모아둔다 |

## 사내 사용 시 주의

- 이 저장소의 내용은 사내 용도로만 사용한다.
- 지표 정의·기준처럼 부서마다 다를 수 있는 값은 플러그인에 박지 않고 참조 문서에서 관리한다. 확인되지 않은 값은 추정으로 채우지 말고 TODO로 남긴다.
- Metabase·로컬 MCP·개인 PC 경로처럼 **특정 환경에서만 되는 것**에 의존하는 기능은, 그 환경이 없는 사용자를 위한 대체 경로를 반드시 함께 만든다. 없는 값은 추정으로 메우지 말고 빈칸 + TODO로 남긴다. ([`AGENTS.md` 2장](AGENTS.md))
