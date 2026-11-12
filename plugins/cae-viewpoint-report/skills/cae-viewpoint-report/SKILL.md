---
name: cae-viewpoint-report
description: >
  Senior CAE-engineer review (cae-expert method) of a VCollab .cax model delivered as THREE files:
  (1) a viewpoint Markdown report (slides + model data + one VCollab Pro viewpoint per slide),
  (2) a CAX with rich PPT-style viewpoints (title bar, text/tables, charts, probes) and (3) a WCAX
  with the same viewpoints - built automatically with VCollab Pro through the vcollab-viewpoints
  tools. Accepts a .cax OR a native solver file (.op2, .bdf, .odb, .rst, .rth, d3plot, .cas+.dat,
  .t16 ...), which is converted to CAX automatically with VMoveCAEBatch first. Use when the user
  asks to "review this cax/op2/odb/rst and create viewpoints", "viewpoint report", "cax and wcax
  with viewpoints", "rich viewpoints", "build the viewpoints from the MD", "VCollab Pro report",
  or gives a CAE result file and wants a review with viewpoints.
---

# CAE viewpoint report: MD + CAX + WCAX

Deliverables (same folder, default `<model folder>/<model>_viewpoints/`; for native input the
converted `<model>.cax` is written there too and is the base of the viewpoint CAX):
1. `<model>_viewpoints.md` — the review: front matter, Model data, build instructions, one
   `## Slide N` per slide with slide content and a `viewpoint:` yaml block.
2. `<model>_viewpoints.cax` — source model + viewpath with one rich viewpoint per slide.
3. `<model>_viewpoints.wcax` — the same viewpoints for VCollab Web.
Plus `<model>_viewpoints_assets/contact_sheet.png` for checking.

## Tools (MCP server `vcollab-viewpoints`)
| Tool | Purpose |
|---|---|
| `vp_env_check` | VCollabPro.exe / VMoveCAEBatch.exe / CaeInfo.exe found? Run first if anything fails |
| `vp_cae_info` | Native file metadata (CaeInfo XML): parts, results, instances, loads, constraints, counts |
| `vp_translate` | Native file → CAX with VMoveCAEBatch (background job) |
| `vp_extract_model` | Catalogue + result sweep → `<model>_model_data.json` (background job) |
| `vp_verify_probes` | Probe candidate node/element IDs and compare with expected values |
| `vp_build` | MD → CAX + WCAX (+ contact sheet). Background job |
| `vp_job_status` | Poll a job (`wait_seconds` ≤ 55); returns progress and the result |

Jobs run VCollab Pro in batch mode in the background, so long builds are fine: keep polling
`vp_job_status` until `state` is `done` or `failed`. Never assume success without the result.

## Workflow

0. **Native input → CAX (automatic)** — if the user gives a native solver file instead of a `.cax`
   (or alongside one), convert it first; do not ask the user to do it:
   - `vp_cae_info(model_file[, results_file])` → read the XML: result names, instances, parts,
     load cases, constraints, element/node/material/property counts (use these in the review).
   - `vp_translate(model_file[, results_file], element_results=...)` → poll `vp_job_status` to `done`.
     Always pass `element_results` with the stress/strain tensor results listed by CaeInfo (e.g.
     `"Stress"`, `"Stress, Strain"`): the CAX then holds unaveraged element values
     (result names become `Element Stress (Top Section)` etc.), so peaks match the solver
     (bracket test: 53,991 psi at element 127 vs 51,986 nodal-averaged). Add `sections` for shells
     if needed, `results` / `parts` / `instances` filters for very large models, `results_file`
     for two-file formats (Fluent `.cas` + `.dat`), `odb_fast_load` for big Abaqus ODBs.
   - If translation fails, show the console tail (format/version/licence) and stop.
   - Continue with the produced CAX as `cax_path`; keep the native file for the review.
1. **Extract** — `vp_extract_model(cax_path)`, poll to `done`, then Read the JSON it wrote.
   It gives exact part names, result names, derived-type names, instances with Time/Frequency,
   per-instance min/max with IDs, peak instance and the top parts at the peak. Also read any native
   files the user supplied (OP2/ODB/F06/BDF… with whatever readers are available) — native data
   (materials, element stresses, loads) takes priority for the engineering review.
2. **Review** — follow `references/review-protocol.md` (always) and `domains.md` /
   `postprocessing.md` as relevant: never invent data, infer and state units, question peaks,
   check equilibrium / energy / plausibility, do hand calculations, give GO / NO-GO / CONDITIONAL.
   Ask (once) for material allowables or acceptance criteria if needed; otherwise state assumptions.
3. **Write the MD** — format in `references/md-format.md` (sections 1–5). Worked examples:
   `references/example-bracket.md` (static, 12 slides) and `references/example-airbag.md`
   (transient, 13 slides). Use the standard slide plan below; add ```` ```chart ```` blocks with real
   extracted data for time histories, per-part comparisons, margins etc.
4. **Verify IDs** — collect every probe `{part, id, result, instance, derived, expected}` and run
   `vp_verify_probes`. Fix or replace anything not `OK` (another part, another ID from the
   extraction, or `type: minmax_label`). Only verified IDs go into the MD.
5. **Build** — `vp_build(md_path, cax_path, out_dir)`; poll `vp_job_status` until done. Check
   `result.viewpoints[*].added`, `probe_issues` (must be empty) and `outputs` (cax, wcax,
   contact_sheet).
6. **Check visually** — Read `contact_sheet.png`. Fix overflowing panels (shorten text, split a
   table, or move detail into a chart), wrong camera, empty views; edit the MD and rebuild.
7. **Deliver** — present the three files (MD, CAX, WCAX) and the contact sheet; reply with the
   verdict in one sentence, slide/viewpoint count, any IDs or data the user must confirm.

## Standard slide plan (adapt to the physics)
| # | Slide | Viewpoint |
|---|---|---|
| 1 | Title (+ verdict badge) | Geometry / thickness overview, iso |
| 2 | Executive summary (KPI table + 4 bullets) | Governing result, legend capped at allowable |
| 3 | 1 · Problem understanding | Loads + restraints (probes at load nodes, notes) |
| 4 | 2 · Model setup review (table + callout) | Property / thickness zones |
| 5 | 3–4 · Mesh and boundary conditions | Mesh display + reaction probes |
| 6 | 5 · Solver assessment | Deformed shape / velocity at key time |
| 7 | 6 · Results interpretation (+ chart) | Governing result, hotspot probes, secondary viewpoints |
| 8 | 7 · Engineering validation – hand calcs (+ chart) | Component checked, critical part only |
| 9 | Margins of safety (+ chart) | Exceedance view: legend min = allowable, filter |
| 10 | 8 · Risks and limitations (HIGH/MED/LOW table) | Riskiest location |
| 11 | 9 · Recommendations | Part to change isolated |
| 12 | 10 · Final verdict (verdict banner) | Closing image |
Transient: add a deployment/peak-time slide with secondary viewpoints at key instances and a
time-history chart; replace margins with a data-quality slide if no allowable exists.
Modal: one slide per key mode + frequency table chart.

## Rules for viewpoint blocks
- Names exactly as in the extraction JSON (parts, results, instances). Derived types may be
  intents; the builder resolves them, but exact names are safest.
- Legend values in model units. Cap at the allowable when known.
- Probes only at verified IDs; give `expected_cax`. Duplicate final states in transient files can be
  incomplete — use the previous instance.
- Every slide gets a viewpoint; viewpoint names `NN_Short_Name`.
- Panels hold ~1,100 characters (no chart) or ~600 (with chart); keep slide text tight.
