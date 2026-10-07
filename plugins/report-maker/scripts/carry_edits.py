#!/usr/bin/env python3
"""refresh 때 작성자가 화면에서 고친 기록(rm-edits)을 새 산출물로 옮긴다.

refresh는 구성을 그대로 두고 숫자만 갈아끼운다. 그래서 단락 번호·편집 대상 번호가
그대로이고, 고친 글·순서·숨김·배치를 그대로 옮길 수 있다.

단, **숫자가 들어간 문장을 고쳤다면** 그 숫자는 새 데이터와 어긋날 수 있다.
그 문장들을 골라 보여준다. 사람이 다시 보고 고친다 — 이 스크립트가 고치지 않는다.

사용:
    python3 carry_edits.py <이전.html> <새.content.html>

새 본문(.content.html)에 rm-edits 블록을 넣어 둔다. 그다음 assemble.py로 조립한다.
의존성 없음.
"""
import json
import re
import sys

PAT = re.compile(r'(<script type="application/json" id="rm-edits">)(.*?)(</script>)', re.S)


def main():
    if len(sys.argv) != 3:
        print(__doc__.strip().splitlines()[-4], file=sys.stderr)
        return 2
    old = open(sys.argv[1], encoding="utf-8").read()
    m = PAT.search(old)
    if not m:
        print("이전 산출물에 편집 기록이 없다 — 옮길 것이 없다.")
        return 0
    try:
        edits = json.loads(m.group(2) or "{}")
    except json.JSONDecodeError:
        print("이전 편집 기록을 읽지 못했다 — 옮기지 않는다.", file=sys.stderr)
        return 1
    if not any(edits.get(k) for k in ("text", "order", "hidden", "layout")):
        print("이전 편집 기록이 비어 있다 — 옮길 것이 없다.")
        return 0

    new_path = sys.argv[2]
    new = open(new_path, encoding="utf-8").read()
    block = m.group(1) + json.dumps(edits, ensure_ascii=False).replace("<", "\\u003c") + m.group(3)
    new = PAT.sub(lambda _: block, new) if PAT.search(new) else new.rstrip() + "\n" + block + "\n"
    open(new_path, "w", encoding="utf-8").write(new)

    txt = edits.get("text") or {}
    with_num = {k: re.sub(r"<[^>]+>", "", v) for k, v in txt.items() if re.search(r"\d", v)}
    print(f"편집 기록을 옮겼다 — 고친 글 {len(txt)}곳, 순서 변경 {'있음' if edits.get('order') else '없음'}, "
          f"숨긴 단락 {len(edits.get('hidden') or [])}개")
    if with_num:
        print(f"\n숫자가 든 문장 {len(with_num)}곳은 새 데이터와 어긋날 수 있다. 다시 보고 고친다:")
        for k, v in with_num.items():
            print(f"  [{k}] {v[:80]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
