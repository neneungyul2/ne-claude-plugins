# 탐색 스펙 규격 (explore-spec-schema)

`spec-schema.md`(설명형)와 같은 자리지만 별도 파일이다. 필드 절반이 "해당 없음"이 되는
공유 스키마를 만들지 않는다 — 탐색형에 없는 개념(`action_title`, `key_takeaway`,
`weight`)은 이 스키마 자체에 없다.

버전: 1.1

## 0. 읽는 법

설명형 `spec-schema.md` §0과 같다 — 코드 조각은 스펙에 실제로 들어갈 필드만 보여준다.
주석은 스펙에 넣지 않는다.

## 1. 최상위 구조

```
{
  spec_version    "1.0"
  subject         string
  basis           string        // 집계 기준. 화면 상단·각주 양쪽에 노출
  axes            [ ]            // 2장
  sections        [ ]            // 4-1장. 선택 — 패널을 대분류로 묶어 목차를 만들 때
  grain           { }            // 3장
  panels          [ ]            // 4장
  glossary        [ ]            // 설명형과 동일 규칙
  calcs           [ ]            // 설명형과 동일 규칙
  footnote        { }            // 출처·기간·단위·집계기준 4요소. 설명형과 동일
  out_of_scope    [ ]
}
```

| 필드 | 필수 | 설명 |
|---|---|---|
| `spec_version` | 필수 | 이 문서의 버전 |
| `subject` | 필수 | 무엇에 대한 대시보드인가 |
| `basis` | 필수 | 집계 기준. `plan-report`의 `basis`와 같은 역할 |
| `axes` | 필수 | 독자가 바꿔볼 수 있는 것. 2장 |
| `grain` | 필수 | 원자료 단위. 3장 |
| `sections` | 선택 | 패널을 대분류(섹션)로 묶는다. 있으면 접이식 목차가 생긴다. 4-1장 |
| `panels` | 필수, 1개 이상 | 4장 |
| `glossary` / `calcs` | 조건부 | 설명형 규칙과 동일 — 축약어·사내용어가 있으면 필수 |
| `footnote` | 필수 | 4요소(출처·기간·단위·집계기준) |
| `out_of_scope` | 필수 | 이 화면이 답하지 않는 것 |

**이 스키마에 없는 필드**: `key_takeaway`, `action_title`, `weight`, `so_what`,
`emphasis`, `emphasis_steps`, `segments`(순환논증 위험이 있는 임의 그룹). 탐색형은
축이 이미 "데이터에 있는 구분"이라 `segments`가 필요한 경우가 드물다. 꼭 필요하면
`axes`의 한 항목으로 넣는다 — 별도 그룹 개념을 만들지 않는다.

## 2. axes

```
axes: [
  {
    id        "date"
    name      "기간"
    type      "date" | "category" | "geo" | "compare"
    control   "select" | "chips" | "range" | "map_click" | "toggle"
    values    [ ]          // type이 category/geo일 때. 데이터에서 뽑은 실제 값 목록
    default   any          // 처음 열 때 보이는 값
    hierarchy [ ]           // type이 geo일 때만. 상위→하위 순서
    groups    [ ]           // type이 compare이고 비교군을 둘 때. [{id, label, rule}]
  }
]
```

- `default`가 없는 축을 두지 않는다 — `plan-explore` 1장에서 확정한다
- `type: geo`는 `hierarchy`를 채운다. 시도 → 시군구처럼 한 번에 한 단계씩 내려가게
  한다. `korea-map.md`가 지역 코드 매핑을 담고 있으면 그걸 참조한다
