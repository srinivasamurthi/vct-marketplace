---
document: cae-review-viewpoints
schema_version: 1.0
title: "Airbag Deployment — Transient Explicit Review"
subtitle: "CAE Engineering Review of Airbag.cax (LS-DYNA d3plot, 0–80 ms)"
source_native: "d3plot (not provided; review based on the CAX only)"
source_cax: "Airbag.cax"
cax_model_name: "Airbag"
solver: "LS-DYNA explicit (from CAX metadata)"
analysis: "Transient / explicit dynamics — airbag deployment"
units: {length: "mm", time: "ms", mass: "kg", force: "kN", stress: "GPa", energy: "J"}
units_basis: "inferred: gravity appears as 0.00981 mm/ms² in Acceleration at t = 0, time steps run 0–80 (ms)"
verdict: "CONDITIONAL"
viewpath: "CAE Review - Airbag"
slide_count: 13
generated: "2026-11-11"
---

# Airbag Deployment — CAE Review: slides and viewpoints

This file describes a 13-slide CAE review of `Airbag.cax` and, for every slide, the VCollab Pro
viewpoint that illustrates it. All numbers were extracted from the CAX with VCollab Pro
(`pxGetResultMinMax`, `pxGetPartMinMax`, `pxGetInstanceAttributeList`). No native deck, material
cards, energy files (glstat/matsum) or test data were available.

## Model data

### Source and translation
| Item | Value |
|---|---|
| Native files | d3plot (LS-DYNA), 13.79 MB — not provided for this review |
| CAX metadata oddity | Results file listed as "blower.dat (Fluent solution, 64 MB)" — inconsistent with an LS-DYNA run; verify the translation inputs |
| CAX file | Airbag.cax (3.87 MB), VMoveCAE 2.1.219.301, CAX 1.2, translated 01 Mar 2019 |
| CAX model name | `Airbag` |
| Parts / nodes | 110 parts (named `id = N`), 8,434 nodes |
| Envelope (t = 0) | X 1978 → 3462, Y −808 → 29, Z 159 → 1284 mm |
| Up axis | +Z (vehicle coordinates; X rearward, airbag deploys towards +X) |
| States | 18 instances `L1M0` … `L18M0`, t = 0 → 80 ms every 5 ms. `L17M0` (79.998 ms) and `L18M0` (80.001 ms) duplicate the end state; **`L18M0` is incomplete** (several nodes return no value) — use `L17M0` for the end state |

### Part groups (identified from the CAX data; part names carry IDs only)
| CAX part(s) | Nodes | Thickness (mm) | Location / behaviour | Role in review |
|---|---|---|---|---|
| `id = 1500` | 349 | 0.3048 | X 2704–2838, Y −697–29, Z 668–1001 | **Airbag fabric panel 1 — critical** |
| `id = 1501` | 349 | 0.3048 | same envelope as 1500 | **Airbag fabric panel 2** |
| `id = 1523` | 221 | — (no thickness result) | X 2988–3343, Z 302–1036; moves up to 506 mm | Large body behind the bag (identity not in CAX) |
| `id = 303`, `id = 304`, `id = 305`, `id = 306`–`id = 312`, `id = 1502`–`id = 1522` | various | 0 / none | move as rigid groups (e.g. 493.4 mm uniform at 80 ms) | Rigid / mechanism parts |
| `id = 86`, `id = 88` | 112 / 167 | 0.5 | X 3027–3350 | Deformable shells (non-fabric) |
| 37 parts | — | 0.0 | — | Zero-thickness parts (rigid, null or beam?) — verify |
| 69 parts | — | no thickness result | — | Solids or non-shell parts |

### Material (not stored in CAX)
| Item | Status |
|---|---|
| Fabric material model, E, density, porosity | **Not available** — needed for stress and inflation assessment |
| Fabric strength / allowable | **Not available.** Typical nylon 6,6 airbag fabric is of the order of 150–250 MPa (literature range, *to be confirmed with supplier data*) |

### Results available in the CAX
| CAX result name | Instances | Type | Derived types to use (exact VCollab names) |
|---|---|---|---|
| `Displacement` | `L1M0`–`L18M0` | Vector (deformation result) | `Resultant`, `X`, `Y`, `Z` |
| `Velocity` | all | Vector | `Resultant` |
| `Acceleration` | all | Vector | `Resultant` |
| `Stress (Centroidal) (Top Section)` | all | Tensor, elemental | `Von Mises Stress`, `Maximum Principal Value`, … |
| `Stress (Centroidal) (Bottom Section)` | all | Tensor, elemental | identical to Top (membrane elements) |
| `Equivalent Plastic Strain (Top Section)` / `(Bottom Section)` | all | Scalar | `""` (scalar) — **see data-quality slide** |
| `Strain Energy` | all | Scalar | `""` |
| `Element Thickness` | all | Scalar | `""` |

