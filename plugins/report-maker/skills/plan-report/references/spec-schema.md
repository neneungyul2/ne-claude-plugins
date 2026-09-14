# 리포트 스펙 규격 (spec-schema)

포맷 중립 스펙. HTML 렌더러와 문서 렌더러가 동일하게 이 구조를 입력으로 받는다.

**현재 버전: 2.4**

- 2.0 — `key_takeaway` · `kpis` · `actions` · `glossary` · `calcs` · `group_detail` 추가
- 2.1 — `brief` · `segments` 추가. exhibit에 `views`(축 전환) · `drilldown`(계층) 추가.
  action에서 `owner` 제거하고 `level` 추가
- 2.2 — `key_takeaway.ask` 추가. `brief`에 `tension` · `mechanism` · `narrative_order` ·
  `three_minute_story` 추가. exhibit에 `emphasis_steps` 추가
- 2.3 — exhibit에 `weight` 추가 (화면 비중). `encoding`에 `claim` 추가 (주장을 만드는 값).
  완결 예시를 `references/examples/`로 분리
- 2.4 — `report_type` 추가. **필수 여부가 유형에 따라 달라진다** (`references/report-types.md` §3)

---

## 0. 이 문서의 코드 조각을 읽는 법

아래 JSON 조각은 **설명 중인 필드의 형태만** 보여준다.

- **구성을 복사하지 않는다.** exhibit이 몇 개인지, 어떤 순서인지, 어떤 차트를 쓰는지는
  전부 `brief.questions`에서 나온다. 조각에 exhibit이 두 개 있다고 두 개를 만들지 않는다
- **값을 복사하지 않는다.** 값은 자리를 보여주려고 넣은 것이다
- **채워야 할 키의 목록이 아니다.** 필수 여부는 각 절의 표가 정한다.
  선택 필드를 "예시에 있으니까" 채우지 않는다

완결된 스펙 한 벌이 필요하면 `${CLAUDE_PLUGIN_ROOT}/references/examples/`를 본다.
거기 있는 것도 **하나의 사례일 뿐 형태가 아니다.**

---

## 1. 최상위 구조

키 목록이다. 값이 아니라 **어떤 키가 어느 층에 있는지**만 본다.

```
spec_version  mode  report_type  title  period_badge
key_takeaway { text  emphasis  ask }
audience  decision  period  basis  unit
brief { }  segments [ ]  dataset_card { }
kpis [ ]  exhibits [ ]  actions [ ]
glossary [ ]  calcs [ ]  footnote { }  open_questions [ ]
```

| 필드 | 필수 | 설명 |
|---|---|---|
| `spec_version` | O | 현재 `"2.4"` |
| `mode` | O | `quick` \| `report` |
| `report_type` | **report 필수** | `diagnostic` \| `choice` \| `watch` \| `track`. **아래 표의 필수 여부를 바꾼다** |
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

### report_type이 "필수"를 바꾼다

아래 표의 `필수` 표기는 **진단형 기준**이다. 유형에 따라 달라진다.
원본은 `${CLAUDE_PLUGIN_ROOT}/references/report-types.md` §3.

| 요소 | `diagnostic` | `choice` | `watch` | `track` |
|---|---|---|---|---|
| `key_takeaway.text` | 판단 문장 | 추천안 | 현재 상태 판정 | 도달 전망 |
| `key_takeaway.ask` | 필수 | 필수 | **이상일 때만** | 이탈 시 필수 |
| `brief.tension` | 필수 | 필수 | **—** | 필수 |
| `brief.three_minute_story` | 필수 | 필수 | **—** | **—** |
| `actions` | 3~5개 | 추천 1 + 대안 | **정상이면 0개** | 이탈 항목만 |
| `weight: primary` | exhibit 하나 | 옵션 표 | **KPI 행** | 시간축 차트 |
| exhibit 수 | 3~7 | 옵션 수 | **고정 슬롯** | 1~3 |
| `narrative_order` 기본 | `lead_with_ending` | `lead_with_ending` | `lead_with_ending` | **`chronological`** |

