#!/usr/bin/env python3
"""license-desk 진행 장부(xlsx) 기록기. 판단 없이 기록만 한다.

사용법:
  ledger.py <장부.xlsx> show
  ledger.py <장부.xlsx> set <업체> <건유형> <단계번호> <근거> [다음할일]

- 단계번호는 house-rules 3절의 1~12.
- 같은 업체·건유형 행이 있으면 갱신, 없으면 추가.
- 단계가 2칸 이상 건너뛰면 기록하지 않고 SKIP 경고를 낸다 (법무 검토 없이 송부 등).
- 모든 변경은 '이력' 시트에 한 줄씩 남는다. 행을 지우지 않는다.
"""
import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook, load_workbook

STAGES = {1: "문의 확인", 2: "기존 계약 확인", 3: "유형 결정", 4: "조건 계산", 5: "제시값 대조",
          6: "초안 완료", 7: "법무 검토 완료", 8: "업체 송부", 9: "업체 동의", 10: "양사 품의",
          11: "날인", 12: "계산서·입금"}
HEAD = ["업체", "건유형", "단계", "단계명", "마지막 변경일", "근거", "다음 할 일"]


def open_book(p: Path):
    if p.exists():
        return load_workbook(p)
    wb = Workbook()
    wb.active.title = "현황"
    wb.active.append(HEAD)
    wb.create_sheet("이력").append(["일자", "업체", "건유형", "이전 단계", "새 단계", "근거", "결과"])
    return wb


def main(argv):
    p, cmd = Path(argv[1]), argv[2]
    wb = open_book(p)
    ws, log = wb["현황"], wb["이력"]
    if cmd == "show":
        for row in ws.iter_rows(min_row=2, values_only=True):
            print(" | ".join("" if v is None else str(v) for v in row))
        return
    if cmd != "set":
        sys.exit("명령은 show 또는 set")
    firm, kind, stage, basis = argv[3], argv[4], int(argv[5]), argv[6]
    nxt = argv[7] if len(argv) > 7 else ""
    today = date.today().isoformat()
    target = None
    for r in range(2, ws.max_row + 1):
        if ws.cell(r, 1).value == firm and ws.cell(r, 2).value == kind:
            target = r
    prev = ws.cell(target, 3).value if target else 0
    if stage > (prev or 0) + 1 and stage >= 7:
        log.append([today, firm, kind, prev, stage, basis, "SKIP: 단계 건너뜀"])
        wb.save(p)
        print(f"SKIP: {firm} {kind} {prev}→{stage} 단계 건너뜀. 기록하지 않음")
        return
    vals = [firm, kind, stage, STAGES.get(stage, "?"), today, basis, nxt]
    if target:
        for i, v in enumerate(vals, 1):
            ws.cell(target, i, v)
    else:
        ws.append(vals)
    log.append([today, firm, kind, prev, stage, basis, "OK"])
    wb.save(p)
    print(f"OK: {firm} {kind} {prev}→{stage} {STAGES.get(stage)}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv)
