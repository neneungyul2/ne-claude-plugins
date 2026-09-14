---
description: 데이터를 빠르게 차트로 보여준다 (본인 확인용)
argument-hint: [파일 경로 또는 보고 싶은 내용]
---

빠른 시각화 모드로 진행한다. 요청: $ARGUMENTS

1. `${CLAUDE_PLUGIN_ROOT}/references/design-rules.md`와
   `${CLAUDE_PLUGIN_ROOT}/references/chart-rules.md`를 읽는다.
2. 수신자·의사결정은 **묻지 않는다.** 데이터와 요청에서 추론하고, 추론한 내용을 한 줄로 밝힌다.
3. `${CLAUDE_PLUGIN_ROOT}/skills/load-data/SKILL.md` → 데이터 정규화 + 데이터셋 카드.
4. `${CLAUDE_PLUGIN_ROOT}/skills/plan-report/SKILL.md` → 스펙 작성 (`mode: "quick"`, exhibit 1~3개).
   exhibit이 하나여도 스펙 단계를 건너뛰지 않는다.
5. `${CLAUDE_PLUGIN_ROOT}/skills/build-html/SKILL.md` → HTML 단일 파일 출력.

빠르다고 품질 기준이 낮아지지 않는다. 파이차트 금지, 기준 표기, 서술형 결론은 그대로 적용한다.
집계 기준을 알 수 없으면 `미확인`으로 표기하고 "확인 필요"에 남긴다.