Derived names above were read with `pxGetCAEResultDerivedTypes` — vectors use `Resultant`, not
`Translational Magnitude`.

### Key time history (global extremes over all parts)
| t (ms) | Instance | Max displacement (mm) | Min displacement (mm) | Max velocity (mm/ms = m/s) | Max von Mises (GPa) | Max strain energy (J) |
|---|---|---|---|---|---|---|
| 0 | `L1M0` | 0.00 | 0.0 | 0.000 | 0.0000 | 0.0000 |
| 20 | `L5M0` | 9.28 | 0.0 | 6.10 | 0.0010 | 0.0000 |
| 25 | `L6M0` | 126.70 | 0.0 | 54.41 | 0.0235 | 0.0030 |
| 30 | `L7M0` | 283.76 | 0.2 | **154.14** | 0.0218 | 0.0119 |
| 35 | `L8M0` | 436.43 | 0.5 | 84.63 | 0.0263 | 0.0317 |
| 40 | `L9M0` | 410.87 | 0.6 | 82.19 | **0.0472** | 0.0314 |
| 55 | `L12M0` | 472.16 | 7.5 | 49.86 | 0.0450 | 0.0337 |
| 60 | `L13M0` | 505.37 | 17.0 | 84.25 | 0.0336 | 0.0341 |
| 70 | `L15M0` | 585.87 | 43.4 | 40.62 | 0.0252 | 0.0408 |
| 80 | `L18M0` | **734.50** | **146.5** | 29.60 | 0.0345 | **0.0438** |

### Key locations (IDs verified with VCollab min/max queries)
| Tag | Type | ID | Part | Meaning |
|---|---|---|---|---|
| VM_PEAK | element | 150220 | fabric (probe under `id = 1501`) | Peak fabric von Mises 0.04717 GPa (47.2 MPa) at 40 ms |
| VM_1501 | element | 150493 | fabric (probe under `id = 1500`) | Panel 2 peak at 40 ms, 0.02759 GPa |
| VM_80 | element | 150230 | fabric (probe under `id = 1500`) | Peak von Mises at 80 ms (`L17M0`), 0.03447 GPa |
| VM_80_1501 | element | 150429 | fabric (probe under `id = 1500`) | Panel 2 peak at 80 ms, 0.02439 GPa |
| DISP_MAX | node | 150157 | `id = 1500` | Max displacement 734.5 mm at 80 ms (`L17M0`: 734.46) |
| DISP_1501 | node | 150141 | `id = 1501` | Panel 2 max displacement 656.3 mm at 80 ms |
| DISP_MIN_1500 | node | 150222 | `id = 1500` | Least-moving fabric node at 80 ms, 409.7 mm |
| VEL_PEAK | node | 150107 | `id = 1500` (seam node, also in 1501) | Peak velocity 154.1 m/s at 30 ms |
| EPS_NEG | element | 150101 | `id = 1500` | "Equivalent plastic strain" −0.351 at 75 ms (non-physical) |
| EPS_MAX | element | 150220 | `id = 1500` | "Equivalent plastic strain" +0.109 at 75 ms |
| BODY_1523 | node | 909294 | `id = 1523` | Max displacement of part 1523, 505.9 mm at 80 ms (`L17M0`) |
| RIGID_303 | node | 158220 | `id = 303` | Rigid group displacement 494.9 mm at 80 ms |

> **ID note:** the two fabric panels share seam nodes, and VCollab's element→part association for
> the fabric is inconsistent (`pxGetPartMinMax` and `xCAEProbeID` disagree). The part names in the
> probe blocks below are the ones verified to return values; per-panel splits are indicative only.

### Key values
| Quantity | Value (model units) | SI | When / where |
|---|---|---|---|
| Peak fabric von Mises | 0.04717 GPa | 47.2 MPa | 40 ms, elem 150220, part 1500 |
| Peak fabric displacement | 734.5 mm | 0.73 m | 80 ms, node 150157 (still increasing) |
| Peak fabric velocity | 154.1 mm/ms | 154 m/s (555 km/h) | 30 ms, node 150107 |
| Peak nodal acceleration | 3945 mm/ms² | ≈ 4.0 × 10⁵ g | 60 ms, fabric node 150203 (unfiltered) |
| Peak element strain energy | 0.0438 J | — | 80 ms, elem 150102 |
| Global minimum displacement | 146.5 mm | — | 80 ms: **no node of the model is stationary** |

