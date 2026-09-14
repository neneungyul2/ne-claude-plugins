# 리포트 스펙 규격 (spec-schema)

포맷 중립 스펙. HTML 렌더러와 문서 렌더러가 동일하게 이 구조를 입력으로 받는다.

**현재 버전: 2.1**

- 2.0 — `key_takeaway` · `kpis` · `actions` · `glossary` · `calcs` · `group_detail` 추가
- 2.1 — `brief` · `segments` 추가. exhibit에 `views`(축 전환) · `drilldown`(계층) 추가.
  action에서 `owner` 제거하고 `level` 추가

---

## 1. 최상위 구조

```json
{
  "spec_version": "2.1",
  "mode": "report",
  "title": "쿠팡 채널 — 고객·시리즈·지역",
  "period_badge": "2026년 8월",
  "key_takeaway": {
    "text": "쿠팡 구매자의 절반이 40대 여성이고, 매출의 38%가 세 시리즈에 몰려 있다",
    "emphasis": ["절반", "세 시리즈"]
  },
  "audience": "본부장",
  "decision": "9월 채널별 배본 비중 조정 여부",
  "period": { "from": "2026-08-01", "to": "2026-08-31" },
  "basis": "쿠팡 리포트 (판매분석 GMV, 반품 차감)",
  "unit": "원/부",
  "brief": { },
  "segments": [ ],
  "dataset_card": { },
  "kpis": [ ],
  "summary": [ ],
  "exhibits": [ ],
  "actions": [ ],
  "glossary": [ ],
  "calcs": [ ],
  "footnote": { },
  "open_questions": [ ]
}
```

| 필드 | 필수 | 설명 |
|---|---|---|
| `spec_version` | O | 현재 `"2.1"` |
| `mode` | O | `quick` \| `report` |
| `title` | O | 문서 제목. 명사구 허용 (문서 이름이지 결론이 아님) |
| `period_badge` | 선택 | 제목 옆 배지. 예: `"2026년 8월"` |
| `key_takeaway` | O | **화면 최상단 강조 블록.** 아래 4장 |
| `audience` | report만 | 수신자 |
| `decision` | report만 | 이걸 보고 정해야 하는 것. 없으면 `"공유"` |
| `period` / `basis` / `unit` | O | 기간·집계 기준·기본 단위 |
| `brief` | **report 필수** | `frame-question`이 만든 `report-brief.json`을 그대로 넣는다. 아래 2장 |
| `segments` | 조건부 | 데이터에 없는 그룹을 쓰면 필수. 아래 10장 |
| `dataset_card` | O | `load-data` 산출 카드 그대로 |
| `kpis` | report만 | 2~4개. 아래 3장 |
| `summary` | report만 | 3줄 이내 요약 문장 배열 |
| `exhibits` | O | 아래 4장 |
| `actions` | **report 필수** | 인사이트·액션아이템. 아래 5장 |
| `glossary` | 조건부 필수 | 축약어·사내 용어가 등장하면 필수. 아래 6장 |
| `calcs` | 조건부 필수 | 별도 계산 로직이 있으면 필수. 아래 6장 |
| `footnote` | O | 공통 각주 |
| `open_questions` | 선택 | 확인 필요 항목 배열. 비어 있어도 키는 유지 |

---

## 2. brief — 무엇을 답하기로 했나

`frame-question`이 만든 브리프를 **그대로** 넣는다. 여기서 고치지 않는다.
질문이 바뀌어야 하면 `frame-question`으로 되돌아간다.

```json
"brief": {
  "why_now": "9월 채널별 배본 비중 조정 판단",
  "audience": "채널마케팅본부장",
  "audience_level": "head",
  "questions": [{ "id":"q1", "text":"쿠팡에서 사는 사람은 누구인가", "why":"…" }],
  "assumptions": [{ "text":"쿠팡 GMV 기준. 사내 SAP 출고와 합산하지 않는다", "confirmed":true }],
  "out_of_scope": ["유입경로 분석"]
}
```

