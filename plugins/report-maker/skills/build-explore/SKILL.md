---
name: build-explore
description: 확정된 탐색 스펙을 HTML 대시보드 하나로 렌더링한다. 공용 계산 엔진 위에 패널을 조립하고, 축을 바꿔도 화면이 깨지지 않게 만든다. 탐색형 파이프라인의 4단계로, plan-explore가 만든 스펙을 입력으로 받고 verify-report로 넘긴다.
---

# 탐색 렌더링 (build-explore)

`explore-spec.json`을 **HTML 파일 하나**로 만든다. `build-html`과 같은 산출물 형태
(단일 파일·인라인 SVG·디자인 토큰)를 쓰지만, 조립 방식이 다르다 — 결론을 그리는 게
아니라 **축이 바뀔 때마다 다시 계산해서 그리는 틀**을 만든다.

## 0. 먼저 읽을 것

- `${CLAUDE_PLUGIN_ROOT}/references/explore-model.md` — **필수.** 그레인·축·패널·엔진 원칙
- `${CLAUDE_PLUGIN_ROOT}/references/design-rules.md` — 배치·타이포·색은 설명형과 동일
- `${CLAUDE_PLUGIN_ROOT}/references/template/explore-parts.html` — **패널 부품 목록. 이것만 읽는다**
- 지역 패널이 있으면 `${CLAUDE_PLUGIN_ROOT}/references/korea-map.md`

**`base.css`·`base.js`·`explore-engine.js`를 읽지 않는다.** `assemble.py`가 그대로
붙인다. `explore-engine.js`의 함수를 고쳐 쓰지 않는다 — 패널마다 계산을 다시 짜면
`explore-model.md` §4가 경고하는 문제(재사용 안 되는 함수 150개)가 그대로 반복된다.
엔진에 없는 계산이 필요하면 **엔진에 함수를 추가**하고, 특정 패널 파일 안에 박아 넣지 않는다.

**`explore-parts.html`은 부품 목록이지 레이아웃이 아니다.** 스펙의 `panels` 배열이
개수·순서·유형을 정한다. 쓰지 않는 부품(지도·기타드릴다운·비교토글)은 지운다.

## 0-1. 무엇을 쓰는가