> **CAX caveat:** no energy summaries, contact forces, airbag pressure/volume, or material data are
> stored in this CAX. Energy balance, inflator performance and margins cannot be verified here.

## Viewpoint build instructions
1. Open `Airbag.cax`. Model name: `Airbag` (`xGetCurCAEModelName()`).
2. Create viewpath `CAE Review - Airbag` (`xAddViewPath`).
3. Use `L17M0` (not `L18M0`) for the 80 ms state. For each slide: reset (show all parts, clear probes/notes/2D labels, deformation scale 0,
   legend auto with 12 colours), apply the `viewpoint` block, capture with
   `xAddViewPoint(name, "CAE Review - Airbag", -1)`.
4. Derived names are exact (`Resultant`, `Von Mises Stress`); scalars use `""`.
5. Legend values are in **model units** (stress in GPa, displacement in mm).
6. `Displacement` is the deformation result; `deformation.scale: 1.0` shows true motion at the
   viewpoint's instance.
7. Camera: `side` = look along +Y (view_dir [0, 1, 0], up [0, 0, 1]) — shows the X–Z deployment
   plane; `iso` = view_dir [-1, 1, -1], up [0, 0, 1].
8. `type: minmax_label` probes: call `xShowCAEFrameMinMaxLabels(model, True)` instead of probing an ID —
   element 150220 does not probe reliably (its part association flips between `id = 1500` and
   `id = 1501`). All other probe IDs below were verified to return `expected_cax`.
9. Probe IDs: nodal results use node IDs, centroidal stress / strain energy / plastic strain use
   element IDs. `expected_cax` values were read from this CAX.

---

## Slide 1 — Title
<!-- slide: 1 | id: title | type: title | role: context -->

### Slide content
- **Title:** Airbag Deployment — Transient Explicit Review
- **Subtitle:** CAE Engineering Review of Airbag.cax (LS-DYNA d3plot, 0–80 ms, 18 states)
- **Source data:** CAX geometry, displacement, velocity, acceleration, centroidal stress, strain energy and thickness results
- **Units:** mm · ms · kg · kN · GPa (inferred) · November 2026
- **Badge:** VERDICT: CONDITIONAL (orange)

### Viewpoint
```yaml
viewpoint:
  name: "01_Title"
  purpose: "Deployed bag at the end of the run, coloured by displacement"
  result: {name: "Displacement", instance: "L17M0", derived: "Resultant"}
  deformation: {enabled: true, result: "Displacement", scale: 1.0, uniform: true}
  legend: {visible: true, mode: auto, title: "Displacement (mm) at 80 ms"}
  parts: {show: all}
  display: {mode: shaded}
  camera: {std_view: Iso, view_dir: [-1, 1, -1], up_axis: "+Z", fit: visible_parts}
  probes: []
  notes: []
  animation: none
```

---

## Slide 2 — Executive Summary
<!-- slide: 2 | id: executive-summary | type: kpi+bullets | role: key-result -->

### Slide content
**Headline:** The bag deploys and loads the fabric to 47 MPa, but the run cannot be signed off from this data alone.

| KPI | Value | Detail |
|---|---|---|
| Peak fabric von Mises | 47.2 MPa | 40 ms · elem 150220 · part 1500 |
| Peak fabric velocity | 154 m/s | 30 ms · punch-out phase |
| Fabric excursion | 734 mm | 80 ms · still increasing |
| Global drift | 146 mm | min. displacement at 80 ms — no node at rest |

- **Deployment sequence:** bag motion starts between 20 and 25 ms, punch-out peaks at 30 ms, fabric stress peaks at 40 ms.
- **Fabric stress:** 47.2 MPa peak, about 20–30 % of typical nylon 6,6 fabric strength (assumed range, to be confirmed).
- **Data-quality issue:** the "Equivalent Plastic Strain" result is negative (down to −0.35) and non-monotonic, so it is not a plastic strain.
- **Not verifiable from CAX:** energy balance, bag pressure/volume, contact, material cards; all parts drift by ≥ 146 mm by 80 ms.