`audience_level`은 **액션의 필터**다. `exec` \| `head` \| `lead` \| `staff`.
받아놓고 쓰지 않으면 이 필드를 넣는 의미가 없다. 5장 참조.

모든 exhibit은 `answers` 필드로 **어느 질문에 답하는지** 밝힌다.
어느 질문에도 안 붙는 exhibit은 빼거나, 질문을 추가할지 되묻는다.

`assumptions`는 산출물 하단(또는 "기준·한계" 섹션)에 그대로 표시된다.
`confirmed: false`인 가정은 `확인 필요`로 표시한다.

---

## 3. key_takeaway

화면에서 **가장 큰 글자**이고 가장 먼저 읽힌다. 서술형 결론 한 문장.

```json
"key_takeaway": {
  "text": "구매자의 절반이 40대 여성이고 매출의 38%가 세 시리즈에 몰려 있다 — 지역이 바꾸는 것은 상품이 아니라 학년이다",
  "emphasis": ["절반", "세 시리즈", "학년"]
}
```

- `text` — 명사구 금지. 제목만 읽고 "그래서 뭐?"가 남으면 반려
- `emphasis` — `text` 안에서 **형광펜으로 칠할 부분.** 부분 문자열이어야 하며 2~4개
  - 수치와 결론어를 고른다. 조사나 접속사를 칠하지 않는다
  - `text`에 없는 문자열이 들어가면 검사에서 걸린다

---

## 4. kpis

히어로 아래 숫자 카드. **2~4개.** 5개를 넘으면 그건 KPI가 아니라 표다.

```json
"kpis": [
  {
    "label": "8월 매출",
    "value": "546.6",
    "unit": "백만원",
    "delta": { "dir": "up", "text": "12.4%", "note": "전월 대비" },
    "calc_ref": "calc-gmv"
  }
]
```

| 필드 | 필수 | 설명 |
|---|---|---|
| `label` | O | 지표명 |
| `value` | O | 숫자만. 단위는 `unit`으로 뺀다 |
| `unit` | 선택 | 값 뒤에 작게 붙는다 |
| `delta` | 선택 | `dir`: `up` \| `dn` \| `flat`. **좋고 나쁨이 아니라 방향이다.** 색은 지표 성격에 맞춰 렌더러가 정한다 |
| `calc_ref` | 선택 | `calcs`의 `id`. 값 옆 `i` 아이콘 → 산식 모달 |
| `term_ref` | 선택 | `glossary`의 `id`. 라벨에 점선 밑줄 + 툴팁 |

비교값 없는 KPI는 의미가 약하다. `delta`를 넣을 수 없으면 그 지표가 KPI인지 다시 본다.

---

## 5. exhibit

```json
{
  "id": "ex5",
  "nav_label": "지역",
  "answers": ["q3"],
  "action_title": "지역이 바꾸는 것은 상품이 아니라 학년이다",
  "so_what": "지역 타깃 기획을 시도 단위로 잡으면 이 차이가 지워진다",
  "views": [
    {
      "id": "by-region",
      "label": "지역별",
      "read": "서울·세종은 고등 우위, 제주·전북은 초등 우위다",
      "question_type": "geo", "chart": "choropleth",
      "data": { "columns": ["시도","고등−초등"], "rows": [["서울", 10.8]] },
      "encoding": { "key": "시도", "value": "고등−초등", "level": "sido", "scale": "diverging" }
    },
    {
      "id": "by-grade",
      "label": "학교급별",
      "read": "중등은 어느 지역에서나 절반을 넘는다. 갈리는 것은 고등과 초등이다",
      "question_type": "composition", "chart": "stacked_bar_100",
      "data": { "columns": ["시도","초등","중등","고등"], "rows": [["서울", 5.7, 51.5, 16.5]] },
      "encoding": { "x": "시도", "y": ["초등","중등","고등"], "sort": "고등" }
    }
  ],
  "drilldown": {
    "label": "시군구",
    "by": "지역 유형",
    "columns": ["시군구","GMV(백만원)","초등","중등","고등","고등−초등"],
    "rows": {
      "학군지": [["서울 강남구", 10.2, 5.7, 51.5, 21.2, 15.5]],
      "신도시": [["경기 김포시", 9.1, 16.4, 56.8, 12.7, -3.7]]
    }
  },
  "footnote": { "source": "…", "period": "…", "unit": "…", "basis": "…" }
}
```

