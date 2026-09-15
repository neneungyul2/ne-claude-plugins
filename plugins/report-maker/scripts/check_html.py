#!/usr/bin/env python3
"""report-maker 산출물 기계 검사.

모델의 판단이 필요 없는 것만 본다. 판단이 필요한 것(강조가 옳은 곳에 걸렸나,
결론이 데이터에서 나오나)은 이 스크립트가 하지 않는다 — verify-report 스킬이 한다.

사용:
    python3 check_html.py <리포트.html> [--spec report-spec.json] [--json]

종료 코드: 0 = FAIL 없음, 1 = FAIL 있음, 2 = 파일을 못 읽음
표준 출력: 사람이 읽는 표. --json 이면 기계용 JSON.

의존성 없음 (표준 라이브러리만).
"""
import argparse
import json
import os
import re
import sys
from collections import Counter

# ── 임계값. 바꾸려면 references/design-rules.md와 함께 바꾼다 ──────────
MAX_FONT_SIZES = 6       # 폰트 크기 종류 (타입 스케일 6단계)
MAX_RADII = 4            # 모서리 라운드 종류 (카드/패널/칩/알약)
GRID = 4                 # 치수 단위. 이 배수 밖의 값이 'AI가 만든 느낌'을 만든다
GRID_EXEMPT = {1, 2, 999}  # 1px 테두리, 2px 미세선, 999px 알약
MAX_BODY_TABLE_ROWS = 12 # 본문 표 행 수 (chart-rules §5)
MAX_SERIES = 4           # 범례 항목 수 (chart-rules §1-1)
MIN_NUMBER_REPEAT = 3    # 같은 숫자가 몇 번 나오면 중복인가 (design-rules §5)

PLACEHOLDERS = [
    "{{", "계열 A", "계열 B", "짧은 라벨", "{{범주}}", "000.0", "0,000",
    "{{항목}}", "{{지표}}", "{{값}}", "{{그룹", "{{축 ", "{{발견",
    "첫 번째 exhibit의 action_title", "부품 목록이지 레이아웃이 아니다",
]

FOOTNOTE_PARTS = ["출처", "기간", "단위", "집계기준"]


class Report:
    def __init__(self):
        self.rows = []

    def add(self, level, rule, detail):
        self.rows.append({"level": level, "rule": rule, "detail": detail})

    fail = lambda self, r, d: self.add("FAIL", r, d)
    warn = lambda self, r, d: self.add("WARN", r, d)
    ok = lambda self, r, d: self.add("OK", r, d)

    @property
    def failed(self):
        return any(r["level"] == "FAIL" for r in self.rows)


def strip_svg(html):
    """SVG 안은 규칙이 다르다 (text-anchor middle, transform 등)."""
    return re.sub(r"<svg\b.*?</svg>", "", html, flags=re.S | re.I)


def style_blocks(html):
    return "\n".join(re.findall(r"<style\b[^>]*>(.*?)</style>", html, re.S | re.I))


_TABPANEL = re.compile(r'<div\b[^>]*\bclass="[^"]*\btabpanel\b[^"]*"[^>]*>', re.I)


def tab_panels(html):
    """탭이 있으면 [(이름, 조각)], 없으면 [].

    탭은 한 화면이 아니라 여러 화면이다. 수평 논리도 숫자 중복도 **탭 안에서**
    성립하고, 탭 경계를 넘어 세면 요약 탭이 하위 탭을 되풀이하는 정상 구성이
    매번 위반으로 잡힌다. 판정 단위를 탭으로 내린다.
    """
    tags = list(_TABPANEL.finditer(html))
    if len(tags) < 2:
        return []
    out = []
    for i, m in enumerate(tags):
        end = tags[i + 1].start() if i + 1 < len(tags) else len(html)
        name = re.search(r'data-tab="([^"]*)"', m.group(0))
        out.append((name.group(1) if name else str(i + 1), html[m.end():end]))
    return out


def per_tab(fn):
    """탭이 있으면 탭마다, 없으면 전체에 한 번 돈다."""
    def wrapped(html, r):
        panels = tab_panels(html)
        if panels:
            for name, frag in panels:
                fn(frag, r, f" · {name}")
        else:
            fn(html, r, "")
    wrapped.__name__ = fn.__name__
    return wrapped


