#!/usr/bin/env python3
"""report-maker 산출물 렌더 검사 — 실제로 그려본 뒤 픽셀을 잰다.

`check_html.py`는 소스를 읽는다. 이 스크립트는 **브라우저로 칠해본다.**
잘린 글자·겹친 라벨·넘치는 폭은 소스로는 안 보이고, 사람이 스크린샷을 봐야 알던 것이다.
그걸 기계로 내린다. 사람의 눈은 "강조가 옳은 곳에 걸렸나"에 써야 한다.

사용:
    python3 lint_render.py <리포트.html> [--json] [--shot out.png]

종료 코드: 0 = FAIL 없음, 1 = FAIL 있음, 2 = 파일/의존성 문제

의존성: playwright (`pip install playwright && playwright install chromium`).
없으면 종료 코드 2와 설치 안내를 낸다 — 조용히 통과시키지 않는다.
"""
import argparse
import json
import os
import sys

# ── 임계값 ─────────────────────────────────────────────────────────────
DESKTOP = (1280, 1400)
MOBILE = (400, 900)
CLIP_TOL = 2          # px. 브라우저 반올림 여유
OVERLAP_TOL = 1.0     # px. 이만큼 겹치면 겹친 것으로 본다
MIN_INK_RATIO = 0.18  # 차트 잉크가 플롯 영역에서 차지하는 최소 비율
FALLBACK_STACK = "'Malgun Gothic','Apple SD Gothic Neo',sans-serif"

# 브라우저 안에서 도는 측정 스크립트. 파이썬으로 못 하는 것만 여기서 한다.
PROBE = r"""
() => {
  const out = {clipped: [], overflowX: null, svgOut: [], overlap: [], ink: [], tiny: []};

  // ① HTML 텍스트 잘림 — 실제 내용이 상자보다 큰가
  for (const el of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(el);
    if (cs.overflow === 'visible' && cs.overflowX === 'visible') continue;
    if (el.closest('.mask, [hidden]')) continue;
    if (el.scrollWidth > el.clientWidth + %(tol)d && el.clientWidth > 0) {
      // overflow-x:auto 로 스크롤을 허용한 컨테이너는 의도된 것이다
      if (cs.overflowX === 'auto' || cs.overflowX === 'scroll') continue;
      out.clipped.push({tag: el.tagName.toLowerCase(), cls: el.className || '',
                        text: (el.textContent || '').trim().slice(0, 40),
                        need: el.scrollWidth, have: el.clientWidth});
    }
  }

  // ② 페이지 가로 넘침
  out.overflowX = {doc: document.documentElement.scrollWidth, win: window.innerWidth};

  // ③~⑤ SVG: viewBox 밖으로 나간 텍스트, 겹친 텍스트, 잉크 비율
  document.querySelectorAll('svg').forEach((svg, si) => {
    const vb = svg.viewBox && svg.viewBox.baseVal;
    if (!vb || !vb.width) return;
    const texts = [...svg.querySelectorAll('text')];
    const boxes = [];
    for (const t of texts) {
      if (t.closest('[hidden]')) continue;
      let b; try { b = t.getBBox(); } catch (e) { continue; }
      if (!b.width) continue;
      const label = (t.textContent || '').trim().slice(0, 30);
      boxes.push({b, label});
      if (b.x < vb.x - %(tol)d || b.x + b.width > vb.x + vb.width + %(tol)d ||
          b.y < vb.y - %(tol)d || b.y + b.height > vb.y + vb.height + %(tol)d) {
        out.svgOut.push({svg: si, label,
                         box: [Math.round(b.x), Math.round(b.y),
                               Math.round(b.width), Math.round(b.height)],
                         vb: [vb.x, vb.y, vb.width, vb.height]});
      }
      const fs = parseFloat(getComputedStyle(t).fontSize);
      if (fs && fs < 9) out.tiny.push({svg: si, label, size: fs});
    }
    for (let i = 0; i < boxes.length; i++)
      for (let j = i + 1; j < boxes.length; j++) {
        const a = boxes[i].b, c = boxes[j].b;
        const ox = Math.min(a.x + a.width, c.x + c.width) - Math.max(a.x, c.x);
        const oy = Math.min(a.y + a.height, c.y + c.height) - Math.max(a.y, c.y);
        if (ox > %(ovl)s && oy > %(ovl)s)
          out.overlap.push({svg: si, a: boxes[i].label, b: boxes[j].label,
                            ox: Math.round(ox), oy: Math.round(oy)});
      }

    // 잉크 비율 — 데이터 마크가 차지하는 넓이 / viewBox 넓이
    let ink = 0;
    for (const m of svg.querySelectorAll('rect,circle,path,polygon,line')) {
      let b; try { b = m.getBBox(); } catch (e) { continue; }
      ink += Math.max(b.width, 1) * Math.max(b.height, 1);
    }
    out.ink.push({svg: si, ratio: ink / (vb.width * vb.height),
                  marks: svg.querySelectorAll('rect,circle,path,polygon').length});
  });
  return out;
}
""" % {"tol": CLIP_TOL, "ovl": OVERLAP_TOL}