| 필드 | 필수 | 설명 |
|---|---|---|
| `id` | O | `ex1`, `ex2` … 목차·앵커에 쓰인다 |
| `nav_label` | report만 | 목차에 쓸 짧은 라벨. 6자 내외 |
| `answers` | report 필수 | **이 exhibit이 답하는 `brief.questions`의 id 배열.** 비어 있으면 왜 있는 exhibit인지 되묻는다 |
| `action_title` | O | **서술형 결론. 주장 하나.** 아래 참조 |
| `so_what` | O | 한 줄. 제목의 반복 금지 |
| `views` | O | **1개 이상.** 하나뿐이면 토글 없이 그냥 그린다. 2개 이상이면 축 전환 버튼이 생긴다 |
| `drilldown` | 선택 | 상위에서 클릭해 개별 단위로 내려가는 계층. 아래 참조 |
| `group_detail` | 조건부 필수 | 항목을 묶었으면 반드시 채운다. 아래 10장 |
| `basis`/`unit` | 선택 | 최상위와 다를 때만 |
| `footnote` | O | 4요소 전부 |

### action_title — 주장 하나

한 exhibit은 **한 가지만 말한다.** 서술형이기만 하면 통과가 아니다.

| 반려 | 왜 | 고친 것 |
|---|---|---|
| 구매자의 절반이 40대 여성이고, 40~50대가 87.4%다 — 사는 사람은 학부모다 | 주장 3개 | 사는 사람은 학생이 아니라 40대 학부모다 |
| 수도권이 54.9%지만 나머지 45%는 251개 시군구에 흩어져 있다 — 대구·광주가 인천·부산과 같은 체급이다 | 주장 2개 | 매출의 45%는 수도권 밖 251개 시군구에 흩어져 있다 |
| 채널별 현황 | 명사구 | (서술형 결론으로) |

판정법 — **"그래서?"를 한 번만 물을 수 있어야 한다.** 두 번 물을 게 남으면 두 개다.

금지

- `—`(em dash)로 두 주장 잇기
- 쉼표로 서로 다른 주장 잇기 (`~이고, ~이다`)
- 한 문장에 마침표 두 개

부가 수치는 `so_what`이나 각주로 내린다. 제목에 다 담으려 하지 않는다.

### views — 같은 질문, 다른 축

한 질문을 여러 각도에서 봐야 할 때 exhibit을 쪼개지 않고 `views`로 묶는다.
"지역별로 보다가 학교급별로 돌려 보는" 것은 **같은 질문의 다른 단면**이지 다른 질문이 아니다.

| 필드 | 필수 | 설명 |
|---|---|---|
| `id` | O | 토글 버튼과 연결 |
| `label` | O | 토글에 표시할 짧은 말 (`지역별`, `학교급별`) |
| `read` | 2개 이상일 때 필수 | **이 축에서 읽히는 것** 한 줄. 축마다 보이는 게 다르므로 각각 적는다 |
| `question_type` / `chart` / `data` / `encoding` | O | 4장 exhibit과 동일 |

규칙

- **3개를 넘기지 않는다.** 넘으면 질문이 둘로 갈린 것이다
- 모든 view는 **같은 데이터에서 나온 같은 사실**이어야 한다. 축만 바뀐다
- 축이 바뀌면 결론이 뒤집히는 경우가 있다. 그러면 그건 축 전환이 아니라 **별도 exhibit**이다
- 첫 번째 view가 기본값이다. `action_title`을 가장 잘 뒷받침하는 것을 앞에 둔다

### drilldown — 같은 축, 더 깊은 단위

