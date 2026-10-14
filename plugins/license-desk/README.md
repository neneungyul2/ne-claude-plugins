# license-desk

외부 업체의 NE능률 교재 저작물 이용 건을 처리한다. 신규 이용 문의, 계약 갱신, 침해 대응, 계약 후속(날인·계산서·입금)을 기존 계약과 표준 저작권료로 검증한 회신·계약 문서 초안과 진행 장부로 바꾼다. **메일 발송, 법무 검토 요청, 품의, 날인은 사람이 한다.**

## 명령

| 명령 | 하는 일 |
|---|---|
| `/license-desk <업체명 또는 메일 제목>` | 건 하나를 초안까지 처리 |
| `/license-status` | 전체 진행 현황, F/U 대상, 갱신 안내 대상 |

## 흐름

```
수집 → 문의 정리 ─┬ 신규 ─ 조회 → 계산 → ✋확인 ─┐
                  ├ 갱신 ─ 조회 → 계산 → 분기 ─┬ 변동없음 ──────┤
                  │                             └ 협의필요 → ✋확인 ┤
                  ├ 침해 ─ 조회 → ✋확인 ──────────────────────────┤
                  └ 후속 ─ 장부 조회 ─────────────────────────────┤
                                                        초안 작성 → 재계산 → 검수(불합격 시 최대 2회 재작성) → 장부 기록 → 전달
```

## 구성

| 위치 | 내용 |
|---|---|
| `skills/license-desk`, `skills/license-status` | 흐름. 외부 시스템 접근은 여기서만 |
| `agents/` | 역할 6개: intake, contract-lookup, fee-calc, drafter, reviewer, tracker |
| `references/house-rules.md` | 모든 역할이 먼저 읽는 기본 규칙 |
| `references/tools.md` | 시스템별 접근 순서와 폴백, 건 폴더·장부 위치 |
| `scripts/calc_fee.py` | 저작권료 계산 (판단 없음) |
| `scripts/route_renewal.py` | 갱신 변동없음/협의필요 판정 (판단 없음) |
| `scripts/ledger.py` | 진행 장부 기록. 단계 건너뛰기 차단 |

## 환경 의존과 폴백

| 의존 | 없을 때 |
|---|---|
| 저작권 폴더(PC) | M365 SharePoint 검색 → 파일 업로드 요청 |
| Outlook (M365) | 메일 본문 붙여넣기 |
| 전자결재 ne-edoc MCP | 사용자에게 결재 상태 확인 |
| python3 + openpyxl | 장부 기록 불가 → 기록할 내용을 화면에 출력 |

설정: 프로젝트의 `.claude/license-desk.local.md`에 `copyright_folder: <저작권 폴더 경로>`. 없으면 첫 실행 때 묻는다.

## 개발 기록

`CURRICULUM.md`(하네스 워크숍 진행), `HANDOUT.md`(미결 사항).
