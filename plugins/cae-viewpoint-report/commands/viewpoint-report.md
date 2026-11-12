---
description: Review a .cax or native CAE file and deliver viewpoint MD + CAX with rich viewpoints + WCAX
argument-hint: <model.cax | model.op2/.odb/.rst/d3plot/...> [results file] [allowable / focus]
---

Create the CAE viewpoint report for: $ARGUMENTS

1. If no model path is given, ask for it (one question) and stop until answered.
2. Run `vp_env_check`; if VCollab Pro (or, for native input, VMoveCAEBatch) is not found, explain
   the README setup and stop.
3. If the input is a native solver file, convert it automatically: `vp_cae_info`, then
   `vp_translate` with `element_results` for the stress/strain results, poll `vp_job_status`
   until done, and use the produced CAX from here on (keep the native file for the review).
4. Follow the `cae-viewpoint-report` skill end to end: extract → review → write
   `<model>_viewpoints.md` → verify probe IDs → `vp_build` → poll `vp_job_status` → read the
   contact sheet and fix issues → rebuild if needed.
5. Finish by presenting the three files (MD, CAX, WCAX) plus the contact sheet, the verdict in one
   sentence, the number of viewpoints, and anything the user must confirm.
