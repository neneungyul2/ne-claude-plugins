# 리포트 스펙 규격 (spec-schema)

포맷 중립 스펙. HTML 렌더러와 문서 렌더러가 동일하게 이 구조를 입력으로 받는다.

**현재 버전: 2.0** — 1.0에서 `key_takeaway` · `kpis` · `actions` · `glossary` · `calcs` · `group_detail`이 추가됐다.

---

## 1. 최상위 구조

```json
{
  "spec_version": "2.0",
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
| `spec_version` | O | 현재 `"2.0"` |
| `mode` | O | `quick` \| `report` |
| `title` | O | 문서 제목. 명사구 허용 (문서 이름이지 결론이 아님) |
| `period_badge` | 선택 | 제목 옆 배지. 예: `"2026년 8월"` |
| `key_takeaway` | O | **화면 최상단 강조 블록.** 아래 2장 |
| `audience` | report만 | 수신자 |
| `decision` | report만 | 이걸 보고 정해야 하는 것. 없으면 `"공유"` |
| `period` / `basis` / `unit` | O | 기간·집계 기준·기본 단위 |
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

## 2. key_takeaway

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

## 3. kpis

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

## 4. exhibit

```json
{
  "id": "ex1",
  "nav_label": "고객 구성",
  "action_title": "구매자의 절반(51.3%)이 40대 여성이다 — 사는 사람은 학생이 아니라 학부모다",
  "so_what": "상품명·상세페이지를 학습자가 아니라 결정자인 학부모의 언어로 맞춰야 한다",
  "question_type": "composition",
  "chart": "stacked_bar",
  "basis": "쿠팡 리포트 기준",
  "unit": "%",
  "data": { "columns": ["연령", "여성", "남성"], "rows": [["40대", 51.3, 14.4]] },
  "encoding": { "x": "연령", "y": ["여성","남성"], "series": null, "sort": "desc", "y_zero": true },
  "series_colors": ["accent", "g3", "g5"],
  "annotations": [ { "type": "target_line", "value": 10000, "label": "월 목표" } ],
  "group_detail": null,
  "footnote": { "source": "…", "period": "…", "unit": "…", "basis": "…" },
  "notes": []
}
```

| 필드 | 필수 | 설명 |
|---|---|---|
| `id` | O | `ex1`, `ex2` … 목차·앵커에 쓰인다 |
| `nav_label` | report만 | 목차에 쓸 짧은 라벨. 6자 내외 |
| `action_title` | O | **서술형 결론.** 명사구 금지 |
| `so_what` | O | 한 줄. 제목의 반복 금지 |
| `question_type` | O | 아래 7장 |
| `chart` | O | 매핑표에서 선택 |
| `basis`/`unit` | 선택 | 최상위와 다를 때만 |
| `data` | O | `columns` + `rows`. 렌더러는 이 값만 그린다 |
| `encoding` | O | 아래 8장 |
| `series_colors` | 선택 | 토큰명 배열. `accent`, `g1`~`g5`, `violet`, `teal`, `amber`, `up`, `dn` |
| `annotations` | 선택 | 목표선·기준선·주석 |
| `group_detail` | 조건부 필수 | **항목을 묶었으면 반드시 채운다.** 아래 9장 |
| `footnote` | O | 4요소 전부 |

`table` 타입은 `chart: "table"`, `encoding`에 `columns_order`·`highlight`.
`kpi` 카드가 exhibit 안에 필요하면 `chart: "kpi_row"`.

---

## 5. actions — 인사이트와 액션

**report 모드에서 필수다.** exhibit만 늘어놓고 끝나는 리포트는 보고서가 아니라 자료집이다.

```json
"actions": [
  {
    "title": "상세페이지 제목을 학년·수준이 먼저 읽히게 바꾼다",
    "why": "구매자의 87%가 40~50대 학부모인데(ex1) 현재 제목은 학습자 기준이다",
    "evidence": ["ex1"],
    "priority": "high",
    "owner": "온라인유통파트",
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
| `owner` | 선택 | 모르면 `null`. 렌더러가 "담당 확인 필요"로 표시한다 |
| `metric` | 선택 | 효과를 확인할 지표. 없으면 `null` |
| `horizon` | 선택 | 언제까지 |

규칙

- **3~5개.** 넘으면 우선순위가 없는 것이다
- 데이터가 뒷받침하지 않는 제안은 쓰지 않는다. 대신 `open_questions`로 보낸다
- 액션이 하나도 안 나오면 그것도 결론이다 — `actions: []`로 두고 `open_questions`에 이유를 적는다

---

## 6. glossary · calcs — 용어와 산식

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

## 7. question_type → chart 매핑

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

## 8. encoding

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

## 9. group_detail — 묶은 항목의 전체 데이터

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

## 10. 금칙

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

---

## 11. footnote (공통)

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

## 12. open_questions

확인되지 않은 것을 **비워두고 표시**하기 위한 필드다. 추정으로 채우지 않는다.

```json
"open_questions": ["YES24 수치의 기준이 SCM인지 BNK인지 미확인"]
```

비어 있지 않으면 렌더러가 산출물 하단에 "확인 필요" 블록으로 표시한다.

---

## 13. 최소 예시 (quick)

quick 모드는 `kpis` · `actions` · `nav_label` · `audience` · `decision`을 생략할 수 있다.
**`key_takeaway`와 `glossary`는 quick에서도 필수다.**

```json
{
  "spec_version": "2.0",
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
    "question_type": "trend", "chart": "line",
    "data": { "columns": ["월","출고량"], "rows": [["2026-01", 41200]] },
    "encoding": { "x": "월", "y": "출고량", "series": null, "sort": "asc", "y_zero": false },
    "footnote": { "source": "출고집계.xlsx", "period": "2026-01 ~ 2026-08", "unit": "부", "basis": "미확인" }
  }],
  "glossary": [{ "id":"chulgo", "term":"출고량", "desc":"SAP 매출수량 기준. 집계 기준(총출고/순출고) 미확인." }],
  "footnote": { "source": "출고집계.xlsx", "period": "2026-01-01 ~ 2026-08-31", "unit": "부", "basis": "미확인" },
  "open_questions": ["집계 기준(총출고/순출고) 미확인"]
}
```
