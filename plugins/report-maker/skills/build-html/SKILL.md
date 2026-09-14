---
name: build-html
description: 확정된 리포트 스펙을 HTML 단일 파일로 렌더링한다. 외부 의존 없이 인라인 SVG로 차트를 그리고, 디자인 토큰·목차·모달·용어 툴팁을 강제한다. report-maker 워크플로의 4단계(HTML 경로)로, plan-report가 만든 스펙을 입력으로 받는다.
---

# HTML 렌더링 (build-html)

`report-spec.json`을 **HTML 파일 하나**로 만든다. 스펙에 없는 결론을 새로 만들지 않는다.

## 0. 먼저 읽을 것

- `${CLAUDE_PLUGIN_ROOT}/references/design-rules.md`
- `${CLAUDE_PLUGIN_ROOT}/references/html-template.html` — 토큰·컴포넌트·스크립트 전부 여기 있다
- 지역 데이터가 있으면 `${CLAUDE_PLUGIN_ROOT}/references/korea-map.md`

**템플릿의 CSS와 스크립트는 그대로 가져다 쓴다.** 색이나 크기를 즉흥적으로 바꾸지 않는다.

## 1. 원칙

- **단일 파일.** 외부 CSS·JS·폰트·이미지를 불러오지 않는다. 사내망 밖·오프라인에서도 열려야 한다
- **차트는 인라인 SVG.** 라이브러리를 CDN에서 불러오지 않는다. 스펙의 `data.rows`로 좌표를 계산해 직접 생성한다
- **디자인 토큰만 사용.** 템플릿의 CSS 변수 밖 색을 쓰지 않는다
- **한국어 줄바꿈 CSS를 반드시 유지한다** (`word-break:keep-all; overflow-wrap:anywhere`).
  이걸 빼면 단어 중간이 잘린다. 템플릿에서 지우지 말 것
- 반응형. 400px에서 가로 스크롤이 없어야 한다. 표와 넓은 차트만 `overflow-x:auto` 컨테이너 안에
- 라이트 전용. 다크모드 분기를 넣지 않는다

## 2. 렌더 순서

```
헤더(스티키)  제목 · 기준 배지 · (탭)
목차          exhibit 3개 이상이면. 1420px 이상에서만
히어로        key_takeaway + emphasis 형광펜 + summary
KPI           kpis 2~4개
① exhibit     shead(번호 배지 + action_title) → so_what → [축 토글] → 차트 → [드릴다운] → 각주
② exhibit …
인사이트 → 액션  발견·근거·제안·우선순위 표 + 실무 후속 과제
가정           brief.assumptions
확인 필요      open_questions
각주          footnote
모달           group_detail · calcs
```

- exhibit은 스펙 배열 순서 그대로. 재배치하지 않는다
- 섹션 번호와 목차 번호와 `id`를 일치시킨다 (`ex1` ↔ `<i>1</i>` ↔ `#ex1`)

### key_takeaway 강조

`emphasis` 배열의 각 문자열을 `text` 안에서 찾아 `<b>`로 감싼다.

- 문자열이 `text`에 없으면 감싸지 않고 **사용자에게 알린다**
- 겹치는 구간이 있으면 긴 쪽을 우선한다
- 전체 길이의 절반을 넘게 칠하지 않는다. 넘으면 `emphasis`를 줄여 달라고 되돌린다

## 3. 차트 생성

| chart | 구현 요점 |
|---|---|
| `bar`, `bar_sorted` | y축 0 시작 필수. 항목 8개 초과면 가로 막대 |
| `line` | 계열 4개 이하. 끝점에 계열명 직접 라벨 |
| `stacked_bar`, `stacked_bar_100` | 계열 5개 이하. 범례 순서 = 스택 순서 |
| `marimekko` | **가로폭 = 열 크기, 세로 = 구성.** 열 5개·계열 6개 이하. 열 라벨 아래 절대값 표기 |
| `waterfall` | 시작·끝은 중립색(`--g2`), 증감만 방향색. 막대 사이 연결선. 값에 부호 |
| `choropleth` | `korea-map.md` 참조. 지도 + 정렬된 표를 `maprow`로 나란히. `data-key` 양쪽 일치 |
| `heatmap` | 단색 계조. 셀에 값 직접 표기. 행·열 값 순 정렬 |
| `diverging_bar` | 0 기준선 굵게, 좌우 스케일 동일 |
| `dot_plot` | 항목 많을 때 막대 대신 |
| `scatter` | 축 라벨에 단위 필수 |
| `kpi_row` | 값 + 라벨 + 비교값. 한 줄 4개까지 |
| `table` | 우측 정렬 수치, tabular-nums, 강조행만 배경색 |

