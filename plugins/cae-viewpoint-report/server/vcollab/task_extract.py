# ---------------------------------------------------------------------------
# task_extract.py - model catalogue + result sweep for the engineering review.
# JOB: {job_dir, cax, out_json, max_instances (40), max_parts (400), top_parts (15)}
# ---------------------------------------------------------------------------


def _mm(m, r, i, d):
    v = call("minmax", V.pxGetResultMinMax, m, r, i, d)
    v = list(v or [])
    if len(v) >= 4 and valid(v[0]) and valid(v[1]):
        return {"min": v[0], "max": v[1], "min_id": int(v[2]), "max_id": int(v[3])}
    return None


def main():
    m = current_model()
    log("model %s" % m)
    max_inst = int(JOB.get("max_instances", 40))
    max_parts = int(JOB.get("max_parts", 400))
    top = int(JOB.get("top_parts", 15))
    parts = list(call("parts", V.pxGetPartsList, m, "", 0) or [])
    data = {"model": m, "cax": JOB.get("cax"), "history": list(call("hist", V.pxGetCaxHistory, "") or []),
            "bounds": list(call("bounds", V.pxGetPartBounds, m, "", False, True) or []),
            "num_parts": len(parts), "parts": [], "results": {}, "notes": []}
    for p in parts[:max_parts]:
        data["parts"].append({"name": p, "nodes": call("nn", V.xGetNoOfNodes, m, [p], False),
                              "bounds": [round(x, 4) for x in (call("pb", V.pxGetPartBounds, m, p, False, True) or [])]})
    if len(parts) > max_parts:
        data["notes"].append("part details limited to first %d of %d parts" % (max_parts, len(parts)))
    results = list(call("results", V.pxGetCAEResultsList, m) or [])
    log("%d parts, %d results" % (len(parts), len(results)))
    for r in results:
        der = list(call("der", V.pxGetCAEResultDerivedTypes, m, r) or [])
        d = default_derived(der)
        inst = list(call("inst", V.pxGetCAEInstanceList, m, r) or [])
        rec = {"derived_types": der, "default_derived": d, "instances": inst}
        for key in ("Time", "Frequency", "Load Factor"):
            vals = call("attr", V.pxGetInstanceAttributeList, m, r, key, inst) if inst else None
            if vals and any(valid(x) for x in vals):
                rec["instance_" + key.lower().replace(" ", "_")] = [x if valid(x) else None for x in vals]
        idx = list(range(len(inst)))
        if len(idx) > max_inst:
            step = len(idx) / float(max_inst)
            idx = sorted(set([int(k * step) for k in range(max_inst)] + [len(idx) - 1]))
            rec["sweep_sampled"] = True
        sweep = []
        for k in (idx or [None]):
            i = inst[k] if k is not None else ""
            mm = _mm(m, r, i, d)
            sweep.append({"instance": i, **(mm or {})})
        rec["sweep"] = sweep
        good = [s for s in sweep if "max" in s]
        if good:
            pk = max(good, key=lambda s: s["max"])
            lo = min(good, key=lambda s: s["min"])
            rec["peak"] = pk
            rec["lowest"] = lo
            pp = []
            for p in parts[:max_parts]:
                v = list(call("pmm", V.pxGetPartMinMax, m, r, pk["instance"], d, p) or [])
                if len(v) >= 4 and valid(v[0]) and valid(v[1]):
                    pp.append({"part": p, "min": v[0], "max": v[1], "min_id": int(v[2]), "max_id": int(v[3])})
            pp.sort(key=lambda x: -x["max"])
            rec["parts_at_peak_top"] = pp[:top]
            rec["parts_with_values"] = len(pp)
        data["results"][r] = rec
        log("result %s done" % r)
    out = JOB["out_json"]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, default=str)
    summary = {"model_data_json": out, "model": m, "num_parts": len(parts),
               "results": {r: {"derived": v["default_derived"], "n_instances": len(v["instances"]),
                               "peak": v.get("peak")} for r, v in data["results"].items()}}
    finish(summary)


run(main)