세그먼트에서 패턴을 보고, 클릭해서 개별로 내려간다.
**시군구 251개를 처음부터 보여주지 않는다.** 유형으로 묶어 보고, 궁금하면 열게 한다.

```json
"drilldown": {
  "label": "시군구",
  "by": "지역 유형",
  "columns": ["시군구","GMV(백만원)","고등−초등"],
  "rows": { "학군지": [["서울 강남구", 10.2, 15.5]], "신도시": [["경기 김포시", 9.1, -3.7]] }
}
```

- `by`는 `segments`의 세그먼트 이름. 그 그룹 값이 곧 `rows`의 키다
- `rows`에는 **그 그룹의 전체**를 넣는다. 상위 몇 개로 줄이지 않는다
- 렌더러는 상위 차트의 각 그룹을 클릭 가능하게 만들고, 그 아래(또는 모달)에 표를 편다
- 2단계까지만. 3단계 이상은 대시보드가 아니라 데이터 탐색 도구다

---

## 6. actions — 인사이트와 액션

**report 모드에서 필수다.** exhibit만 늘어놓고 끝나는 리포트는 보고서가 아니라 자료집이다.

```json
"actions": [
  {
    "title": "상세페이지 제목을 학년·수준이 먼저 읽히게 바꾼다",
    "why": "구매자의 87%가 40~50대 학부모인데(ex1) 현재 제목은 학습자 기준이다",
    "evidence": ["ex1"],
    "priority": "high",
    "level": "head",
    "metric": "상세페이지 전환율",
    "horizon": "2주"
  }
]
```

| 필드 | 필수 | 설명 |
|---|---|---|
| `title` | O | **무엇을 할지 한 문장.** 동사로 끝낸다. "검토가 필요하다"는 액션이 아니다 |
| `why` | O | 왜 이 액션인지. **어느 exhibit의 어떤 수치가 근거인지 명시** |
| `evidence` | O | exhibit id 배열. 근거 없는 액션은 넣지 않는다 |
| `priority` | O | `high` \| `mid` \| `low` |
| `level` | **O** | 이 액션을 결정·실행하는 층. `exec` \| `head` \| `lead` \| `staff` |
| `metric` | 선택 | 효과를 확인할 지표. 없으면 `null` |
| `horizon` | 선택 | 언제까지 |

규칙

- **3~5개.** 넘으면 우선순위가 없는 것이다
- 데이터가 뒷받침하지 않는 제안은 쓰지 않는다. 대신 `open_questions`로 보낸다
- 액션이 하나도 안 나오면 그것도 결론이다 — `actions: []`로 두고 `open_questions`에 이유를 적는다
- **담당자를 적지 않는다.** 액션이 누구 일인지는 조직이 정한다. 리포트가 정하지 않는다

### level — 수신자 레벨과 맞춘다

`brief.audience_level`과 비교해 **본문에 넣을지 아래로 내릴지**를 가른다.

| 관계 | 처리 |
|---|---|
| 같은 레벨 | 본문 액션 |
| 한 단계 아래 | 본문 액션 (실행 주체가 바로 아래 층이면 자연스럽다) |
| **두 단계 이상 아래** | 본문에서 빼고 **"실무 후속 과제"** 블록으로 내린다 |
| 위 | 본문 액션. 단 "상위 결정 필요"로 표시 |

레벨 순서: `exec` > `head` > `lead` > `staff`

예 — 본부장(`head`) 보고에 `lineage 마스터의 영역 공백 136종을 채운다`(`staff`)가 들어가면
두 단계 아래다. 지우지 않고 "실무 후속 과제"로 내린다. 정보는 살리되 본문 흐름에서 뺀다.

렌더러는 두 블록을 시각적으로 구분해 표시한다.

---

## 7. glossary · calcs — 용어와 산식

읽는 사람이 모르는 말이 하나라도 있으면 리포트는 그 지점에서 멈춘다.

### glossary — 인라인 툴팁