**`—`인 것을 억지로 채우지 않는다.** 감시형에 만들어 낸 긴장, 정상인데 지어낸 액션은
다음부터 그 칸을 아무도 안 읽게 만든다.

---

## 2. brief — 무엇을 답하기로 했나

`frame-question`이 만든 브리프를 **그대로** 넣는다. 여기서 고치지 않는다.
질문이 바뀌어야 하면 `frame-question`으로 되돌아간다.

```
brief {
  why_now  audience  audience_level  mechanism  tone  narrative_order
  three_minute_story
  tension { what_is  what_could_be }
  questions   [{ id  text  why }]
  assumptions [{ text  confirmed }]
  out_of_scope [ ]
}
```

| 필드 | 필수 | 값 | 쓰임 |
|---|---|---|---|
| `audience` | O | 자유 | **한 사람으로 특정한다.** "이해관계자"는 반려 |
| `audience_level` | O | `exec`\|`head`\|`lead`\|`staff` | **액션의 필터.** 5장 참조 |
| `mechanism` | O | `presentation`\|`document` | **밀도를 정한다.** 아래 참조 |
| `tone` | 선택 | `serious`\|`neutral`\|`celebratory` | 색·문장 톤 |
| `narrative_order` | O | `lead_with_ending`\|`chronological` | 아래 참조 |
| `three_minute_story` | report 필수 | 문단 하나 | 슬라이드 없이 말로 할 수 있는 이야기 |
| `tension` | report 필수 | `what_is` / `what_could_be` | **긴장이 없으면 이야기가 아니다** |

**`mechanism`** — 전달 매체가 밀도를 정한다.
`presentation`이면 화면당 정보를 줄이고 `emphasis_steps`를 슬라이드로 펼친다.
`document`(HTML 산출물의 기본값)이면 **"그래서 무엇인가"가 화면 안에 글자로 전부 있어야 한다.**
둘을 겸하려 하면 발표도 문서도 아닌 것이 된다.

**`narrative_order`** — `lead_with_ending`이 HTML 산출물의 기본값이다
(히어로에 결론과 요청이 먼저 온다). 신뢰를 쌓아야 하거나 독자가 과정을 보고 싶어하면
`chronological`로 두고 exhibit 순서를 문제 → 데이터 → 분석 → 판정 순으로 배치한다.

**`tension`** — "우리는 문제가 없는데요"라고 생각되면 다시 생각한다.
모든 것이 장밋빛인 이야기는 행동을 부르지 않는다. 자세한 것은 `references/storytelling.md`.

모든 exhibit은 `answers` 필드로 **어느 질문에 답하는지** 밝힌다.
어느 질문에도 안 붙는 exhibit은 빼거나, 질문을 추가할지 되묻는다.

`assumptions`는 산출물 하단(또는 "기준·한계" 섹션)에 그대로 표시된다.
`confirmed: false`인 가정은 `확인 필요`로 표시한다.

---

## 3. key_takeaway

화면에서 **가장 큰 글자**이고 가장 먼저 읽힌다.
**판단 한 문장 + 요청 한 줄 + 섹션 헤더 목록**, 세 부분이다.

```
key_takeaway { text  emphasis[]  ask  ask_level }
```

| 필드 | 필수 | 설명 |
|---|---|---|
| `text` | O | **판단.** 명사구 금지. 읽고 "그래서 뭐?"가 남으면 반려 |
| `emphasis` | O | `text` 안에서 형광펜으로 칠할 **부분 문자열** 2~4개 |
| `ask` | **report 필수** | **요청.** 독자가 무엇을 알거나 하기를 원하는가. `watch`는 이상일 때만 |
| `ask_level` | 선택 | 요청의 결정 레벨. `brief.audience_level`과 맞아야 한다 |

**Big Idea 3요소** — `text`+`ask`가 아래를 만족해야 한다.
1. 고유한 관점을 담을 것 (사실 나열이 아니라 판단)
2. 무엇이 걸려 있는지 전달할 것
3. 완전한 문장일 것

