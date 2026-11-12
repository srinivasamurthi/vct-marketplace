# cae-viewpoint-report

Senior CAE review of a VCollab `.cax` model, delivered as three files:

| # | File | What it is |
|---|---|---|
| 1 | `<model>_viewpoints.md` | Review slides + model data + one VCollab Pro viewpoint spec per slide |
| 2 | `<model>_viewpoints.cax` | The model with a viewpath of rich viewpoints: title bar, text/table panel, chart, probes, 3D notes |
| 3 | `<model>_viewpoints.wcax` | The same viewpoints for VCollab Web |

plus `<model>_viewpoints_assets/` (HTML panels, chart PNGs, per-viewpoint screenshots and
`contact_sheet.png`).

## Install

Add **CAE Viewpoint Report** from the plugin directory in Claude (**Customize > Plugins**), or in
Claude Code (2.1.275 or later):

```
/plugin install cae-viewpoint-report --marketplace vcollab/vct-marketplace
```

## Components
| Component | Purpose |
|---|---|
| Skill `cae-viewpoint-report` | Review method (cae-expert protocol), MD format, slide plan, workflow |
| Command `/viewpoint-report <model.cax> [native files] [allowable]` | One-shot run |
| MCP server `vcollab-viewpoints` (`server/vp_server.py`) | Starts VCollab Pro batch jobs in the background and reports progress |

MCP tools: `vp_env_check`, `vp_extract_model`, `vp_verify_probes`, `vp_build`, `vp_job_status`,
`vp_list_jobs`.

## Requirements
- Windows with **VCollab Pro 2026** (tested with 26.1) — the jobs run in VCollab Pro's embedded
  Python, which already contains yaml, matplotlib, numpy and PIL.
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** on your `PATH` (same as the
  VCollab plugin). It starts the small MCP server, which uses only the Python standard library.
- Claude Code, or Cowork sessions that run on your computer.
- VCollabPro.exe is found automatically under `C:\Program Files\VCollab\<version>\VCollabPro64\`.
  Set the **VCollab installation folder** setting (or env `VCOLLABPRO_EXE`) to override.

## How it works
1. `vp_extract_model` runs `VCollabPro.exe -b job.py model.cax` and writes
   `<model>_model_data.json` (parts, results, exact derived names, instances, min/max with IDs).
2. Claude reviews the data (plus any native solver files) and writes the viewpoint MD.
3. `vp_verify_probes` checks every node/element ID before it goes into the MD.
4. `vp_build` reads the MD inside VCollab Pro, creates the HTML panels and charts, builds one
   viewpoint per slide, saves the CAX, exports the WCAX (`xExportWCax`, current viewpath, with
   thumbnails) and takes a screenshot of every viewpoint for the contact sheet.
Jobs run in the background (default limit 60 min); job files are kept in `<out_dir>/_jobs/`.

## Usage
- `/viewpoint-report D:\models\bracket.cax`
- "Review Airbag.cax and give me the viewpoint report with CAX and WCAX"
- "Build the CAX and WCAX from D:\out\airbag_viewpoints.md"

## Notes and limits
- Rich labels are created with Auto Resize; they scale with the VCollab window. Text is sized
  automatically by panel length — check the contact sheet for overflow.
- The WCAX is exported from the same viewpath; rich-text panels are VCollab 2D labels — check in
  VCollab Web that they display as expected for your viewer version.
- Probe values in VCollab are those stored in the CAX (often nodal-averaged); the MD states native
  element values separately where they differ.
- The CAX contains no material, energy or solver data; supply native files or allowables for a
  full verdict.

## Privacy and license

See [PRIVACY.md](PRIVACY.md). MIT licensed; see [LICENSE](LICENSE). VCollab itself is commercial
software licensed separately.
