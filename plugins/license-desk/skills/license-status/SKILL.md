---
name: license-status
description: 저작권 계약 건 전체의 진행 현황, 업체 회신 F/U 대상, 만료가 다가온 갱신 대상을 정리한다. "저작권 건 현황", "F/U 할 저작권 건 있어?", "갱신 다가오는 계약 알려줘"에 쓴다.
disable-model-invocation: true
---

# license-status 흐름

1. `${CLAUDE_PLUGIN_ROOT}/references/house-rules.md`, `tools.md`를 읽는다
2. 저작권 폴더 위치를 정한다 (license-desk 0단계와 같은 방식)
3. 자료를 모아 임시 폴더 `<저작권 폴더>\_license-desk_status\<YYMMDD>\`에 저장한다
   - 진행 장부 `01. 계약현황\license-desk_진행장부.xlsx` (`ledger.py show` 결과)
   - 진행 중인 건: `10. 업체별\*\_license-desk\*` 폴더를 훑어 찾는다
   - 전자결재 목록: `계약서 검토 요청서`, `품의서` 양식, 최근 3개월 → `edoc.md`
   - 저작권 관련 메일 최근 30일 목록(제목·보낸 사람·날짜) → `mail.md`
   - `01. 계약현황\★CP저작권 계약현황.xlsx`, `01. 계약현황\1. CP 계약 관리.xlsx` 복사본
   - 도구가 없거나 실패하면 tools.md 순서대로 대체하고 `sources.md`에 적는다
4. `license-tracker`를 부른다. 넘길 것: 위 폴더 경로, 장부 경로
5. 결과를 그대로 보여 준다: 건별 현재 단계, F/U 대상, 갱신 안내 대상, 장부와 CP 계약 관리 파일의 차이
6. 장부 변경이 있으면 tracker가 `ledger.py set`으로 기록한 결과(OK/SKIP)를 함께 보여 준다
