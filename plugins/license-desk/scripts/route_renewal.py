#!/usr/bin/env python3
"""갱신 건 2차 분기 판정. 판단 없이 조건만 대조한다.

입력: 건 폴더 경로
  - 03_fee_input_result.json  (calc_fee.py 결과)
  - 03_route_input.json       (license-fee-calc가 작성)
    {"기존_품목": ["공통영어I/민병천", ...], "요청_품목": [...],
     "기존_개월": 12, "요청_개월": 12, "할인_조건_요청": false}

출력: 표준출력 첫 줄 `ROUTE: 변동없음` 또는 `ROUTE: 협의필요`, 이어서 사유.
같은 내용을 04_route.md로 저장.
경계·누락이 있으면 항상 협의필요.
"""
import json
import sys
from pathlib import Path


def main(case_dir):
    d = Path(case_dir)
    reasons = []
    try:
        fee = json.loads((d / "03_fee_input_result.json").read_text(encoding="utf-8"))
        ri = json.loads((d / "03_route_input.json").read_text(encoding="utf-8"))
    except Exception as e:  # 파일 누락 = 판정 불가 = 협의필요
        reasons.append(f"판정 입력 파일 없음: {e}")
        fee, ri = {"품목": [], "잠정여부": True}, {}

    if fee.get("잠정여부"):
        reasons.append("할인율 잠정(매출 증빙 미접수)")
    for r in fee.get("품목", []):
        new, old = r.get("연환산금액"), r.get("기존계약금액(참고)")  # 둘 다 1년 기준
        if old is None or new is None:
            reasons.append(f"{r.get('품목')}/{r.get('저자','')}: 기존 금액 또는 계산값 없음")
        elif new != old:
            reasons.append(f"{r.get('품목')}/{r.get('저자','')}: 표준가 기준 연 {new:,} ≠ 기존 연 {old:,}")
    old_items, new_items = set(ri.get("기존_품목", [])), set(ri.get("요청_품목", []))
    if not old_items or old_items != new_items:
        reasons.append(f"품목 변경: 추가 {sorted(new_items - old_items)}, 제외 {sorted(old_items - new_items)}")
    if ri.get("기존_개월") is None or ri.get("기존_개월") != ri.get("요청_개월"):
        reasons.append(f"기간 변경: {ri.get('기존_개월')}개월 → {ri.get('요청_개월')}개월")
    if ri.get("할인_조건_요청") is not False:
        reasons.append("업체 할인·조건 요청 있음 또는 미확인")
    if fee.get("확인필요"):
        reasons.append("계산 단계 확인 필요 항목 있음")

    route = "협의필요" if reasons else "변동없음"
    lines = [f"ROUTE: {route}"] + [f"- {x}" for x in reasons]
    out = "\n".join(lines)
    (d / "04_route.md").write_text(out + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("사용법: route_renewal.py <건 폴더>")
    main(sys.argv[1])
