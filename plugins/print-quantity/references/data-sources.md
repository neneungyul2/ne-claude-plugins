# 데이터 소스

**Metabase는 사내망 전용이다.** 접근이 안 되면 `report-maker`의 `sources/metabase.md`와 같은
방식으로 붙여넣기·엑셀 경로로 우회한다. 여기서는 이 플러그인이 쓰는 테이블만 적는다.

**DB 번호와 스키마는 런타임에 조회해 확인한다.** 아래는 2026년 9월 기준이며, 바뀌었을 수 있다.
먼저 `information_schema`로 존재를 확인하고 쓴다.

---

## 1. 쓰는 테이블

| 용도 | DB | 테이블 | 비고 |
|---|---|---|---|
| 경쟁서 추정 판매량 | DB1 (PostgreSQL) | `mart.yes24_sales_daily` | `isbn13`, `canonical_title`, `publisher_name`, `estimated_sales_qty`, `model_version` |
| 도서 분류·메타 | DB1 | `raw.yes24_item_meta` | `subject`가 YES24 카테고리 경로. **세그먼트 후보를 긁는 핵심 필드** |
| ISBN ↔ YES24 id | DB1 | `raw.yes24_items` | `yes24_book_id`, `isbn13` |
| 서점 실판매 | DB3 (PostgreSQL) | `mart.actual_sales_daily` | `channel_code`, `sales_qty`. 자사 품목만 |
| SAP 순출고 | DB4 (PostgreSQL) | `raw.sap_sales` | `posting_date`, `item_code`, `customer_code`, `customer_name`, `quantity` |
| 품목 ↔ ISBN | DB4 | `raw.sap_item_isbn` | `basedate` 최신본만 쓴다 |
| 쿠팡 입고 | DB9 (PostgreSQL) | `raw.stocked_items` | `_stocked_date`, `sku_name`, `quantity` |
| 쿠팡 실판매 | DB9 | `raw.sales_analysis` | 적재 시작이 늦다. 기간 확인 후 쓴다 |
| **재고 (기간본)** | DB4 | `raw.sap_inventory_wh` | `basedate`, `품목코드`, `창고코드`, `창고이름`, `재고수량`. 일별 스냅샷 |
| **생산입고·납품 (기간본)** | DB4 | `mart.sap_inventory_daily` | `itemcode`, `docdate`, `생산입고수량`, `납품수량`. 제작 이력이 여기 있다 |
| 재고 트랜잭션 | DB4 | `raw.sap_inventory_txn` | 건별 원장. 위 둘로 안 풀릴 때만 |

---

## 2. 반드시 지킬 것

### 추정 판매량은 모델 버전이 같은 구간만 쓴다

`mart.yes24_sales_daily`의 `model_version`이 바뀌면 값의 성격이 달라진다.
**조회 전에 대상 기간의 `model_version`을 확인하고, 단일 버전 구간으로 자른다.**

```sql
SELECT model_version, MIN(sales_date), MAX(sales_date)
FROM mart.yes24_sales_daily
WHERE sales_date >= '<시작>'
GROUP BY 1 ORDER BY 2
```

### 채널별 소스가 다르다

집계 기준을 섞지 않으려면 채널마다 정해진 소스를 쓴다.

| 채널 | 소스 | 성격 |
|---|---|---|
| 온라인 4사 (예스24·교보·알라딘·영풍) | DB3 `mart.actual_sales_daily` | 실판매 |
| 쿠팡 | 2025년 이전 SAP 거래처 / 2026년 이후 DB9 `raw.stocked_items` | 출고·입고 |
| 총판 | DB4 `raw.sap_sales` 중 **온라인 5사 거래처 코드를 제외한 나머지** | 출고 |

**총판은 "순출고에서 앞의 둘을 뺀 잔여"가 아니다.** 거래처 코드로 제외한다.
거래처 코드는 런타임에 이름으로 찾는다. 하드코딩하지 않는다.

```sql
SELECT DISTINCT customer_code, customer_name
FROM raw.sap_sales
WHERE customer_name ~ '예스|YES|교보|영풍|알라딘|쿠팡'
```

지역 서점 판매(`LOCAL` 채널)는 부분 표본이라 신뢰도가 낮다. **쓰지 않는다.** 총판 출고로 갈음한다.

### LOCAL 제외와 중복 계상

교보문고는 2026년 4월에 총판(고앤고에듀) 경유에서 직거래로 전환됐다. 그 이전 구간에서는
교보 물량이 총판 출고에도 잡히고 교보 실판매에도 잡힌다. **채널 합계가 SAP 순출고보다 커진다.**
비중 산출에는 영향이 없으므로 그대로 두되, 보고서 각주에 반드시 남긴다.

### 쿠팡

- `raw.stocked_items`는 적재 시작일이 있다. 조회 전에 `MIN(_stocked_date)`를 확인한다.
- SAP 쿠팡 거래처 출고와 `stocked_items`가 어긋나는 종이 있다. SAP는 월말 일괄 계상이고,
  쿠팡 전용 SAP 품목코드가 따로 잡힌 경우가 있다. 차이가 크면 보고서 유의사항에 적는다.

### MSSQL·타임아웃

DB2(MSSQL)를 쓸 일이 생기면 `TOP n` + 쿼리 끝 `--`로 자동 LIMIT을 막는다.
복잡한 다중 CTE는 자주 끊긴다. **단순 쿼리로 쪼개고 후처리에서 합친다.**

---

### 재고는 창고를 가려서 더한다 (기간본)