금칙(`pie`, `donut`, 3D, 이중 Y축, 잘린 축, 무지개)이 스펙에 있으면 **렌더링하지 않고** 대안으로 바꾼 뒤 알린다.

### SVG 라벨

- 라벨이 길면 CSS로 못 접는다. **`<tspan>`으로 직접 줄을 나눈다**
- 겹칠 것 같으면 라벨을 빼고 툴팁으로 보낸다. 겹친 채 두지 않는다
- `data-tip="제목|항목 값|항목 값"` 형식. 템플릿 스크립트가 파싱한다

## 3-1. views — 축 전환

`views`가 **2개 이상**이면 토글을 만든다. 1개면 토글 없이 그냥 그린다.

- `.seg` 버튼 그룹을 차트 위에 둔다. 첫 view가 기본값(`aria-pressed="true"`)
- 각 view를 `.view[data-view="<id>"]`로 감싸고 선택되지 않은 것은 `hidden`
- **각 view의 `read`를 차트 바로 위에 표시한다.** 축이 바뀌면 읽히는 것도 바뀐다
- 토글해도 `action_title`과 `so_what`은 그대로다. 결론은 하나다
- 스크립트는 템플릿에 있다. 버튼의 `data-view`와 패널의 `data-view`만 맞추면 된다

3개를 넘으면 렌더링 전에 사용자에게 알린다. 질문이 둘로 갈린 것이다.

## 3-2. drilldown — 계층

`drilldown`이 있으면 상위 차트의 각 그룹을 열 수 있게 만든다.

- 차트 아래에 그룹별 `.drillbtn` 버튼을 둔다 (`학군지 시군구 보기`)
- 패널은 `.drill[data-drill="<id>"]`. 한 번에 하나만 열린다 (템플릿 스크립트가 처리)
- 패널 상단에 **분류 근거**를 한 줄로 적는다 (`segments[].basis`)
- `rows`에 들어 있는 **그 그룹 전체**를 표로 넣는다. 상위 몇 개로 줄이지 않는다
- 각주에도 세그먼트 정의를 남긴다. `confirmed: false`면 **"이번 분석에서 정의한 구분"**으로 표시

## 4. 묶은 항목 → 모달

스펙에 `group_detail`이 있으면 **반드시** 모달을 만든다.

1. 해당 항목(막대·행·지도 영역)에 클릭 표시를 붙인다 — 표는 `tr.clickable`, 그 외는 `i` 아이콘
2. `data-modal="<id>"`로 모달과 연결한다
3. 모달 본문에 `group_detail.rows` **전체**를 표로 넣는다. 여기서 또 줄이지 않는다
4. 모달 상단에 합계와 전체 대비 비중
5. 각주에도 무엇이 묶였는지 한 줄 — 인쇄·문서 변환 환경을 위해

`group_detail`이 비어 있는데 "기타"·"나머지 N개" 항목이 있으면 **렌더링을 멈추고** 스펙을 되돌려 보낸다.

## 5. 용어와 산식

- `glossary`의 각 항목을 스크립트 상단 `GLOSSARY` 객체에 넣는다
- 본문·라벨·각주에서 **첫 등장 지점**에 `<abbr class="term" data-term="id">용어</abbr>`
  - 같은 용어를 매번 감싸지 않는다. 처음 한 번이면 된다
- `calcs`의 각 항목을 모달로 만들고, 해당 수치 옆에 `i` 아이콘을 붙인다
  - KPI는 `calc_ref`로 연결
  - 본문·각주는 인라인 `<button class="infoi" data-modal="calc-id">i</button>`
- 스펙에 축약어가 등장하는데 `glossary`에 없으면 렌더링 전에 사용자에게 알린다

## 6. 네비게이션

- **목차** — exhibit 3개 이상이면 생성. `nav_label`을 쓴다. `action_title`을 그대로 넣지 않는다
- **스크롤 연동** — IntersectionObserver로 현재 섹션을 `.on`으로 표시 (템플릿에 구현돼 있다)
- **탭** — exhibit 8개 초과이거나 성격이 갈릴 때만. 아니면 템플릿의 `<nav class="tabs">`를 지운다
- 앵커(`#ex1`)로 직접 접근할 수 있어야 한다