```json
"glossary": [
  {
    "id": "gmv",
    "term": "GMV",
    "full": "Gross Merchandise Volume",
    "desc": "플랫폼에서 거래된 총 상품 금액. 여기서는 반품을 차감한 순액이다. 사내 SAP 출고 기준과 다르므로 합산하지 않는다."
  }
]
```

**다음이 본문에 등장하면 반드시 등록한다.**

- 영문 축약어 (GMV, SKU, MAU, DOS, ITR …)
- 사내에서만 쓰는 말 (초도배본, 순출고, 수불, SCM/BNK …)
- 일반어처럼 보이지만 정의가 갈리는 말 (실판매량, 반품률, 품절 …)

정의는 `references/metrics.md`에서 가져온다. **여기서 새로 만들지 않는다.**
metrics.md에 없고 확인도 안 됐으면 `desc`에 `확인 필요`를 적고 `open_questions`에도 올린다.

렌더러는 본문 첫 등장 지점에 점선 밑줄 + 호버 툴팁을 붙인다.

### calcs — 산식 모달

한 줄로 설명되지 않는 계산은 툴팁이 아니라 모달이다.

```json
"calcs": [
  {
    "id": "calc-gmv",
    "title": "매출 산출 방법",
    "scope": "이 화면의 모든 매출 수치",
    "formula": "매출 = 판매금액 − 반품금액",
    "steps": [
      "판매금액: 판매분석 리포트의 일자×SKU 합계",
      "반품금액: 같은 리포트의 음수 행 합계 (−3,950,060원)"
    ],
    "caveats": ["세트 상품은 구성품이 아니라 세트 단위로 집계된다"]
  }
]
```

판정 기준

| 설명 길이 | 처리 |
|---|---|
| 한 문장 | `glossary` 툴팁 |
| 산식 + 단계 2개 이상, 또는 예외·제외 조건이 있음 | `calcs` 모달 |

모달을 여는 자리는 `i` 아이콘이다. KPI는 `calc_ref`, 본문·각주는 인라인 `i`.

---

## 8. question_type → chart 매핑

`chart-rules.md`와 **동일한 표**를 유지한다. 한쪽만 고치지 않는다.

| question_type | 질문 | 기본 chart | 대안 |
|---|---|---|---|
| `trend` | 시간에 따라 어떻게 변했나 | `line` | `area` |
| `comparison` | 어느 쪽이 큰가 | `bar` | `dot_plot` |
| `ranking` | 순위가 어떻게 되나 | `bar_sorted` | `dot_plot` |
| `composition` | 무엇이 전체를 구성하나 | `stacked_bar` | `stacked_bar_100` |
| `composition_2d` | **두 축으로 동시에 쪼개면 어디에 몰려 있나** | `marimekko` | `heatmap` |
| `bridge` | **A에서 B로 가는 동안 무엇이 더하고 뺐나** | `waterfall` | `bar` |
| `distribution` | 어떻게 흩어져 있나 | `histogram` | `box_plot` |
| `correlation` | 두 값이 같이 움직이나 | `scatter` | — |
| `deviation` | 기준 대비 얼마나 벗어났나 | `diverging_bar` | `bullet` |
| `part_to_whole_time` | 구성이 시간에 따라 변했나 | `stacked_area` | `stacked_bar` |
| `flow` | 어디서 어디로 이동했나 | `sankey`(≤6) | `waterfall` |
| `geo` | **어느 지역인가** | `choropleth` | `bar_sorted` |
| `single_value` | 지금 값이 얼마인가 | `kpi` | — |
| `detail` | 정확한 숫자를 봐야 함 | `table` | — |

매핑에 없는 질문이면 억지로 끼우지 말고 사용자에게 무엇을 알고 싶은지 되묻는다.

---

## 9. encoding