# ── 개별 검사 ─────────────────────────────────────────────────────────

def c_external(html, r):
    """외부 리소스. 단일 파일 원칙."""
    hits = set()
    for m in re.finditer(r"""(?:src|href)\s*=\s*["'](https?://[^"']+)""", html, re.I):
        hits.add(m.group(1))
    for m in re.finditer(r"""@import\s+(?:url\()?["']?(https?://[^"')]+)""", html, re.I):
        hits.add(m.group(1))
    for m in re.finditer(r"""url\(\s*["']?(https?://[^"')]+)""", html, re.I):
        hits.add(m.group(1))
    if hits:
        r.fail("외부 리소스", f"{len(hits)}건: " + ", ".join(sorted(hits)[:3]))
    else:
        r.ok("외부 리소스", "0건")


def c_placeholder(html, r):
    found = [p for p in PLACEHOLDERS if p in html]
    if found:
        r.fail("템플릿 자리표시자 잔존", ", ".join(found[:6]))
    else:
        r.ok("템플릿 자리표시자", "없음")


def c_korean_break(html, r):
    css = style_blocks(html)
    if "keep-all" not in css:
        r.fail("한국어 줄바꿈", "word-break:keep-all 없음 — 단어 중간이 잘린다")
    else:
        r.ok("한국어 줄바꿈", "keep-all 있음")


def c_darkmode(html, r):
    if "prefers-color-scheme" in html:
        r.fail("다크모드 분기", "보고 문서는 라이트 전용이다")
    else:
        r.ok("다크모드 분기", "없음")


def c_token_inventory(html, r):
    """아티클 #10. 규칙이 아니라 세어보는 검사."""
    css = style_blocks(html)
    sizes = Counter(m.group(1).strip()
                    for m in re.finditer(r"font-size\s*:\s*([^;}\n]+)", css))
    radii = Counter(m.group(1).strip()
                    for m in re.finditer(r"border-radius\s*:\s*([^;}\n]+)", css))
    sizes.pop("inherit", None)
    n_s, n_r = len(sizes), len(radii)
    detail_s = f"{n_s}종 ({', '.join(sorted(sizes))})"
    (r.fail if n_s > MAX_FONT_SIZES else r.ok)(
        f"폰트 크기 종류 ≤{MAX_FONT_SIZES}", detail_s)
    detail_r = f"{n_r}종 ({', '.join(sorted(radii))})"
    (r.fail if n_r > MAX_RADII else r.ok)(
        f"모서리 라운드 종류 ≤{MAX_RADII}", detail_r)


def c_grid(html, r):
    """4px 그리드. 치수가 제각각이면 화면이 동시에 빽빽하고 성기게 느껴진다."""
    css = re.sub(r":root\s*\{.*?\}", "", style_blocks(html), flags=re.S)
    off = sorted({float(m.group(1))
                  for m in re.finditer(r"(?<![\w-])(\d+(?:\.\d+)?)px", css)
                  if float(m.group(1)) not in GRID_EXEMPT
                  and float(m.group(1)) % GRID != 0})
    if off:
        r.fail(f"{GRID}px 그리드",
               f"{len(off)}개 값이 배수가 아니다: "
               + ", ".join(f"{v:g}px" for v in off[:8]))
    else:
        r.ok(f"{GRID}px 그리드", "통과")


def c_hardcoded_color(html, r):
    """토큰 밖 색. :root 정의부는 제외."""
    css = style_blocks(html)
    css_wo_root = re.sub(r":root\s*\{.*?\}", "", css, flags=re.S)
    hexes = set(re.findall(r"#[0-9a-fA-F]{3,8}\b", css_wo_root))
    hexes -= {"#fff", "#ffffff", "#FFF", "#FFFFFF", "#000", "#000000"}
    if hexes:
        r.warn("토큰 밖 색", f"{len(hexes)}개: " + ", ".join(sorted(hexes)[:6]))
    else:
        r.ok("토큰 밖 색", "없음 (var()만 사용)")


def c_rotated_text(html, r):
    hits = re.findall(r"<text[^>]*transform\s*=\s*[\"'][^\"']*rotate", html, re.I)
    hits += re.findall(r"writing-mode\s*:", html, re.I)
    if hits:
        r.fail("기울어진 텍스트", f"{len(hits)}건 — 45°는 52%, 90°는 205% 느리게 읽힌다")
    else:
        r.ok("기울어진 텍스트", "없음")


