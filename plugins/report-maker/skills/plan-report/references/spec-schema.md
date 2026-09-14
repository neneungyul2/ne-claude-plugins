# 리포트 스펙 규격 (spec-schema)

포맷 중립 스펙. HTML 렌더러와 문서 렌더러가 동일하게 이 구조를 입력으로 받는다.

---

## 1. 최상위 구조

```json
{
  "spec_version": "1.0",
  "mode": "report",
  "title": "8월 채널별 출고 실적",
  "headline": "온라인 3사가 8월 출고 증가분의 82%를 차지했다",
  "audience": "본부장",
  "decision": "9월 채널별 배본 비중 조정 여부",
  "period": { "from": "2026-08-01", "to": "2026-08-31" },
  "basis": "순출고",
  "unit": "부",
  "dataset_card": { },
  "summary": [ ],
  "exhibits": [ ],
  "footnote": { },
  "open_questions": [ ]
}
```

| 필드 | 필수 | 설명 |
|---|---|---|
| `spec_version` | O | 현재 `"1.0"` |
| `mode` | O | `quick` \| `report` |
| `title` | O | 문서 제목. 명사구 허용 (문서 이름이지 결론이 아님) |
| `headline` | O | **서술형 결론 한 문장.** 화면 최상단 좌측 |
| `audience` | report만 | 수신자 |
| `decision` | report만 | 이걸 보고 정해야 하는 것. 없으면 `"공유"` |
| `period` | O | 데이터 기간 |
| `basis` | O | 집계 기준. `metrics.md`의 기준명 또는 `"미확인"` |
| `unit` | O | 기본 단위 |
| `dataset_card` | O | `load-data` 산출 카드 그대로 |
| `summary` | report만 | 3줄 이내 요약 문장 배열 |
| `exhibits` | O | 아래 참조 |
| `footnote` | O | 공통 각주 |
| `open_questions` | 선택 | 확인 필요 항목 배열. 비어 있어도 키는 유지 |

---

## 2. exhibit

```json
{
  "id": "ex1",
  "action_title": "온라인 3사가 8월 출고 증가분의 82%를 차지했다",
  "so_what": "9월 배본 비중을 온라인 쪽으로 재조정할 근거가 된다",
  "question_type": "composition",
  "chart": "stacked_bar",
  "basis": "순출고",
  "unit": "부",
  "data": {
    "columns": ["채널", "출고량"],
    "rows": [["A온라인", 12400], ["B온라인", 9800]]
  },
  "encoding": {
    "x": "채널",
    "y": "출고량",
    "series": null,
    "sort": "desc",
    "y_zero": true
  },
  "annotations": [
    { "type": "target_line", "value": 10000, "label": "월 목표" }
  ],
  "footnote": {
    "source": "SAP 출고 데이터 (Metabase card 412)",
    "period": "2026-08-01 ~ 2026-08-31",
    "unit": "부",
    "basis": "순출고 (총출고 − 반품)"
  },
  "notes": []
}
```

| 필드 | 필수 | 설명 |
|---|---|---|
| `id` | O | `ex1`, `ex2` ... |
| `action_title` | O | **서술형 결론.** 명사구 금지 |
| `so_what` | O | 한 줄. 제목의 반복 금지 |
| `question_type` | O | 아래 4장 |
| `chart` | O | 매핑표에서 선택 |
| `basis` | 선택 | 최상위와 다를 때만. 다르면 화면에 명시적으로 표시 |
| `unit` | 선택 | 최상위와 다를 때만 |
| `data` | O | `columns` + `rows`. 렌더러는 이 값만 그린다 |
| `encoding` | O | 아래 3장 |
| `annotations` | 선택 | 목표선·기준선·주석 |
| `footnote` | O | 4요소 전부 |
| `notes` | 선택 | 데이터 한계·주의 |

`table` 타입 exhibit은 `chart: "table"`, `encoding`에 `columns_order`, `highlight` 사용.
`kpi` 타입은 `chart: "kpi"`, `data.rows`에 `[라벨, 값, 전기대비]` 형태.

---

## 3. encoding

| 키 | 설명 |
|---|---|
| `x` | x축 컬럼명 |
| `y` | y축 컬럼명 (복수면 배열) |
| `series` | 계열 구분 컬럼. 없으면 `null` |
| `sort` | `asc` \| `desc` \| `none` \| 컬럼명 |
| `y_zero` | 막대는 항상 `true`. 선그래프에서만 `false` 허용 |
| `format` | `{ "y": "#,##0", "pct": "0.0%" }` |
| `limit` | 상위 N개만 표시. 나머지는 "기타"로 묶고 각주에 명시 |