## 7. 인사이트 → 액션

`.advice` 블록 안에 **표**로 렌더링한다. 카드 목록보다 표가 낫다 —
근거가 열로 분리되어야 검증할 수 있다.

| 열 | 내용 |
|---|---|
| 발견 | 액션의 근거가 된 사실. 짧게 |
| 근거 | 수치 + 출처 exhibit 번호 (`①`) |
| 제안 액션 | `title` |
| 우선순위 | `priority` 태그 |

- **담당자 열을 만들지 않는다.** `owner` 필드는 스펙에서 제거됐다
- 리드 문장에 "근거는 데이터, 액션은 제안이다"를 명시한다
- `brief.audience_level`보다 **두 단계 이상 아래**인 액션은 본문 표에서 빼고
  `.subacts` 블록("실무 후속 과제")의 별도 표로 내린다. **지우지 않는다**
- `actions`가 비어 있으면 블록을 만들되 **"현재 데이터로는 실행 가능한 액션이 도출되지 않았다"**와
  그 이유를 적는다. 블록 자체를 지우지 않는다

## 7-1. 가정 블록

`brief.assumptions`를 `.assume` 블록으로 렌더링한다. 액션 아래, 확인 필요 위.

- `confirmed: false`인 가정에는 `확인 필요` 배지를 붙인다
- `segments`의 `confirmed: false`도 여기에 한 줄 추가한다
  (`지역 유형 구분은 이번 분석에서 정의한 것이다`)
- 가정이 없으면 블록을 만들지 않는다. quick 모드는 대개 없다

## 8. 사외 반출 대비

산출물이 사외로 나갈 가능성이 있으면 확인하고, 원하면 비밀번호 보호를 안내한다.

- 권장: [StatiCrypt](https://github.com/robinmoisson/staticrypt)
- 자동으로 적용하지 않는다. 비밀번호를 임의로 정하지 않는다

## 9. 파일명과 전달

- `<주제>_<기간>_<기준>.html` (예: `쿠팡채널_2026-08_쿠팡리포트기준.html`)
- 작업 폴더에 저장하고 사용자에게 전달한다
- 다시 열어볼 대시보드·트래커면 링크로 남길 수 있게 아티팩트 게시를 제안한다

## 10. 검수

전달 전에 **직접 렌더링해서 눈으로 확인한다.** 코드만 보고 넘기지 않는다.

- [ ] 외부 리소스 참조 0건 (`http://`, `https://`, `src=`, `@import` 검색)
- [ ] `word-break:keep-all`이 살아 있는가 — **한국어가 단어 중간에서 잘리지 않는가**
- [ ] 모든 막대 차트가 0에서 시작하는가
- [ ] 모든 exhibit에 각주 4요소가 있는가
- [ ] 상단에 기준이 표시되는가
- [ ] `key_takeaway`의 `emphasis`가 실제로 칠해졌는가
- [ ] `actions`가 표로 렌더링됐고 담당자 열이 없는가 (report 모드)
- [ ] 수신자보다 두 단계 아래 액션이 "실무 후속 과제"로 내려갔는가
- [ ] `views`가 2개 이상인 exhibit에 토글이 있고, 전환이 실제로 되는가
- [ ] `drilldown` 버튼이 동작하고 한 번에 하나만 열리는가
- [ ] 드릴다운 패널과 각주에 세그먼트 분류 근거가 표시되는가
- [ ] `brief.assumptions`가 가정 블록으로 표시되는가
- [ ] 축약어에 툴팁이 붙었는가
- [ ] 묶은 항목이 모두 클릭해서 열리는가
- [ ] 목차 번호와 섹션 번호가 일치하는가
- [ ] 400px 폭에서 가로 스크롤이 없는가
- [ ] `open_questions`가 화면에 표시되는가
- [ ] 스펙의 `action_title`과 화면 제목이 글자 그대로 일치하는가

### 렌더링 확인 방법

작업 환경에 헤드리스 브라우저가 있으면 스크린샷을 찍어 직접 본다.

```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width':1280,'height':1000}, device_scale_factor=2)
    pg.goto('file:///절대경로.html'); pg.wait_for_timeout(1500)
    pg.screenshot(path='check.png', full_page=True); b.close()
```

줄바꿈·겹침·색은 코드로는 안 보인다. 반드시 그림으로 확인한다.