def c_center_align(html, r):
    css = style_blocks(html)
    n = len(re.findall(r"text-align\s*:\s*center", css))
    if n:
        r.warn("중앙정렬", f"{n}건 — 왼쪽 정렬이 기본이다 (KPI 값은 예외일 수 있다)")
    else:
        r.ok("중앙정렬", "없음")


def c_footnote(html, r):
    """exhibit마다 각주 4요소."""
    blocks = re.findall(r"<section class=\"block\"[^>]*>(.*?)</section>", html, re.S)
    if not blocks:
        r.warn("각주 4요소", "section.block을 못 찾았다 — 구조가 템플릿과 다르다")
        return
    bad = []
    for i, b in enumerate(blocks, 1):
        note = " ".join(re.findall(r"<p class=\"note\"[^>]*>(.*?)</p>", b, re.S))
        missing = [k for k in FOOTNOTE_PARTS if k not in note]
        if missing:
            bad.append(f"#{i}({'/'.join(missing)} 없음)")
    if bad:
        r.fail("각주 4요소", f"{len(bad)}/{len(blocks)} exhibit: " + ", ".join(bad[:4]))
    else:
        r.ok("각주 4요소", f"{len(blocks)}개 exhibit 전부")


@per_tab
def c_hero_list(html, r, tag=""):
    """히어로 요약 항목 수 == exhibit 수 (수평 논리). 탭마다 따로 성립한다."""
    hero = re.search(
        r"<ul[^>]*class=\"[^\"]*\bsummary\b[^\"]*\bsteps\b[^\"]*\"[^>]*>(.*?)</ul>",
        html, re.S)
    n_ex = len(re.findall(r"<div class=\"shead\"", html))
    if not hero:
        if n_ex:
            r.warn(f"히어로 요약{tag}", "summary.steps가 없다 — action_title 목록을 넣는다")
        return
    n_li = len(re.findall(r"<li", hero.group(1)))
    if n_ex and n_li != n_ex:
        r.fail(f"히어로 요약 = exhibit 수{tag}", f"요약 {n_li}개 vs exhibit {n_ex}개")
    else:
        r.ok(f"히어로 요약 = exhibit 수{tag}", f"{n_li}개")


def c_action_title(html, r):
    """주장 하나. em dash로 두 주장 잇기 / 마침표 2개."""
    titles = [re.sub(r"<[^>]+>", "", t).strip()
              for t in re.findall(r"<div class=\"shead\".*?<h2[^>]*>(.*?)</h2>", html, re.S)]
    bad = []
    for t in titles:
        if "—" in t or t.count(".") >= 2 or re.search(r"[이가]고,", t):
            bad.append(t[:40])
        elif t and not re.search(r"[다요]$|[다요][.!?]$", t):
            bad.append(t[:40] + " (서술형 아님?)")
    if bad:
        r.warn("action_title 주장 하나", f"{len(bad)}건: " + " / ".join(bad[:3]))
    elif titles:
        r.ok("action_title 주장 하나", f"{len(titles)}건 통과")


def c_body_table(html, r):
    """본문 표 12행 상한. 모달·드릴다운 안은 제외."""
    body = html
    for pat in (r"<div class=\"mask\".*?</div>\s*$", r"<div class=\"drill\".*?</div>"):
        body = re.sub(pat, "", body, flags=re.S)
    over = []
    for i, t in enumerate(re.findall(r"<table\b.*?</table>", body, re.S), 1):
        n = len(re.findall(r"<tr\b", re.sub(r"<thead\b.*?</thead>", "", t, flags=re.S)))
        if n > MAX_BODY_TABLE_ROWS:
            over.append(f"표{i}: {n}행")
    if over:
        r.fail(f"본문 표 ≤{MAX_BODY_TABLE_ROWS}행", ", ".join(over) + " — 묶고 전량은 모달로")
    else:
        r.ok(f"본문 표 ≤{MAX_BODY_TABLE_ROWS}행", "통과")


