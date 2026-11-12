#!/usr/bin/env python3
"""
vp_server.py - MCP (stdio) server for the cae-viewpoint-report plugin.

Pure standard library (no pip installs). It launches VCollab Pro in batch mode
(`VCollabPro.exe -b job.py model.cax`) as background jobs, so long builds are not
cut off by client time-outs, and reports progress / results.

Tools: vp_env_check, vp_extract_model, vp_verify_probes, vp_build, vp_job_status, vp_list_jobs
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
    env = dict(os.environ, VCOLLAB_ENABLE_VCOLLABPRO_SCRIPT="1")
    flags = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW
    proc = subprocess.Popen([exe, "-b", script, cax], cwd=jdir, stdout=out, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, env=env, creationflags=flags)
    with LOCK:
        JOBS[jid] = {"id": jid, "kind": kind, "proc": proc, "dir": jdir, "start": time.time(),
                     "timeout": timeout_s, "job": job, "log": out}
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
        return st
    try:
        j["log"].close()
    except Exception:
        pass
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
    return {"vcollabpro_exe": exe, "found": bool(exe), "server_python": sys.version.split()[0],
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
                "serverInfo": {"name": "vcollab-viewpoints", "version": "0.1.0"}}
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
