---
description: Review a .cax model and deliver viewpoint MD + CAX with rich viewpoints + WCAX
argument-hint: <path-to-model.cax> [native files] [allowable / focus]
---

Create the CAE viewpoint report for: $ARGUMENTS

1. If no `.cax` path is given, ask for it (one question) and stop until answered.
2. Run `vp_env_check`; if VCollab Pro is not found, explain the README setup and stop.
3. Follow the `cae-viewpoint-report` skill end to end: extract → review → write
   `<model>_viewpoints.md` → verify probe IDs → `vp_build` → poll `vp_job_status` → read the
   contact sheet and fix issues → rebuild if needed.
4. Finish by presenting the three files (MD, CAX, WCAX) plus the contact sheet, the verdict in one
   sentence, the number of viewpoints, and anything the user must confirm.