- `type: compare`는 이전 구간(전기·전년) 비교면 `values`, **비교군** 비교면 `groups`를
  채운다. `rule`에는 그 비교군을 어떻게 묶는지 한 줄로 적는다(예: "같은 시도", "같은
  세그먼트"). 구성 방법 자체는 스펙마다 정한다 — 플러그인이 고정하지 않는다.
  `groups`는 **전부 한 화면에 함께 그린다** — 독자가 하나만 고르는 축이 아니다.
  `control`은 차이를 잴 기준 하나를 고르는 자리에만 쓴다
- `values`가 20개를 넘으면 `control`을 `select`가 아니라 `chips` 또는 검색 가능한
  형태로 정한다 (`explore-model.md` §2)

## 3. grain

```
grain: {
  dimensions   [ "date", "category", "channel" ]   // 원자료가 실제로 쪼개진 단위
  confirmed    true | false
  source_note  string       // grain이 axes 조합보다 굵을 때, 어떤 조합을 못 받치는지
}
```

- `dimensions`는 `axes`의 `id`와 이름을 맞춘다. 다르면 어느 축이 어느 차원에
  대응하는지 매핑을 `source_note`에 적는다
- `confirmed: false`로 남겨두지 않는다. `plan-explore` 1장에서 실측 후 `true`로 바꾼다

## 4. panels

```
panels: [
  {
    id            "p1"
    title         string        // 명사구 가능. "이것만 봐도 알 수 있나"만 통과하면 됨
    type          "kpi" | "trend" | "mix" | "map" | "table" | "tree_table"
    section       "s1"          // sections를 쓰면 필수. 이 패널이 속한 대분류
    hierarchy     [ ]           // type이 mix·tree_table이고 분류에 위계가 있을 때. 상위→하위 차원 id
    units         [ ]           // 비교 단위. 원래 단위(금액·부수)가 앞, 크기 맞춘 값·지수가 뒤
    guide         [ ]           // 사용법 문구. 화면에 펼치지 않고 ⓘ 뒤에 둔다
    notes         [ ]           // 기준·비고. 화면에 펼치지 않고 ⓘ 뒤에 둔다
    axes_used     [ "date", "category" ]
    chart         string        // question_type 대신 panel type이 차트를 좁힌다. chart-rules.md 참고
    encoding      { }           // 설명형과 동일 개념 — 값이 어느 채널에 실리는지
    etc_drilldown { top_n, basis, opens_to }   // type이 mix일 때만. 3장(plan-explore) 참고
    weight        "kpi_row" | "primary_view" | "detail"   // 서열 표시. 결론을 만드는 게 아니라 화면 위치 우선순위
  }
]
```

- `weight`가 설명형과 이름은 비슷해도 뜻이 다르다 — **결론의 무게가 아니라 화면에서
  먼저 봐야 할 순서**다. `primary`라는 값 이름을 재사용하지 않는다 (`kpi_row` /
  `primary_view` / `detail` 3단계)
- `hierarchy`가 있는 `mix`는 `etc_drilldown` 대신 계층 드릴다운을 쓴다 — 모든 항목을
  상위 분류 안의 비중으로 보여주고, 행을 누르면 한 단계 내려간다
- `tree_table`은 처음에 최상위 단계만 펼친다. 12행 상한은 펼치기 전 기준으로 본다
- `units`의 첫 값은 원래 단위(금액·부수 등)로 둔다. 지수·비율만 있는 패널은 그 앞에
  원래 단위로 비교하는 패널이 있는지 확인한다
- `guide`·`notes`는 문장 목록이다. 패널 위에 펼치지 않는다 (`explore-model.md` §7)
- `etc_drilldown`이 있는 패널은 `axes_used`가 바뀔 때 드릴다운 내용도 다시 계산돼야
  한다 — 렌더 시점에 고정 목록으로 굽지 않는다 (`build-explore`가 지킨다)

## 4-1. sections

```
sections: [
  { id  "s1"   label  "실적"   order  1 }
]
```

- 패널이 여러 주제로 갈릴 때만 둔다. 섹션이 하나뿐이거나 패널이 4개 이하면 두지 않는다
- 섹션 번호가 대분류, 섹션 안 패널 순서가 중분류 번호가 된다 (`1`, `1.1`, `1.2`)
- 목차는 접을 수 있고, 접어도 현재 위치가 보인다 — `build-explore`가 지킨다

## 5. glossary / calcs / footnote

설명형 `spec-schema.md` §7과 완전히 동일한 규칙을 쓴다 — desc는 쉬운 말 먼저,
한 문장을 넘는 계산은 calcs 모달, footnote는 출처·기간·단위·집계기준 4요소.
별도로 정의하지 않고 그대로 재사용한다.

## 6. out_of_scope

```
out_of_scope: [
  { text  reason }
]
```

`reason`에 그레인이 못 받치는 조합인지, 애초에 데이터가 없는 것인지를 구분해 적는다.
화면에도 같은 문구가 노출돼야 한다 — 조용히 빈 화면만 보여주지 않는다.

## 7. 변경 이력

- 1.1 (2026-09) — 선택 필드 추가: `sections`, `axes[].groups`(비교군), `panels[].section`·
  `hierarchy`·`units`·`guide`·`notes`, panel type `tree_table`. 1.0 스펙은 그대로 유효하다.

- 1.0 (2026-09) — 신설. `product-lines.md`의 탐색형 계열 분리에 따라
  `spec-schema.md`(설명형)와 별도로 만듦.
