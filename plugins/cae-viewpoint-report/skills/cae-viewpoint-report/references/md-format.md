# Markdown format: CAE review slides + VCollab Pro viewpoints (schema 1.0)

One UTF-8 `.md` file, in this order.

## 1. Front matter
```yaml
---
document: cae-review-viewpoints
schema_version: 1.0
title: "<report title>"
subtitle: "<analysis summary>"
source_native: "<file or null>"
source_cax: "<file or null>"
cax_model_name: "<name returned by xGetCurCAEModelName, if known>"
solver: "<solver + solution type>"
analysis: "<linear static | modal | transient | thermal | CFD ...>"
units: {length: "", force: "", stress: "", time: ""}
units_basis: "<stated | assumed because ...>"
verdict: "GO | NO-GO | CONDITIONAL"
viewpath: "CAE Review - <model>"
slide_count: <n>
generated: "<YYYY-MM-DD>"
---
```

## 2. `## Model data`
Sub-sections, as Markdown tables:
- **Source and translation** – files, sizes, translator version, node/element counts, envelope, up axis.
- **Parts** – CAX part name | native ID | thickness/section | elements | zone/location | role.
- **Material** – all material values with a note on what is suspect or missing.
- **Results available in the CAX** – exact result name | instances | type | location
  (nodal/elemental/averaged) | derived types to use.
- **Load cases** – native name | CAX instance | label/time/frequency.
- **Key locations** – Tag | node/element | ID(s) | part | coordinates | meaning (loads, SPCs,
  hotspots, max displacement). Tags are referenced in slides.
- **Key values** – quantity | native value | CAX value | limit.
- **Name mapping** (only when names were not verified in a CAX) – native → expected CAX name.
- A `> CAX caveat:` line whenever CAX values differ from native ones (averaging, units, missing data).

## 3. `## Viewpoint build instructions`
Numbered steps for the VCollab Pro assistant: open the file, model name, create the viewpath,
per-slide reset → apply → `xAddViewPoint(name, viewpath, -1)`, legend units, probe/note API,
camera conventions.

## 4. One section per slide
```markdown
## Slide <n> — <title as on the slide>
<!-- slide: <n> | id: <kebab-id> | type: <title|kpi+bullets|bullets+3d|table+callout|table+bullets|risk-list|numbered-list|verdict|...> | role: <context|setup|key-result|validation|summary> -->

### Slide content
<all text exactly as it should appear: headline, bullets (bold lead-ins), tables, KPI table,
callouts as **Callout (info|warning|critical) — Title:** text, 2D charts as
**Chart (2D, not a viewpoint):** description>

### Viewpoint
```yaml
viewpoint:
  name: "<NN_Short_Name>"
  purpose: "<what the image must show>"
  result: {name: "<exact CAX result>", instance: "<exact instance>", derived: "<intent>"}
  deformation: {enabled: <bool>, result: "Displacement", scale: <float>, uniform: true,
                show_undeformed: <bool>}
  legend: {visible: true, mode: auto|user, user_min: <model units>, user_max: <model units>,
           filter_out_of_range: <bool>, levels: <int>, title: "<legend title with units>"}
  parts: {show: all | [..], show_only: [..], hide: [..], transparent: [{part: "", level: 0-1}]}
  display: {mode: shaded | shaded_with_mesh | mesh | wireframe}
  camera: {std_view: Iso|Front|Back|Top|Bottom|Left|Right, up_axis: "+Z", fit: visible_parts|window,
           zoom_target: {node: <id>, part: ""}}
  probes:
    - {type: node|element, id: <id>, part: "", result: "", derived: "", expected_cax: <value>,
       label: "<text shown>"}
  notes:
    - {part: "", node: <id>, text: ["line 1", "line 2"]}
  secondary_viewpoints: [ {name: "", result: {...}, parts: {...}, probes: [...]} ]   # optional
  animation: none | {type: deformation|transient, frames: <n>}
  caveat: "<optional>"
```
```

