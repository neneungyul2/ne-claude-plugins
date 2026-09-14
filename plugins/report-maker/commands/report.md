---
description: 정식 보고용 대시보드·보고서를 만든다
argument-hint: [무엇을 누구에게 보고할지]
---

정식 보고 모드로 진행한다. 요청: $ARGUMENTS

1. `${CLAUDE_PLUGIN_ROOT}/references/design-rules.md`,
   `${CLAUDE_PLUGIN_ROOT}/references/chart-rules.md`,
   `${CLAUDE_PLUGIN_ROOT}/references/metrics.md`를 읽는다.
2. 아래 3가지를 **한 번에 묶어서** 확인한다. 이미 대화에 나온 건 다시 묻지 않는다.
   - 수신자 (대표 / 본부장 / 팀장 / 파트원 / 타 부서)
   - 이걸 보고 정해야 하는 것 (없으면 "공유")
   - 이미 알고 있는 결론 (없으면 데이터에서 찾는다)
   - 산출 포맷: HTML 단일 파일 / 문서·슬라이드 중 하나
3. `${CLAUDE_PLUGIN_ROOT}/skills/load-data/SKILL.md` → 데이터 정규화 + 데이터셋 카드.
   집계 기준이 판정되지 않으면 임의로 정하지 말고 확인한다.
4. `${CLAUDE_PLUGIN_ROOT}/skills/plan-report/SKILL.md` → 스펙 작성 (`mode: "report"`, exhibit 3~7개).
   자체 검사를 통과시키고 결과를 한 줄로 보고한다.
5. 포맷에 맞는 렌더러로 출력한다.
   - HTML → `${CLAUDE_PLUGIN_ROOT}/skills/build-html/SKILL.md`
   - 문서·슬라이드 → `${CLAUDE_PLUGIN_ROOT}/skills/build-doc/SKILL.md`

수정 요청이 오면 스펙(`report-spec.json`)을 고치고 다시 렌더링한다. 산출물을 직접 편집하지 않는다.