def c_legend_series(html, r):
    for i, lg in enumerate(re.findall(r"<div class=\"legend\"[^>]*>(.*?)</div>", html, re.S), 1):
        n = len(re.findall(r"<span", lg))
        if n > MAX_SERIES:
            r.warn(f"계열 수 ≤{MAX_SERIES}", f"범례{i}: {n}개 — 묶거나 small multiples로")
            return
    r.ok(f"계열 수 ≤{MAX_SERIES}", "통과")


@per_tab
def c_number_repeat(html, r, tag=""):
    """같은 숫자가 화면 여러 곳에. design-rules §5.

    탭마다 센다. 요약 탭이 하위 탭의 수치를 다시 보이는 것은 중복이 아니라
    구성이다 — 한 화면에 두 번 나오는 것만 잡는다.
    """
    text = re.sub(r"<[^>]+>", " ", strip_svg(html))
    nums = re.findall(r"\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b|\b\d+\.\d+\b", text)
    nums = [n for n in nums if n not in {"0.0", "1.0", "100.0"}]
    dup = {n: c for n, c in Counter(nums).items() if c >= MIN_NUMBER_REPEAT}
    if dup:
        top = sorted(dup.items(), key=lambda kv: -kv[1])[:4]
        r.warn(f"같은 숫자 반복{tag}",
               ", ".join(f"{n}×{c}" for n, c in top) + " — 숫자마다 자리를 하나만 준다")
    else:
        r.ok(f"같은 숫자 반복{tag}", "없음")


def c_glossary(html, r):
    used = set(re.findall(r"data-term\s*=\s*[\"']([^\"']+)", html))
    gl = re.search(r"var\s+GLOSSARY\s*=\s*\{(.*?)\n\s*\};", html, re.S)
    defined = set(re.findall(r"[\"']?([A-Za-z0-9_\-]+)[\"']?\s*:\s*\{", gl.group(1))) if gl else set()
    missing = used - defined
    if missing:
        r.fail("용어 등록", "툴팁은 있는데 GLOSSARY에 없다: " + ", ".join(sorted(missing)))
    elif used:
        r.ok("용어 등록", f"{len(used)}개 전부 등록")
    else:
        r.warn("용어 등록", "abbr.term이 하나도 없다 — 축약어·사내 용어가 정말 없는가")


def c_spec_match(html, spec, r):
    """스펙과 화면 대조. --spec 을 준 경우만."""
    titles = [re.sub(r"<[^>]+>", "", t).strip()
              for t in re.findall(r"<div class=\"shead\".*?<h2[^>]*>(.*?)</h2>", html, re.S)]
    want = [e.get("action_title", "").strip() for e in spec.get("exhibits", [])]
    miss = [w for w in want if w and w not in " ".join(titles)]
    if miss:
        r.fail("스펙 action_title 일치", f"{len(miss)}건이 화면에 없거나 바뀌었다: {miss[0][:40]}")
    elif want:
        r.ok("스펙 action_title 일치", f"{len(want)}건")

    kt = spec.get("key_takeaway", {}) or {}
    for e in spec.get("exhibits", []):
        for v in e.get("views", []):
            enc = v.get("encoding", {}) or {}
            claim = enc.get("claim")
            if not claim:
                r.warn("encoding.claim", f"{e.get('id','?')}/{v.get('id','?')}: 비어 있다 — "
                       "주장을 만드는 값이 무엇인지 적는다")
            elif claim not in (enc.get("x"), enc.get("y")):
                r.fail("encoding.claim이 위치·길이에", f"{e.get('id','?')}/{v.get('id','?')}: "
                       f"claim='{claim}' 인데 x='{enc.get('x')}' y='{enc.get('y')}'")

    for em in kt.get("emphasis", []):
        if em and em not in kt.get("text", ""):
            r.fail("emphasis 부분 문자열", f"'{em}' 이 key_takeaway.text 에 없다")

    n_primary = sum(1 for e in spec.get("exhibits", []) if e.get("weight") == "primary")
    rtype = spec.get("report_type")
    if n_primary > 1:
        r.fail("weight: primary 는 하나", f"{n_primary}개 — 결론이 둘이라는 뜻이다")
    elif spec.get("exhibits") and n_primary == 0 and rtype not in ("watch", "choice"):
        r.warn("weight: primary 는 하나", "primary가 없다 — 가장 큰 자리를 누가 갖는가")

    # report_type이 바꾸는 필수 (references/report-types.md §3)
    if spec.get("mode") == "report" and not rtype:
        r.fail("report_type", "report 모드인데 유형이 없다 — frame-question에서 정한다")
    if rtype and rtype not in ("diagnostic", "choice", "watch", "track"):
        r.fail("report_type", f"알 수 없는 값: {rtype}")
    if rtype == "watch":
        if (spec.get("brief") or {}).get("tension"):
            r.warn("유형별 해당 없음", "watch인데 tension이 있다 — 억지로 만든 긴장인지 본다")
        if (spec.get("brief") or {}).get("three_minute_story"):
            r.warn("유형별 해당 없음", "watch인데 three_minute_story가 있다")
    elif rtype in ("diagnostic", "choice"):
        b = spec.get("brief") or {}
        for k in ("tension", "three_minute_story"):
            if not b.get(k):
                r.fail(f"{rtype} 필수", f"brief.{k}가 없다")
        # stance: data_only — 수신자가 판단·제안을 빼라고 한 보고.
        # 없는 것이 정답이므로 감점하지 않는다 (report-types.md §3).
        if (spec.get("stance") or b.get("stance") or "judgment") == "data_only":
            if kt.get("ask") or spec.get("actions"):
                r.warn("stance: data_only",
                       "판단·제안을 빼라고 한 보고인데 ask/actions가 남아 있다")
            else:
                r.ok("stance: data_only", "ask·actions 없음 — 요청대로다")
        else:
            if not kt.get("ask"):
                r.fail(f"{rtype} 필수", "key_takeaway.ask가 없다 — 발견에서 끝났다")
            if not spec.get("actions"):
                r.fail(f"{rtype} 필수", "actions가 비어 있다")