## Mapping to the VCollab Pro API (for the assistant)
| Field | API |
|---|---|
| result / instance / derived | `xSetCAEResult(model, result, instance, derived)`; resolve derived with `pxGetCAEResultDerivedTypes` |
| deformation | `xSetCAEDeformScaleFactorEx(model, uniform, sx, sy, sz)` |
| legend user range | `xSetCAELegendRangeEx(model, bAllInstances, bUserMax, max, bUserMin, min, bFilter)` |
| parts.show_only | `xDisplayOnePart(model, part, fit)` or `xShowPartsID` |
| camera std_view | `xSetStdView(i)` / best view `pxGetBestStdViewList` |
| fit | `xFitView()` / `xFitWindowViewEx` |
| probes | `xCAEProbeID(model, part, id, result, instance, derived)` |
| notes | `xAdd3DNotesByID(model, part, node, [lines])` |
| capture | `xAddViewPath(viewpath)` then `xAddViewPoint(name, viewpath, -1)` |

Rules: legend values in model units; IDs only if verified; every slide has a viewpoint; names
quoted exactly; derived types written as intent.

## 5. Additions used by the plugin build (`vp_build`)

### Charts — ```` ```chart ```` blocks inside "### Slide content"
The first chart block of a slide is rendered (matplotlib, inside VCollab Pro) and placed below the
slide's text panel. Data must come from the model data / extraction JSON — never invented.
```chart
type: line            # line | bar | barh
title: "Deployment time history"
xlabel: "Time (ms)"
ylabel: "mm"
y2label: "MPa"        # optional right axis label
x: [0, 20, 25, 30, 40, 80]
series:
  - {label: "Max displacement (mm)", y: [0, 9.3, 126.7, 283.8, 410.9, 734.5]}
  - {label: "Max von Mises (MPa)", y: [0, 1.0, 23.5, 21.8, 47.2, 34.5], axis: right}
  - {label: "min (non-physical)", y: [...], fill_negative: true}       # shades values < 0
hlines: [{y: 42, label: "ST = 42 ksi", color: "#c0392b"}]
vlines: [{x: 30, label: "punch-out"}]
color_by_sign: true   # bar/barh: green >= 0, red < 0 (margins)
value_labels: true    # bar/barh: print values
ylim: [0, 60]         # optional
```
A slide with a chart block should NOT also contain a "Chart (2D, not a viewpoint)" line (those
lines are dropped from the panel anyway).

### Special slide-content lines (rendered as styled blocks)
| Line | Rendered as |
|---|---|
| `**Headline:** …` / `**Subtitle:** …` | Subtitle in the title bar |
| `**Callout (info\|warning\|critical) — Title:** text` | Coloured callout box |
| `**Verdict banner (red\|orange\|green):** text` | Full-width verdict banner |
| Table whose first header cell is `KPI` (columns KPI \| Value \| Detail, max 4 rows) | KPI cards |
| Table cells `HIGH` / `MED` / `LOW` | Coloured risk badges |
| Slide 1 (or `type: title`) lines `**Title:**`, `**Subtitle:**`, `**Source data:**`, `**Units:**`, `**Badge:**` | Title page; badge colour from NO-GO / GO / CONDITIONAL |

### Viewpoint fields the builder understands
- `camera`: `std_view` (Iso, Front, Back, Left, Right, Top, Bottom, side) with `up_axis` (+Z or +Y),
  or explicit `view_dir: [x, y, z]` and optional `up_vector`.
- `probes`: `{type: node|element, id, part, result, derived, expected_cax, label}` — verified at
  build time (status OK / MISMATCH / NO VALUE in the job result) — or
  `{type: minmax_label, show: max}` to let VCollab label the max/min automatically
  (use when an element ID does not probe reliably).
- `derived`: intent names are resolved to the exact VCollab name (Von Mises → "Von Mises Stress",
  Translational Magnitude → "Resultant" where needed, …); exact names are used as-is.
- `secondary_viewpoints`: extra viewpoints inheriting the parent's settings (title bar only, no panel).
