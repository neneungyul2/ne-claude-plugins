# 템플릿 — 세 조각

`html-template.html` 하나였던 것을 쪼갰다. **CSS와 스크립트를 모델이 읽지도 쓰지도
않게 하는 것이 목적이다.** 한 글자도 바뀌지 않는 25,000자를 매번 읽고 산출물마다
다시 출력하고 있었다.

| 파일 | 크기 | 리포트 만들 때 |
|---|---|---|
| `parts.html` | ~9K | **이것만 읽는다.** 부품 목록 |
| `base.css` | ~18K | **읽지 않는다.** assemble.py가 붙인다 |
| `base.js` | ~7K | **읽지 않는다.** assemble.py가 붙인다 |

## 만드는 법

```bash
# 본문(<main> 안쪽 + 필요하면 모달)만 쓴 파일을 만들고
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/assemble.py <이름>.content.html -o <이름>.html
```

**본문 파일을 남긴다.** 수정할 때 그걸 고치고 다시 조립한다 —
9만 자짜리 산출물을 통째로 다시 쓰지 않는다.

```
report-spec.json        무엇을 말할지
<이름>.content.html     부품을 조립한 본문. 고치는 것은 여기
<이름>.html             조립 결과. 전달물. 직접 고치지 않는다
```

## 고칠 때

| 무엇을 고치나 | 어디를 |
|---|---|
| 색·크기·간격 토큰, 컴포넌트 스타일 | `base.css` — **모든 리포트에 영향을 준다.** 한 리포트 때문에 고치지 않는다 |
| 툴팁·토글·드릴다운·모달 동작 | `base.js` — 위와 같다 |
| 부품의 구조·클래스 이름 | `parts.html` |
| 그 리포트 하나의 내용 | `<이름>.content.html` |

`base.css`나 `base.js`를 고쳤으면 `html-template.html`을 **다시 조립해서 커밋한다.**
`verify_docs_sync.py`가 최신인지 검사한다.

## 이 리포트에만 필요한 스타일

본문에 `<style data-extra>`로 둔다. assemble.py가 그대로 통과시킨다.
**단, 토큰 밖 값을 쓰면 `check_html.py`가 잡는다.** 스케일 안에서 해결한다.