| 키 | 설명 |
|---|---|
| `x` / `y` | 축 컬럼명 (`y`는 복수면 배열) |
| `series` | 계열 구분 컬럼. 없으면 `null` |
| `sort` | `asc` \| `desc` \| `none` \| 컬럼명 |
| `y_zero` | 막대는 항상 `true`. 선그래프에서만 `false` 허용 |
| `format` | `{ "y": "#,##0", "pct": "0.0%" }` |
| `limit` | 상위 N개만 표시. **나머지를 묶으면 `group_detail` 필수** |

### marimekko 전용

```json
"encoding": { "x": "채널", "width_by": "매출", "y": "시리즈", "value": "비중" }
```
가로폭 = 해당 열의 크기, 세로 분할 = 그 안의 구성. 열 5개·계열 6개를 넘기지 않는다.

### waterfall 전용

```json
"encoding": { "x": "구간", "y": "증감", "kind": "종류" }
```
`kind`는 `start` \| `delta` \| `end`. 시작·끝은 중립색, 증감만 방향색.

### choropleth 전용

```json
"encoding": { "key": "시도", "value": "매출", "level": "sido", "scale": "sequential", "link_table": true }
```
`level`: `sido` \| `sigungu`. `link_table: true`면 지도와 표가 서로 연동된다.
자세한 내용은 `references/korea-map.md`.

---

## 10. group_detail — 묶은 항목의 전체 데이터

**"기타", "나머지 N개", "상위 N 외"로 묶었으면 반드시 채운다.**
각주에 글로만 적는 것은 안 된다. 클릭해서 전체를 볼 수 있어야 한다.

```json
"group_detail": {
  "label": "나머지 8개 지역",
  "total": 65.2,
  "columns": ["지역", "매출(백만원)", "비중"],
  "rows": [["충북", 14.0, "2.6%"], ["충남", 13.9, "2.5%"]],
  "note": "시도 미상 1.8백만원 포함"
}
```

- `rows`는 **묶기 전 원자료 전체**다. 여기서 또 줄이지 않는다
- 렌더러는 해당 항목에 `i` 아이콘 또는 클릭 행을 만들고 모달로 띄운다
- 묶은 항목이 여러 개면 `group_detail`을 배열로 둔다

---

## 11. segments — 데이터에 없는 그룹

"학군지 vs 신도시", "핵심 시리즈 vs 롱테일"처럼 **데이터 컬럼에는 없지만 판단에 필요한 묶음**.
`frame-question`에서 합의한 것을 그대로 옮긴다.

```json
"segments": [
  {
    "name": "지역 유형",
    "groups": {
      "학군지": ["서울 강남구","서울 송파구","대구 수성구","경기 부천시"],
      "신도시": ["경기 김포시","광주 광산구","경남 김해시"],
      "기타": []
    },
    "basis": "고등 비중이 전국 평균(15.5%) +5%p 이상이면 학군지, 초등 비중이 전국 평균(11.5%) +3%p 이상이면 신도시",
    "confirmed": false,
    "drill_to": "시군구"
  }
]
```

| 필드 | 필수 | 설명 |
|---|---|---|
| `name` | O | 세그먼트 축의 이름 |
| `groups` | O | 그룹명 → 소속 값 배열 |
| `basis` | **O** | **분류 근거.** 이게 없으면 임의 분류다. 각주에 그대로 표시된다 |
| `confirmed` | O | 사내 합의된 기준이면 `true`, 이번에 제안하는 것이면 `false` |
| `drill_to` | 선택 | 드릴다운할 하위 단위 이름 |

규칙

- **이번 리포트 안에서만 쓰는 정의다.** 사내 표준으로 만들지 않는다
- `confirmed: false`면 렌더러가 각주에 **"이번 분석에서 정의한 구분"**으로 표시한다
- `basis`를 비워두지 않는다. 사용자가 목록만 주고 근거를 안 주면 `담당자 판단`이라고 적는다
- 어느 그룹에도 안 들어가는 값이 있으면 `기타`를 만든다. 조용히 빼지 않는다
- 그룹은 3~5개. 넘으면 묶는 의미가 없다

---

## 12. 금칙

렌더러에서도 다시 막지만, 스펙 단계에서 나오면 안 된다.