```
explore-spec.json       무엇을 보여줄지 (plan-explore가 만든 것)
data.json (또는 인라인)  그레인 원자료. 크면 별도 파일, 작으면 <이름>.content.html 안에 인라인
<이름>.content.html     ← 여기를 쓴다. <main> 안쪽 + 패널 마크업 + 데이터
<이름>.html             ← assemble.py가 만든다. 직접 쓰지 않는다
```

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/assemble.py <이름>.content.html -o <이름>.html
```

원자료가 `explore-model.md` §5 기준을 넘으면(대략 1MB 이상) 사용자에게 알리고
정밀도·기간 범위를 먼저 줄인다. 압축 트릭보다 범위 합의가 먼저다.

## 1. 원칙

`build-html` §1과 동일 — 단일 파일, 인라인 SVG, 토큰만 사용, 한국어 줄바꿈 CSS,
반응형, 라이트 전용. 탐색형에만 추가되는 것:

- **원자료는 그레인 그대로 싣는다.** 패널이 미리 계산한 값이 아니라, 필터가 바뀔 때마다
  `explore-engine.js`가 원자료에서 다시 계산한다. 계산 결과를 데이터에 미리 박아 넣지 않는다
- **상태는 하나의 객체로 관리한다.** 축마다 전역 변수를 따로 두지 않는다.
  `state = { date:…, category:…, channel:… }` 하나를 두고, 축 컨트롤이 바뀌면
  `state`를 갱신한 뒤 **모든 패널을 다시 그린다.** 패널 하나만 갱신하는 개별 로직을
  패널마다 따로 만들지 않는다

## 2. 조립 순서

```
헤더(스티키)   제목 · 기준 배지
축 컨트롤 바   axes 전부. 항상 최상단, 스크롤해도 고정
KPI 행         panels 중 type: kpi
① 패널         패널 제목(명사구 가능) → [비교토글] → 차트 → [기타 드릴다운]
② 패널 …
각주           footnote
모달           기타 드릴다운 전체 보기 · calcs
```

- 패널은 스펙 배열 순서 그대로 — `plan-explore` 2장에서 정한 개요→추이→구성→위치→상세 순
- **목차·탭은 기본적으로 두지 않는다.** 패널이 8개를 넘거나 성격이 크게 갈릴 때만 검토한다
  — 탐색형은 필터로 이미 화면을 좁히는 도구라, 탭까지 더하면 통제축이 두 겹이 된다
- 히어로·`key_takeaway`·번호 배지 요약을 만들지 않는다 — 결론이 없다

### 축 컨트롤 바

- 각 축을 `explore-model.md` §2의 컨트롤 유형대로 렌더링한다
- 축을 바꾸면 `state`를 갱신하고 **영향받는 모든 패널을 다시 그린다.**
  `panels[].axes_used`에 그 축이 없는 패널은 다시 그리지 않아도 되지만,
  틀렸을 때의 위험(그리지 않아 오래된 값이 남는 것)이 다시 그리는 비용보다 크므로
  **애매하면 전부 다시 그린다**
- 현재 선택값을 URL이나 화면에 항상 보이게 한다 — "지금 무슨 조합을 보고 있는지"가
  안 보이면 스크린샷을 공유해도 무슨 조합인지 알 수 없다

### 패널 제목

명사구로 둔다. `build-html`의 `action_title` 검사(서술형 문장인가)를 적용하지 않는다.
대신 **"이것만 봐도 무엇을 보여주는지 알 수 있나"**만 확인한다 — "요약" 같은 제목은
이것도 통과하지 못하므로 여전히 반려된다.

## 3. 패널 구현

| type | 구현 요점 |
|---|---|
| `kpi` | 현재 `state`로 필터한 값의 합·비교값. `explore-engine.rollup`으로 계산. 비교값 없으면 KPI가 아니다 |
| `trend` | 시간축 line/bar. 계열 5개 초과면 상위 N + 기타로 접는다(`explore-engine.renorm`) |
| `mix` | 구성 비중(막대·stacked_bar_100). 기타는 `etc_drilldown` 설정대로 클릭해 열린다 |
| `map` | `korea-map.md` 좌표 사용. 지도만 있고 표가 없으면 값 비교가 안 되므로 `maprow`로 표를 나란히 둔다 |
| `table` | 상세 행. 12행 넘으면 페이지네이션 또는 스크롤 컨테이너. 정렬 가능 헤더 |

차트 종류·금칙은 `chart-rules.md`를 그대로 따른다 (파이·3D·이중Y축·잘린축·무지개 금지).

### 기타(etc) 드릴다운은 축에 반응한다

`build-html`의 `group_detail` 모달과 다른 점 — 탐색형은 **필터가 바뀔 때마다
기타의 내용이 다시 계산돼야 한다.** 렌더 시점에 "기타 = A, B, C"로 고정하지 않는다.

```js
function renderMix(panel, state) {
  const rows = filterByState(DATA, state, panel.axes_used);
  const { top, etc } = splitTopN(rollupBy(rows, panel.dim), panel.etc_drilldown.top_n);
  // top, etc 둘 다 state가 바뀔 때마다 새로 계산된다. 이전 결과를 재사용하지 않는다
}
```

드릴다운 모달을 열 때도 **현재 `state` 기준으로** 내용을 채운다.

## 4. 계산 엔진 사용

`references/template/explore-engine.js`의 함수만 쓴다. 목록은 `explore-model.md` §4.
패널 코드에서 직접 합산·평균 루프를 새로 짜지 않는다 — 엔진 함수를 부른다.

엔진에 없는 계산이 필요해지면:
1. 다른 패널에서도 쓸 만한 계산인가 확인한다 — 대개 그렇다
2. `explore-engine.js`에 함수를 추가한다 (패널 파일이 아니라 엔진 파일에)
3. 함수 이름과 인자를 이 SKILL.md 위 표에 추가해 다음 작업자가 찾을 수 있게 한다

## 5. 용어와 산식

`build-html` §5와 동일한 방식 — `glossary`는 첫 등장 지점에 `<abbr>`, `calcs`는 모달.
탐색형에서 다른 점은 하나: 필터에 따라 값이 계속 바뀌므로, **calc 모달에 "지금 보고 있는
조합" 기준 값이 아니라 산식 자체**만 설명한다. 가변값을 모달에 하드코딩하지 않는다.

## 6. 검수

전달 전에 렌더링해서 확인한다. `build-html` §10과 겹치는 항목은 생략하고, 탐색형에만
해당하는 것만 추가한다.

- [ ] 외부 리소스 참조 0건, 자리표시자 0건, `word-break:keep-all` 유지 — `build-html` 동일
- [ ] **모든 축을 하나씩 바꿔봤을 때 관련 패널이 실제로 다시 그려지는가**
- [ ] **축 조합을 2~3개 이상 무작위로 섞어봤을 때 화면이 깨지지 않는가**
      (빈 배열, undefined 라벨, NaN%가 나오지 않는가)
- [ ] 그레인이 못 받치는 조합에서 **"볼 수 없음"이 표시되는가** (빈 화면이나 0으로
      새어나가지 않는가)
- [ ] 기타 드릴다운이 축을 바꿔도 다시 계산되는가 (고정된 목록이 남아 있지 않은가)
- [ ] KPI가 항상 최상단이고, 축 컨트롤 바가 스크롤해도 보이는가
- [ ] 현재 선택된 축 조합이 화면에서 항상 보이는가
- [ ] 파일 크기가 관리 가능한가 (`explore-model.md` §5)
- [ ] `check_html.py`·`lint_render.py`가 FAIL 0인가

### 렌더링 확인 방법

`build-html` §10과 동일하게 헤드리스 브라우저로 스크린샷을 찍는다. 탐색형은
**한 조합만 찍고 끝내지 않는다** — 최소 3개 조합(기본값, 극단값 하나, 데이터가 적은
값 하나)을 찍어 각각 확인한다.

## 7. 다음 단계

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/assemble.py <이름>.content.html -o <이름>.html
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check_html.py <이름>.html
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lint_render.py <이름>.html
```

FAIL 0이 되면 `${CLAUDE_PLUGIN_ROOT}/skills/verify-report/SKILL.md`의 탐색형 분기로 넘어간다.
**결론 검사(수평논리·역스토리보딩)는 탐색형에 적용하지 않는다** — 대신 축 조합 검사를 한다.
