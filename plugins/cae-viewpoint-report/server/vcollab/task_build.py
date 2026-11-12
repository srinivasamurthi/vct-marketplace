# ---------------------------------------------------------------------------
# task_build.py - viewpoint MD file  ->  CAX with (rich) viewpoints  +  WCAX.
# JOB: {job_dir, cax, md, out_cax, out_wcax (or ""), assets_dir, rich (bool),
#       screenshots (bool), viewpath (optional override)}
# Runs inside VCollab Pro's embedded Python (yaml, matplotlib, numpy, PIL available).
# ---------------------------------------------------------------------------
import html as _html
import yaml

BLUE, RED, ORANGE, GREEN, GREY = "#1f4e79", "#c0392b", "#b35900", "#00802b", "#5f6873"
CALLOUT = {"critical": ("#fdecea", RED), "warning": ("#fff4e5", ORANGE), "info": ("#e8f1fa", BLUE)}
BANNER = {"red": RED, "orange": ORANGE, "green": GREEN, "blue": BLUE}
HEAD = '<html><head><meta charset="utf-8"></head>'

# ============================ MD parsing ====================================

def parse_md(path):
    md = open(path, encoding="utf-8").read()
    fm = {}
    if md.startswith("---"):
        parts = md.split("---", 2)
        fm = yaml.safe_load(parts[1]) or {}
        md = parts[2]
    slides = []
    for chunk in re.split(r"^## Slide ", md, flags=re.M)[1:]:
        head = chunk.split("\n", 1)[0]
        mnum = re.match(r"\s*(\d+)", head)
        num = int(mnum.group(1)) if mnum else len(slides) + 1
        title = head.split("—", 1)[1].strip() if "—" in head else head.strip()
        meta = re.search(r"<!--(.*?)-->", chunk)
        stype = ""
        if meta:
            mt = re.search(r"type:\s*([\w+\-]+)", meta.group(1))
            stype = mt.group(1) if mt else ""
        content = chunk.split("### Slide content", 1)[1] if "### Slide content" in chunk else ""
        content = content.split("### Viewpoint", 1)[0].strip()
        charts = [yaml.safe_load(c) for c in re.findall(r"```chart\s*\n(.*?)```", content, re.S)]
        content = re.sub(r"```chart\s*\n.*?```", "", content, flags=re.S)
        vpm = re.search(r"### Viewpoint.*?```yaml\s*\n(.*?)```", chunk, re.S)
        vp = (yaml.safe_load(vpm.group(1)) or {}).get("viewpoint") if vpm else None
        slides.append({"num": num, "title": title, "type": stype, "content": content,
                       "charts": [c for c in charts if c], "vp": vp})
    return fm, slides


# ============================ MD -> HTML ====================================

def inline(t):
    t = _html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def table_html(rows):
    head, body = rows[0], [r for r in rows[1:] if not re.match(r"^[\s:\-|]+$", "|".join(r))]
    if head and head[0].strip().upper() == "KPI":
        tds = []
        for i, r in enumerate(body[:4]):
            r = (r + ["", "", ""])[:3]
            col = [RED, BLUE, BLUE, ORANGE][i % 4]
            tds.append('<td width="25%%" align="center" bgcolor="#f4f6f9"><font size="2" color="%s">%s</font><br>'
                       '<font size="5" color="%s"><b>%s</b></font><br><font size="2" color="%s">%s</font></td>'
                       % (GREY, inline(r[0]), col, inline(r[1]), GREY, inline(r[2])))
        return '<table width="100%" cellpadding="6" cellspacing="4"><tr>' + "".join(tds) + "</tr></table>"
    h = ['<table width="100%" cellpadding="4" cellspacing="0" border="1" style="border-collapse:collapse; border-color:#c8ced6;">',
         '<tr bgcolor="%s">' % BLUE + "".join('<th><font color="white">%s</font></th>' % inline(c) for c in head) + "</tr>"]
    for k, r in enumerate(body):
        tds = []
        for c in r:
            u = c.strip().upper()
            if u in ("HIGH", "MED", "MEDIUM", "LOW"):
                col = {"HIGH": RED, "MED": ORANGE, "MEDIUM": ORANGE, "LOW": GREEN}[u]
                tds.append('<td align="center" bgcolor="%s"><font color="white"><b>%s</b></font></td>' % (col, inline(c)))
            else:
                tds.append("<td>%s</td>" % inline(c))
        h.append(('<tr bgcolor="#eef1f4">' if k % 2 else "<tr>") + "".join(tds) + "</tr>")
    h.append("</table>")
    return "".join(h)


