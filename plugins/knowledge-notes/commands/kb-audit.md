---
description: vault 점검 — 중복·빈 링크·고아 노트·규칙 위반 확인
argument-hint: [점검 범위, 생략하면 전체]
---

vault를 점검한다. 범위: $ARGUMENTS (없으면 전체)

`${CLAUDE_PLUGIN_ROOT}/skills/kb-audit/SKILL.md`를 읽고 그 절차를 그대로 따른다.

- **즉시 고칠 것**(frontmatter 오류, schema 누락)은 목록을 보여주고 승인 후 일괄 수정한다.
- **판단이 필요한 것**(중복 의심, 원자성 위반)은 자동으로 건드리지 않는다. 하나씩 묻는다.
- **빈 링크는 고치는 게 아니다.** 참조 횟수 순 목록으로 남긴다. 그게 다음에 만들 노트다.
- 노트를 삭제하지 않는다.
