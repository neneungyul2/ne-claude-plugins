---
description: 이미 만든 대시보드·보고서를 검수한다 (만들지 않는다)
argument-hint: [HTML 파일 경로. 스펙·브리프가 있으면 함께]
---

검수만 한다. 대상: $ARGUMENTS

**만들지 않는다. 고치지도 않는다.** 무엇이 잘못됐는지만 낸다.
남이 만든 것, 지난달 것, 방금 만든 것 전부 받는다.

`${CLAUDE_PLUGIN_ROOT}/skills/verify-report/SKILL.md`를 읽고 그 절차를 따른다.

```
1) check_html.py     소스를 읽는다
2) lint_render.py    브라우저로 칠해보고 픽셀을 잰다
3) report-verifier   만든 맥락이 없는 서브에이전트가 눈으로 본다
```

- `report-spec.json`이 같이 있으면 `--spec`으로 넘긴다. 스펙 대조까지 된다
- `report-brief.json`이 있으면 **역스토리보딩**이 된다 — 답하기로 한 것과 답한 것을 대조한다
- 둘 다 없으면 산출물만으로 할 수 있는 것까지만 하고, **무엇을 못 봤는지 밝힌다**

**고칠 것을 심각도 순으로 낸다.** 좋은 점을 나열해 균형을 맞추지 않는다.
사용자가 고쳐 달라고 하면 그때 고친다 — 검수와 수정은 분리한다.

`brief.report_type`에 따라 필수가 다르다. 감시형에 액션이 없다고 지적하면 틀린 검수다
(`${CLAUDE_PLUGIN_ROOT}/references/report-types.md` §3).
