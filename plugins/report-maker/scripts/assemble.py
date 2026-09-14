#!/usr/bin/env python3
"""본문만 받아 단일 HTML 파일로 조립한다.

**CSS와 스크립트를 모델이 읽지도 쓰지도 않게 하는 것이 목적이다.**
템플릿 전체는 34,000자인데 그중 CSS 18,000 + JS 6,700이 매번 읽히고
산출물마다 다시 출력됐다. 한 글자도 바뀌지 않는데.

이제 모델은 `references/template/parts.html`(부품 목록)만 읽고,
본문(`<main>` 안쪽)만 쓴다. 나머지는 이 스크립트가 붙인다.

사용:
    python3 assemble.py <본문.html> -o <산출물.html> [--title "제목"]

본문 파일에 담는 것 — `<main class="wrap">` 안의 내용, 그리고 필요하면
`<div class="mask">` 모달 블록. `<head>`·`<style>`·`<script>`는 쓰지 않는다.
차트별 추가 스타일이 꼭 필요하면 본문에 `<style data-extra>...</style>`을
두면 그대로 따라 들어간다.

의존성 없음.
"""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(ROOT, "references", "template")

SHELL = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>
{body}
<div id="tt"></div>
<script>
{js}
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("content", help="본문 HTML (<main> 안쪽 + 선택적 모달)")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--title", help="생략하면 본문의 <h1>에서 가져온다")
    ap.add_argument("--css", help="base.css 대신 쓸 파일")
    ap.add_argument("--js", help="base.js 대신 쓸 파일")
    a = ap.parse_args()

    for p in (a.content, a.css or os.path.join(TPL, "base.css"),
              a.js or os.path.join(TPL, "base.js")):
        if not os.path.isfile(p):
            print(f"파일이 없다: {p}", file=sys.stderr)
            return 2

    body = open(a.content, encoding="utf-8").read().strip()
    css = open(a.css or os.path.join(TPL, "base.css"), encoding="utf-8").read().strip()
    js = open(a.js or os.path.join(TPL, "base.js"), encoding="utf-8").read().strip()

    # 본문이 셸까지 들고 있으면 벗긴다 — 흔한 실수다
    if "<!doctype" in body.lower() or "<html" in body.lower():
        m = re.search(r"<body[^>]*>(.*)</body>", body, re.S | re.I)
        if m:
            body = m.group(1).strip()
            print("본문에 문서 셸이 있어 <body> 안쪽만 썼다.", file=sys.stderr)

    # 본문 안의 <style data-extra>는 그대로 두되, 그 밖의 <style>·<script>는 경고
    stray = [t for t in re.findall(r"<(style|script)\b[^>]*>", body, re.I)
             if "data-extra" not in t]
    if stray:
        print(f"경고: 본문에 {len(stray)}개의 style/script가 있다. "
              "공통 CSS·JS는 base.css/base.js에 있다 — 중복인지 확인하라.",
              file=sys.stderr)

    title = a.title
    if not title:
        m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
        title = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else "리포트"

    out = SHELL.format(title=title, css=css, body=body, js=js)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    open(a.out, "w", encoding="utf-8").write(out)

    print(f"{a.out}  {len(out):,}자 "
          f"(본문 {len(body):,} + CSS {len(css):,} + JS {len(js):,})")
    print("다음: check_html.py 와 lint_render.py 를 돌린다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