| 금칙 | 대신 |
|---|---|
| `pie`, `donut` | `bar_sorted`, `stacked_bar_100`, `marimekko` |
| 3D 효과 | 2D |
| 이중 Y축 | 차트 2개로 분리하거나 지수화(기준=100) |
| 잘린 축 (막대) | `y_zero: true` |
| 무지개 팔레트 | 단색 계조 + 강조 1색 |
| 묶은 항목에 `group_detail` 없음 | 전체 데이터를 채운다 |
| 축약어에 `glossary` 없음 | 용어를 등록한다 |
| `action_title`에 주장 2개 이상 | exhibit을 쪼개거나 부가 수치를 `so_what`으로 내린다 |
| 액션에 `owner` | 담당자는 적지 않는다. 조직이 정한다 |
| `segments`에 `basis` 없음 | 분류 근거를 적는다 |
| 수신자보다 두 단계 아래 액션이 본문에 | "실무 후속 과제"로 내린다 |
| exhibit에 `answers` 없음 | 어느 질문에 답하는지 밝히거나 뺀다 |

---

## 13. footnote (공통)

```json
{
  "source": "쿠팡 셀프서비스 리포트 CSV × Metabase core.item_lineage",
  "period": "2026-08-01 ~ 2026-08-31",
  "unit": "원/부",
  "basis": "쿠팡 리포트 기준 (판매분석 GMV, 반품 차감)",
  "extracted_at": "2026-09-14 09:30",
  "caveats": ["ISBN 미매칭 4.5%"]
}
```

exhibit별 각주가 있으면 공통 각주를 덮어쓴다.

---

## 14. open_questions

확인되지 않은 것을 **비워두고 표시**하기 위한 필드다. 추정으로 채우지 않는다.

```json
"open_questions": ["YES24 수치의 기준이 SCM인지 BNK인지 미확인"]
```

비어 있지 않으면 렌더러가 산출물 하단에 "확인 필요" 블록으로 표시한다.

---

## 15. 최소 예시 (quick)

quick 모드는 `brief` · `kpis` · `actions` · `nav_label` · `answers` · `audience` · `decision`을 생략할 수 있다.
**`key_takeaway`와 `glossary`는 quick에서도 필수다.**
exhibit의 `views`는 quick에서도 배열이다 — 하나만 넣으면 토글 없이 그려진다.

```json
{
  "spec_version": "2.1",
  "mode": "quick",
  "title": "월별 출고 추이",
  "key_takeaway": {
    "text": "6월 이후 3개월 연속 감소했으나 감소폭은 줄고 있다",
    "emphasis": ["3개월 연속 감소", "감소폭은 줄고"]
  },
  "period": { "from": "2026-01-01", "to": "2026-08-31" },
  "basis": "미확인",
  "unit": "부",
  "dataset_card": { "source": "출고집계.xlsx", "rows": 8, "basis": "미확인" },
  "exhibits": [{
    "id": "ex1",
    "action_title": "6월 이후 3개월 연속 감소했으나 감소폭은 줄고 있다",
    "so_what": "감소 추세가 꺾이는지 9월 데이터로 확인이 필요하다",
    "views": [{
      "id": "main", "label": "월별",
      "question_type": "trend", "chart": "line",
      "data": { "columns": ["월","출고량"], "rows": [["2026-01", 41200]] },
      "encoding": { "x": "월", "y": "출고량", "series": null, "sort": "asc", "y_zero": false }
    }],
    "footnote": { "source": "출고집계.xlsx", "period": "2026-01 ~ 2026-08", "unit": "부", "basis": "미확인" }
  }],
  "glossary": [{ "id":"chulgo", "term":"출고량", "desc":"SAP 매출수량 기준. 집계 기준(총출고/순출고) 미확인." }],
  "footnote": { "source": "출고집계.xlsx", "period": "2026-01-01 ~ 2026-08-31", "unit": "부", "basis": "미확인" },
  "open_questions": ["집계 기준(총출고/순출고) 미확인"]
}
```
