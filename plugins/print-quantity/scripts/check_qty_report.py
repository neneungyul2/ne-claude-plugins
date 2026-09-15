#!/usr/bin/env python3
"""제작 수량 검토 보고서 정합 검사 (신간·기간본).

    python3 check_qty_report.py <보고서.html>

검사 항목
  1. getElementById 참조가 HTML에 존재하는지
  2. 중복 id
  3. 스크립트 문법 (node가 있으면)
  4. 초기 표시값과 render() 산출값 일치 여부  ← 가장 많이 틀리는 곳
  5. 본문의 퍼센트 표기를 뽑아 대조할 수 있게 나열
  6. 기간본이면 — 계절지수 합, 가용재고와 창고 목록의 정합

데이터 블록을 보고 신간(BOOKS/TAM_EST)인지 기간본(ITEMS/SEASON)인지 스스로 가른다.

종료 코드 0이면 통과.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FAIL = []
WARN = []
SKIP_COMPUTE = []


def fail(msg):
    FAIL.append(msg)


def warn(msg):
    WARN.append(msg)


def main(path: Path) -> int:
    html = path.read_text(encoding="utf-8")

    if "<script>" not in html:
        fail("스크립트 블록이 없습니다.")
        return report()
    js = html[html.index("<script>") + len("<script>"): html.index("</script>")]

    # ── 1·2. id 참조 ────────────────────────────────────────────
    used = set(re.findall(r'getElementById\("([^"]+)"\)', html))
    used |= set(re.findall(r'\$\("([^"]+)"\)', html))   # $("id") 축약형도 참조로 본다
    ids = re.findall(r'id="([^"]+)"', html)
    idset = set(ids)

    missing = sorted(used - idset)
    if missing:
        fail(f"HTML에 없는 id를 참조합니다: {', '.join(missing)}")

    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        fail(f"중복된 id: {', '.join(dup)}")

    unused = sorted(i for i in idset - used
                    if i.startswith(("c_", "ch", "sl", "t_", "sam", "som", "need", "qty", "delta")))
    if unused:
        warn(f"스크립트가 쓰지 않는 계산용 id: {', '.join(unused)}")

    # ── 3. 문법 ────────────────────────────────────────────────
    node = shutil.which("node")
    if node:
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(js)
            tmp = f.name
        r = subprocess.run([node, "--check", tmp], capture_output=True, text=True)
        if r.returncode != 0:
            fail("스크립트 문법 오류\n" + r.stderr.strip()[:500])
    else:
        warn("node가 없어 문법 검사와 수치 검산을 건너뜁니다.")

    # ── 4. 초기 표시값 대조 ────────────────────────────────────
    if node:
        kind = "reprint" if "var ITEMS" in js and "var SEASON" in js else "launch"
        if kind == "reprint":
            check_reprint_data(js)
            computed = compute_reprint(js)
        elif re.search(r"K_EST\s*=\s*0\b", js) or re.search(r"TAM_EST\s*=\s*0\b", js):
            warn("데이터 블록이 비어 있습니다 (K_EST·TAM_EST가 0). "
                 "템플릿 원본이면 정상이고, 보고서면 3단계 계수를 먼저 채우세요.")
            computed = None
            SKIP_COMPUTE.append(1)
        else:
            computed = compute(js)
        if computed is None and not SKIP_COMPUTE:
            warn("데이터 블록을 파싱하지 못해 수치 검산을 건너뜁니다.")
        if computed is None:
            pass
        else:
            for key, expected in computed.items():
                m = re.search(r'id="%s"[^>]*>([^<]*)' % re.escape(key), html)
                if not m:
                    continue
                shown = norm(m.group(1))
                want = norm(f"{expected:,}" if isinstance(expected, int) else str(expected))
                if shown and shown != want:
                    fail(f'초기 표시값 불일치 — id="{key}" 화면 {shown} / 계산 {want}')

    # ── 5. 퍼센트 표기 나열 ────────────────────────────────────
    body = html[: html.index('<div id="ctl">')] if '<div id="ctl">' in html else html
    body = re.sub(r"<style[\s\S]*?</style>", " ", body)
    body = re.sub(r"<script[\s\S]*?</script>", " ", body)
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body))
    pcts = re.findall(r"[^.。]{0,70}\d[\d,.]*\s?%[^.。]{0,40}", text)
    hardcoded = [x.strip() for x in pcts if "px" not in x and "var(" not in x]
    if hardcoded:
        print("본문 퍼센트 표기 — 실제 값과 대조하세요")
        for p in hardcoded:
            print("   ·", p[:150])
        print()

    return report()


def compute(js: str):
    """데이터 블록만 떼어내 브라우저와 같은 반올림으로 계산한다."""
    def grab(pattern):
        m = re.search(pattern, js, re.S)
        return m.group(0) if m else ""

    books = grab(r"var BOOKS = \[[\s\S]*?\n  \];")
    consts = grab(r"var TAM_EST[\s\S]*?;\n")
    scen = grab(r"var SCENARIOS = \[[\s\S]*?\n  \];")
    if not (books and consts and scen):
        return None

    script = books + consts + scen + r"""
    var S = function(a){ return a.reduce(function(x,b){ return x+b.v; }, 0); };
    var B = BOOKS.filter(function(b){ return b.g==="b"; });
    var T = BOOKS.filter(function(b){ return b.g==="t"; });
    var estB = S(B), estT = S(T), hard = S(BOOKS.filter(function(b){ return b.hard; }));
    var toShip = function(e){ return e / K_EST * K_YEAR * K_SHIP; };
    var r1000 = function(x){ return Math.round(x/1000)*1000; };
    var r100  = function(x){ return Math.round(x/100)*100; };
    var base = SCENARIOS.filter(function(x){ return x.pick; })[0] || SCENARIOS[1];
    var samB = toShip(estB), samT = toShip(estT);
    var somB = samB * base.b;
    var somT = hard > 0
      ? toShip(hard)*(base.t/2) + toShip(estT-hard)*base.t
      : samT * base.t;
    var needB = somB*K_FIRST, needT = somT*K_FIRST;
    var onB = needB*ONLINE, onT = needT*ONLINE;
    var usesInit = typeof INIT !== "undefined" && INIT > 0;
    var rawB = usesInit ? INIT + r100(onB)*K_PRINT : needB*K_PRINT;
    var rawT = usesInit ? INIT + r100(onT)*K_PRINT : needT*K_PRINT;
    console.log(JSON.stringify({
      samBasic:  r1000(samB),       samType:   r1000(samT),
      somVal:    r1000(somB+somT),  somFirst:  r1000((somB+somT)*K_FIRST),
      needBasic: r100(needB),       needType:  r100(needT),
      chOnBv:    r100(onB),         chOnTv:    r100(onT),
      chOffBv:   r100(needB-onB),   chOffTv:   r100(needT-onT),
      c_finB:    r1000(r100(rawB)), c_finT:    r1000(r100(rawT)),
      qtyBasic:  r1000(r100(rawB)), qtyType:   r1000(r100(rawT))
    }));
    """
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(script)
        tmp = f.name
    r = subprocess.run([shutil.which("node"), tmp], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout.strip())
    except json.JSONDecodeError:
        return None


# ── 기간본 ────────────────────────────────────────────────────

DOM_SHIM = r"""
var __OUT = {};
function __el(id){
  return {
    _id:id,
    set textContent(v){ __OUT[id] = String(v); },
    get textContent(){ return __OUT[id] || ""; },
    set innerHTML(v){ __OUT[id] = String(v).replace(/<[^>]+>/g," ").replace(/\s+/g," ").trim(); },
    get innerHTML(){ return __OUT[id] || ""; },
    set value(v){ this._v = v; }, get value(){ return this._v; },
    set className(v){ this._c = v; }, get className(){ return this._c || ""; },
    set hidden(v){ this._h = v; }, get hidden(){ return !!this._h; },
    classList:{ add:function(){}, remove:function(){}, toggle:function(){ return false; } },
    addEventListener:function(){}, setAttribute:function(){}, getAttribute:function(){ return null; },
    closest:function(){ return null; }, getBoundingClientRect:function(){ return {left:0,bottom:0}; },
    style:{}
  };
}
var __cache = {};
var document = {
  getElementById:function(id){ return __cache[id] || (__cache[id] = __el(id)); },
  querySelectorAll:function(){ return []; },
  addEventListener:function(){}
};
var window = { innerWidth: 1200 };
"""


def check_reprint_data(js: str):
    """기간본 데이터 블록 자체의 정합."""
    m = re.search(r"var SEASON\s*=\s*\[([^\]]*)\]", js)
    if m:
        try:
            vals = [float(x) for x in m.group(1).split(",") if x.strip()]
        except ValueError:
            vals = []
        if len(vals) != 12:
            fail(f"SEASON은 12개여야 합니다 (현재 {len(vals)}개).")
        elif abs(sum(vals) - 1) > 0.005:
            fail(f"계절지수 합이 1이 아닙니다 ({sum(vals):.3f}). 산출이 틀렸다는 신호입니다.")

    stocks = [int(x) for x in re.findall(r"stock:\s*(\d+)", js)]
    wh = re.findall(r"qty:\s*(\d+),\s*use:\s*(true|false)", js)
    if stocks and wh:
        wh_use = sum(int(q) for q, u in wh if u == "true")
        if wh_use != sum(stocks):
            fail(f"가용재고 불일치 — ITEMS.stock 합 {sum(stocks):,} / "
                 f"WAREHOUSE use:true 합 {wh_use:,}. 창고 분류를 다시 보세요.")

    if "E:" not in js:
        warn("개정·폐간 예정(E)이 한 종도 없습니다. '없음'으로 확인받은 것이 맞습니까.")


def compute_reprint(js: str):
    """템플릿의 스크립트를 DOM 대역으로 그대로 돌려 render() 결과를 받는다."""
    node = shutil.which("node")
    if not node:
        return None
    script = DOM_SHIM + "\n" + js + "\nconsole.log(JSON.stringify(__OUT));"
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(script)
        tmp = f.name
    r = subprocess.run([node, tmp], capture_output=True, text=True)
    if r.returncode != 0:
        warn("render()를 대역 DOM으로 돌리지 못했습니다:\n" + r.stderr.strip()[:400])
        return None
    try:
        out = json.loads(r.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        return None
    # 숫자만 든 값은 그대로, 나머지는 문자열 비교
    return {k: v for k, v in out.items() if v}


ENT = {"&mdash;": "—", "&middot;": "·", "&minus;": "−", "&nbsp;": " ", "&amp;": "&"}


def norm(x: str) -> str:
    """표시값 비교용 정규화 — 엔티티·단위·공백을 지운다."""
    x = str(x)
    for k, v in ENT.items():
        x = x.replace(k, v)
    x = x.replace("부", "")
    return re.sub(r"\s+", " ", x).strip()


def report() -> int:
    for w in WARN:
        print("주의 ·", w)
    if FAIL:
        for f in FAIL:
            print("실패 ·", f)
        print(f"\n{len(FAIL)}건 실패. 고치고 다시 돌리세요.")
        return 1
    print("통과. 전달해도 됩니다.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1])))