`raw.sap_inventory_wh`에는 창고가 36개 있고 **팔 수 없는 재고가 섞여 있다.**
`폐기`·`반품`·`수리본`·`수출`·`세트` 창고를 그대로 더하면 소진 시점이 한참 뒤로 밀린다.
분류 기준은 `reprint-model.md` 2절에 있다. **창고 코드는 하드코딩하지 않고 이름으로 조회**한다.

`basedate`는 일별 스냅샷이다. 항상 `MAX(basedate)`로 자른다. 과거 시점 재고가 필요하면
그 날짜를 직접 지정한다.

### 제작 이력은 생산입고로 본다 (기간본)

`mart.sap_inventory_daily`의 `생산입고수량`이 곧 제작 입고 실적이다. 같은 `itemcode`·`docdate`로
묶으면 로트 하나가 된다. **SAP에 생산 발주 잔량(제작 진행 중 물량) 테이블은 없다.**
미입고분은 제작팀에서 확정값으로 받는다.

생산입고 실적은 계획 부수보다 1~3% 많다(과부수). 이력값을 "지난 제작 부수"로 그대로 쓰지 않는다.

## 3. 자주 쓰는 쿼리 골격

### 세그먼트 후보 긁기 (DB1)

```sql
WITH s AS (
  SELECT yes24_book_id, isbn13,
         MAX(canonical_title) t, MAX(publisher_name) pub,
         SUM(estimated_sales_qty) est
  FROM mart.yes24_sales_daily
  WHERE sales_date BETWEEN '<시작>' AND '<끝>'
  GROUP BY 1,2
),
m AS (
  SELECT DISTINCT ON (yes24_book_id) yes24_book_id, subject
  FROM raw.yes24_item_meta ORDER BY yes24_book_id, ingested_at DESC
)
SELECT s.t, s.pub, ROUND(s.est) est, m.subject, s.isbn13
FROM s JOIN m ON m.yes24_book_id = s.yes24_book_id
WHERE m.subject ILIKE '<카테고리>'     -- 예: '%중등참고서%'
  AND s.t ~* '<세그먼트 키워드>'
  AND s.t !~* '수학|국어|과학|사회|한국사'
ORDER BY est DESC
```

`subject`는 `국내/중등참고서/예비고등` 같은 경로 문자열이다. 값 목록은 런타임에 조회한다.

```sql
SELECT DISTINCT subject FROM raw.yes24_item_meta
WHERE subject ILIKE '%<학교급>%' ORDER BY 1
```

### 채널 분해 (자사 벤치마크 품목)

```sql
-- ① 온라인 4사 실판매 (DB3)
SELECT SUM(sales_qty) FROM mart.actual_sales_daily
WHERE channel_code IN ('YES24','KYOBO_ONLINE','KYOBO_OFFLINE',
                       'ALADIN_ONLINE','YOUNGPOONG_ONLINE','YOUNGPOONG_OFFLINE')
  AND isbn13 IN (...) AND sales_date BETWEEN '<시작>' AND '<끝>'

-- ② SAP 순출고 · 총판 (DB4)
SELECT SUM(quantity) net,
       SUM(quantity) FILTER (WHERE customer_code NOT IN (<온라인5사 코드>)) chongpan
FROM raw.sap_sales
WHERE item_code IN (...) AND posting_date BETWEEN '<시작>' AND '<끝>'

-- ③ 쿠팡 입고 (DB9, 2026년 이후)
SELECT SUM(quantity) FROM raw.stocked_items
WHERE _stocked_date BETWEEN '<시작>' AND '<끝>' AND sku_name ILIKE '%<서명>%'
```

`item_code`는 `raw.sap_item_isbn`에서 최신 `basedate` 기준으로 ISBN을 매핑해 얻는다.
ISBN 직접 조인은 타임아웃이 잦다. **먼저 `item_code`를 뽑아 상수로 넣고 조회한다.**

### 재고·소진 (DB4, 기간본)

```sql
-- ① 가용재고 — 창고를 가린다
SELECT 창고코드, 창고이름, SUM(재고수량) qty
FROM raw.sap_inventory_wh
WHERE basedate = (SELECT MAX(basedate) FROM raw.sap_inventory_wh)
  AND 품목코드 IN (...)
GROUP BY 1,2 ORDER BY qty DESC
-- 결과를 보고 정품/비정품을 갈라 합계를 낸다. 코드로 필터를 박지 않는다

-- ② 월별 출고 — 추세용(총출고)과 소진용(순출고)을 함께 뽑는다
SELECT date_trunc('month', posting_date) m,
       SUM(quantity) FILTER (WHERE quantity > 0) gross,
       SUM(quantity)                              net
FROM raw.sap_sales
WHERE item_code IN (...) AND posting_date >= '<36개월 전>'
GROUP BY 1 ORDER BY 1

-- ③ 제작 이력 — 로트 단위와 소진 속도
SELECT docdate, SUM(생산입고수량) q
FROM mart.sap_inventory_daily
WHERE itemcode IN (...) AND 생산입고수량 > 0
GROUP BY 1 ORDER BY 1 DESC
```

계절지수는 ②의 `gross`로, 재고 소진 시뮬레이션은 ②의 `net`으로 만든다. 섞지 않는다.

**개정으로 품목코드가 바뀐 이력이 있으면 구품목코드를 함께 넣는다.** `raw.sap_item_isbn`에서
같은 서명·다른 ISBN을 찾아 확인한다. 품목코드 하나만 보면 계절성이 1년치밖에 안 나온다.
