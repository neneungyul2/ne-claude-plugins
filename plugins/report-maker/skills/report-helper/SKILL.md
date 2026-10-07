---
name: report-helper
description: 데이터를 보여줘야 하는 모든 상황의 진입점. "차트로 보여줘", "이 엑셀 보고용으로 정리해줘", "대시보드 만들어줘", "실적 정리해서 보고해야 해", "이 표 시각화", "일보 만들어줘", "숫자 좀 정리해줘", "본부장 보고용으로", "추이 좀 보자", "비교해서 보여줘"처럼 데이터·표·엑셀·실적·지표를 시각화하거나 보고 형태로 정리해달라는 요청이면 먼저 이 스킬을 사용한다. 목적과 수신자를 확인해 빠른 시각화(quick)인지 정식 보고(report)인지 판단하고 다음 단계로 연결한다.
---

# 대시보드·보고서 제작 진입점

데이터를 보여주는 작업 전체의 시작점이다. 여기서 **모드를 정하고**, 이후 단계로 넘긴다.
이 파일로 되돌아올 필요는 없다.

## 0. 먼저 읽을 것

- `${CLAUDE_PLUGIN_ROOT}/references/report-types.md` — **필수. 가장 먼저 읽는다.**
  무엇을 만들지는 이 문서의 질문 하나("결론을 누가 내는가")와 조건 셋으로 정해진다

quick·report 어느 쪽이든 동일하게 적용되는 두 문서:

- `${CLAUDE_PLUGIN_ROOT}/references/design-rules.md`
- `${CLAUDE_PLUGIN_ROOT}/references/chart-rules.md`

지표 이름이 등장하면 `${CLAUDE_PLUGIN_ROOT}/references/metrics.md`도 읽는다.

## 0-1. 탐색형인지 먼저 가른다

다섯 종류 중 **탐색형만 파이프라인이 다르다.** 그래서 이것부터 가른다.
사용자 말에서 "필터로 볼 수 있게", "날짜·기간을 바꿔가며", "대시보드로 계속 쓸",
"직접 파볼 수 있게" 같은 신호가 나오면 되묻지 않고 **탐색형**으로 보고
`${CLAUDE_PLUGIN_ROOT}/skills/frame-explore/SKILL.md`로 바로 넘어간다.
quick/report 구분도, frame-question도 거치지 않는다.

나머지 넷(결정·진단·점검·조망)은 아래 1장부터 이어서 간다. 종류는 frame-question이 정한다.
**종류 이름을 사용자에게 묻지 않는다** — `report-types.md` §8.

둘 다 필요하다는 요청("일보도 만들고, 필터로도 보게")이 오면 **산출물 두 개**라고
알린다. `report-types.md` §8의 점검형·탐색형 구분을 보여주며 하나씩 순서대로 진행한다.

## 1. 모드 판단 — 탐색형이 아닐 때

| | quick (빠른 시각화) | report (정식 보고) |
|---|---|---|
| 신호 | "그냥 좀 보자", "확인만", 본인이 볼 것, 파일 하나 던져줌 | 수신자가 있음, 보고·회의·공유 언급, 의사결정이 걸림 |
| 브리프 | 묻지 않고 추론. **추론했다고 밝힌다** | 아래 3가지를 반드시 묻는다 |
| 분량 | exhibit 1~3개 | exhibit 3~7개 + 요약 |
| 품질 기준 | **report와 동일** | — |

애매하면 한 줄로 묻는다: "본인 확인용으로 빠르게 볼까요, 아니면 보고용으로 정리할까요?"

> quick이라고 품질이 낮아도 되는 게 아니다. 파이차트 금지, 기준 표기, 결론 먼저 —
> 이 세 가지는 두 모드에 똑같이 적용된다.

## 2. report면 frame-question으로 넘긴다

여기서 수신자·의사결정을 캐묻지 않는다. **질문 설계는 별도 단계다.**

`${CLAUDE_PLUGIN_ROOT}/skills/frame-question/SKILL.md`를 읽고 그 절차를 따른다.
거기서 핵심 질문 후보를 내놓고 고르게 하고, 수신자 레벨·가정·분석 축을 확정해
`report-brief.json`으로 남긴다.

**데이터를 먼저 열지 않는다.** 값을 보면 질문이 데이터에 끌려간다.

quick 모드는 이 단계를 건너뛰고 `load-data`로 바로 간다.

## 3. 산출 포맷 결정

동시 산출하지 않는다. 하나만 고른다.

- **HTML 단일 파일** — 인터랙션이 필요하거나, 링크로 공유하거나, 수치를 훑어봐야 할 때
- **문서·슬라이드** — 회의에서 넘기며 설명하거나, 결재 문서에 붙일 때

