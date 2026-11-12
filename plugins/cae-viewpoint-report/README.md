# cae-viewpoint-report

Senior CAE review of a VCollab `.cax` model **or a native solver file** (Nastran `.op2`/`.bdf`, Abaqus
`.odb`, ANSYS `.rst`/`.rth`, LS-DYNA `d3plot`, Fluent `.cas`+`.dat`, Marc `.t16`, ...), delivered as
three files:

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

MCP tools: `vp_env_check`, `vp_cae_info`, `vp_translate`, `vp_extract_model`, `vp_verify_probes`, `vp_build`, `vp_job_status`,
`vp_list_jobs`.

## Requirements
- Windows with **VCollab Pro 2026** (tested with 26.1); for native input also **VMoveCAE** (same
  install, `VMoveCAE64\VMoveCAEBatch.exe` and `CaeInfo.exe`) licensed for your solver formats — the jobs run in VCollab Pro's embedded
  Python, which already contains yaml, matplotlib, numpy and PIL.
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** on your `PATH` (same as the
  VCollab plugin). It starts the small MCP server, which uses only the Python standard library.
- Claude Code, or Cowork sessions that run on your computer.
- VCollabPro.exe is found automatically under `C:\Program Files\VCollab\<version>\VCollabPro64\`.
  Set the **VCollab installation folder** setting (or env `VCOLLABPRO_EXE`) to override.

## How it works
0. **Native input** is converted automatically: `vp_cae_info` runs VMoveCAE **CaeInfo** (parts,
   results, instances, loads, constraints) and `vp_translate` runs **VMoveCAEBatch** with
   `--element-results` for stress/strain, so the CAX keeps unaveraged element values. Tested on
   `Samples\Native CAE Files\bracket.op2`: peak von Mises 53,991 psi at element 127, matching the
   solver, instead of 51,986 psi node-averaged in a default CAX.
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
- `/viewpoint-report D:\models\bracket.op2` (converted to CAX automatically)
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

## Troubleshooting
| Symptom | Cause / fix |
|---|---|
| `ModuleNotFoundError: _CaeEngineWrap_x64_Release` / `_CaeInfoWrap_x64_Release` | VMoveCAE / VCollab Pro started without `VCOLLAB_DIR` (an empty plugin setting hid the system value). Fixed in 0.2.2: children always get the detected install folder; `vp_env_check` shows `vcollab_dir_for_children`. |
| Job stays `running` with no progress; console ends at `OGRE Initialising` | VCollab Pro cannot start (before 0.2.2 usually the missing `VCOLLAB_DIR`). Otherwise end leftover `VCollabPro.exe` processes, unlock the Windows session, re-run. |
| Translation fails for a format | Check the console tail: unsupported version, missing VMoveCAE licence for that solver, or a separate results file (Fluent `.dat`). |

## Privacy and license

See [PRIVACY.md](PRIVACY.md). MIT licensed; see [LICENSE](LICENSE). VCollab itself is commercial
software licensed separately.
