---
type: term
aliases: [평균절대백분율오차, Mean Absolute Percentage Error]
domain: [S&OP, 데이터]
status: seed
created: 2026-09-14
schema: 1
---

# MAPE

> 예측 오차를 실제값 대비 백분율로 평균한 지표.

## 산식
mean(|실제 − 예측| ÷ |실제|) × 100

## 사내 정의
- TODO: 예측 평가에 어떤 지표를 쓰는지 확인 필요

## 혼동 주의
- 실제값이 0에 가까우면 값이 발산한다. 저판매 종이 많으면 MAPE는 왜곡된다

선행:: [[수요예측]]