### Viewpoint
```yaml
viewpoint:
  name: "02_Executive_Summary"
  purpose: "Fabric stress at its peak time"
  result: {name: "Stress (Centroidal) (Top Section)", instance: "L9M0", derived: "Von Mises Stress"}
  deformation: {enabled: true, result: "Displacement", scale: 1.0, uniform: true}
  legend: {visible: true, mode: user, user_min: 0.0, user_max: 0.05, filter_out_of_range: false,
           title: "von Mises (GPa) at 40 ms"}
  parts: {show_only: ["id = 1500", "id = 1501"]}
  camera: {std_view: Iso, view_dir: [-1, 1, -1], up_axis: "+Z", fit: visible_parts}
  probes:
    - {type: minmax_label, show: max, expected_cax: 0.04717, at: "element 150220",
       label: "Peak 47.2 MPa (40 ms)", api: "xShowCAEFrameMinMaxLabels(model, True)"}
  notes: []
  animation: none
```

---

## Slide 3 — 1 · Problem Understanding
<!-- slide: 3 | id: problem-understanding | type: bullets+3d | role: setup -->

### Slide content
- **System:** airbag module with two fabric panels (parts 1500 and 1501, t = 0.3048 mm) deploying inside a 110-part interior model.
- **Physics:** explicit transient: inflation, unfolding and punch-out of a membrane bag, with large motion and contact.
- **Time window:** 0–80 ms, 18 states every 5 ms.
- **Load path (inferred):** inflator gas pressure on the fabric. Pressure, mass flow and porosity are not in the CAX.
- **Scale:** bag envelope at t = 0 is 134 × 726 × 333 mm (X × Y × Z). It deploys towards +X, towards part 1523 at X ≈ 3000–3340 mm.

### Viewpoint
```yaml
viewpoint:
  name: "03_Problem_Understanding"
  purpose: "Initial configuration: fabric panels and the parts around them"
  result: {name: "Element Thickness", instance: "L1M0", derived: ""}
  deformation: {enabled: false}
  legend: {visible: true, mode: auto, levels: 4, title: "Shell thickness (mm)"}
  parts: {show: all}
  display: {mode: shaded_with_mesh}
  camera: {std_view: side, view_dir: [0, 1, 0], up_axis: "+Z", fit: visible_parts}
  probes: []
  notes:
    - {part: "id = 1500", node: 150222, text: ["Airbag fabric 1500 / 1501", "t = 0.3048 mm"]}
    - {part: "id = 1523", node: 909294, text: ["Part 1523 (221 nodes)", "in the deployment path"]}
  animation: none
```

---

## Slide 4 — 2 · Model Setup Review
<!-- slide: 4 | id: model-setup | type: table+callout | role: setup -->

### Slide content
| Item | Value from CAX | Assessment |
|---|---|---|
| Solver / source | LS-DYNA d3plot via VMoveCAE 2.1.219 | OK |
| Units | mm · ms · kg · GPa (gravity 0.00981 mm/ms²) | Inferred, not stated |
| Fabric | parts 1500, 1501 · 349 nodes each · t = 0.3048 mm | Critical parts |
| Other shells | parts 86, 88 · t = 0.5 mm | Low stress (< 3 MPa) |
| Zero-thickness parts | 37 parts | Rigid / null? Verify |
| Parts without thickness | 69 parts | Solids or rigid bodies |
| Materials, contacts, inflator | Not in CAX | Cannot be reviewed |
| Output states | 5 ms interval, duplicate state at 80 ms | Too coarse for peaks |

**Callout (warning) — Translation metadata:** The CAX lists a Fluent "blower.dat" results file alongside the LS-DYNA d3plot. Confirm the CAX was created from the intended run and that no results were mapped from another solver.

### Viewpoint
```yaml
viewpoint:
  name: "04_Model_Setup"
  purpose: "Thickness map: fabric, 0.5 mm shells and zero-thickness parts"
  result: {name: "Element Thickness", instance: "L1M0", derived: ""}
  deformation: {enabled: false}
  legend: {visible: true, mode: auto, levels: 4, title: "Element thickness (mm)"}
  parts: {show: all}
  camera: {std_view: Iso, view_dir: [-1, 1, -1], up_axis: "+Z", fit: visible_parts}
  probes: []
  notes:
    - {part: "id = 1501", node: 150141, text: ["Fabric t = 0.3048 mm"]}
  animation: none
```

---

## Slide 5 — 3–4 · Mesh Evaluation and Boundary Conditions
<!-- slide: 5 | id: mesh-bc | type: table+bullets | role: setup -->

### Slide content
**Mesh**

| Metric | Result | Status |
|---|---|---|
| Fabric nodes | 349 per panel (698 total) | Coarse for an airbag |
| Fabric envelope | 726 × 333 mm per panel | ≈ 20–30 mm elements (estimate) |
| Total nodes | 8,434 in 110 parts | Small model |
| Element quality | Not in CAX | Not reviewable |