def callout_html(level, title, text):
    bg, fg = CALLOUT.get(level.lower(), CALLOUT["info"])
    return ('<table width="100%%" cellpadding="6" cellspacing="0" border="0"><tr><td bgcolor="%s" width="6"></td>'
            '<td bgcolor="%s"><font color="%s"><b>%s</b></font><br>%s</td></tr></table>' % (fg, bg, fg, inline(title), inline(text)))


def md_to_html(content):
    """Returns (body_html, subtitle, plain_length)."""
    out, para, sub, plain = [], [], "", 0
    lines = content.split("\n")
    i = 0

    def flush():
        if para:
            out.append("<p>%s</p>" % inline(" ".join(para)))
            del para[:]
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        plain += len(s)
        if not s:
            flush(); i += 1; continue
        m = re.match(r"^\*\*(Headline|Subtitle):\*\*\s*(.*)", s)
        if m:
            sub = m.group(2); i += 1; continue
        if "Chart (2D" in s:
            i += 1; continue
        m = re.match(r"^\*\*Callout \((\w+)\)\s*[—-]\s*(.+?):\*\*\s*(.*)", s)
        if m:
            flush(); out.append(callout_html(m.group(1), m.group(2), m.group(3))); i += 1; continue
        m = re.match(r"^\*\*Verdict banner(?:\s*\((\w+)\))?:\*\*\s*(.*)", s)
        if m:
            flush()
            col = BANNER.get((m.group(1) or "orange").lower(), ORANGE)
            out.append('<table width="100%%" cellpadding="10"><tr><td bgcolor="%s" align="center"><font size="5" color="white"><b>%s</b></font></td></tr></table>'
                       % (col, inline(m.group(2))))
            i += 1; continue
        if s.startswith("|"):
            flush(); rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(cells(lines[i])); plain += 40; i += 1
            out.append(table_html(rows)); continue
        if re.match(r"^[-*]\s+", s) or re.match(r"^\d+\.\s+", s):
            flush()
            ordered = bool(re.match(r"^\d+\.\s+", s))
            items = []
            while i < len(lines):
                t = lines[i].strip()
                if re.match(r"^[-*]\s+", t) or re.match(r"^\d+\.\s+", t):
                    if "Chart (2D" not in t:
                        items.append(re.sub(r"^([-*]|\d+\.)\s+", "", t))
                elif t and items and lines[i].startswith(" "):
                    items[-1] += " " + t
                else:
                    break
                plain += len(t); i += 1
            tag = "ol" if ordered else "ul"
            out.append("<%s>" % tag + "".join('<li style="margin-bottom:3px;">%s</li>' % inline(x) for x in items) + "</%s>" % tag)
            continue
        if s.startswith("#"):
            flush(); out.append("<p><b>%s</b></p>" % inline(s.lstrip("# "))); i += 1; continue
        para.append(s); i += 1
    flush()
    return "".join(out), sub, plain