class Report:
    def __init__(self):
        self.rows = []

    def add(self, level, rule, detail):
        self.rows.append({"level": level, "rule": rule, "detail": detail})

    fail = lambda s, r, d: s.add("FAIL", r, d)
    warn = lambda s, r, d: s.add("WARN", r, d)
    ok = lambda s, r, d: s.add("OK", r, d)

    @property
    def failed(self):
        return any(x["level"] == "FAIL" for x in self.rows)


def judge(r, probe, label, strict=True):
    """한 번의 렌더 결과를 판정한다. strict=False면 FAIL 대신 WARN."""
    lv = r.fail if strict else r.warn

    cl = probe["clipped"]
    if cl:
        ex = ", ".join(f"{c['text'] or c['cls']}({c['need']}>{c['have']})" for c in cl[:4])
        lv(f"{label} 글자 잘림", f"{len(cl)}건: {ex}")
    else:
        r.ok(f"{label} 글자 잘림", "없음")

    ox = probe["overflowX"]
    if ox["doc"] > ox["win"] + CLIP_TOL:
        lv(f"{label} 가로 스크롤", f"문서 {ox['doc']}px > 화면 {ox['win']}px")
    else:
        r.ok(f"{label} 가로 스크롤", "없음")

    so = probe["svgOut"]
    if so:
        ex = ", ".join(f"'{s['label']}'" for s in so[:4])
        lv(f"{label} 차트 밖으로 나간 라벨", f"{len(so)}건: {ex}")
    else:
        r.ok(f"{label} 차트 라벨 범위", "통과")

    ov = probe["overlap"]
    if ov:
        ex = ", ".join(f"'{o['a']}'↔'{o['b']}'" for o in ov[:4])
        lv(f"{label} 라벨 겹침", f"{len(ov)}쌍: {ex}")
    else:
        r.ok(f"{label} 라벨 겹침", "없음")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--shot", help="전체 스크린샷을 이 경로에 저장한다")
    ap.add_argument("--no-fallback", action="store_true",
                    help="폰트 폴백 검사를 건너뛴다")
    ap.add_argument("--quick", action="store_true",
                    help="데스크톱 1회만. 표현 수정 루프용 — 전달 전에는 전체를 돈다")
    a = ap.parse_args()

    if not os.path.isfile(a.html):
        print(f"파일이 없다: {a.html}", file=sys.stderr)
        return 2
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright가 없다. 설치:\n"
              "  pip install playwright && playwright install chromium\n"
              "설치할 수 없는 환경이면 이 검사는 건너뛰되, "
              "verify-report의 눈 검사를 반드시 돈다.", file=sys.stderr)
        return 2

    url = "file://" + os.path.abspath(a.html)
    r = Report()
    js_err, req_fail, con_err = [], [], []

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": DESKTOP[0], "height": DESKTOP[1]})
        pg.on("pageerror", lambda e: js_err.append(str(e)[:120]))
        pg.on("console", lambda m: con_err.append(m.text[:120]) if m.type == "error" else None)
        pg.on("requestfailed", lambda q: req_fail.append(q.url[:120]))
        pg.goto(url, wait_until="load")
        pg.wait_for_timeout(700)

        probe = pg.evaluate(PROBE)
        judge(r, probe, "데스크톱")

        tiny = probe["tiny"]
        if tiny:
            r.fail("차트 글자 크기",
                   ", ".join(f"'{t['label']}' {t['size']:g}px" for t in tiny[:4])
                   + " — 9px 미만은 인쇄·축소에서 사라진다")
        else:
            r.ok("차트 글자 크기", "9px 이상")

        ink = probe["ink"]
        thin = [i for i in ink if i["marks"] >= 2 and i["ratio"] < MIN_INK_RATIO]
        if thin:
            r.warn("차트 여백 과다",
                   ", ".join(f"svg{i['svg']}: 잉크 {i['ratio']*100:.0f}%" for i in thin[:4])
                   + " — 가장 큰 자리를 차지했다면 축 범위를 분포에 맞춘다")
        elif ink:
            r.ok("차트 여백", f"{len(ink)}개 차트 통과")

        if a.shot:
            pg.screenshot(path=a.shot, full_page=True)

        # 모바일 — 가로 스크롤이 핵심
        if a.quick:
            b.close()
            return _emit(r, a, js_err, req_fail, con_err, quick=True)
        pg.set_viewport_size({"width": MOBILE[0], "height": MOBILE[1]})
        pg.wait_for_timeout(400)
        judge(r, pg.evaluate(PROBE), "모바일 400px")

        # 폰트 폴백 — Pretendard가 없는 PC에서 무너지는가
        if not a.no_fallback:
            pg.set_viewport_size({"width": DESKTOP[0], "height": DESKTOP[1]})
            pg.add_style_tag(content="*{font-family:%s !important}" % FALLBACK_STACK)
            pg.wait_for_timeout(400)
            judge(r, pg.evaluate(PROBE), "폰트 폴백", strict=False)

        b.close()

    return _emit(r, a, js_err, req_fail, con_err)


