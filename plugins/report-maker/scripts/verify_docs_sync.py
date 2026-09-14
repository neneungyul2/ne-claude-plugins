#!/usr/bin/env python3
"""참조 문서 정합성 검사 — 같은 사실이 두 곳에 적혀 있으면 어긋난다.

플러그인 곳곳에 "이 표는 저기와 동일하다, 한쪽만 고치지 않는다"가 적혀 있다.
그건 규칙일 뿐 검사가 아니었다. 사람이 지키기를 바라는 것으로는 안 지켜진다.

개발용이다. 산출물이 아니라 **플러그인 자신**을 검사한다.
릴리스 전에 돌린다.

사용:
    python3 verify_docs_sync.py [플러그인_루트] [--json]

종료 코드: 0 = FAIL 없음, 1 = FAIL 있음
의존성 없음.
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Report:
    def __init__(self):
        self.rows = []

    def add(self, lv, rule, detail):
        self.rows.append({"level": lv, "rule": rule, "detail": detail})

    fail = lambda s, r, d: s.add("FAIL", r, d)
    warn = lambda s, r, d: s.add("WARN", r, d)
    ok = lambda s, r, d: s.add("OK", r, d)

    @property
    def failed(self):
        return any(x["level"] == "FAIL" for x in self.rows)


def read(root, rel):
    p = os.path.join(root, rel)
    if not os.path.isfile(p):
        return None
    return open(p, encoding="utf-8").read()


def md_files(root):
    """플러그인 안의 모든 텍스트 문서."""
    out = {}
    for base, _, names in os.walk(root):
        if ".git" in base:
            continue
        for n in names:
            if n.endswith((".md", ".py", ".json", ".html")):
                p = os.path.join(base, n)
                out[os.path.relpath(p, root)] = open(p, encoding="utf-8",
                                                     errors="replace").read()
    return out


# ── 검사 ──────────────────────────────────────────────────────────────

def c_plugin_root_paths(root, files, r):
    """${CLAUDE_PLUGIN_ROOT}/... 로 가리킨 파일이 실제로 있는가.

    없는 경로를 가리키면 스킬이 그 지침을 영영 못 읽는다. 조용히 실패한다.
    """
    missing = {}
    for rel, txt in files.items():
        for m in re.finditer(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_\-./]+)", txt):
            target = m.group(1).rstrip(".,)`")
            full = os.path.join(root, target)
            if not (os.path.isfile(full) or os.path.isdir(full)):
                missing.setdefault(target, set()).add(rel)
    if missing:
        ex = "; ".join(f"{t} ({', '.join(sorted(s))[:40]})"
                       for t, s in list(missing.items())[:4])
        r.fail("플러그인 경로 실존", f"{len(missing)}개가 없다: {ex}")
    else:
        r.ok("플러그인 경로 실존", "전부 존재")


def c_frontmatter_name(root, files, r):
    """SKILL.md의 name == 폴더명, agents/X.md의 name == X."""
    bad = []
    for rel, txt in files.items():
        parts = rel.replace("\\", "/").split("/")
        if parts[-1] == "SKILL.md" and len(parts) >= 3 and parts[0] == "skills":
            want = parts[1]
        elif len(parts) == 2 and parts[0] == "agents" and rel.endswith(".md"):
            want = parts[1][:-3]
        else:
            continue
        m = re.match(r"---\n(.*?)\n---", txt, re.S)
        got = re.search(r"^name:\s*(\S+)", m.group(1), re.M) if m else None
        if not m:
            bad.append(f"{rel}: frontmatter 없음")
        elif not got:
            bad.append(f"{rel}: name 없음")
        elif got.group(1) != want:
            bad.append(f"{rel}: name='{got.group(1)}' != '{want}'")
    if bad:
        r.fail("name과 경로 일치", "; ".join(bad[:4]))
    else:
        r.ok("name과 경로 일치", "통과")


def c_spec_version(root, files, r):
    """spec-schema의 '현재 버전' == 필드 표의 값 == 예시 JSON의 spec_version."""
    txt = read(root, "skills/plan-report/references/spec-schema.md")
    if not txt:
        r.warn("spec_version 일치", "spec-schema.md를 못 찾았다")
        return
    head = re.search(r"\*\*현재 버전:\s*([\d.]+)\*\*", txt)
    field = re.search(r"`spec_version`[^|]*\|[^|]*\|\s*현재\s*`\"([\d.]+)\"`", txt)
    if not head:
        r.fail("spec_version 일치", "spec-schema에 '현재 버전'이 없다")
        return
    v = head.group(1)
    bad = []
    if field and field.group(1) != v:
        bad.append(f"필드 표 {field.group(1)} != 머리말 {v}")
    for rel, t in files.items():
        if rel.replace("\\", "/").startswith("references/examples/") and rel.endswith(".json"):
            try:
                got = json.loads(t).get("spec_version")
            except Exception:
                continue
            if got != v:
                bad.append(f"{rel} {got} != {v}")
    # 변경 이력에 그 버전 줄이 있는가
    if not re.search(r"^-\s*%s\s+—" % re.escape(v), txt, re.M):
        bad.append(f"변경 이력에 {v} 항목이 없다")
    if bad:
        r.fail("spec_version 일치", "; ".join(bad[:4]))
    else:
        r.ok("spec_version 일치", f"{v} — 머리말·필드표·예시·이력")


def _mapping_rows(txt, header):
    """question_type → chart 매핑표를 {유형: (기본, 대안)} 으로 읽는다."""
    m = re.search(header + r"(.*?)(?=\n## |\Z)", txt, re.S)
    if not m:
        return None
    out = {}
    for line in m.group(1).split("\n"):
        if not line.startswith("|") or set(line) <= set("|- "):
            continue
        c = [x.strip() for x in line.strip("|").split("|")]
        if len(c) < 4:
            continue
        key = c[0].strip("`*").strip()
        if key in ("question_type", ""):
            continue
        norm = lambda v: re.sub(r"\s+", "", v.replace("`", "").replace("*", ""))
        out[key] = (norm(c[2]), norm(c[3]))
    return out


def c_question_types(root, files, r):
    """chart-rules와 spec-schema의 매핑표가 줄 단위로 같은가.

    두 곳에 같은 표를 두기로 한 결정이라, 어긋나는 것은 시간 문제다.
    """
    ch = read(root, "references/chart-rules.md")
    sp = read(root, "skills/plan-report/references/spec-schema.md")
    if not (ch and sp):
        r.warn("question_type 매핑표", "파일을 못 찾았다")
        return
    a = _mapping_rows(ch, r"## 1\. question_type → chart 매핑")
    b = _mapping_rows(sp, r"## \d+\. question_type → chart 매핑")
    if a is None or b is None:
        r.fail("question_type 매핑표",
               f"표를 못 찾았다 (chart-rules={'O' if a else 'X'}, spec-schema={'O' if b else 'X'})")
        return
    bad = []
    only_a, only_b = sorted(set(a) - set(b)), sorted(set(b) - set(a))
    if only_a:
        bad.append("chart-rules에만: " + ", ".join(only_a))
    if only_b:
        bad.append("spec-schema에만: " + ", ".join(only_b))
    for k in sorted(set(a) & set(b)):
        if a[k] != b[k]:
            bad.append(f"{k}: {a[k]} != {b[k]}")
    if bad:
        r.fail("question_type 매핑표", "; ".join(bad[:4]))
    else:
        r.ok("question_type 매핑표", f"{len(a)}종 전부 일치")


def c_report_types(root, files, r):
    """유형 슬러그가 report-types·spec-schema·check_html.py 세 곳에서 같은가."""
    want = {"diagnostic", "choice", "watch", "track"}
    places = {
        "report-types.md": read(root, "references/report-types.md"),
        "spec-schema.md": read(root, "skills/plan-report/references/spec-schema.md"),
        "check_html.py": read(root, "scripts/check_html.py"),
    }
    bad = []
    for name, txt in places.items():
        if txt is None:
            bad.append(f"{name} 없음")
            continue
        found = {w for w in want if re.search(r"\b%s\b" % w, txt)}
        if found != want:
            bad.append(f"{name}에 없음: {', '.join(sorted(want - found)) or '—'}")
    if bad:
        r.fail("유형 슬러그 3곳 일치", "; ".join(bad))
    else:
        r.ok("유형 슬러그 3곳 일치", ", ".join(sorted(want)))


def c_thresholds(root, files, r):
    """check_html.py의 임계값이 design-rules·chart-rules에 적힌 숫자와 같은가."""
    chk = read(root, "scripts/check_html.py")
    dr = read(root, "references/design-rules.md")
    cr = read(root, "references/chart-rules.md")
    if not (chk and dr and cr):
        r.warn("임계값 일치", "파일을 못 찾았다")
        return

    def const(n):
        m = re.search(r"^%s\s*=\s*(\d+)" % n, chk, re.M)
        return int(m.group(1)) if m else None

    bad = []
    # 타입/라운드 단계 수 == design-rules 표의 행 수
    tbl = re.search(r"\|\s*타입\s*\|.*?\n((?:\|.*\n)+)", dr)
    if tbl:
        rows = tbl.group(1)
        n_t = len(re.findall(r"`--t\d`", rows))
        n_r = len(re.findall(r"`--r\w*`", rows))
        if const("MAX_FONT_SIZES") != n_t:
            bad.append(f"MAX_FONT_SIZES={const('MAX_FONT_SIZES')} != 표의 타입 {n_t}단계")
        if const("MAX_RADII") != n_r:
            bad.append(f"MAX_RADII={const('MAX_RADII')} != 표의 라운드 {n_r}단계")
    else:
        bad.append("design-rules에서 스케일 표를 못 읽었다")

    grid = const("GRID")
    if grid and f"{grid}의 배수" not in dr:
        bad.append(f"GRID={grid}인데 design-rules에 '{grid}의 배수'가 없다")

    rows_n = const("MAX_BODY_TABLE_ROWS")
    if rows_n and f"{rows_n}행" not in cr:
        bad.append(f"MAX_BODY_TABLE_ROWS={rows_n}인데 chart-rules에 '{rows_n}행'이 없다")

    ser = const("MAX_SERIES")
    if ser and f"{ser}계열" not in cr and f"계열 {ser}" not in cr and f"{ser}개 이하" not in cr:
        bad.append(f"MAX_SERIES={ser}인데 chart-rules에 근거 문장이 없다")

    if bad:
        r.fail("임계값 일치", "; ".join(bad[:4]))
    else:
        r.ok("임계값 일치", "스크립트 상수 == 문서 숫자")


def c_version(root, files, r):
    """plugin.json의 version == marketplace.json의 해당 항목."""
    pj = read(root, ".claude-plugin/plugin.json")
    if not pj:
        r.warn("버전 일치", "plugin.json 없음")
        return
    d = json.loads(pj)
    mk_path = os.path.join(os.path.dirname(os.path.dirname(root)),
                           ".claude-plugin", "marketplace.json")
    if not os.path.isfile(mk_path):
        r.warn("버전 일치", "marketplace.json을 못 찾았다 (플러그인만 단독 검사)")
        return
    mk = json.load(open(mk_path, encoding="utf-8"))
    entry = next((p for p in mk.get("plugins", []) if p.get("name") == d["name"]), None)
    if not entry:
        r.fail("버전 일치", f"marketplace에 {d['name']} 항목이 없다")
    elif entry.get("version") != d.get("version"):
        r.fail("버전 일치",
               f"plugin.json {d.get('version')} != marketplace {entry.get('version')}")
    elif entry.get("description") != d.get("description"):
        r.warn("설명 일치", "plugin.json과 marketplace의 description이 다르다")
    else:
        r.ok("버전 일치", d.get("version"))


def c_template_fresh(root, files, r):
    """html-template.html이 template/의 세 조각과 일치하는가.

    생성물이라 원본만 고치고 다시 조립하는 것을 잊기 쉽다.
    """
    import subprocess, tempfile
    gen = os.path.join(root, "references", "html-template.html")
    src = os.path.join(root, "references", "template", "parts.html")
    asm = os.path.join(root, "scripts", "assemble.py")
    if not all(os.path.isfile(p) for p in (gen, src, asm)):
        r.warn("템플릿 최신 여부", "파일을 못 찾았다")
        return
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as t:
        tmp = t.name
    try:
        subprocess.run([sys.executable, asm, src, "-o", tmp, "--title", "{{TITLE}}"],
                       capture_output=True, check=True)
        norm = lambda s: re.sub(r"\s+", " ", re.sub(r"<!--.*?-->", "", s, flags=re.S)).strip()
        if norm(open(tmp, encoding="utf-8").read()) != norm(open(gen, encoding="utf-8").read()):
            r.fail("템플릿 최신 여부",
                   "html-template.html이 template/의 원본과 다르다 — assemble.py를 다시 돌린다")
        else:
            r.ok("템플릿 최신 여부", "조립 결과와 일치")
    except subprocess.CalledProcessError as e:
        r.fail("템플릿 최신 여부", f"조립 실패: {e.stderr.decode()[:80]}")
    finally:
        os.unlink(tmp)


def c_skill_refs(root, files, r):
    """스킬이 서로를 가리킬 때 그 스킬이 실제로 있는가."""
    have = {d for d in os.listdir(os.path.join(root, "skills"))
            if os.path.isdir(os.path.join(root, "skills", d))} \
        if os.path.isdir(os.path.join(root, "skills")) else set()
    agents = {f[:-3] for f in os.listdir(os.path.join(root, "agents"))
              if f.endswith(".md")} if os.path.isdir(os.path.join(root, "agents")) else set()
    bad = []
    for rel, txt in files.items():
        if not rel.endswith(".md"):
            continue
        for m in re.finditer(r"`(report-[a-z\-]+|frame-question|load-data|plan-report|"
                             r"build-html|build-doc|verify-report)`", txt):
            n = m.group(1)
            if n not in have and n not in agents:
                bad.append(f"{rel}: '{n}'")
    if bad:
        uniq = sorted(set(bad))
        r.fail("스킬·에이전트 참조", f"{len(uniq)}건: " + "; ".join(uniq[:4]))
    else:
        r.ok("스킬·에이전트 참조", f"스킬 {len(have)}개, 에이전트 {len(agents)}개")


CHECKS = [c_plugin_root_paths, c_frontmatter_name, c_spec_version, c_question_types,
          c_report_types, c_thresholds, c_version, c_template_fresh, c_skill_refs]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=ROOT)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)

    files = md_files(root)
    r = Report()
    for fn in CHECKS:
        try:
            fn(root, files, r)
        except Exception as e:
            r.warn(fn.__name__, f"검사 실패: {e}")

    if a.json:
        print(json.dumps({"root": root, "failed": r.failed, "results": r.rows},
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
            print("\n같은 사실이 두 곳에 적혀 있으면 언젠가 어긋난다. "
                  "고칠 때 한쪽만 고치지 않는다.")
    return 1 if r.failed else 0


if __name__ == "__main__":
    sys.exit(main())
