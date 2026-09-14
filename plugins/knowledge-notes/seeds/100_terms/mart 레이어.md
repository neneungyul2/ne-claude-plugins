---
type: term
aliases: [마트, mart, 마트 레이어]
domain: [데이터]
status: seed
created: 2026-09-14
schema: 1
---

# mart 레이어

> raw → core → mart 구조에서 분석·리포트가 직접 조회하는 최종 레이어.

## 사내 정의
- NE능률 데이터 인프라는 PostgreSQL 기반 raw / core / mart 구조다.
- 리포트는 mart를 우선 조회한다. core나 raw를 직접 쓰면 기준이 어긋난다.
- **테이블 목록과 컬럼명은 런타임에 조회한다.** 노트에 적어두면 실제와 어긋난다.

상위:: [[데이터 인프라]]
대조:: [[팩트 테이블]]
