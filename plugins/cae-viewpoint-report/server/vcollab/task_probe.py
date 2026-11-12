# ---------------------------------------------------------------------------
# task_probe.py - verify probe IDs before they go into a viewpoint MD file.
# JOB: {job_dir, cax, probes: [{part, id, result, instance, derived, expected}]}
# ---------------------------------------------------------------------------


def main():
    m = current_model()
    out = []
    for p in JOB.get("probes", []):
        r, i, d = p["result"], p.get("instance", ""), p.get("derived", "")
        call("set", V.xSetCAEResult, m, r, i, d)
        v = call("probe", V.xCAEProbeID, m, p.get("part", ""), int(p["id"]), r, i, d)
        exp = p.get("expected")
        rec = dict(p)
        if valid(v):
            rec["value"] = v
            rec["status"] = "OK" if exp is None or abs(v - exp) <= 0.02 * abs(exp) + 1e-9 else "MISMATCH"
        else:
            rec["value"] = None
            rec["status"] = "NO VALUE (wrong part/ID or entity type) - try another part, or use type: minmax_label"
        out.append(rec)
    call("del", V.xDeleteAllProbeLabels, "")
    finish({"probes": out, "all_ok": all(x["status"] == "OK" for x in out)})


run(main)
