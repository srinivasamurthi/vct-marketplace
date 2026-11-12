# ---------------------------------------------------------------------------
# common.py - shared helpers for VCollab Pro batch jobs (runs INSIDE VCollab
# Pro's embedded Python 3.12). The server prepends `JOB = {...}` to this file.
# ---------------------------------------------------------------------------
import json, os, re, time, traceback
import _VCollabAPI as V

_T0 = time.time()
os.makedirs(JOB["job_dir"], exist_ok=True)
_LOGF = open(os.path.join(JOB["job_dir"], "progress.log"), "a", encoding="utf-8")
ERRORS = []
FLT = 1e30


def log(msg):
    _LOGF.write("%7.1f %s\n" % (time.time() - _T0, msg))
    _LOGF.flush()


def call(tag, fn, *a):
    try:
        return fn(*a)
    except Exception as e:
        ERRORS.append("%s: %s" % (tag, e))
        log("ERR %s: %s" % (tag, e))
        return None


def valid(v):
    return v is not None and isinstance(v, (int, float)) and abs(v) < FLT


def finish(result, ok=True):
    result["ok"] = ok
    result["errors"] = ERRORS[:200]
    result["elapsed_s"] = round(time.time() - _T0, 1)
    with open(os.path.join(JOB["job_dir"], "result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, default=str)
    log("DONE ok=%s" % ok)
    try:
        write_output(result)  # noqa: F821  (only defined when run via the vcollab MCP)
    except NameError:
        pass


def run(main):
    try:
        main()
    except Exception:
        tb = traceback.format_exc()
        log("FATAL " + tb.replace("\n", " | "))
        finish({"traceback": tb}, ok=False)


def current_model():
    m = V.xGetCurCAEModelName()
    if not m and JOB.get("cax"):
        call("open", V.xFileOpen, JOB["cax"])
        m = V.xGetCurCAEModelName()
    return m


DERIVED_PREF = ["Von Mises Stress", "Translational Magnitude", "Resultant", "Magnitude"]


def default_derived(lst):
    for d in DERIVED_PREF:
        if d in lst:
            return d
    return lst[0] if lst else ""