**Boundary conditions and global motion**
- **No reaction forces** are stored, so the restraint of the module cannot be checked.
- **Global drift:** minimum displacement rises from 0 (t ≤ 25 ms) to 7.5 mm at 55 ms and **146.5 mm at 80 ms**. After ~55 ms no node of the model is at rest.
- **Rigid groups:** parts 303–312 and 1502–1505 move together (≈ 493 mm at 80 ms), which suggests a prescribed vehicle / sled motion or an unconstrained module. Verify the intent.

### Viewpoint
```yaml
viewpoint:
  name: "05_Mesh_and_BC"
  purpose: "Fabric mesh density and global motion at 80 ms"
  result: {name: "Displacement", instance: "L17M0", derived: "Resultant"}
  deformation: {enabled: false}
  legend: {visible: true, mode: auto, title: "Displacement (mm) at 80 ms — undeformed view"}
  parts: {show: all}
  display: {mode: shaded_with_mesh}
  camera: {std_view: side, view_dir: [0, 1, 0], up_axis: "+Z", fit: visible_parts}
  probes:
    - {type: node, id: 158220, part: "id = 303", result: "Displacement", derived: "Resultant",
       expected_cax: 494.9, label: "Rigid group 303: 495 mm"}
    - {type: node, id: 909294, part: "id = 1523", result: "Displacement", derived: "Resultant",
       expected_cax: 505.94, label: "Part 1523: 506 mm"}
  notes: []
  animation: none
```

---

## Slide 6 — 5 · Solver Assessment
<!-- slide: 6 | id: solver | type: bullets+3d | role: key-result -->

### Slide content
**Headline:** A completed explicit run is not enough. Energy and noise checks are missing.
- **Energy balance:** no glstat / matsum data in the CAX. Hourglass, contact and total-energy error cannot be checked (criteria: hourglass < 5 %, error < 10 %).
- **Punch-out velocity:** 154 m/s at 30 ms (node 150107). High but possible for an unrestrained fabric edge. Check the inflator mass flow.
- **Acceleration noise:** nodal accelerations of the fabric reach 3945 mm/ms² (≈ 4 × 10⁵ g). These are unfiltered membrane oscillations; filter (e.g. SAE CFC) before any use.
- **Output:** the 5 ms state interval misses short peaks, and the 80 ms state is written twice.

### Viewpoint
```yaml
viewpoint:
  name: "06_Solver_Velocity_30ms"
  purpose: "Punch-out phase: velocity field at its peak time"
  result: {name: "Velocity", instance: "L7M0", derived: "Resultant"}
  deformation: {enabled: true, result: "Displacement", scale: 1.0, uniform: true}
  legend: {visible: true, mode: auto, title: "Velocity (m/s) at 30 ms"}
  parts: {show_only: ["id = 1500", "id = 1501"]}
  camera: {std_view: side, view_dir: [0, 1, 0], up_axis: "+Z", fit: visible_parts}
  probes:
    - {type: node, id: 150107, part: "id = 1500", result: "Velocity", derived: "Resultant",
       expected_cax: 154.14, label: "Peak 154 m/s (30 ms)"}
  notes: []
  animation: none
```

---

## Slide 7 — Deployment Sequence (time history)
<!-- slide: 7 | id: deployment-sequence | type: table+chart | role: key-result -->

### Slide content
| t (ms) | Max disp. (mm) | Max vel. (m/s) | Max vM (MPa) | Phase |
|---|---|---|---|---|
| 20 | 9.3 | 6.1 | 1.0 | Inflation start |
| 25 | 126.7 | 54.4 | 23.5 | Unfolding |
| 30 | 283.8 | 154.1 | 21.8 | Punch-out (velocity peak) |
| 40 | 410.9 | 82.2 | 47.2 | Stress peak |
| 60 | 505.4 | 84.2 | 33.6 | Excursion |
| 80 | 734.5 | 29.6 | 34.5 | End of run, still moving |

- **Chart (2D, not a viewpoint):** max displacement, max velocity and max von Mises against time, 0–80 ms.
- The fabric is still moving outwards at 80 ms, so the run ends before the bag settles or the occupant interaction completes.

