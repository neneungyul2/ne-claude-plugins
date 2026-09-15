---
name: derive-coefficients
description: 신간 제작 수량 검토의 3단계. 자사 유사 신간 실적에서 추정→실판매·기간→연간·실판매→총출고·온라인 비중 계수를 직접 산출하고 검산한다. 다른 카테고리의 계수를 재사용하지 않는다. print-quantity 신간 경로의 3단계.
---

# 보정계수 산출 (derive-coefficients)

## 0. 먼저 읽을 것

- `${CLAUDE_PLUGIN_ROOT}/references/coefficients.md` — **필수**
- `${CLAUDE_PLUGIN_ROOT}/references/channel-model.md` — **필수**
- `${CLAUDE_PLUGIN_ROOT}/references/benchmarks.md` — 대조용

## 1. 벤치마크를 고른다

같은 세그먼트 · 같은 학년대의 자사 품목. 최근 신간이 1순위다.
없으면 노후 품목이라도 쓰되 방향성을 유의사항에 적는다.

고른 이유를 한 줄로 적는다. 보고서 부록에 그대로 들어간다.

## 2. 네 계수를 뽑는다

**같은 기간으로 뽑는다.** 기간이 섞이면 계수끼리 모순된다.

| 계수 | 기간 | 소스 |
|---|---|---|
| `K_EST` | SAM 조회 구간과 동일 | DB1 추정 ÷ DB3 YES24 실판매 |
| `K_YEAR` | 직전 완결 연도 월별 | DB3 YES24 실판매 |
| `K_SHIP` | SAM 조회 구간과 동일 | 채널 합계 ÷ YES24 실판매 |
| `ONLINE` | 직전 연도 1월 ~ 최근월 | 채널 합계 (반품 포함 구간) |

`K_EST`와 `K_SHIP`은 **물량가중**으로 뽑는다. 종별 비율의 단순 평균을 쓰지 않는다.

`ONLINE`은 반품이 포함된 긴 구간으로 뽑는다. 반품은 대부분 총판에서 나오므로,
반품 이전 구간만 보면 총판 비중이 과대평가된다.

`K_FIRST = 0.75`, `K_PRINT = 0.75`는 고정값이다. 바꿨으면 이유를 적는다.

## 3. 총판은 거래처 코드로 제외한다

잔여 차감이 아니다. 거래처명으로 코드를 런타임 조회해 `NOT IN`으로 뺀다.

```sql
SELECT DISTINCT customer_code, customer_name FROM raw.sap_sales
WHERE customer_name ~ '예스|YES|교보|영풍|알라딘|쿠팡'
```

## 4. 검산한다

```
벤치마크 추정 ÷ K_EST × K_YEAR × K_SHIP  ≈  벤치마크 연간 SAP 순출고
```

10% 이상 어긋나면 기간이 섞였거나 채널 정의가 틀렸다. **그대로 진행하지 않는다.**

## 5. 대조한다

`benchmarks.md`의 기존 값과 비교해 터무니없지 않은지 본다.
`K_SHIP`이 10을 넘거나 `K_EST`가 2를 넘으면 벤치마크 선정이나 기간을 다시 본다.

## 6. 산출물

```
벤치마크 : <품목> <n>종 (<선정 이유>)
K_EST    : ÷ 0.00  — <실제 숫자>
K_YEAR   : × 0.00  — <실제 숫자>
K_SHIP   : × 0.00  — <실제 숫자>
ONLINE   : 0.00    — 온라인 X ÷ (온라인 X + 총판 Y)
검산     : 산출 00,000 vs 실측 00,000 (오차 0%)
```