> **발견에서 멈추면 반려다** (`watch`·정상 상태는 예외 — "이상 없음"이 결론이다). "가격이 하락했다"는 관찰이고,
> "그러므로 이 범위로 출시하자"까지가 결론이다.
> 액션 표는 문서 맨 아래에 있다. 위에서 아래로 읽는 독자는 요청을 마지막에 만난다.
> `ask`는 그래서 히어로 안에 있어야 한다.

`emphasis` 주의 — 수치와 결론어를 고른다. 조사나 접속사를 칠하지 않는다.
`text`에 없는 문자열이 들어가면 검사에서 걸린다.

**히어로 요약 목록**은 스펙에 따로 두지 않는다. 렌더러가 **각 exhibit의 `action_title`을
순서대로** 나열한다. 이것이 수평 논리 검사이자 독자에게 주는 목차다.
그래서 `action_title`이 서술형이 아니면 히어로가 무너진다.

---

## 4. kpis

히어로 아래 숫자 카드. **2~4개.** 5개를 넘으면 그건 KPI가 아니라 표다.

```
kpis [{ label  value  unit  delta { dir  text  note }  calc_ref  term_ref }]
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

```
exhibit {
  id  nav_label  answers[]  action_title  so_what  weight
  views [{ id  label  read  question_type  chart  data{columns,rows}
           encoding{ x  y  series  claim  sort  y_zero } }]
  emphasis_steps [{ id  label  read  highlight[] }]
  drilldown { label  by  columns  rows{} }
  group_detail { }
  basis  unit
  footnote { source  period  unit  basis }
}
```

**exhibit이 몇 개인지, 어떤 순서인지, 어떤 차트를 쓰는지는 이 조각이 정하지 않는다.**
`brief.questions`에 답하는 데 필요한 만큼만 만든다. 질문 하나에 exhibit 하나가 기본이고,
한 질문을 여러 각도로 봐야 하면 `views`로 묶는다.

| 필드 | 필수 | 설명 |
|---|---|---|
| `id` | O | `ex1`, `ex2` … 목차·앵커에 쓰인다 |
| `nav_label` | report만 | 목차에 쓸 짧은 라벨. 6자 내외 |
| `answers` | report 필수 | **이 exhibit이 답하는 `brief.questions`의 id 배열.** 비어 있으면 왜 있는 exhibit인지 되묻는다 |
| `action_title` | O | **서술형 결론. 주장 하나.** 아래 참조 |
| `so_what` | O | 한 줄. 제목의 반복 금지 |
| `weight` | O | `primary` \| `supporting` \| `appendix`. **화면에서 차지할 비중.** 아래 참조 |
| `views` | O | **1개 이상.** 하나뿐이면 토글 없이 그냥 그린다. 2개 이상이면 축 전환 버튼이 생긴다 |
| `emphasis_steps` | 선택 | **같은 차트·같은 순서, 강조만 이동.** 아래 참조 |
| `drilldown` | 선택 | 상위에서 클릭해 개별 단위로 내려가는 계층. 아래 참조 |
| `group_detail` | 조건부 필수 | 항목을 묶었으면 반드시 채운다. 아래 10장 |
| `basis`/`unit` | 선택 | 최상위와 다를 때만 |
| `footnote` | O | 4요소 전부 |

### weight — 자리 크기는 서열의 선언이다

전부 같은 크기로 깔면 "전부 똑같이 중요하다"고 말한 것이고,
독자는 그것을 "아무것도 중요하지 않다"로 읽는다.

| 값 | 뜻 | 렌더러가 하는 일 |
|---|---|---|
| `primary` | 결론을 직접 만드는 exhibit. **정확히 하나** | 가장 큰 자리. 전체 폭. 강조 예산을 여기에 쓴다 |
| `supporting` | 결론을 뒷받침하거나 반례를 막는다 | 기본 크기 |
| `appendix` | 참고. 없어도 결론은 선다 | 접거나 문서 뒤로 내린다 |

- **`primary`가 둘이면 결론이 둘이다.** 질문으로 되돌아간다
- `primary`가 없으면 가장 큰 자리를 누가 갖는지 아무도 정하지 않은 것이다
- `appendix`가 절반을 넘으면 그건 리포트가 아니라 자료 모음이다

**빈 공간이 많은 차트는 `primary`가 될 수 없다.** 데이터가 플롯 영역의 절반도 안 채우면
가장 많은 주의를 받는 자리에서 가장 적게 돌려주는 것이다. 축 범위를 분포에 맞추거나
`supporting`으로 내린다.

### encoding.claim — 주장을 만드는 값

`action_title`이 하는 주장을 만드는 **필드 이름 하나**를 적는다.

| 상태 | 판정 |
|---|---|
| `claim`이 `x` 또는 `y`와 같다 | 통과 |
| `claim`이 `series`에만 있다 | 경고. 색으로는 크기를 못 읽는다 |
| `claim`이 값 라벨·툴팁에만 있다 | **반려.** 차트나 축을 바꾼다 |
| `claim`을 못 적겠다 | `action_title`이 이 차트에서 안 나온다. 질문으로 되돌아간다 |

막대 길이가 *건수*인데 제목이 *건당 효율*을 말하는 것이 전형적인 실패다.
건당 효율이 주장이면 건당 효율이 막대 길이여야 한다.
`scripts/check_html.py --spec` 이 이 항목을 기계적으로 본다.
서열의 근거는 `references/chart-rules.md` §1-1.

### action_title — 주장 하나

한 exhibit은 **한 가지만 말한다.** 서술형이기만 하면 통과가 아니다.

| 반려 | 왜 | 고친 것 |
|---|---|---|
| A가 절반이고 A와 B를 합치면 87%다 — 따라서 주 고객층은 X다 | 주장 3개 | 주 고객층은 우리가 가정한 Y가 아니라 X다 |
| 상위 지역이 55%지만 나머지는 흩어져 있다 — 중위 지역이 상위권과 같은 체급이다 | 주장 2개 | 매출의 45%는 상위 지역 밖에 흩어져 있다 |
| 채널별 현황 | 명사구 | (서술형 결론으로) |

위 칸의 A·B·X는 자리표시자다. 실제 action_title은 **데이터에서 나온 말**로 쓴다.

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

### emphasis_steps — 같은 차트, 강조만 이동

한 차트로 여러 가지를 순서대로 짚어야 할 때 쓴다. **데이터·순서·축·색 체계는 전부 그대로 두고
무엇을 강조할지만 바꾼다.**

```
emphasis_steps [
  { id label read highlight[] }          # highlight 빈 배열 = 전체를 먼저 보여주는 단계
  { id label read highlight[ {series} {key} ] }
]
```

단계를 몇 개 둘지는 이 조각이 정하지 않는다. **짚어야 할 것이 몇 개인지가 정한다.**
짚을 것이 하나뿐이면 `emphasis_steps`를 쓰지 않는다.

| 필드 | 필수 | 설명 |
|---|---|---|
| `id` | O | 단계 버튼과 연결 |
| `label` | O | 버튼에 쓸 짧은 말 |
| `read` | O | **이 단계에서 읽히는 것** 한 줄 |
| `highlight` | O | 강조할 대상. `series`(계열명) / `key`(범주값) / `index`(위치) 중 하나 이상. 빈 배열 = 강조 없음 |

**규칙**

- **정렬을 바꾸지 않는다.** 단계마다 정렬을 최적화하고 싶어지지만, 독자를 데이터에 익숙하게
  만들어 놓고 재배열하는 것은 불필요한 인지 세금이다
- 강조 대상은 **전체의 10% 이하**. 절반을 강조하면 강조가 아니다
- 첫 단계는 보통 `highlight: []` — 전체를 먼저 보여주고 읽는 법을 알린다
- 4단계를 넘지 않는다. 넘으면 이야기가 둘로 갈린 것이다
- `read` 문장의 강조색과 차트의 강조색을 **같은 색**으로 묶는다
- `brief.mechanism`이 `presentation`이면 각 단계가 슬라이드 한 장이 된다.
  `document`면 단계 버튼으로 렌더링하고, **마지막 단계를 기본값으로 하되
  모든 단계의 `read`를 화면에 함께 남긴다** (발표자가 없으므로)

**`views`와 혼동하지 않는다.**

| | 바뀌는 것 | 예 |
|---|---|---|
| `views` | 축이나 단위 | 구성비(%) ↔ 절대금액 / 분류 A별 ↔ 분류 B별 |
| `emphasis_steps` | 강조만 | 같은 차트에서 ①전체 → ②특정 계열 강조 |

### drilldown — 같은 축, 더 깊은 단위

세그먼트에서 패턴을 보고, 클릭해서 개별로 내려간다.
**개별 항목이 수백 개면 처음부터 보여주지 않는다.** 유형으로 묶어 보고, 궁금하면 열게 한다.

```
drilldown { label  by  columns[]  rows{ 그룹명: [[...]] } }
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