### Viewpoint
```yaml
viewpoint:
  name: "07_Deployment_25ms"
  purpose: "Unfolding / punch-out moment"
  result: {name: "Displacement", instance: "L6M0", derived: "Resultant"}
  deformation: {enabled: true, result: "Displacement", scale: 1.0, uniform: true}
  legend: {visible: true, mode: user, user_min: 0.0, user_max: 750.0, title: "Displacement (mm) — common scale"}
  parts: {show: all}
  camera: {std_view: side, view_dir: [0, 1, 0], up_axis: "+Z", fit: visible_parts}
  probes: []
  notes: []
  secondary_viewpoints:
    - name: "07b_Deployment_40ms"
      result: {name: "Displacement", instance: "L9M0", derived: "Resultant"}
    - name: "07c_Deployment_60ms"
      result: {name: "Displacement", instance: "L13M0", derived: "Resultant"}
    - name: "07d_Deployment_80ms"
      result: {name: "Displacement", instance: "L17M0", derived: "Resultant"}
      probes: [{type: node, id: 150157, part: "id = 1500", result: "Displacement", derived: "Resultant",
                expected_cax: 734.46, label: "Max 734.5 mm (80 ms)"}]
  animation: {type: transient, frames: 18, note: "optional: animate L1M0 → L18M0 on the common legend"}
```

---

## Slide 8 — 6 · Results Interpretation — Fabric Stress
<!-- slide: 8 | id: results | type: table+bullets+chart | role: key-result -->

### Slide content
| Part | Max vM at 40 ms | Max vM at 80 ms | Peak element |
|---|---|---|---|
| id = 1500 (fabric, as reported) | 47.2 MPa | 34.5 MPa | 150220 / 150230 |
| id = 1501 (fabric, as reported) | 27.6 MPa | 24.4 MPa | 150493 / 150429 |
| id = 36 | 0.18 MPa | 5.5 MPa | 3174 |
| id = 12, id = 37 | < 0.1 MPa | 3.1 MPa | 3142 / 3110 |
| All other parts | < 0.04 MPa | < 2.7 MPa | — |

- **Hot spot:** element 150220 at 40 ms. VCollab reports 47.2 MPa on panel 1500 and 27.6 MPa on panel 1501, but the element→part association is inconsistent, so treat the split as indicative.
- **Membrane behaviour:** top and bottom centroidal stresses are identical, so the fabric acts as a pure membrane.
- **Strain energy** rises steadily to 0.0438 J per element by 80 ms and sits only in the fabric.
- **Chart (2D, not a viewpoint):** max von Mises per fabric panel against time.

### Viewpoint
```yaml
viewpoint:
  name: "08_Results_Fabric_vonMises_40ms"
  purpose: "Fabric von Mises at peak time with both panel hotspots"
  result: {name: "Stress (Centroidal) (Top Section)", instance: "L9M0", derived: "Von Mises Stress"}
  deformation: {enabled: true, result: "Displacement", scale: 1.0, uniform: true}
  legend: {visible: true, mode: auto, levels: 12, title: "von Mises (GPa) at 40 ms"}
  parts: {show_only: ["id = 1500", "id = 1501"]}
  camera: {std_view: Iso, view_dir: [-1, 1, -1], up_axis: "+Z", fit: visible_parts}
  probes:
    - {type: minmax_label, show: max, expected_cax: 0.04717, at: "element 150220",
       label: "Panel 1500: 47.2 MPa", api: "xShowCAEFrameMinMaxLabels(model, True)"}
    - {type: element, id: 150493, part: "id = 1500", result: "Stress (Centroidal) (Top Section)",
       derived: "Von Mises Stress", expected_cax: 0.02759, label: "Panel 1501: 27.6 MPa"}
  secondary_viewpoints:
    - name: "08b_Fabric_vonMises_80ms"
      result: {name: "Stress (Centroidal) (Top Section)", instance: "L17M0", derived: "Von Mises Stress"}
      probes: [{type: element, id: 150230, part: "id = 1500", result: "Stress (Centroidal) (Top Section)",
                derived: "Von Mises Stress", expected_cax: 0.03447, label: "80 ms: 34.5 MPa"}]
  notes: []
  animation: none
```

---

## Slide 9 — Data Quality — "Equivalent Plastic Strain"
<!-- slide: 9 | id: data-quality | type: table+callout | role: validation -->

### Slide content
| Check | Observation | Physical expectation |
|---|---|---|
| Sign | min −0.351 (elem 150101, 75 ms) | Plastic strain is ≥ 0 |
| Time trend | max 0.111 (50 ms) → 0.099 (65 ms) → 0.109 (75 ms) | Accumulated plastic strain never decreases |
| Location | Non-zero only in fabric parts 1500 / 1501 | — |
| Top vs bottom | identical | Membrane elements |

