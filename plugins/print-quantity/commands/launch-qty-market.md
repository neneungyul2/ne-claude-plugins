---
description: 특정 세그먼트의 시장 규모만 본다 (1~2단계)
argument-hint: [세그먼트 또는 도서 콘셉트]
---

시장 규모만 산출한다. 요청: $ARGUMENTS

1~2단계만 돌고 멈춘다. 계수 산출과 부수 계산은 하지 않는다.

```
1) define-segment   세그먼트 축 정의
2) size-market      경쟁서 전수 조회 → 목차 검증 → TAM/SAM
```

`${CLAUDE_PLUGIN_ROOT}/skills/<이름>/SKILL.md`를 Read로 읽고 따른다.

**시작할 때 "시장 규모까지만 보겠다"고 먼저 말한다.** 부수까지 기대하고 있을 수 있다.

결과는 글자 표로 전달한다. HTML 보고서를 만들지 않는다.
부수까지 필요해지면 `/launch-qty`로 이어서 진행한다고 안내한다.