```
glossary [ { id term full desc } ]
```

`desc`는 뜻만 적고 끝내지 않는다. **그 말이 오해받는 지점이 있으면 그것까지 적는다.**
예: 외부 플랫폼 기준 금액 지표라면 "사내 출고 기준과 다르므로 합산하지 않는다"를 `desc`에 넣는다.

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
| `trend_many` | **계열이 많은데 각각의 추이를 봐야 하나** | `small_multiples` | `line`(강조 1개) |
| `change_2point` | **두 시점 사이에 무엇이 오르고 내렸나** | `slopegraph` | `dot_plot`, `diverging_bar` |
| `comparison` | 어느 쪽이 큰가 | `bar` | `dot_plot` |
| `ranking` | 순위가 어떻게 되나 | `bar_sorted` | `dot_plot` |
| `composition` | 무엇이 전체를 구성하나 | `stacked_bar` | `stacked_bar_100` |
| `headline_number` | **전할 숫자가 한두 개다** | `simple_text` | `kpi` |
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

데이터 컬럼에는 없지만 판단에 필요한 묶음.
`frame-question`에서 합의한 것을 그대로 옮긴다.

```
segments [{ name  groups{ 그룹명: [소속 값들] }  basis  confirmed  drill_to }]
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

### 분류 근거가 결과에서 나오면 순환논증이다

가장 자주 나오는 실패다. **결론을 만들 때 쓸 지표로 그룹을 나누면**,
그 그룹이 그 지표에서 차이를 보이는 것은 당연하고 아무것도 증명하지 않는다.

| 위험한 `basis` | 왜 |
|---|---|
| "지표 X가 평균보다 높은 항목을 A 그룹으로" 후 "A 그룹은 X가 높다"고 서술 | 동어반복 |
| 상위 N개를 뽑아 이름 붙인 뒤 그 이름의 특성이라고 설명 | 선택 편향. 이름의 원래 정의에 해당하는 항목이 표본에 없을 수 있다 |
| 규모가 큰 항목만 남은 표본에서 그룹을 만들고 규모를 통제하지 않음 | 교란 |

분류 축을 쓰려면 **분류 근거가 결과 변수와 독립**이어야 한다.
`basis`는 결과를 보기 전에 정해진 외부 정의(제도·지리·조직·제품 계보 등)에서 나와야 하고,
그렇지 않으면 그룹에 이름을 붙이지 말고 **관측된 사실 그대로**("지표 X 상위/하위") 서술한다.

`confirmed: false`이면서 `basis`가 결과 변수에서 나왔으면 **스펙을 되돌린다.**

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
| **`key_takeaway.ask` 없음 (report)** | 발견에서 끝내지 않는다. 요청을 적는다 |
| **`brief.tension` 없음 (report)** | 긴장이 없으면 이야기가 아니다 |
| **선·누적 계열 5개 초과** | 단기기억 한계. 묶거나 `small_multiples` |
| **`emphasis_steps`에서 정렬이 바뀜** | 순서를 고정한다. 강조만 옮긴다 |
| **차트·축에 제목 없음** | 모든 차트에 제목, 모든 축에 축 제목 |
| **축 눈금과 값 라벨을 둘 다 표시** | 하나만 고른다 (추세면 축, 수치면 직접 라벨) |

---

## 12-1. 스토리 자체검사 — 스펙을 넘기기 전에 돈다

렌더링 전에 반드시 통과시킨다. 자세한 것은 `references/storytelling.md` 8장.

**① 수평 논리** — `key_takeaway.text` → 각 exhibit의 `action_title`을 **순서대로만 읽는다.**
그것이 하나의 이야기가 되는가?
- 제목만으로 결론이 안 나온다 → 서술형이 아니다
- 순서가 뒤죽박죽이다 → exhibit 순서가 데이터 순서로 돼 있다
- 중간이 비어 논리가 점프한다 → exhibit이 빠졌다
- 마지막이 요청으로 닿지 않는다 → `ask`와 액션이 연결되지 않았다

**② 수직 논리** — 각 exhibit에서 `action_title` ↔ 차트 ↔ `so_what` ↔ `footnote`가
같은 것을 말하는가? 무관한 정보가 섞여 있지 않은가?

**③ cascading** — 뒤 exhibit의 비교 표현("더 낮다", "다르다")이 앞 exhibit에서
비교 틀을 세운 뒤에 나오는가? 세부 수치가 `key_takeaway`에 먼저 나와 있지 않은가?

**④ 역스토리보딩** — 각 exhibit의 요점을 한 줄씩 적어 목록으로 만든다.
그 목록이 `brief.questions`와 대응하는가?

---

## 13. footnote (공통)

```
footnote { source period unit basis extracted_at caveats[] }
```

| 필드 | 무엇을 적나 |
|---|---|
| `source` | 원천을 **결합까지 포함해** 적는다. 두 소스를 이어 붙였으면 둘 다 적는다 |
| `basis` | 어느 기준의 숫자인가. 같은 이름의 지표라도 기준이 다르면 다른 숫자다 |
| `caveats` | 매칭 실패율·제외분·추정 구간 등 **숫자를 깎는 것**을 적는다. 없으면 빈 배열 |

exhibit별 각주가 있으면 공통 각주를 덮어쓴다.

---

## 14. open_questions

확인되지 않은 것을 **비워두고 표시**하기 위한 필드다. 추정으로 채우지 않는다.

```json
"open_questions": ["YES24 수치의 기준이 SCM인지 BNK인지 미확인"]
```

비어 있지 않으면 렌더러가 산출물 하단에 "확인 필요" 블록으로 표시한다.

---

## 15. quick 모드에서 생략할 수 있는 것

quick 모드는 `brief` · `kpis` · `actions` · `nav_label` · `answers` · `audience` · `decision`을 생략할 수 있다.

**quick에서도 생략할 수 없는 것**

- `key_takeaway` — 결론 없는 산출물은 모드와 무관하게 만들지 않는다
- `glossary` — 읽는 사람이 모르는 말이 있으면 리포트는 그 지점에서 멈춘다
- `footnote`의 `source` · `basis` — 기준을 못 밝힌 숫자는 쓰지 않는다
- `open_questions` — 확인 안 된 것은 추정으로 채우지 않고 여기 올린다

exhibit의 `views`는 quick에서도 배열이다. 하나만 넣으면 토글 없이 그려진다.

형식이 맞는 스펙 한 벌을 대조해봐야 하면
`${CLAUDE_PLUGIN_ROOT}/references/examples/quick-minimal.json`을 본다.
**거기서 가져올 수 있는 것은 키의 중첩 위치와 자료형뿐이다** — exhibit 개수·순서·차트·흐름은 아니다.
자세한 것은 같은 폴더의 `README.md`.