def title_slide_html(content, fm):
    f = {}
    for m in re.finditer(r"\*\*(Title|Subtitle|Source data|Units|Badge):\*\*\s*(.*)", content):
        f[m.group(1)] = m.group(2).strip()
    badge = f.get("Badge", "VERDICT: " + str(fm.get("verdict", "")))
    bcol = RED if "NO-GO" in badge.upper() else GREEN if re.search(r"\bGO\b", badge.upper()) and "NO" not in badge.upper() else ORANGE
    badge = re.sub(r"\((red|orange|green)\)", "", badge).strip()
    body = ('<p><font size="6" color="%s"><b>%s</b></font></p>' % (BLUE, inline(f.get("Title", fm.get("title", ""))))
            + '<p><font size="4" color="#333">%s</font></p>' % inline(f.get("Subtitle", fm.get("subtitle", "")))
            + ("<p>Source data: %s</p>" % inline(f["Source data"]) if "Source data" in f else "")
            + ("<p>Units: %s</p>" % inline(f["Units"]) if "Units" in f else "")
            + '<table cellpadding="10"><tr><td bgcolor="%s"><font size="5" color="white"><b>%s</b></font></td></tr></table>' % (bcol, inline(badge)))
    return body, f.get("Title", fm.get("title", "")), f.get("Subtitle", fm.get("subtitle", ""))


# ============================ charts ========================================

def render_chart(spec, path, w_px, h_px):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    dpi = 150
    fig, ax = plt.subplots(figsize=(w_px / 100.0, h_px / 100.0), dpi=dpi)
    typ = spec.get("type", "line")
    x = spec.get("x", [])
    series = spec.get("series", [])
    palette = [BLUE, RED, ORANGE, GREEN, "#7d3c98", "#117a65"]
    ax2 = None
    if typ in ("bar", "barh"):
        n = max(1, len(series))
        width = 0.8 / n
        for k, s in enumerate(series):
            ys = s.get("y", [])
            pos = [j + (k - (n - 1) / 2.0) * width for j in range(len(ys))]
            cols = s.get("color") or palette[k % len(palette)]
            if spec.get("color_by_sign"):
                cols = [GREEN if v >= 0 else RED for v in ys]
            if typ == "bar":
                ax.bar(pos, ys, width, label=s.get("label"), color=cols)
            else:
                ax.barh(pos, ys, width, label=s.get("label"), color=cols)
            if spec.get("value_labels"):
                for p_, v in zip(pos, ys):
                    if typ == "bar":
                        ax.text(p_, v, ("%.3g" % v), ha="center", va="bottom", fontsize=7)
                    else:
                        ax.text(v, p_, (" %+.3g " % v), va="center", ha="left" if v >= 0 else "right", fontsize=7)
        if typ == "bar":
            ax.set_xticks(range(len(x))); ax.set_xticklabels([str(v) for v in x], fontsize=7, rotation=spec.get("rotate", 0))
        else:
            ax.set_yticks(range(len(x))); ax.set_yticklabels([str(v) for v in x], fontsize=7)
            ax.axvline(0, color="k", lw=0.8)
    else:
        for k, s in enumerate(series):
            target = ax
            if s.get("axis") == "right":
                ax2 = ax2 or ax.twinx(); target = ax2
            xs = s.get("x", x)
            target.plot(xs, s.get("y", []), s.get("style", "o-"), ms=3, lw=1.5,
                        color=s.get("color") or palette[k % len(palette)], label=s.get("label"))
            if s.get("fill_negative"):
                import numpy as np
                yy = np.array(s.get("y", []), dtype=float)
                target.fill_between(xs, yy, 0, where=yy < 0, color=RED, alpha=0.12)
    for h in spec.get("hlines", []) or []:
        ax.axhline(h["y"], ls="--", lw=1, color=h.get("color", "k"))
        if h.get("label"):
            ax.text(ax.get_xlim()[0], h["y"], " " + h["label"], fontsize=7, va="bottom", color=h.get("color", "k"))
    for v in spec.get("vlines", []) or []:
        ax.axvline(v["x"], ls=":", lw=1, color=v.get("color", "grey"))
        if v.get("label"):
            ax.text(v["x"], ax.get_ylim()[1], " " + v["label"], fontsize=7, va="top", color=v.get("color", "grey"))
    ax.set_title(spec.get("title", ""), fontsize=9)
    ax.set_xlabel(spec.get("xlabel", ""), fontsize=8); ax.set_ylabel(spec.get("ylabel", ""), fontsize=8)
    if ax2 is not None and spec.get("y2label"):
        ax2.set_ylabel(spec["y2label"], fontsize=8)
    if spec.get("ylim"):
        ax.set_ylim(*spec["ylim"])
    if spec.get("xlim"):
        ax.set_xlim(*spec["xlim"])
    ax.tick_params(labelsize=7); ax.grid(alpha=0.3)
    hs, ls = ax.get_legend_handles_labels()
    if ax2 is not None:
        h2, l2 = ax2.get_legend_handles_labels(); hs += h2; ls += l2
    if any(ls):
        ax.legend(hs, ls, fontsize=7, frameon=False)
    fig.tight_layout(); fig.savefig(path, dpi=dpi); plt.close(fig)
    return path