# 템플릿(부품 목록)에도 도는 검사 — CSS 스케일·구조
STRUCTURAL = [c_external, c_korean_break, c_darkmode, c_token_inventory, c_grid,
              c_hardcoded_color, c_rotated_text, c_center_align, c_footnote,
              c_body_table, c_legend_series]
# 실제 리포트에만 도는 검사 — 내용이 채워졌는지
CONTENT = [c_placeholder, c_hero_list, c_action_title, c_number_repeat, c_glossary]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--spec", help="report-spec.json 경로. 주면 스펙 대조까지 한다")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--template", action="store_true",
                    help="html-template.html 자체를 볼 때. 자리표시자 검사를 건너뛴다")
    a = ap.parse_args()

    if not os.path.isfile(a.html):
        print(f"파일이 없다: {a.html}", file=sys.stderr)
        return 2
    html = open(a.html, encoding="utf-8", errors="replace").read()

    r = Report()
    checks = STRUCTURAL if a.template else STRUCTURAL + CONTENT
    for fn in checks:
        try:
            fn(html, r)
        except Exception as e:  # 검사 하나가 죽어도 나머지는 돈다
            r.warn(fn.__name__, f"검사 실패: {e}")
    if a.spec and os.path.isfile(a.spec):
        try:
            c_spec_match(html, json.load(open(a.spec, encoding="utf-8")), r)
        except Exception as e:
            r.warn("스펙 대조", f"검사 실패: {e}")

    if a.json:
        print(json.dumps({"file": a.html, "failed": r.failed, "results": r.rows},
                         ensure_ascii=False, indent=2))
    else:
        order = {"FAIL": 0, "WARN": 1, "OK": 2}
        w = max((len(x["rule"]) for x in r.rows), default=10)
        for x in sorted(r.rows, key=lambda x: order[x["level"]]):
            print(f"{x['level']:<4} │ {x['rule']:<{w}} │ {x['detail']}")
        n_f = sum(1 for x in r.rows if x["level"] == "FAIL")
        n_w = sum(1 for x in r.rows if x["level"] == "WARN")
        print(f"\nFAIL {n_f} · WARN {n_w} · OK {len(r.rows) - n_f - n_w}")
        if n_f:
            print("\nFAIL이 남은 채로 전달하지 않는다.")
        print("이 스크립트는 판단이 필요 없는 것만 본다. "
              "강조가 옳은 곳에 걸렸는지, 결론이 데이터에서 나오는지는 verify-report가 본다.")
    return 1 if r.failed else 0


if __name__ == "__main__":
    sys.exit(main())
