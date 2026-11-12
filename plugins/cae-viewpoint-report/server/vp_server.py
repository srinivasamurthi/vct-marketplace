#!/usr/bin/env python3
"""
vp_server.py - MCP (stdio) server for the cae-viewpoint-report plugin.

Pure standard library (no pip installs). It launches VCollab Pro in batch mode
(`VCollabPro.exe -b job.py model.cax`) as background jobs, so long builds are not
cut off by client time-outs, and reports progress / results.

Tools: vp_env_check, vp_cae_info, vp_translate, vp_extract_model, vp_verify_probes, vp_build, vp_job_status, vp_list_jobs
Stdout is the MCP channel - never print to it.
"""
import glob
import json
import os
import subprocess
import sys
import threading
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
VC_DIR = os.path.join(HERE, "vcollab")
PROTOCOL = "2024-11-05"
JOBS = {}
LOCK = threading.Lock()


def err(*a):
    print(*a, file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- VCollab
def find_vcollabpro():
    cand = []
    if os.environ.get("VCOLLABPRO_EXE"):
        cand.append(os.environ["VCOLLABPRO_EXE"])
    if os.environ.get("VCOLLAB_DIR"):
        cand.append(os.path.join(os.environ["VCOLLAB_DIR"], "VCollabPro64", "VCollabPro.exe"))
    for root in (os.environ.get("ProgramFiles", r"C:\Program Files"), r"C:\Program Files", r"D:\Program Files"):
        found = glob.glob(os.path.join(root, "VCollab", "*", "VCollabPro64", "VCollabPro.exe"))

        def ver(p):
            v = os.path.basename(os.path.dirname(os.path.dirname(p)))
            try:
                return tuple(int(x) for x in v.split("."))
            except ValueError:
                return (0,)
        cand += sorted(found, key=ver, reverse=True)
    for c in cand:
        if c and os.path.isfile(c):
            return c
    return None


PY_ENV_VARS = ("PYTHONHOME", "PYTHONPATH", "PYTHONSTARTUP", "PYTHONEXECUTABLE", "PYTHONUSERBASE",
               "PYTHONNOUSERSITE", "PYTHONSAFEPATH", "PYTHONPLATLIBDIR", "VIRTUAL_ENV", "VIRTUAL_ENV_PROMPT",
               "__PYVENV_LAUNCHER__", "CONDA_PREFIX", "CONDA_DEFAULT_ENV", "CONDA_PYTHON_EXE")


def clean_env(extra=None):
    """Environment for VCollab / VMoveCAE child processes.

    Those programs embed their own Python 3.12. When this server is started by uv (or any venv),
    variables such as PYTHONHOME / PYTHONPATH / VIRTUAL_ENV and the venv's folders on PATH leak
    into the child and break its imports (ModuleNotFoundError: _CaeEngineWrap_x64_Release)."""
    env = {k: v for k, v in os.environ.items()
           if k.upper() not in PY_ENV_VARS and not k.upper().startswith("UV_")}
    venv = os.environ.get("VIRTUAL_ENV", "")
    here_py = os.path.dirname(sys.executable)
    keep = []
    for p in env.get("PATH", "").split(os.pathsep):
        pl = p.lower()
        own_venv_py = pl.rstrip("\\/") == here_py.lower().rstrip("\\/") and (venv or "uv" in here_py.lower())
        if not p or (venv and pl.startswith(venv.lower())) or own_venv_py or "\\uv\\" in pl or "/uv/" in pl:
            continue
        keep.append(p)
    env["PATH"] = os.pathsep.join(keep)
    # VCollab executables (VMoveCAEBatch, CaeInfo, VCollabPro) need VCOLLAB_DIR at runtime and fail
    # with ModuleNotFoundError (_CaeEngineWrap_x64_Release) without it. The plugin setting is passed
    # as VCOLLAB_DIR="" when left empty, which would hide the installer's system-wide value.
    root = vcollab_root()
    if root:
        env["VCOLLAB_DIR"] = root
    elif not env.get("VCOLLAB_DIR"):
        env.pop("VCOLLAB_DIR", None)
    env.update(extra or {})
    return env


def vcollab_root():
    """Install root, e.g. C:\\Program Files\\VCollab\\26.1 (VCOLLAB_DIR if valid, else from VCollabPro.exe)."""
    d = os.environ.get("VCOLLAB_DIR", "").strip()
    if d and os.path.isdir(d):
        return d
    pro = find_vcollabpro()
    return os.path.dirname(os.path.dirname(pro)) if pro else None


def find_vmove_tool(exe_name):
    """VMoveCAE64 tools (VMoveCAEBatch.exe, CaeInfo.exe, caxinfo.exe) next to the VCollab Pro install."""
    cand = []
    if os.environ.get("VMOVECAE_DIR"):
        cand.append(os.path.join(os.environ["VMOVECAE_DIR"], exe_name))
    if os.environ.get("VCOLLAB_DIR"):
        cand.append(os.path.join(os.environ["VCOLLAB_DIR"], "VMoveCAE64", exe_name))
    pro = find_vcollabpro()
    if pro:
        cand.append(os.path.join(os.path.dirname(os.path.dirname(pro)), "VMoveCAE64", exe_name))
    for root in (os.environ.get("ProgramFiles", r"C:\Program Files"), r"C:\Program Files"):
        cand += sorted(glob.glob(os.path.join(root, "VCollab", "*", "VMoveCAE64", exe_name)), reverse=True)
    for c in cand:
        if c and os.path.isfile(c):
            return c
    return None


def model_stem(path):
    """Stem for a native model; 'd3plot'-style names use the parent folder name."""
    s = stem_of(path)
    if s.lower() in ("d3plot", "d3thdt", "binout") or not s:
        s = os.path.basename(os.path.dirname(norm(path))) or s
    return s


def norm(p):
    return os.path.abspath(os.path.expanduser(str(p))).replace("\\", "/") if p else p


def stem_of(path):
    return os.path.splitext(os.path.basename(path))[0]


def default_out_dir(cax, out_dir):
    d = norm(out_dir) if out_dir else norm(os.path.join(os.path.dirname(norm(cax)), stem_of(cax) + "_viewpoints"))
    os.makedirs(d, exist_ok=True)
    return d


def compose(task, job):
    with open(os.path.join(VC_DIR, "common.py"), encoding="utf-8") as f:
        common = f.read()
    with open(os.path.join(VC_DIR, task), encoding="utf-8") as f:
        body = f.read()
    header = "import json\nJOB = json.loads(%r)\n" % json.dumps(job)
    return header + common + "\n" + body


def start_job(kind, task, job, cax, timeout_s=3600):
    exe = find_vcollabpro()
    if not exe:
        raise RuntimeError("VCollabPro.exe not found. Set VCOLLABPRO_EXE or VCOLLAB_DIR (see README).")
    if not os.path.isfile(cax):
        raise FileNotFoundError(cax)
    jid = "%s-%s" % (kind, uuid.uuid4().hex[:8])
    jdir = norm(os.path.join(job.pop("_jobs_root"), jid))
    os.makedirs(jdir, exist_ok=True)
    job["job_dir"] = jdir
    job["cax"] = cax
    script = os.path.join(jdir, "job.py")
    with open(script, "w", encoding="utf-8") as f:
        f.write(compose(task, job))
    out = open(os.path.join(jdir, "vcollab_console.log"), "w", encoding="utf-8", errors="replace")
    env = clean_env({"VCOLLAB_ENABLE_VCOLLABPRO_SCRIPT": "1"})
    flags = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW
    proc = subprocess.Popen([exe, "-b", script, cax], cwd=jdir, stdout=out, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, env=env, creationflags=flags)
    with LOCK:
        JOBS[jid] = {"id": jid, "kind": kind, "proc": proc, "dir": jdir, "start": time.time(),
                     "timeout": timeout_s, "job": job, "log": out}
    err("started %s pid=%s" % (jid, proc.pid))
    return jid


def start_exe_job(kind, argv, jobs_root, expected, timeout_s=3600):
    """Run a VMoveCAE command-line tool in the background; success = expected output file written."""
    jid = "%s-%s" % (kind, uuid.uuid4().hex[:8])
    jdir = norm(os.path.join(jobs_root, jid))
    os.makedirs(jdir, exist_ok=True)
    for v in expected.values():  # never report a stale file from an earlier run as success
        if os.path.isfile(v):
            try:
                os.replace(v, v + ".previous")
            except OSError:
                pass
    with open(os.path.join(jdir, "command.json"), "w", encoding="utf-8") as f:
        json.dump({"argv": argv, "expected": expected}, f, indent=1)
    out = open(os.path.join(jdir, "console.log"), "w", encoding="utf-8", errors="replace")
    flags = 0x08000000 if os.name == "nt" else 0
    proc = subprocess.Popen(argv, cwd=os.path.dirname(argv[0]) or jdir, stdout=out, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, env=clean_env(), creationflags=flags)
    with LOCK:
        JOBS[jid] = {"id": jid, "kind": kind, "proc": proc, "dir": jdir, "start": time.time(),
                     "timeout": timeout_s, "job": {"argv": argv}, "log": out, "expected": expected}
    err("started %s pid=%s" % (jid, proc.pid))
    return jid


def tail(path, n=15):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return [l.rstrip() for l in f.readlines()[-n:]]
    except OSError:
        return []


def job_state(jid, wait_s=0):
    with LOCK:
        j = JOBS.get(jid)
    if not j:
        # job from an earlier server session: look for a result file
        hits = glob.glob(os.path.join("**", jid, "result.json"), recursive=True)
        return {"job_id": jid, "state": "unknown", "hint": "job not in this session"}
    deadline = time.time() + max(0, min(float(wait_s or 0), 55))
    while j["proc"].poll() is None and time.time() < deadline:
        time.sleep(1)
    elapsed = time.time() - j["start"]
    if j["proc"].poll() is None and elapsed > j["timeout"]:
        j["proc"].kill()
    res_path = os.path.join(j["dir"], "result.json")
    st = {"job_id": jid, "kind": j["kind"], "elapsed_s": round(elapsed, 1),
          "progress": tail(os.path.join(j["dir"], "progress.log"))}
    if j["proc"].poll() is None:
        st["state"] = "running"
        if not st["progress"] and not j.get("expected") and elapsed > 90:
            st["hint"] = ("No progress after %d s: VCollab Pro has not started the job script. It is probably stuck "
                          "at start-up (see vcollab_console.log - e.g. stops at 'OGRE Initialising'). End leftover "
                          "VCollabPro.exe processes in Task Manager, make sure the Windows session is unlocked, then "
                          "re-run the step." % elapsed)
            st["console_tail"] = tail(os.path.join(j["dir"], "vcollab_console.log"), 5)
        return st
    try:
        j["log"].close()
    except Exception:
        pass
    if j.get("expected"):  # VMoveCAE command-line job
        outs = {k: v for k, v in j["expected"].items() if os.path.isfile(v) and os.path.getsize(v) > 0}
        st["returncode"] = j["proc"].returncode
        st["console_tail"] = tail(os.path.join(j["dir"], "console.log"), 25)
        outs = {k: v for k, v in outs.items() if os.path.getmtime(v) >= j["start"] - 1}
        st["state"] = "done" if (len(outs) == len(j["expected"]) and j["proc"].returncode == 0) else "failed"
        st["result"] = {"outputs": {k: {"path": v, "size_kb": round(os.path.getsize(v) / 1024.0, 1)} for k, v in outs.items()},
                        "missing": [v for k, v in j["expected"].items() if k not in outs]}
        if j["kind"] == "caeinfo" and "xml" in outs:
            with open(outs["xml"], encoding="utf-8", errors="replace") as f:
                txt = f.read()
            st["result"]["xml_preview"] = txt[:12000]
            st["result"]["xml_truncated"] = len(txt) > 12000
        if st["state"] == "failed":
            st["hint"] = ("No output written. Check the console tail: unsupported format/version, missing licence for "
                          "the solver format, or a results file that must be passed separately (e.g. Fluent .dat).")
        return st
    if os.path.isfile(res_path):
        with open(res_path, encoding="utf-8") as f:
            res = json.load(f)
        st["state"] = "done" if res.get("ok") else "failed"
        st["result"] = res
    else:
        st["state"] = "failed"
        st["console_tail"] = tail(os.path.join(j["dir"], "vcollab_console.log"), 25)
        st["hint"] = "VCollab Pro exited without writing result.json (crash, licence or script error)."
    return st


# --------------------------------------------------------------------------- tools
def t_env_check(a):
    exe = find_vcollabpro()
    return {"vcollabpro_exe": exe, "found": bool(exe),
            "vmovecaebatch_exe": find_vmove_tool("VMoveCAEBatch.exe"), "caeinfo_exe": find_vmove_tool("CaeInfo.exe"),
            "vcollab_dir_for_children": vcollab_root(), "vcollab_dir_in_server_env": os.environ.get("VCOLLAB_DIR"),
            "server_python": sys.version.split()[0], "server_python_exe": sys.executable,
            "leaking_python_vars": sorted(k for k in os.environ if k.upper() in PY_ENV_VARS or k.upper().startswith("UV_")),
            "platform": sys.platform, "jobs_this_session": len(JOBS),
            "note": "Jobs run VCollab Pro's own embedded Python (needs yaml, matplotlib, PIL - bundled with VCollab Pro 2026)."}


def t_extract(a):
    cax = norm(a["cax_path"])
    out_dir = default_out_dir(cax, a.get("out_dir"))
    job = {"_jobs_root": os.path.join(out_dir, "_jobs"),
           "out_json": os.path.join(out_dir, stem_of(cax) + "_model_data.json").replace("\\", "/"),
           "max_instances": a.get("max_instances", 40), "max_parts": a.get("max_parts", 400),
           "top_parts": a.get("top_parts", 15)}
    jid = start_job("extract", "task_extract.py", job, cax, a.get("timeout_s", 1800))
    return job_state(jid, a.get("wait_seconds", 45))


def t_probe(a):
    cax = norm(a["cax_path"])
    out_dir = default_out_dir(cax, a.get("out_dir"))
    job = {"_jobs_root": os.path.join(out_dir, "_jobs"), "probes": a["probes"]}
    jid = start_job("probe", "task_probe.py", job, cax, a.get("timeout_s", 900))
    return job_state(jid, a.get("wait_seconds", 45))


def t_build(a):
    cax = norm(a["cax_path"])
    md = norm(a["md_path"])
    if not os.path.isfile(md):
        raise FileNotFoundError(md)
    out_dir = default_out_dir(cax, a.get("out_dir"))
    base = a.get("basename") or stem_of(md).replace("_viewpoints", "") + "_viewpoints"
    job = {"_jobs_root": os.path.join(out_dir, "_jobs"), "md": md,
           "out_cax": "%s/%s.cax" % (out_dir, base),
           "out_wcax": ("%s/%s.wcax" % (out_dir, base)) if a.get("wcax", True) else "",
           "assets_dir": "%s/%s_assets" % (out_dir, base),
           "rich": a.get("rich", True), "screenshots": a.get("screenshots", True),
           "viewpath": a.get("viewpath", "")}
    if norm(job["out_cax"]) == cax:
        raise ValueError("Output CAX would overwrite the input; choose another basename/out_dir.")
    jid = start_job("build", "task_build.py", job, cax, a.get("timeout_s", 3600))
    st = job_state(jid, a.get("wait_seconds", 45))
    st["expected_outputs"] = {"md": md, "cax": job["out_cax"], "wcax": job["out_wcax"],
                              "contact_sheet": job["assets_dir"] + "/contact_sheet.png"}
    return st


def _native_out_dir(model, out_dir):
    d = norm(out_dir) if out_dir else norm(os.path.join(os.path.dirname(norm(model)), model_stem(model) + "_viewpoints"))
    os.makedirs(d, exist_ok=True)
    return d


def t_cae_info(a):
    exe = find_vmove_tool("CaeInfo.exe")
    if not exe:
        raise RuntimeError("CaeInfo.exe not found (VMoveCAE64 folder). Set VCOLLAB_DIR or VMOVECAE_DIR.")
    model = norm(a["model_file"])
    if not os.path.exists(model):
        raise FileNotFoundError(model)
    out_dir = _native_out_dir(model, a.get("out_dir"))
    xml = "%s/%s_caeinfo.xml" % (out_dir, model_stem(model))
    argv = [exe, model] + ([norm(a["results_file"])] if a.get("results_file") else []) + ["--output=%s" % xml]
    jid = start_exe_job("caeinfo", argv, os.path.join(out_dir, "_jobs"), {"xml": xml}, a.get("timeout_s", 900))
    return job_state(jid, a.get("wait_seconds", 45))


def t_translate(a):
    exe = find_vmove_tool("VMoveCAEBatch.exe")
    if not exe:
        raise RuntimeError("VMoveCAEBatch.exe not found (VMoveCAE64 folder). Set VCOLLAB_DIR or VMOVECAE_DIR.")
    model = norm(a["model_file"])
    if not os.path.exists(model):
        raise FileNotFoundError(model)
    out_dir = _native_out_dir(model, a.get("out_dir"))
    cax = norm(a["out_cax"]) if a.get("out_cax") else "%s/%s.cax" % (out_dir, model_stem(model))
    if os.path.isfile(cax) and not a.get("overwrite", True):
        return {"state": "done", "result": {"outputs": {"cax": {"path": cax}}}, "note": "existing CAX reused"}
    opts = []
    for key, flag in (("results", "--results"), ("element_results", "--element-results"),
                      ("filter_results", "--filter-results"), ("sections", "--sections"),
                      ("parts", "--parts"), ("filter_parts", "--filter-parts"), ("part_ids", "--part-ids"),
                      ("instances", "--instances"), ("filter_instances", "--filter-instances"),
                      ("part_grouping", "--part-grouping"), ("model_file_format", "--model-file-format")):
        if a.get(key):
            opts.append("%s=%s" % (flag, a[key]))
    for key, flag in (("mid_nodes", "--enable-mid-nodes"), ("odb_fast_load", "--enable-odb-fast-load"),
                      ("odb_zero_frames", "--enable-odb-load-zero-frames"),
                      ("no_averaging_across_materials", "--no-averaging-across-materials")):
        if a.get(key):
            opts.append(flag)
    opts += [str(x) for x in (a.get("extra_args") or [])]
    argv = [exe] + opts + [model] + ([norm(a["results_file"])] if a.get("results_file") else []) + [cax]
    jid = start_exe_job("translate", argv, os.path.join(out_dir, "_jobs"), {"cax": cax}, a.get("timeout_s", 3600))
    st = job_state(jid, a.get("wait_seconds", 45))
    st["command"] = argv
    return st


def t_status(a):
    return job_state(a["job_id"], a.get("wait_seconds", 45))


def t_list(a):
    with LOCK:
        ids = list(JOBS)
    return [{"job_id": i, "kind": JOBS[i]["kind"], "running": JOBS[i]["proc"].poll() is None,
             "dir": JOBS[i]["dir"]} for i in ids]


S = {"type": "string"}
TOOLS = [
    ("vp_env_check", "Check that VCollab Pro (VCollabPro.exe) is found and report the server environment.",
     {"type": "object", "properties": {}}, t_env_check),
    ("vp_cae_info",
     "Run VMoveCAE CaeInfo on a NATIVE solver file (.op2, .bdf, .odb, .rst, .rth, d3plot, .cas+.dat, .t16, ...) "
     "and return its metadata XML (parts, results, instances). Use before vp_translate to choose results/parts.",
     {"type": "object", "required": ["model_file"], "properties": {
         "model_file": S, "results_file": S, "out_dir": S, "wait_seconds": {"type": "number"}}}, t_cae_info),
    ("vp_translate",
     "Convert a NATIVE solver file to CAX with VMoveCAEBatch (background job). Default output "
     "<model folder>/<model>_viewpoints/<model>.cax. Options map to VMoveCAEBatch flags: results, element_results "
     "(keep unaveraged element values, e.g. 'Stress'), filter_results, sections ('Top, Bottom, Maximum'), parts, "
     "filter_parts, part_ids, instances, filter_instances, part_grouping, model_file_format, mid_nodes, odb_fast_load, "
     "odb_zero_frames, no_averaging_across_materials, extra_args. results_file for two-file formats (Fluent .cas+.dat).",
     {"type": "object", "required": ["model_file"], "properties": {
         "model_file": S, "results_file": S, "out_cax": S, "out_dir": S, "results": S, "element_results": S,
         "filter_results": S, "sections": S, "parts": S, "filter_parts": S, "part_ids": S, "instances": S,
         "filter_instances": S, "part_grouping": S, "model_file_format": S,
         "mid_nodes": {"type": "boolean"}, "odb_fast_load": {"type": "boolean"}, "odb_zero_frames": {"type": "boolean"},
         "no_averaging_across_materials": {"type": "boolean"}, "extra_args": {"type": "array", "items": S},
         "overwrite": {"type": "boolean"}, "wait_seconds": {"type": "number"}, "timeout_s": {"type": "number"}}},
     t_translate),
    ("vp_extract_model",
     "Start a VCollab Pro job that catalogues a .cax: model name, parts (node counts, bounds), every result with exact "
     "derived-type names, instances + Time/Frequency attributes, min/max (+IDs) per instance, peak instance and the top "
     "parts at the peak. Writes <model>_model_data.json in out_dir. Returns a job status (waits up to wait_seconds).",
     {"type": "object", "required": ["cax_path"], "properties": {
         "cax_path": S, "out_dir": S, "max_instances": {"type": "integer"}, "max_parts": {"type": "integer"},
         "top_parts": {"type": "integer"}, "wait_seconds": {"type": "number"}}}, t_extract),
    ("vp_verify_probes",
     "Probe node/element IDs in VCollab Pro and compare with expected values before writing them into the MD. "
     "probes: [{part, id, result, instance, derived (exact VCollab name), expected}].",
     {"type": "object", "required": ["cax_path", "probes"], "properties": {
         "cax_path": S, "probes": {"type": "array", "items": {"type": "object"}}, "out_dir": S,
         "wait_seconds": {"type": "number"}}}, t_probe),
    ("vp_build",
     "Build the deliverables from a viewpoint MD file: (1) the MD itself, (2) <basename>.cax with one (rich) viewpoint "
     "per slide - title bar, HTML text/table panel, chart - and (3) <basename>.wcax with the same viewpoints, plus a "
     "contact sheet PNG of all viewpoints for checking. Runs in the background; poll with vp_job_status.",
     {"type": "object", "required": ["md_path", "cax_path"], "properties": {
         "md_path": S, "cax_path": S, "out_dir": S, "basename": S, "viewpath": S,
         "rich": {"type": "boolean"}, "wcax": {"type": "boolean"}, "screenshots": {"type": "boolean"},
         "wait_seconds": {"type": "number"}, "timeout_s": {"type": "number"}}}, t_build),
    ("vp_job_status", "Status of a background VCollab job: running/done/failed, progress log tail and the result "
     "(viewpoints, probe checks, output files). Waits up to wait_seconds (max 55) for completion.",
     {"type": "object", "required": ["job_id"], "properties": {"job_id": S, "wait_seconds": {"type": "number"}}}, t_status),
    ("vp_list_jobs", "List VCollab jobs started in this session.", {"type": "object", "properties": {}}, t_list),
]
TOOL_MAP = {t[0]: t for t in TOOLS}


# --------------------------------------------------------------------------- JSON-RPC
def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def handle(msg):
    mid, method = msg.get("id"), msg.get("method")
    if method == "initialize":
        pv = (msg.get("params") or {}).get("protocolVersion", PROTOCOL)
        return {"protocolVersion": pv, "capabilities": {"tools": {}},
                "serverInfo": {"name": "vcollab-viewpoints", "version": "0.2.2"}}
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": [{"name": n, "description": d, "inputSchema": s} for n, d, s, _ in TOOLS]}
    if method == "tools/call":
        p = msg.get("params") or {}
        name, args = p.get("name"), p.get("arguments") or {}
        if name not in TOOL_MAP:
            raise KeyError("unknown tool %s" % name)
        try:
            res = TOOL_MAP[name][3](args)
            return {"content": [{"type": "text", "text": json.dumps(res, indent=1, default=str)}], "isError": False}
        except Exception as e:
            return {"content": [{"type": "text", "text": "%s: %s" % (type(e).__name__, e)}], "isError": True}
    raise NotImplementedError(method)


def main():
    err("vcollab-viewpoints MCP server started (python %s)" % sys.version.split()[0])
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        if "id" not in msg:  # notification
            continue
        try:
            send({"jsonrpc": "2.0", "id": msg["id"], "result": handle(msg)})
        except NotImplementedError as e:
            send({"jsonrpc": "2.0", "id": msg["id"], "error": {"code": -32601, "message": "Method not found: %s" % e}})
        except Exception as e:
            send({"jsonrpc": "2.0", "id": msg["id"], "error": {"code": -32603, "message": str(e)}})


if __name__ == "__main__":
    main()
