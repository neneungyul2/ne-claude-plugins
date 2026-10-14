#!/usr/bin/env python3
"""license-desk 저작권료 계산기.

판단 없이 계산만 한다. 같은 입력이면 항상 같은 결과를 낸다.

입력 (JSON 파일 경로 하나):
{
  "업체_연매출": 750000000,        # 원. 모르면 null → 할인율 잠정 표시
  "할인율_지정": null,              # 사용자가 확정한 할인율(0~1). 있으면 연매출보다 우선
  "개월": 12,                       # 계약 기간 개월 수
  "품목": [
    {"품목": "공통영어I", "개정": "2022", "저자": "민병천",
     "표준저작권료": 40000000, "묶음종수": 2, "출처": "운영원칙 p.12",
     "업체제시값": 2000000, "기존계약금액": 2500000}
  ]
}
- 표준저작권료가 여러 품목 합산값이면 묶음종수에 종수를 적는다(기본 1).
- 업체제시값, 기존계약금액은 비교용. 없으면 생략.
- 기존계약금액은 반드시 1년 환산 금액으로 넣는다(6개월 계약이면 ×2). 비교는 연환산금액끼리 한다.

출력: 마크다운 금액표·대조표를 표준출력으로, 같은 내용을 입력 옆 *_result.json으로 저장.
"""
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

# 운영 원칙(26.01.19) 연매출 구간별 '표준 저작권료 대비 적용 비율'
BANDS = [
    (Decimal("100000000"), Decimal("0.125"), "1억 미만"),
    (Decimal("1000000000"), Decimal("0.25"), "10억 미만"),
    (Decimal("3000000000"), Decimal("0.5"), "30억 미만"),
]


def won(x: Decimal) -> int:
    return int(x.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def fmt(n) -> str:
    return "-" if n is None else f"{int(n):,}"


def rate_for(revenue, override):
    if override is not None:
        r = Decimal(str(override))
        return (Decimal(1) - r), f"사용자 지정 할인 {r*100:g}%", False
    if revenue is None:
        return None, "[잠정: 매출 증빙 미접수]", True
    rev = Decimal(str(revenue))
    for limit, ratio, label in BANDS:
        if rev < limit:
            return ratio, f"연매출 {label} → 표준가 × {ratio}", False
    return Decimal(1), "연매출 30억 이상 → 표준가 그대로", False


def main(path):
    src = json.loads(Path(path).read_text(encoding="utf-8"))
    months = Decimal(str(src["개월"]))
    period = months / Decimal(12)
    ratio, ratio_note, provisional = rate_for(src.get("업체_연매출"), src.get("할인율_지정"))

    rows, total, warnings = [], 0, []
    for it in src["품목"]:
        bundle = int(it.get("묶음종수", 1) or 1)
        std_raw = Decimal(str(it["표준저작권료"]))
        std = std_raw / bundle
        if bundle > 1:
            warnings.append(f"{it['품목']}({it.get('저자','')}): 합산값 {fmt(std_raw)} ÷ {bundle}종 = {fmt(won(std))} — 사용자 확인 필요")
        annual = None if ratio is None else won(std * ratio)
        if ratio is None:
            amount, formula = None, f"{fmt(won(std))} × [할인율 미정] × {months}/12"
        else:
            exact = std * ratio * period
            amount = won(exact)
            formula = f"{fmt(won(std))} × {ratio} × {months}/12 = {fmt(amount)}"
            if exact != Decimal(amount):
                warnings.append(f"{it['품목']}: 원 단위 반올림 ({exact} → {amount})")
            total += amount
        offer = it.get("업체제시값")
        diff = None if (offer is None or amount is None) else offer - amount
        rows.append({
            "품목": it["품목"], "개정": it.get("개정", ""), "저자": it.get("저자", ""),
            "표준저작권료(종당)": won(std), "적용비율": None if ratio is None else str(ratio),
            "개월": int(months), "적용금액": amount, "연환산금액": annual, "계산식": formula, "출처": it.get("출처", "[출처 없음]"),
            "업체제시값": offer, "차이(제시-계산)": diff, "기존계약금액(참고)": it.get("기존계약금액"),
        })

    out = {"적용비율_근거": ratio_note, "잠정여부": provisional, "합계_VAT별도": None if ratio is None else total,
           "품목": rows, "확인필요": warnings}
    Path(path).with_name(Path(path).stem + "_result.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"적용 비율: {ratio_note}\n")
    print("| 품목 | 개정 | 저자 | 표준 저작권료 | 적용 금액 | 계산식 | 출처 |")
    print("|---|---|---|---:|---:|---|---|")
    for r in rows:
        print(f"| {r['품목']} | {r['개정']} | {r['저자']} | {fmt(r['표준저작권료(종당)'])} | {fmt(r['적용금액'])} | {r['계산식']} | {r['출처']} |")
    print(f"\n합계(VAT 별도): {fmt(out['합계_VAT별도'])}\n")
    if any(r["업체제시값"] is not None for r in rows):
        print("| 품목 | 업체 제시값 | 계산값 | 차이 | 기존 계약(참고) |")
        print("|---|---:|---:|---:|---:|")
        for r in rows:
            if r["업체제시값"] is not None:
                print(f"| {r['품목']} | {fmt(r['업체제시값'])} | {fmt(r['적용금액'])} | {fmt(r['차이(제시-계산)'])} | {fmt(r['기존계약금액(참고)'])} |")
    if warnings:
        print("\n확인 필요:")
        for w in warnings:
            print(f"- {w}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("사용법: calc_fee.py <입력.json>")
    main(sys.argv[1])