모르면 묻는다. quick은 기본값 HTML.

## 4. 진행 순서

```
[이 스킬] 모드 판단
   ↓
frame-question   종류·조건 판정 → 질문·가정·수신자 레벨·분석 축 합의  ← report 필수
   ↓
load-data        데이터 확보 + 정규화 + 데이터셋 카드
   ↓
plan-report      포맷 중립 스펙 작성 (결론·차트·배치가 여기서 확정된다)
   ↓
build-html  또는  build-doc
   ↓
verify-report    기계 검사 + 만든 맥락 없는 검수  ← report 필수
```

**사용자 확인은 두 곳이다** — `frame-question`에서 **형태**(데이터 전),
`plan-report`에서 **배치**(데이터 후). 둘 다 **글자 와이어프레임**으로 보여준다.
HTML을 그려서 확인받지 않는다 — 화면을 만들면 사용자는 구조가 아니라 색에 반응하고,
만든 쪽은 애착이 생겨 틀렸어도 못 버린다.

**앞뒤 두 단계가 핵심이다.** 앞에서 무엇을 답할지 합의하지 않으면 있는 데이터로
만들 수 있는 것을 만들게 되고, 뒤에서 다른 눈으로 보지 않으면 만든 사람만
읽히는 화면이 나간다.

다음 스킬로 넘어갈 때는 해당 SKILL.md를 Read 도구로 읽고 그 지침을 따른다.

- `${CLAUDE_PLUGIN_ROOT}/references/report-types.md` — **종류가 형태를 정한다. 먼저 읽는다**
- `${CLAUDE_PLUGIN_ROOT}/skills/frame-question/SKILL.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/load-data/SKILL.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/plan-report/SKILL.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/build-html/SKILL.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/build-doc/SKILL.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/verify-report/SKILL.md`

탐색형(0-1장에서 그렇게 갈린 경우)은 위 목록이 아니라 아래를 순서대로 읽는다.

- `${CLAUDE_PLUGIN_ROOT}/skills/frame-explore/SKILL.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/load-data/SKILL.md` (같은 어댑터, 긴 형식으로 남긴다)
- `${CLAUDE_PLUGIN_ROOT}/skills/plan-explore/SKILL.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/build-explore/SKILL.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/verify-report/SKILL.md` (탐색형 분기)

결정·진단형은 **요청과 액션이 필수**다. exhibit만 늘어놓고 끝내지 않는다.
점검형은 정상이면 액션 0개가 정답이고, 조망형은 판단 대신 "눈여겨볼 곳"으로 끝난다.
축약어·사내 용어가 나오면 용어 설명(툴팁)을 붙이고, 계산은 계산 방법 창으로 뺀다 —
창에는 **실제 숫자로 쓴 계산**을 넣는다. 읽는 사람이 계산기로 따라 할 수 있어야 한다.

**스펙 단계를 건너뛰지 않는다.** exhibit이 하나뿐이어도 "무엇을 어떤 차트로 어떤 메시지로"를
먼저 적고 나서 그린다. 이 순서를 지키지 않으면 같은 데이터로 만든 두 산출물의 결론이 달라진다.

## 5. 반복해서 여는 화면 — 점검형

"일보", "매주 확인", "이상 있으면 알아야" 같은 요청은 **질문이 고정되어 있다.**
매번 브리프를 다시 돌리지 않는다.

- 처음 만들 때는 `frame-question`을 돈다. **임계값을 정하는 것이 이 단계의 핵심**이고,
  `${CLAUDE_PLUGIN_ROOT}/references/watch-thresholds.md`를 읽는다
- 두 번째부터는 `/refresh`다. 구성은 그대로 두고 데이터만 갈아끼운다.
  작성자가 화면에서 고친 기록은 `scripts/carry_edits.py`로 옮긴다
- **아무것도 안 걸리면 "특이사항 없음"이 정답이다.** 억지로 액션을 만들지 않는다

기존 산출물을 갱신하는 것인지 새로 만드는 것인지 애매하면 **묻는다.**
"지난번 화면을 이번 달 데이터로 갱신할까요, 아니면 새로 보실까요?"

## 6. 사용자에게 말할 때

- 기능 용어를 쓰지 않는다. "스펙 레이어를 거쳐서" 대신 "무엇을 어떻게 보여줄지 먼저 정리하고".
- 추론한 것은 추론이라고 밝힌다. "기간은 데이터에 있는 8월 전체로 잡았습니다. 다르면 알려주세요."
- 데이터에 없는 것을 지어내지 않는다. 빠진 값은 빠졌다고 표시한다.