**Callout (critical) — Do not use as plastic strain:** For fabric materials the d3plot "effective plastic strain" slot is often reused for another history variable. Identify the variable from the material card before using this result. No plasticity conclusions are drawn in this review.

### Viewpoint
```yaml
viewpoint:
  name: "09_DataQuality_EPS"
  purpose: "Show the negative values that make the result non-physical"
  result: {name: "Equivalent Plastic Strain (Top Section)", instance: "L16M0", derived: ""}
  deformation: {enabled: true, result: "Displacement", scale: 1.0, uniform: true}
  legend: {visible: true, mode: user, user_min: -0.36, user_max: 0.36, filter_out_of_range: false,
           title: "'Equivalent Plastic Strain' at 75 ms (symmetric scale)"}
  parts: {show_only: ["id = 1500", "id = 1501"]}
  camera: {std_view: Iso, view_dir: [-1, 1, -1], up_axis: "+Z", fit: visible_parts}
  probes:
    - {type: element, id: 150101, part: "id = 1500", result: "Equivalent Plastic Strain (Top Section)",
       derived: "", expected_cax: -0.3509, label: "−0.351: non-physical"}
    - {type: element, id: 150220, part: "id = 1500", result: "Equivalent Plastic Strain (Top Section)",
       derived: "", expected_cax: 0.1091, label: "+0.109"}
  notes: []
  animation: none
```

---

## Slide 10 — 7 · Engineering Validation — Hand Calculation
<!-- slide: 10 | id: hand-calcs | type: table | role: validation -->

### Slide content
**Subtitle:** Membrane check of the fabric: σ = p·R / (2·t) for a pressurised spherical bag, t = 0.3048 mm

| Quantity | Value | Basis |
|---|---|---|
| Peak fabric stress σ | 47.2 MPa | CAX, elem 150220, 40 ms |
| Implied pressure, R = 250 mm | 2 t σ / R = 0.115 MPa (115 kPa) | Hand calculation |
| Implied pressure, R = 350 mm | 0.082 MPa (82 kPa) | Hand calculation |
| Implied pressure, R = 500 mm | 0.058 MPa (58 kPa) | Hand calculation |
| Bag pressure from the run | Not in CAX | Needs the airbag history output |

- The peak stress corresponds to a uniform bag pressure of about 60–115 kPa, depending on the effective radius. This is the order of magnitude expected for a deployed airbag, so the stress level is **plausible**.
- The peak is local (one element). The panel average is lower, which is consistent with stress concentrating at seams or folds.
- Confirm with the bag pressure–time curve and the inflator tank-test data.

### Viewpoint
```yaml
viewpoint:
  name: "10_HandCalc_Fabric"
  purpose: "Fabric stress field compared with the membrane estimate"
  result: {name: "Stress (Centroidal) (Top Section)", instance: "L9M0", derived: "Von Mises Stress"}
  deformation: {enabled: true, result: "Displacement", scale: 1.0, uniform: true}
  legend: {visible: true, mode: user, user_min: 0.0, user_max: 0.05, title: "von Mises (GPa) at 40 ms"}
  parts: {show_only: ["id = 1500"]}
  camera: {std_view: side, view_dir: [0, 1, 0], up_axis: "+Z", fit: visible_parts}
  probes:
    - {type: minmax_label, show: max, expected_cax: 0.04717, at: "element 150220",
       label: "47.2 MPa ⇒ p ≈ 58–115 kPa", api: "xShowCAEFrameMinMaxLabels(model, True)"}
  notes: []
  animation: none
```

---

## Slide 11 — 8 · Risks and Limitations
<!-- slide: 11 | id: risks | type: risk-list | role: summary -->

### Slide content
| Level | Risk |
|---|---|
| HIGH | Energy balance (hourglass, contact, total-energy error) not available, so the solution quality is unverified |
| HIGH | "Equivalent plastic strain" is negative and non-monotonic; the result is misidentified or corrupted |
| HIGH | Whole model drifts (≥ 146 mm at 80 ms); restraint of the module or vehicle motion is unverified |
| MED | Fabric mesh is coarse (349 nodes per panel), so peak stress and fold behaviour depend on the mesh |
| MED | Run ends at 80 ms while the fabric is still moving; the bag never reaches a settled state |
| MED | No allowable, material card or pressure history, so no margin can be computed |
| LOW | CAX metadata references a Fluent file; final state `L18M0` is incomplete; fabric element→part association is inconsistent. Translation quality needs checking |
| LOW | 5 ms output interval and unfiltered accelerations distort peaks |