# ============================ viewpoint helpers =============================

SYN = {"von mises": ["Von Mises Stress", "Von Mises"], "max principal": ["Maximum Principal Value"],
       "min principal": ["Minimum Principal Value"], "mid principal": ["Middle Principal Value"],
       "max shear": ["Maximum Shear"], "translational magnitude": ["Translational Magnitude", "Resultant", "Magnitude"],
       "magnitude": ["Translational Magnitude", "Resultant", "Magnitude"], "resultant": ["Resultant", "Translational Magnitude"],
       "x": ["Translational X", "X"], "y": ["Translational Y", "Y"], "z": ["Translational Z", "Z"],
       "rotational magnitude": ["Rotational Magnitude"], "scalar": [""]}
_DER = {}


def resolve_derived(m, result, intent):
    if result not in _DER:
        _DER[result] = list(call("der", V.pxGetCAEResultDerivedTypes, m, result) or [])
    lst = _DER[result]
    intent = (intent or "").strip()
    if not lst:
        return ""
    if intent in lst:
        return intent
    key = intent.lower()
    for c in SYN.get(key, []):
        if c in lst or c == "":
            return c
    for c in lst:
        if c.lower() == key:
            return c
    for c in lst:
        if key and key in c.lower():
            return c
    d = default_derived(lst)
    log("WARN derived '%s' not found for %s, using '%s'" % (intent, result, d))
    return d


STD_Z = {"iso": ([-1, 1, -1], [0, 0, 1]), "front": ([0, 1, 0], [0, 0, 1]), "side": ([0, 1, 0], [0, 0, 1]),
         "back": ([0, -1, 0], [0, 0, 1]), "right": ([-1, 0, 0], [0, 0, 1]), "left": ([1, 0, 0], [0, 0, 1]),
         "top": ([0, 0, -1], [0, 1, 0]), "bottom": ([0, 0, 1], [0, 1, 0])}
STD_Y = {"iso": ([-1, -1, -1], [0, 1, 0]), "front": ([0, 0, -1], [0, 1, 0]), "side": ([-1, 0, 0], [0, 1, 0]),
         "back": ([0, 0, 1], [0, 1, 0]), "right": ([-1, 0, 0], [0, 1, 0]), "left": ([1, 0, 0], [0, 1, 0]),
         "top": ([0, -1, 0], [0, 0, -1]), "bottom": ([0, 1, 0], [0, 0, 1])}


def view_vectors(cam):
    cam = cam or {}
    up = str(cam.get("up_axis", "+Z")).upper()
    table = STD_Y if "Y" in up else STD_Z
    vd, uv = table.get(str(cam.get("std_view", "iso")).lower(), table["iso"])
    if cam.get("view_dir"):
        vd = cam["view_dir"]
    if cam.get("up_vector"):
        uv = cam["up_vector"]
    return vd, uv


DISPLAY = {"shaded": 0, "shaded_with_mesh": 1, "mesh": 1, "wireframe": 2, "hidden_line": 3}


# ============================ build =========================================