def _emit(r, a, js_err, req_fail, con_err, quick=False):
    """페이지 수준 결과를 보태고 출력한다."""
    if js_err:
        r.fail("JS 에러", f"{len(js_err)}건: {js_err[0]}")
    else:
        r.ok("JS 에러", "없음")
    if req_fail:
        r.fail("요청 실패", f"{len(req_fail)}건: {req_fail[0]} — 단일 파일이어야 한다")
    else:
        r.ok("요청 실패", "없음")
    if con_err:
        r.warn("콘솔 error", f"{len(con_err)}건: {con_err[0]}")

    if a.json:
        print(json.dumps({"file": a.html, "quick": quick, "failed": r.failed,
                          "results": r.rows}, ensure_ascii=False, indent=2))
    else:
        order = {"FAIL": 0, "WARN": 1, "OK": 2}
        w = max((len(x["rule"]) for x in r.rows), default=10)
        for x in sorted(r.rows, key=lambda x: order[x["level"]]):
            print(f"{x['level']:<4} │ {x['rule']:<{w}} │ {x['detail']}")
        n_f = sum(1 for x in r.rows if x["level"] == "FAIL")
        n_w = sum(1 for x in r.rows if x["level"] == "WARN")
        print(f"\nFAIL {n_f} · WARN {n_w} · OK {len(r.rows) - n_f - n_w}")
        if quick:
            print("빠른 모드 — 데스크톱만 봤다. "
                  "전달 전에는 --quick 없이 한 번 전부 돌린다.")
        else:
            print("폰트 폴백은 WARN이다 — Pretendard가 없는 PC에서 이렇게 보인다는 뜻이고,\n"
                  "사내 배포라면 고치는 쪽이 맞다.")
    return 1 if r.failed else 0


if __name__ == "__main__":
    sys.exit(main())