---

## 4. question_type → chart 매핑

`chart-rules.md`와 **동일한 표**를 유지한다. 한쪽만 고치지 않는다.

| question_type | 질문 | 기본 chart | 대안 |
|---|---|---|---|
| `trend` | 시간에 따라 어떻게 변했나 | `line` | `area`(누적 의미 있을 때) |
| `comparison` | 어느 쪽이 큰가 | `bar` | `dot_plot`(항목 많을 때) |
| `ranking` | 순위가 어떻게 되나 | `bar_sorted` | `dot_plot` |
| `composition` | 무엇이 전체를 구성하나 | `stacked_bar` | `stacked_bar_100`(비중만 볼 때) |
| `distribution` | 어떻게 흩어져 있나 | `histogram` | `box_plot` |
| `correlation` | 두 값이 같이 움직이나 | `scatter` | — |
| `deviation` | 기준 대비 얼마나 벗어났나 | `diverging_bar` | `bullet` |
| `part_to_whole_time` | 구성이 시간에 따라 어떻게 변했나 | `stacked_area` | `stacked_bar`(구간 수 적을 때) |
| `flow` | 어디서 어디로 이동했나 | `waterfall` | `sankey`(항목 6개 이하) |
| `single_value` | 지금 값이 얼마인가 | `kpi` | — |
| `detail` | 정확한 숫자를 봐야 함 | `table` | — |

매핑에 없는 질문이면 억지로 끼우지 말고 사용자에게 무엇을 알고 싶은지 되묻는다.
— TODO: 파일럿에서 누락 유형 발견 시 이 표와 `chart-rules.md`를 함께 갱신

---

## 5. 금칙

렌더러에서도 다시 막지만, 스펙 단계에서 나오면 안 된다.

| 금칙 | 대신 |
|---|---|
| `pie`, `donut` | `bar_sorted` 또는 `stacked_bar_100` |
| 3D 효과 | 2D |
| 이중 Y축 | 차트 2개로 분리하거나 지수화(기준=100) |
| 잘린 축 (막대) | `y_zero: true` |
| 무지개 팔레트 | 단색 계조 + 강조 1색 |

---

## 6. footnote (공통)

```json
{
  "source": "SAP 출고 데이터 (Metabase card 412) / 8월 수불자료.xlsx",
  "period": "2026-08-01 ~ 2026-08-31",
  "unit": "부",
  "basis": "순출고 (총출고 − 반품)",
  "extracted_at": "2026-09-14 09:30",
  "caveats": ["A채널 8/15 데이터 누락"]
}
```

exhibit별 각주가 있으면 공통 각주를 덮어쓴다. 없으면 공통을 그대로 쓴다.

---

## 7. open_questions

확인되지 않은 것을 **비워두고 표시**하기 위한 필드다. 추정으로 채우지 않는다.

```json
"open_questions": [
  "YES24 수치의 기준이 SCM인지 BNK인지 미확인",
  "8월 반품 데이터가 9월 초 반영분을 포함하는지 확인 필요"
]
```

비어 있지 않으면 렌더러가 산출물 하단에 "확인 필요" 블록으로 표시한다.

---

## 8. 최소 예시 (quick)

```json
{
  "spec_version": "1.0",
  "mode": "quick",
  "title": "월별 출고 추이",
  "headline": "6월 이후 3개월 연속 감소했으나 감소폭은 줄고 있다",
  "period": { "from": "2026-01-01", "to": "2026-08-31" },
  "basis": "미확인",
  "unit": "부",
  "dataset_card": { "source": "출고집계.xlsx", "rows": 8, "basis": "미확인" },
  "exhibits": [
    {
      "id": "ex1",
      "action_title": "6월 이후 3개월 연속 감소했으나 감소폭은 줄고 있다",
      "so_what": "감소 추세가 꺾이는지 9월 데이터로 확인이 필요하다",
      "question_type": "trend",
      "chart": "line",
      "data": { "columns": ["월", "출고량"], "rows": [["2026-01", 41200]] },
      "encoding": { "x": "월", "y": "출고량", "series": null, "sort": "asc", "y_zero": false },
      "footnote": {
        "source": "출고집계.xlsx",
        "period": "2026-01 ~ 2026-08",
        "unit": "부",
        "basis": "미확인"
      }
    }
  ],
  "footnote": {
    "source": "출고집계.xlsx",
    "period": "2026-01-01 ~ 2026-08-31",
    "unit": "부",
    "basis": "미확인"
  },
  "open_questions": ["집계 기준(총출고/순출고) 미확인"]
}
```
