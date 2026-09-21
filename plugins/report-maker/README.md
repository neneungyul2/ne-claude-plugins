# report-maker

경영컨설팅 펌 수준의 대시보드·보고서 제작을 표준화한다.
데이터를 다루지 않는 인력도 같은 품질의 산출물을 낼 수 있게 하는 것이 목표다.

## 쓰는 법

그냥 말하면 된다. `report-helper`가 받는다.

```
"이 엑셀 좀 차트로 보여줘"
"8월 채널별 실적 정리해서 본부장 보고용으로"
"지난달 화면 이번 달 걸로 갱신해줘"
```

| 커맨드 | 용도 |
|---|---|
| `/quick` | 본인 확인용 빠른 시각화 |
| `/report` | 정식 보고 (5단계 전부) — 결론을 내미는 설명형 |
| `/explore` | **축을 바꿔가며 보는 탐색형 대시보드.** 결론이 아니라 틀을 만든다 |
| `/verify` | **이미 있는 산출물을 검수만 한다** — 남이 만든 것도 |
| `/refresh` | **기존 리포트를 새 데이터로** — 구성은 그대로 |

`report-helper`가 요청을 받으면 `references/product-lines.md`의 질문("다음에 열 때
무엇을 볼지도 그때 정하나요?")으로 설명형/탐색형을 먼저 가르고, 그다음 설명형 안에서
진단·선택·감시·추적 유형을 가른다. 두 계열은 아예 다른 파이프라인이다 — 아래 표.

## 산출물 유형 — 독자가 무엇을 모르는가

형태를 정하는 것은 주제가 아니라 **독자가 무엇을 모르는가**다.
같은 매출 데이터로도 "왜 이런지"를 모르면 진단이고 "지금 괜찮은지"를 모르면 감시다.

| 모르는 것 | 유형 | 주인공 | 결론 |
|---|---|---|---|
| 무슨 일이 일어나나 | `diagnostic` 진단 | 근거 exhibit 하나 | "실은 X다" |
| 어느 쪽이 나은가 | `choice` 선택 | 옵션 × 판단기준 표 | "X를 하자, Y가 아닌 이유는" |
| 지금 괜찮은가 | `watch` 감시 | 지표 행과 임계값 | **"이상 없음"도 정상 출력** |
| 계획대로 가나 | `track` 추적 | 시간축과 기준선 | "이 속도면 도달/미달" |

**유형을 사용자에게 묻지 않는다.** 사용자가 한 말에서 읽어내고 형태를 보여 확인받는다.
유형에 따라 **무엇이 필수인지가 달라진다** (`references/report-types.md`).

위 네 유형은 전부 **설명형**이다. "필터로 볼 수 있게", "날짜·기간을 바꿔가며",
"직접 파볼 수 있게" 같은 요청은 다섯 번째 유형이 아니라 **다른 계열, 탐색형**이다 —
`key_takeaway`·`action_title`·`weight: primary`가 원천적으로 성립하지 않는다.
`references/product-lines.md`가 왜 나뉘는지, `/explore`가 어떻게 도는지 정리한다.

## 동작 구조 — 5단계 (설명형)

```
질문·유형 → 데이터 → [스펙·배치] → 렌더 → 검수
  ①확인                  ②확인
```

**앞뒤 두 단계가 핵심이다.** 앞에서 무엇을 답할지 합의하지 않으면 있는 데이터로 만들 수
있는 것을 만들게 되고, 뒤에서 다른 눈으로 보지 않으면 만든 사람만 읽히는 화면이 나간다.

가운데 **포맷 중립 스펙**을 반드시 거친다. 같은 데이터로 만든 HTML과 슬라이드의 결론이
달라지지 않는다.

사용자 확인은 두 곳이고 **둘 다 글자 와이어프레임**이다 — HTML을 그려서 확인받지 않는다.
화면을 만들면 사용자는 구조가 아니라 색에 반응하고, 만든 쪽은 애착이 생겨 틀렸어도 못 버린다.

| 스킬 | 하는 일 |
|---|---|
| `report-helper` | 진입점. 모드(quick/report) 판단 후 안내 |
| `frame-question` | **유형 판정 + 질문·가정·수신자·3분 스토리·긴장 합의.** report 필수. 데이터를 열기 전에 |
| `load-data` | 엑셀·CSV·붙여넣기·Metabase → 정규화 데이터셋 + 데이터셋 카드 |
| `plan-report` | 스펙 작성 + **배치 설계**(서열·숫자 소유권·강조 예산) + 자체 검사 |
| `build-html` | HTML 단일 파일 출력 (외부 의존 없음) |
| `build-doc` | 문서·슬라이드 출력 |
| `verify-report` | **검수.** report 필수 |

| 에이전트 | 모델 | 하는 일 |
|---|---|---|
| `report-verifier` | `inherit` | **만든 맥락 없이** 결과물만 보고 검수. 발견만 하고 고치지 않는다 |
| `report-data-prep` | `sonnet` | 파싱·정제·집계. 해석하지 않는다 |

| 스크립트 | 언제 |
|---|---|
| `scripts/assemble.py` | 항상. 본문 + CSS + JS → 단일 파일 |
| `scripts/check_html.py` | 항상. 소스를 읽는다. 의존성 없음 |
| `scripts/lint_render.py` | 항상. **브라우저로 칠해보고 픽셀을 잰다** (playwright) |
| `scripts/verify_docs_sync.py` | 개발용. 릴리스 전에 플러그인 자신을 검사한다 |

## 동작 구조 — 탐색형

```
축·그레인·패널 합의 → 데이터(그레인 전체) → [탐색 스펙] → 공용 엔진 렌더링 → 검수
     ①확인                                       ②확인
```

결론을 검사하지 않는다 — **축 조합을 바꿔도 화면이 안 깨지는가**를 검사한다.

| 스킬 | 설명형 대응 | 하는 일 |
|---|---|---|
| `frame-explore` | `frame-question` | 질문이 아니라 **축(axis)**을 합의한다 |
| `plan-explore` | `plan-report` | 축·그레인·패널을 확정한 탐색 스펙을 만든다 |
| `build-explore` | `build-html` | 공용 계산 엔진(`template/explore-engine.js`) 위에 패널을 조립한다 |

`references/explore-model.md`가 데이터 그레인(long format)·축 유형·패널 유형·계산
엔진 원칙을 담는다. `template/explore-engine.js`(계산: 필터·rollup·wavg·상위N+기타)와
`template/explore.css`·`template/explore-parts.html`(패널 부품)이 `base.css`·`base.js` 위에
얹힌다 — `assemble.py --css base.css,explore.css --js base.js,explore-engine.js`.

## 산출물이 갖춰야 할 것

아래는 **진단형 기준**이다. 유형에 따라 달라진다 (`references/report-types.md` §3).

| 요소 | 규칙 |
|---|---|
| **핵심 결론** | 화면 최상단, 가장 큰 글자. 수치와 결론어에 형광펜(`emphasis` 2~4개) |
| **요청(`ask`)** | 결론은 발견에서 끝나지 않는다. 히어로 안에 요청이 있어야 한다 |
| **히어로 요약** | 각 exhibit의 `action_title`을 **순서대로 그대로**. 요약을 새로 쓰지 않는다 |
| **KPI** | 2~4개. 비교값 없는 지표는 KPI가 아니다 |
| **인사이트 → 액션** | report 모드 3~5개. 발견·근거·제안·우선순위 **표**. 제목은 동사로 끝난다. **담당자는 적지 않는다** |
| **수신자 레벨** | 액션의 `level`이 `brief.audience_level`보다 두 단계 아래면 "실무 후속 과제"로 내린다 |
| **용어 설명** | 축약어·사내 용어는 점선 밑줄 + 호버 툴팁. 정의는 `metrics.md`에서 가져온다 |
| **산식 모달** | 한 문장으로 안 되는 계산은 `i` 아이콘 → 모달 |
| **묶은 항목** | "기타"·"나머지 N개"는 클릭해서 전체를 볼 수 있어야 한다 (`group_detail`) |
| **네비게이션** | exhibit 3개 이상이면 좌측 스티키 목차 + 섹션 번호 배지 |
| **주장 하나** | `action_title`은 한 exhibit당 주장 하나. `—`로 두 주장 잇기 금지 |
| **축 전환** | 같은 질문을 다른 각도로 봐야 하면 exhibit을 쪼개지 말고 `views` 토글 |
| **강조 단계** | 같은 차트로 여러 이야기를 하면 `emphasis_steps`. **정렬을 바꾸지 않는다** |
| **텍스트** | 모든 차트에 제목, 모든 축에 축 제목. 범례 대신 직접 라벨 |
| **강조 상한** | 화면의 10% 이하. 계열은 4~5개 이하 (단기기억 한계) |
| **드릴다운** | 묶음에서 개별로 2단계. 수백 개를 처음부터 보여주지 않는다 |
| **인코딩 서열** | `action_title`의 주장을 만드는 값이 `x`나 `y`에 있어야 한다 (`encoding.claim`) |
| **자리 크기** | `weight: primary`는 정확히 하나. 빈 공간이 많은 차트는 primary가 못 된다 |
| **숫자 소유권** | 같은 숫자를 두 곳에서 크게 말하지 않는다 |
| **본문 표** | 12행 이하. 넘으면 묶고 전량은 모달로 |
| **치수** | 타입 6단계·라운드 4단계, **전부 4px의 배수** |
| **가정 명시** | `brief.assumptions`를 산출물에 그대로 표시. 미확인은 `확인 필요` 배지 |

## 지원 차트

기본형 — `simple_text` `bar` `bar_sorted` `line` `stacked_bar` `stacked_bar_100` `stacked_area`
`dot_plot` `scatter` `histogram` `diverging_bar` `bullet` `kpi` `table`

컨설팅 계열 — **`slopegraph`**(두 시점 증감) **`small_multiples`**(계열이 많을 때)
**`marimekko`**(크기와 구성을 동시에) **`waterfall`**(증감 분해)
**`choropleth`**(한국 지도) `heatmap` `sankey`

금칙 — 파이, 도넛, 3D, 이중 Y축, 잘린 축, 무지개 팔레트, 게이지, 워드클라우드

## 참조 문서

| 파일 | 내용 |
|---|---|
| `references/storytelling.md` | **스토리 규칙.** Big Idea·3막 구조·긴장·서사 순서·수평/수직 논리 |
| `references/design-rules.md` | 게슈탈트·강조 상한·배치·색·정렬·여백·각주·용어·검수 |
| `references/chart-rules.md` | 질문 유형별 차트 선택, 금칙과 이유, 차트별 세부 규칙 |
| `references/metrics.md` | 지표 정의와 복수 기준. **glossary의 원본** |
| `references/korea-map.md` | 한국 지도 그리는 법, 색 계조, 착시 주의 |
| `skills/frame-question/SKILL.md` | 질문 후보 도출, 수신자 레벨, 가정, 분석 축 정의 |
| `references/watch-thresholds.md` | 감시형 임계값 설정·결론문 |
| `references/sources/` | 엑셀·Metabase·붙여넣기 어댑터별 주의사항 |
| `references/template/parts.html` | **부품 목록(설명형). 리포트 만들 때 읽는 것은 이것뿐** |
| `references/template/base.css` `base.js` | 읽지 않는다. `assemble.py`가 붙인다 |
| `references/html-template.html` | 위 셋의 **조립 결과.** 검사용. 직접 고치지 않는다 |
| `assets/korea_paths.json` | 시도 17개 + 시군구 전체 SVG 경로 (441KB) |
| `references/report-types.md` | **산출물 유형 4종과 유형별 필수·해당없음** (설명형 안의 갈래) |
| `references/product-lines.md` | **설명형 vs 탐색형.** `report-types.md`보다 앞서 읽는 문서 |
| `references/explore-model.md` | 탐색형 데이터 그레인·축·패널 유형·계산 엔진 원칙 |
| `references/examples/` | **의도적으로 비어 있다.** 완결 예시가 형태를 고정시켰다 — 좋은 패턴은 `design-rules.md`로 옮겼다 |
| `skills/plan-report/references/spec-schema.md` | 설명형 스펙 규격 v2.5 (`groups` 추가) |
| `skills/plan-explore/references/explore-spec-schema.md` | 탐색형 스펙 규격 v1.0 (신설) |
| `references/template/explore-engine.js` `explore.css` `explore-parts.html` | 탐색형 부품·계산 엔진. `build-explore`에서만 읽는다 |

## 설계 원칙

1. **포맷 중립 스펙을 거친다.** 렌더러가 레이아웃을 스스로 판단하지 않는다.
2. **기준은 규칙이 아니라 파라미터다.** 총출고든 순출고든 강제하지 않는다.
   강제하는 것은 *기준을 명시했다는 사실*이다. 기준이 바뀌면 결론문도 다시 쓴다.
3. **데이터 소스는 어댑터 구조.** Metabase 전용이 아니다.
4. **참조 문서에는 조회로 알 수 없는 것만 쓴다.** 테이블 목록·컬럼명은 런타임 조회.
5. **quick과 report는 형식이 다를 뿐 품질 기준은 같다.**
6. **읽는 사람이 멈추지 않게 한다.** 모르는 용어, 열어볼 수 없는 묶음, 액션 없는 결론은 거기서 멈추게 만든다.
7. **질문을 먼저 합의한다.** 데이터가 질문을 정하게 두지 않는다.
8. **수신자 레벨이 액션의 필터다.** 수신자를 묻기만 하고 쓰지 않으면 실무 과제가 본부장 보고에 섞인다.
9. **발견에서 끝내지 않는다.** 결론 = 판단 + 요청. 액션 표는 그 전개일 뿐이다.
10. **위에서부터 좁혀 들어간다.** "다르다"는 말은 비교 틀이 먼저 서야 성립한다.
11. **같은 데이터를 다시 보여줄 때 순서를 바꾸지 않는다.** 강조만 옮긴다.

## 사내 사용 전제

- **Metabase는 사내망 전용**이다. 접근 불가 시 붙여넣기·엑셀 경로로 자동 전환된다.
- HTML 산출물이 사외로 나갈 가능성이 있으면 비밀번호 보호(StatiCrypt 등)를 안내한다.
- 산출물은 **라이트 전용**이다. 보고 문서는 보는 사람마다 색이 달라지면 안 된다.

## 미결 사항

지표 정의, 감시형 임계값, `action_title` 반려 강도 등 미확정 항목은
저장소 루트의 [`docs/open-issues.md`](../../docs/open-issues.md)에서 관리한다.
설계 근거는 [`docs/design-decisions.md`](../../docs/design-decisions.md) 참조.

## 변경 이력

- **v0.10.0** — **설명형/탐색형 계열 분리.** "필터로 볼 수 있게" 요청을 다섯 번째
  `report_type`으로 억지로 끼우지 않는다 — `references/product-lines.md`가 계열을
  가르고, 탐색형은 별도 파이프라인(`frame-explore` → `plan-explore` → `build-explore`,
  `/explore`)으로 돈다. `explore-model.md`(데이터 그레인·축·패널 카탈로그),
  `explore-spec-schema.md`(v1.0), `template/explore-engine.js`(공용 계산: 필터·rollup·
  wavg·상위N+기타·기간비교)·`explore.css`·`explore-parts.html` 신설.
  `assemble.py`가 `--css`/`--js`에 쉼표로 여러 파일을 받아 이어 붙이도록 확장.
  `report-helper`·`verify-report`에 계열 판정·탐색형 검수 분기 추가.
  설명형 쪽은: 자체검사를 실패마다 줄을 추가하던 방식에서 **"이것만 봐도 알 수 있나"·
  "제일 큰 얘기가 먼저 나오나"** 두 질문 × 다섯 크기(리포트 전체·그룹·exhibit·문단·용어)
  틀로 재구성(`plan-report/SKILL.md` §6). 결론이 두 갈래 이상 나뉠 때 exhibit을 묶는
  `groups` 스펙 필드 신설(v2.5, §5-1). `so_what`·모달 소개문에도 "주장 하나" 규칙 적용,
  glossary `desc`에 "쉬운 말이 먼저" 규칙 적용. 완결 예시(`examples/quick-minimal.json`)를
  삭제하고 그게 보여주던 좋은 패턴(목차·결론 먼저·헤더 위계)은 `design-rules.md`의
  기존 절로 명시적으로 연결. 감시형·추적형 전용 렌더 부품(`.freshness`·`.watchrow`·
  `.normalfold`·`.baseline`·`.projection`)을 실제로 구현 — 이전에는 진단형 부품만 있었다.
- **v0.8.0** — **수정이 오래 걸리던 원인을 고쳤다.** 라벨 하나 옮기려고 9만 자를 다시 쓰고 있었다.
  템플릿을 `template/{parts.html, base.css, base.js}`로 쪼개고 `scripts/assemble.py` 신설 —
  **CSS 18K와 JS 7K를 이제 읽지도 쓰지도 않는다.**
  수정을 결론/내용/표현 3층으로 가르고, 표현 수정은 본문만 `Edit`한다
  (판정 기준: 바꿀 것이 스펙에 대응하는 필드가 있는가).
  표현 수정 루프에서는 참조 문서를 다시 읽지 않고 서브에이전트도 다시 부르지 않는다.
  `lint_render.py --quick`(데스크톱 1회) 추가.
- **v0.7.0** — 커맨드 재편. `/daily` 제거하고 `/verify`(이미 있는 산출물 검수만)와
  `/refresh`(기존 리포트를 새 데이터로, 구성은 그대로) 신설.
  `daily-report.md`를 `watch-thresholds.md`로 일반화 — 영업일보 사례를 걷어내고
  **감시형 임계값을 어떻게 정하는가**(빈도에서 역산, 과거 사건 backtest, 못 정하면 null)만 남겼다.
- **v0.6.0** — `scripts/lint_render.py` 신설. Playwright로 실제 렌더해 잘린 글자·겹친 라벨·
  viewBox 밖 라벨·가로 스크롤·JS 에러·9px 미만 글자·잉크 비율을 잰다.
  데스크톱·모바일·**폰트 폴백** 세 번 돈다. `scripts/verify_docs_sync.py`(개발용) 신설 —
  같은 사실이 두 곳에 적힌 곳을 전부 대조한다.
- **v0.5.0** — 5단계 파이프라인. 산출물 유형 4종(`report_type`)과 유형별 필수 표.
  `verify-report` 스킬과 `report-verifier`·`report-data-prep` 에이전트.
  `scripts/check_html.py`. 스펙 2.3~2.4: `weight`·`encoding.claim`·`report_type`.
  인코딩 서열, 자리 크기=정보량, 숫자 소유권, 본문 표 12행.
  타입 6단계·라운드 4단계로 정리하고 **모든 치수를 4px의 배수로**.
  참조 문서의 완성 예시를 `references/examples/`로 분리하고 도메인 사례 제거.
- **v0.4.0** — *Storytelling with Data*(Knaflic, 2015) 전문을 반영.
  `references/storytelling.md` 신설(Big Idea·3막 구조·긴장·서사 순서·Bing-Bang-Bongo·
  수평/수직 논리·역스토리보딩). 스펙 2.2: `key_takeaway.ask`, `brief.tension`·`mechanism`·
  `narrative_order`·`three_minute_story`, exhibit `emphasis_steps`.
  차트 추가: `slopegraph` `small_multiples` `simple_text`, 스파게티 대응 3전략.
  규칙 추가: 게슈탈트 6원칙, 강조 10% 상한, 계열 4개 상한, 제로 베이스라인 근거,
  모든 차트·축에 제목, 범례 대신 직접 라벨, 색맹 근거, 중앙정렬·대각선 금지,
  "눈이 먼저 가는 곳" 테스트.
- **v0.3.0** — `frame-question` 스킬 신설(질문·가정·수신자 레벨·분석 축 합의).
  스펙 2.1: `brief`·`segments`, exhibit에 `views`(축 전환)·`drilldown`(계층)·`answers`.
  액션에서 `owner` 제거하고 `level` 추가 — 수신자보다 두 단계 아래면 "실무 후속 과제"로 분리.
  `action_title` 주장 하나 규칙. 인사이트→액션을 표로.
- **v0.2.0** — 시안 기준 디자인 전면 개편. 한국어 줄바꿈 버그 수정(`word-break:keep-all`).
  스펙 2.0(`key_takeaway`·`kpis`·`actions`·`glossary`·`calcs`·`group_detail`).
  마리메코·워터폴·한국 지도·히트맵 추가. 목차·모달·용어 툴팁 도입.
- **v0.1.0** — 스펙 레이어와 어댑터 구조 골격.