def main():
    m = current_model()
    parts = list(call("parts", V.pxGetPartsList, m, "", 0) or [])
    fm, slides = parse_md(JOB["md"])
    vpath = JOB.get("viewpath") or fm.get("viewpath") or ("CAE Review - %s" % m)
    rich = bool(JOB.get("rich", True))
    assets = JOB["assets_dir"]
    os.makedirs(assets, exist_ok=True)
    shots_dir = os.path.join(assets, "screenshots")
    if JOB.get("screenshots", True):
        os.makedirs(shots_dir, exist_ok=True)
    log("model=%s slides=%d viewpath=%s rich=%s" % (m, len(slides), vpath, rich))

    # ---- assets per slide (title, panel, chart)
    W, H = 1600, 900
    for s in slides:
        n = s["num"]
        if s["type"] == "title" or n == 1:
            body, title, sub = title_slide_html(s["content"], fm)
            plain = 300
            s["title_text"] = title or s["title"]
        else:
            body, sub, plain = md_to_html(s["content"])
            s["title_text"] = s["title"]
        sub = sub or "%s · %s" % (os.path.basename(JOB["cax"]), fm.get("title", "CAE Review"))
        has_chart = bool(s["charts"])
        split = 0.60
        if has_chart:
            split = min(0.72, 0.56 + max(0, plain - 450) / 4000.0)
        avail = (split - 0.16) if has_chart else 0.82
        fs = max(8.5, min(12.5, 12.5 - max(0, plain - 1100 * avail) / (260 * avail)))
        s["split"] = split
        s["panel"] = os.path.join(assets, "s%02d_panel.html" % n)
        s["title_html"] = os.path.join(assets, "s%02d_title.html" % n)
        with open(s["panel"], "w", encoding="utf-8") as f:
            f.write(HEAD + '<body style="font-family:Arial; font-size:%.1fpt; color:#1b1f24;">%s</body></html>' % (fs, body))
        with open(s["title_html"], "w", encoding="utf-8") as f:
            f.write(HEAD + '<body style="font-family:Arial;"><font size="5" color="white"><b>%s</b></font><br>'
                    '<font size="3" color="#dbe6f2">%s</font></body></html>' % (inline(s["title_text"]), inline(sub)))
        s["chart"] = None
        if has_chart:
            p = os.path.join(assets, "s%02d_chart.png" % n)
            try:
                render_chart(s["charts"][0], p, int(0.445 * W), int((0.975 - split) * H))
                s["chart"] = p
            except Exception as e:
                ERRORS.append("chart slide %d: %s" % (n, e))
    log("assets written")

    # ---- viewpoints
    call("addpath", V.xAddViewPath, vpath)
    label_ids, records = [], []
    for s in slides:
        if not s["vp"]:
            continue
        base = s["vp"]
        variants = [(base, True)]
        for sv in base.get("secondary_viewpoints") or []:
            merged = {k: v for k, v in base.items() if k not in ("secondary_viewpoints", "probes", "notes", "name")}
            merged.update(sv)
            variants.append((merged, False))
        for vp, primary in variants:
            name = vp.get("name") or ("%02d_%s" % (s["num"], re.sub(r"\W+", "_", s["title"])[:30]))
            rec = {"name": name, "slide": s["num"], "probes": []}
            # reset
            for p in parts:
                call("show", V.xShowPart, m, p, True)
            call("delprobes", V.xDeleteAllProbeLabels, "")
            call("delnotes", V.xDeleteAllUser3DLabels)
            call("minmaxoff", V.xShowCAEFrameMinMaxLabels, m, False)
            for lid, lt in label_ids:
                call("dellabel", V.xDeleteLabel, lid, lt)
            label_ids = []
            call("delall", V.xDeleteAllLabels)
            for lid in list(call("richids", V.pxGetRichTextLabelIDs, 0) or []):
                call("delrich", V.xDeleteLabel, lid, 5)
            call("display", V.xSetDisplayMode, 0)
            call("undef", V.xShowCAEUnDeformedMesh, m, False)
            # result
            r = vp.get("result") or {}
            rname, inst = r.get("name", ""), r.get("instance", "")
            der = resolve_derived(m, rname, r.get("derived", "")) if rname else ""
            rec["result"] = [rname, inst, der]
            rec["set_result"] = bool(call("result", V.xSetCAEResult, m, rname, inst, der)) if rname else None
            # deformation
            d = vp.get("deformation") or {}
            if d.get("enabled"):
                call("defres", V.xSetAsCAEDeformationResult, m, d.get("result", "Displacement"))
                sc = float(d.get("scale", 1.0))
                call("defscale", V.xSetCAEDeformScaleFactorEx, m, True, sc, sc, sc)
                if d.get("show_undeformed"):
                    call("undefmode", V.xSetCAEUndeformedMeshDisplayMode, m, 1)
                    call("undefon", V.xShowCAEUnDeformedMesh, m, True)
            else:
                call("defscale0", V.xSetCAEDeformScaleFactorEx, m, True, 0.0, 0.0, 0.0)
            # legend
            lg = vp.get("legend") or {}
            if lg.get("mode") == "user":
                umax, umin = lg.get("user_max"), lg.get("user_min")
                call("legend", V.xSetCAELegendRangeEx, m, False, umax is not None, float(umax or 0),
                     umin is not None, float(umin or 0), bool(lg.get("filter_out_of_range", False)))
            else:
                call("legendauto", V.xSetCAELegendRangeEx, m, False, False, 0.0, False, 0.0, False)
            call("levels", V.xSetCAELegendDefaultColors, m, int(lg.get("levels") or 12))
            # parts
            pv = vp.get("parts") or {}
            if pv.get("show_only"):
                for p in parts:
                    call("vis", V.xShowPart, m, p, p in pv["show_only"])
            elif isinstance(pv.get("show"), list):
                for p in parts:
                    call("vis", V.xShowPart, m, p, p in pv["show"])
            for p in pv.get("hide") or []:
                call("hide", V.xShowPart, m, p, False)
            for t in pv.get("transparent") or []:
                if call("transp", V.xSetPartTransparency, m, t["part"], float(t.get("level", 0.5))) is None:
                    rec.setdefault("warnings", []).append("transparency not applied: %s" % t["part"])
            mode = DISPLAY.get(str((vp.get("display") or {}).get("mode", "shaded")).lower(), 0)
            if mode:
                call("display", V.xSetDisplayMode, mode)
            # legend placement + camera
            if rich:
                call("legendpos", V.xSetCAELegendPosition, m, 0.012, 0.30, 0)
            vd, uv = view_vectors(vp.get("camera"))
            call("view", V.xSetStandardView, vd, uv)
            if rich:
                call("fitwin", V.xFitWindowViewEx, 0.10, 0.16, 0.53, 0.97, 1)
            else:
                call("fit", V.xFitView)
            # probes
            for pr in vp.get("probes") or []:
                if pr.get("type") == "minmax_label":
                    call("minmaxon", V.xShowCAEFrameMinMaxLabels, m, True)
                    rec["minmax_label"] = True
                    continue
                pres = pr.get("result", rname)
                pder = resolve_derived(m, pres, pr.get("derived", r.get("derived", ""))) if pres else der
                val = call("probe", V.xCAEProbeID, m, pr.get("part", ""), int(pr["id"]), pres, inst, pder)
                exp = pr.get("expected_cax")
                st = "NO VALUE" if not valid(val) else ("OK" if exp is None or abs(val - exp) <= 0.02 * abs(exp) + 1e-9 else "MISMATCH")
                rec["probes"].append({"id": pr["id"], "part": pr.get("part"), "value": val if valid(val) else None,
                                      "expected": exp, "status": st})
            for nt in vp.get("notes") or []:
                call("note", V.xAdd3DNotesByID, m, nt["part"], int(nt["node"]), [str(x) for x in nt.get("text", [])])
            # rich layer
            if rich:
                tid = call("title", V.xAddRichTextLabel2D, s["title_html"], [0.0, 0.118], [1.0, 0.125],
                           [1, 0.122, 0.306, 0.475, 1.0], [0, 0, 0, 0, 0], [0, 2, 1, 0])
                if tid:
                    label_ids.append((tid, 5))
                if primary:
                    if s["chart"]:
                        sp = s["split"]
                        pid = call("panel", V.xAddRichTextLabel2D, s["panel"], [0.545, sp - 0.015], [0.445, sp - 0.16],
                                   [1, 1, 1, 1, 1.0], [1, 0.78, 0.81, 0.84, 1], [0, 2, 1, 0])
                        iid = call("chart", V.xInsert2DImageLabel, s["chart"], 0.545, sp, 0.99, 0.975, "", True, [1, 1, 0])
                        if iid:
                            label_ids.append((iid, 3))
                    else:
                        pid = call("panel", V.xAddRichTextLabel2D, s["panel"], [0.545, 0.975], [0.445, 0.84],
                                   [1, 1, 1, 1, 1.0], [1, 0.78, 0.81, 0.84, 1], [0, 2, 1, 0])
                    if pid:
                        label_ids.append((pid, 5))
            else:
                call("fitlabels", V.xFitView, True)
            rec["added"] = bool(call("addvp", V.xAddViewPoint, name, vpath, -1))
            if JOB.get("screenshots", True):
                rec["screenshot"] = call("shot", V.xGenerateImage, os.path.join(shots_dir, "%s.png" % name))
            records.append(rec)
            log("viewpoint %s added=%s" % (name, rec["added"]))

    # ---- save CAX, export WCAX
    outputs = {}
    os.makedirs(os.path.dirname(JOB["out_cax"]), exist_ok=True)
    if call("save", V.xFileSave, JOB["out_cax"]) and os.path.isfile(JOB["out_cax"]):
        outputs["cax"] = JOB["out_cax"]
    log("cax saved")
    if JOB.get("out_wcax"):
        vps = list(call("vplist", V.pxGetViewPathList) or [])
        if vpath in vps:
            call("curpath", V.xSetCurrentViewPath, vps.index(vpath))
        ok = call("wcax", V.xExportWCax, JOB["out_wcax"], 1, True, False, "")
        if not (ok and os.path.isfile(JOB["out_wcax"])):
            ok = call("wcax_all", V.xExportWCax, JOB["out_wcax"], 0, True, False, "")
        if os.path.isfile(JOB["out_wcax"]):
            outputs["wcax"] = JOB["out_wcax"]
        log("wcax exported=%s" % bool(ok))

    # ---- contact sheet
    if JOB.get("screenshots", True):
        try:
            from PIL import Image, ImageDraw
            shots = [(r["name"], os.path.join(shots_dir, r["name"] + ".png")) for r in records]
            shots = [(n, p) for n, p in shots if os.path.isfile(p)]
            if shots:
                tw, th, cols = 480, 270, 3
                rows = (len(shots) + cols - 1) // cols
                sheet = Image.new("RGB", (cols * tw, rows * (th + 22)), "white")
                dr = ImageDraw.Draw(sheet)
                for k, (n, p) in enumerate(shots):
                    im = Image.open(p).convert("RGB").resize((tw, th))
                    x, y = (k % cols) * tw, (k // cols) * (th + 22)
                    sheet.paste(im, (x, y + 22)); dr.text((x + 4, y + 4), n, fill=(0, 0, 0))
                cs = os.path.join(assets, "contact_sheet.png")
                sheet.save(cs); outputs["contact_sheet"] = cs
        except Exception as e:
            ERRORS.append("contact sheet: %s" % e)

    bad = [p for r in records for p in r["probes"] if p["status"] != "OK"]
    finish({"model": m, "viewpath": vpath, "viewpoints": records, "n_viewpoints": len(records),
            "outputs": outputs, "probe_issues": bad,
            "final_viewpoints": list(call("vplist2", V.pxGetViewPointList, vpath, -1) or [])},
           ok=("cax" in outputs))


run(main)