### Viewpoint
```yaml
viewpoint:
  name: "11_Risks_Drift"
  purpose: "Global drift: every part has moved by 80 ms"
  result: {name: "Displacement", instance: "L17M0", derived: "Resultant"}
  deformation: {enabled: true, result: "Displacement", scale: 1.0, uniform: true, show_undeformed: true,
                undeformed_style: "grey transparent outline"}
  legend: {visible: true, mode: user, user_min: 140.0, user_max: 750.0, filter_out_of_range: false,
           title: "Displacement (mm) at 80 ms — min 146.5 mm"}
  parts: {show: all}
  camera: {std_view: side, view_dir: [0, 1, 0], up_axis: "+Z", fit: visible_parts}
  probes:
    - {type: node, id: 158220, part: "id = 303", result: "Displacement", derived: "Resultant",
       expected_cax: 494.9, label: "Rigid group moved 495 mm"}
  notes: []
  animation: none
```

---

## Slide 12 — 9 · Recommendations
<!-- slide: 12 | id: recommendations | type: numbered-list | role: summary -->

### Slide content
1. **Provide energy output:** glstat / matsum (and abstat for the airbag). Check hourglass < 5 % and energy error < 10 %; check airbag pressure, volume and temperature against tank tests.
2. **Identify the "plastic strain" variable:** read the fabric material card. Re-translate with the correct history variable, or exclude it from reports.
3. **Clarify global motion:** confirm whether a vehicle / sled pulse is prescribed. Otherwise fix the module mounting and re-run.
4. **Refine the fabric mesh:** about 5–10 mm elements at seams, vents and folds. Repeat at two mesh levels to check the peak stress.
5. **Extend the run:** run past bag settling and occupant contact (typically 100–150 ms). Output states every 1 ms.
6. **Add allowables:** supply fabric strength and seam strength. Report margins with a fixed legend at the allowable.
7. **Filter accelerations:** apply SAE CFC filtering before evaluating any acceleration-based criteria.

### Viewpoint
```yaml
viewpoint:
  name: "12_Recommendations_Fabric_Mesh"
  purpose: "Fabric mesh to be refined, shown at peak stress time"
  result: {name: "Stress (Centroidal) (Top Section)", instance: "L9M0", derived: "Von Mises Stress"}
  deformation: {enabled: true, result: "Displacement", scale: 1.0, uniform: true}
  legend: {visible: true, mode: auto, title: "von Mises (GPa) at 40 ms"}
  parts: {show_only: ["id = 1500", "id = 1501"]}
  display: {mode: shaded_with_mesh}
  camera: {std_view: Iso, view_dir: [-1, 1, -1], up_axis: "+Z", fit: visible_parts}
  probes: []
  notes:
    - {part: "id = 1500", node: 150157, text: ["Rec 4: refine to 5–10 mm", "349 nodes per panel today"]}
  animation: none
```

---

## Slide 13 — 10 · Final Engineering Verdict
<!-- slide: 13 | id: verdict | type: verdict | role: summary -->

### Slide content
**Verdict banner (orange):** CONDITIONAL — plausible deployment, not yet sign-off quality
- **Strength:** the fabric peaks at 47.2 MPa (40 ms). The membrane hand calculation implies a plausible bag pressure of 60–115 kPa. No allowable is available, so no margin can be stated.
- **Model validity:** no energy balance, an invalid "plastic strain" result and a whole-model drift of ≥ 146 mm all need to be explained.
- **Method:** the run ends at 80 ms while the fabric is still moving, and the coarse fabric mesh limits the accuracy of the peaks.
- **Path forward:** close recommendations 1–3 to make the run reviewable, then 4–6 for sign-off, and re-review.

### Viewpoint
```yaml
viewpoint:
  name: "13_Verdict"
  purpose: "Closing image: deployed bag at peak fabric stress"
  result: {name: "Stress (Centroidal) (Top Section)", instance: "L9M0", derived: "Von Mises Stress"}
  deformation: {enabled: true, result: "Displacement", scale: 1.0, uniform: true}
  legend: {visible: true, mode: user, user_min: 0.0, user_max: 0.05, title: "von Mises (GPa) at 40 ms"}
  parts: {show: all}
  camera: {std_view: Iso, view_dir: [-1, 1, -1], up_axis: "+Z", fit: visible_parts}
  probes:
    - {type: minmax_label, show: max, expected_cax: 0.04717, at: "element 150220",
       label: "47.2 MPa — allowable needed", api: "xShowCAEFrameMinMaxLabels(model, True)"}
  notes: []
  animation: none
```
