---
document: cae-review-viewpoints
schema_version: 1.0
title: "Thin-Wall Bracket — Torsion Load Case"
subtitle: "CAE Engineering Review of bracket.op2 (Nastran SOL 101, linear static)"
source_native: "bracket.op2"
source_cax: "bracket.cax"
cax_model_name: "Bracket"
solver: "MSC/NX Nastran SOL 101"
analysis: "Linear static"
units: {length: "in", force: "lbf", stress: "psi", time: "s"}
units_basis: "assumed; consistent with rho = 2.591e-4 lbf·s²/in⁴ and alpha = 12.55e-6 /°F"
verdict: "NO-GO"
viewpath: "CAE Review - bracket"
slide_count: 12
generated: "2026-11-11"
---

# Thin-Wall Bracket — CAE Review: slides and viewpoints

This file describes a 12-slide CAE review and, for each slide, the VCollab Pro viewpoint that
illustrates it. A VCollab Pro assistant can read it top to bottom and, for every `## Slide`,
set the model state in the `viewpoint` block and capture it with `xAddViewPoint`.

## Model data

### Source and translation
| Item | Value |
|---|---|
| Native file | bracket.op2 (75 KB), Nastran SOL 101, SUBCASE 1 |
| CAX file | bracket.cax (17 KB), VMoveCAE 2.1.217.309, CAX 1.2 |
| CAX model name | `Bracket` |
| Nodes / elements | 219 grids / 358 CTRIA3 |
| Envelope | X −1.04 → 0.96, Y 0.82 → 1.32, Z 0.20 → 7.00 in (2.0 in wide, ~6.8 in long) |
| Up axis for views | +Z (bracket length runs along Z; clamp at top, Z = 6.995) |

### Parts
| CAX part name | Nastran PID | Thickness (in) | Elements | Zone | Role |
|---|---|---|---|---|---|
| `PSHELL PID_1` | 1 | 0.50 | 102 | Upper flat, Y = 1.322, Z 4.0–7.0, circular cut-out | Clamp flange, low stress |
| `PSHELL PID_2` | 2 | 0.24 | 128 | Inclined web, Z 2.8–4.0 | Transition |
| `PSHELL PID_3` | 3 | 0.10 | 128 | Lower flat, Y = 0.822, Z 0.2–2.8 | **Critical part** |

### Material (MAT1 ID 1, from OP2 — not stored in CAX)
| E | G | ν | ρ | α | ST / SC / SS |
|---|---|---|---|---|---|
| 1.0e6 psi (**suspect, likely 1.0e7**) | 4.0226e6 psi | 0.33 | 2.591e-4 | 1.255e-5 | 42 / 40 / 38 ksi |

### Results available in the CAX
| CAX result name | Instance(s) | Type | Location in CAX | Derived types to use |
|---|---|---|---|---|
| `Displacement` | `L1M1` | 6-DOF | Nodal | Translational Magnitude, Y, Rotational Z |
| `Stress (Top Section)` | `L1M1` | Tensor | Nodal (averaged) | Von Mises Stress, Maximum/Minimum Principal Value, ZX (in-plane shear of PSHELL 3) |
| `Stress (Bottom Section)` | `L1M1` | Tensor | Nodal (averaged) | Von Mises, Max/Min Principal |
| `Reaction Force` | `L1M1` | 6-DOF | Nodal | Translational Magnitude, Y, Rotational Z |
| `External Applied Force` | `L1M1` | 6-DOF | Nodal | Translational Magnitude, Y |
| `Thickness` | (none) | Scalar | Element | Scalar |

Derived-type labels differ between VCollab versions: resolve the exact string with
`pxGetCAEResultDerivedTypes(model, result)` and pick the closest match to the name given here.

### Load case
| Native | CAX instance | Label |
|---|---|---|
| SUBCASE 1 | `L1M1` | "SUBCASE 1" / "UNTITLED.SC1" |

### Key locations (IDs are Nastran grid / element IDs; same IDs in the CAX)
| Tag | Type | ID(s) | Part | Coordinates (in) | Meaning |
|---|---|---|---|---|---|
| LOAD_A | node | 1 | PSHELL PID_3 | (−1.042, 0.822, 0.195) | 100 lbf in −Y |
| LOAD_B | node | 25 | PSHELL PID_3 | (0.958, 0.822, 0.195) | 100 lbf in +Y |
| SPC_EDGE | node | 171–179 | PSHELL PID_1 | Z = 6.995 | SPC1 123456 clamped edge |
| RF_PEAK | node | 171, 179 | PSHELL PID_1 | (−1.042 / 0.958, 1.322, 6.995) | Reaction ±74 lbf |
| HS_VM_ELEM | element | 127, 15 | PSHELL PID_3 | X +0.88 / −0.96, Z 2.58 | Peak von Mises 53.99 ksi (element) |
| HS_LOADEND | element | 99, 19, 83, 35 | PSHELL PID_3 | Z ≈ 0.63 | ≈ 52.5 ksi near load points |
| HS_SHEAR | element | 99 | PSHELL PID_3 | Z ≈ 0.63 | Peak \|τxy\| 30.30 ksi |
| HS_VM_NODE | node | 68, 40 | PSHELL PID_3 | (0.458 / −0.542, 0.822, 0.52) | Peak nodal-averaged von Mises in CAX, 51,986 psi |
| HS_P1_NODE | node | 8 | PSHELL PID_3 | (−1.042, 0.822, 2.47) | Peak nodal max principal in CAX, 44,734 psi |
| NOTE_MID | node | 54, 62 | PSHELL PID_3 | (−0.042, 0.822, 0.52) / (0.208, 0.822, 0.845) | Far-field anchors for notes/probes |
| STEP_EDGE | node | 8, 106 | PSHELL PID_3 | (−1.042, 0.822, 2.47) / (0.958, 0.822, 2.795) | Free-edge nodes at the 0.10 → 0.24 step |
| CLAMP_MID | node | 175 | PSHELL PID_1 | (−0.042, 1.322, 6.995) | Mid clamp edge, note anchor |
| DISP_MAX | node | 1 | PSHELL PID_3 | (−1.042, 0.822, 0.195) | Max displacement 1.867 in |

### Key values
| Quantity | Native OP2 (element) | CAX (nodal-averaged) | Limit |
|---|---|---|---|
| Max von Mises | 53.99 ksi (elem 127/15) | 51,986 psi (node 68) | ST 42 ksi |
| Max principal | 56.95 ksi | 44,734 psi (node 8) | ST 42 ksi |
| Min principal | −56.95 ksi | — | SC 40 ksi |
| Max \|τxy\| | 30.30 ksi (elem 99) | — | SS 38 ksi |
| Max displacement | 1.867 in (grid 1) | 1.867 (node 1) | — |
| Peak twist R3 | 1.87 rad | — | small-rotation limit ≈ 0.1 rad |
| Max reaction | ±74 lbf (grids 171/179) | 73.97 (node 171) | — |
| Elements > 42 ksi vM | 100 / 128 in PSHELL 3 | — | — |

> **CAX caveat:** VMoveCAE stored the stresses as nodal-averaged values, so probe values in
> VCollab Pro are 4–21 % below the element values quoted on the slides. Probe labels below
> quote both values where it matters.

## Viewpoint build instructions
1. Open `bracket.cax`. Model name: `Bracket` (`xGetCurCAEModelName()`).
2. Create viewpath `CAE Review - bracket` (`xAddViewPath`).
3. For each slide, in order: reset the previous state (show all parts, clear labels and notes,
   deformation off, legend auto), apply the `viewpoint` block, then capture with
   `xAddViewPoint(name, "CAE Review - bracket", -1)`.
4. Legend values are in **psi** (model units). `user_max: 42000` = ST limit.
5. `probes` use `xCAEProbeID(model, part, id, result, instance, derived)` for result values.
   `notes` use `xAdd3DNotesByID(model, part, node_id, [lines])` for free text.
6. Camera `std_view` names follow VCollab standard views (Iso, Front, Back, Top, Bottom,
   Left, Right). Then fit to visible parts.

---

## Slide 1 — Title
<!-- slide: 1 | id: title | type: title | role: context -->

### Slide content
- **Title:** Thin-Wall Bracket — Torsion Load Case
- **Subtitle:** CAE Engineering Review of bracket.op2 (Nastran SOL 101, linear static)
- **Source data:** OP2 geometry, property, material, displacement, SPC force, load and CTRIA3 stress tables
- **Units:** inch · lbf · psi · November 2026
- **Badge:** VERDICT: NO-GO (red)

### Viewpoint
```yaml
viewpoint:
  name: "01_Title"
  purpose: "Model overview: three thickness zones of the bracket"
  result: {name: "Thickness", instance: "", derived: "Scalar"}
  deformation: {enabled: false}
  legend: {visible: true, mode: auto, levels: 3, title: "Shell thickness (in)"}
  parts: {show: all}
  display: {mode: shaded_with_mesh}
  camera: {std_view: Iso, up_axis: "+Z", fit: visible_parts}
  probes: []
  notes:
    - {part: "PSHELL PID_1", node: 175, text: ["t = 0.50 in (PID 1)"]}
    - {part: "PSHELL PID_3", node: 8, text: ["t = 0.10 in (PID 3) — critical"]}
  animation: none
```

---

## Slide 2 — Executive Summary
<!-- slide: 2 | id: executive-summary | type: kpi+bullets | role: key-result -->

### Slide content
**Headline:** The thin plate is overstressed everywhere, the material card is invalid, and a linear solution does not apply.

| KPI | Value | Detail |
|---|---|---|
| Peak von Mises | 53.99 ksi | Elem 127 / 15 · limit 42 ksi |
| Peak max principal | 56.95 ksi | Strip corner, Z = 2.58 in |
| Peak twist (R3) | 1.87 rad | ≈ 107°, far beyond small rotation |
| Elements > 42 ksi | 100 / 128 | in PSHELL 3 (t = 0.10 in) |

- **Overstress:** the 0.10 in plate sits at 50–54 ksi von Mises over its whole length. Hand calculation (τ = 30.0 ksi) matches the FE (30.3 ksi).
- **Material card error:** E = 1.0e6 psi with G = 4.02e6 psi; G > E is physically impossible. E is likely 1.0e7 (aluminium), so displacements are ~10× too large.
- **Wrong analysis type:** twist 1.87 rad (≈ 0.2 rad once E is corrected). Either way a linear static solution is not valid.
- **Sound foundations:** equilibrium exact, element shapes good, flange around the cut-out lightly loaded (4.7 ksi).

### Viewpoint
```yaml
viewpoint:
  name: "02_Executive_Summary"
  purpose: "Show at a glance that the whole 0.10 in plate exceeds the 42 ksi limit"
  result: {name: "Stress (Top Section)", instance: "L1M1", derived: "Von Mises"}
  deformation: {enabled: false}
  legend: {visible: true, mode: user, user_min: 0, user_max: 42000, filter_out_of_range: false,
           note: "values above 42 ksi saturate in the top colour", title: "von Mises (psi), capped at ST = 42 ksi"}
  parts: {show: all}
  camera: {std_view: Iso, up_axis: "+Z", fit: visible_parts}
  probes:
    - {type: node, id: 68, part: "PSHELL PID_3", result: "Stress (Top Section)", derived: "Von Mises",
       expected_cax: 51986, label: "Peak vM (nodal) 52.0 ksi · element peak 53.99 ksi"}
  notes: []
  animation: none
```

---

## Slide 3 — 1 · Problem Understanding
<!-- slide: 3 | id: problem-understanding | type: bullets+3d | role: setup -->

### Slide content
- **Geometry:** Z-shaped bracket, 2.0 in wide and about 6.8 in long, made of three shell zones.
- **Restraint:** top edge (grids 171–179) fully clamped with SPC1 123456.
- **Loading:** 100 lbf in −Y at grid 1 and 100 lbf in +Y at grid 25, 2.0 in apart.
- **Net effect:** pure torque T = 200 in·lbf about Z, zero net force.
- **Physics:** torsion of thin open strips, dominated by twisting. Peak bending component 52.7 ksi against 1.8 ksi membrane.
- **Figure:** von Mises (top fibre), red = 100 lbf loads, green = SPC 123456.

### Viewpoint
```yaml
viewpoint:
  name: "03_Problem_Understanding"
  purpose: "Loads, restraint and the torsion load path"
  result: {name: "External Applied Force", instance: "L1M1", derived: "Y"}
  deformation: {enabled: false}
  legend: {visible: true, mode: auto, title: "Applied force Fy (lbf)"}
  parts: {show: all}
  display: {mode: shaded_with_mesh}
  camera: {std_view: Iso, up_axis: "+Z", fit: visible_parts}
  probes:
    - {type: node, id: 1, part: "PSHELL PID_3", result: "External Applied Force", derived: "Y",
       expected_cax: -100, label: "Grid 1: Fy = −100 lbf"}
    - {type: node, id: 25, part: "PSHELL PID_3", result: "External Applied Force", derived: "Y",
       expected_cax: 100, label: "Grid 25: Fy = +100 lbf"}
  notes:
    - {part: "PSHELL PID_1", node: 175, text: ["SPC1 123456", "grids 171–179 clamped"]}
    - {part: "PSHELL PID_3", node: 54, text: ["T = 100 × 2.0 = 200 in·lbf about Z"]}
  animation: none
```

---

## Slide 4 — 2 · Model Setup Review
<!-- slide: 4 | id: model-setup | type: table+callout | role: setup -->

### Slide content
| Item | Value from OP2 | Assessment |
|---|---|---|
| Solution | SUBCASE 1, linear static, DISP / SPCF / STRESS = ALL | Inadequate for the computed rotations |
| PSHELL 1 | t = 0.50 in · upper flat with cut-out · 102 elements | OK |
| PSHELL 2 | t = 0.24 in · inclined web · 128 elements | OK |
| PSHELL 3 | t = 0.10 in · lower flat · 128 elements | Critical part |
| Shell options | MID1=MID2=MID3=1, 12I/t³ = 1.0, Ts/t = 0.833, no offsets | Standard; no offsets at thickness steps |
| MAT1 | E = 1.0e6, G = 4.02e6, ν = 0.33, ρ = 2.59e-4, α = 1.255e-5 | Inconsistent: G > E |
| Stress limits | ST / SC / SS = 42 / 40 / 38 ksi | Yield or ultimate not stated |

**Callout (critical) — Material card error:** For an isotropic material G = E / 2(1+ν) = 0.376e6 psi, but the card gives 4.02e6 (implied ν = −0.88). Nastran accepts all three values and uses them independently, so no error is raised. Density, thermal expansion and limits indicate aluminium, so E = 1.0e7 is the likely intent. Confirm with the model owner.

### Viewpoint
```yaml
viewpoint:
  name: "04_Model_Setup"
  purpose: "Property zones and thickness steps (no offsets at the steps)"
  result: {name: "Thickness", instance: "", derived: "Scalar"}
  deformation: {enabled: false}
  legend: {visible: true, mode: auto, levels: 3, title: "PSHELL thickness (in)"}
  parts: {show: all}
  display: {mode: shaded_with_mesh}
  camera: {std_view: Right, up_axis: "+Z", fit: visible_parts,
           note: "side view along X shows the Z-shape and the two thickness steps"}
  probes: []
  notes:
    - {part: "PSHELL PID_3", node: 106, text: ["Step 0.24 → 0.10 in at Z = 2.8", "no mid-surface offset"]}
  animation: none
```

---

## Slide 5 — 3–4 · Mesh Evaluation and Boundary Conditions
<!-- slide: 5 | id: mesh-bc | type: table+bullets | role: setup -->

### Slide content
**Mesh quality**

| Metric | Result | Status |
|---|---|---|
| Element type | CTRIA3 only (358 el, 219 grids) | Acceptable |
| Aspect ratio | median 1.64, max 1.83 | Good |
| Interior angles | 33.0° min / 107.8° max | Good |
| Edge length | ≈ 0.24–0.33 in (~6 across width) | Coarse |
| Convergence study | None | Missing |

**Boundary conditions and loads**
- **Equilibrium:** reaction moment −199.999 in·lbf balances the applied +200 in·lbf. Passes.
- **Reactions:** end grids 171 and 179 carry ±74 lbf, an expected edge peak. Clamp-zone stress is low (4.7 ksi).
- **Point loads:** local effect small (52.5 ksi vs 52 ksi far field), but distribute with an RBE3.
- **Coverage:** one load case only; no bending, combined, fatigue or buckling case.

### Viewpoint
```yaml
viewpoint:
  name: "05_Mesh_and_BC"
  purpose: "Mesh density on the critical plate and the reaction distribution at the clamp"
  result: {name: "Reaction Force", instance: "L1M1", derived: "Translational Magnitude"}
  deformation: {enabled: false}
  legend: {visible: true, mode: auto, title: "Reaction force (lbf)"}
  parts: {show: all}
  display: {mode: mesh, note: "shaded + mesh lines so the ~6 elements across the width are visible"}
  camera: {std_view: Front, up_axis: "+Z", fit: visible_parts}
  probes:
    - {type: node, id: 171, part: "PSHELL PID_1", result: "Reaction Force", derived: "Translational Magnitude",
       expected_cax: 73.97, label: "Grid 171: 74 lbf"}
    - {type: node, id: 179, part: "PSHELL PID_1", result: "Reaction Force", derived: "Translational Magnitude",
       expected_cax: 71.57, label: "Grid 179: 72 lbf"}
  notes:
    - {part: "PSHELL PID_1", node: 175, text: ["ΣMz reaction = −199.999 in·lbf", "applied = +200.0 → equilibrium OK"]}
  animation: none
```

---

## Slide 6 — 5 · Solver Assessment
<!-- slide: 6 | id: solver | type: bullets+3d | role: key-result -->

### Slide content
**Headline:** A completed run does not make the result valid.
- **Conditioning:** run completed with exact equilibrium; no mechanism or rigid-body mode.
- **Kinematics violated:** SOL 101 assumes small rotations, but the computed twist is 1.87 rad.
- **Visible symptom:** at true scale the strip appears to stretch and fan outward; linear kinematics turn a large rotation into artificial extension.
- **Not reviewed:** no .f06 available, so epsilon, maximum-ratio and warning messages were not checked.
- **Figure:** deformed shape at TRUE scale (1:1) vs undeformed (grey).

### Viewpoint
```yaml
viewpoint:
  name: "06_Solver_Deformed_1to1"
  purpose: "True-scale deformation exposes the large-rotation problem"
  result: {name: "Displacement", instance: "L1M1", derived: "Translational Magnitude"}
  deformation: {enabled: true, result: "Displacement", scale: 1.0, uniform: true,
                show_undeformed: true, undeformed_style: "grey transparent outline"}
  legend: {visible: true, mode: auto, title: "Displacement (in), scale 1:1"}
  parts: {show: all}
  camera: {std_view: Iso, up_axis: "+Z", fit: visible_parts}
  probes:
    - {type: node, id: 1, part: "PSHELL PID_3", result: "Displacement", derived: "Translational Magnitude",
       expected_cax: 1.867, label: "Max 1.867 in on a 2.0 in wide plate"}
  notes:
    - {part: "PSHELL PID_3", node: 25, text: ["Twist R3 ≈ 1.87 rad (107°)", "linear analysis invalid"]}
  animation: {type: deformation, frames: 10, note: "optional linear animation 0 → 1"}
```

---

## Slide 7 — 6 · Results Interpretation
<!-- slide: 7 | id: results | type: table+bullets+chart | role: key-result -->

### Slide content
| Region | Max vM | Max σ₁ | Min σ₃ |
|---|---|---|---|
| PSHELL 1 (t 0.50) | 4.66 ksi | 3.80 ksi | −3.81 ksi |
| PSHELL 2 (t 0.24) | 17.04 ksi | 14.84 ksi | −14.84 ksi |
| PSHELL 3 (t 0.10) | 53.99 ksi | 56.95 ksi | −56.95 ksi |

- **Hot spots:** elements 127 and 15 at the free-edge corners just below the 0.10 → 0.24 in step (Z = 2.58), then 99/19 and 83/35 near the load end.
- **Symmetry:** values antisymmetric in ±X, consistent with a pure torque.
- **Field condition:** most PSHELL 3 elements sit at 50–54 ksi; not an isolated peak.
- **Chart (2D, not a viewpoint):** element von Mises histogram by property; dashed line ST = 42 ksi.

### Viewpoint
```yaml
viewpoint:
  name: "07_Results_vonMises_Hotspots"
  purpose: "von Mises field with the corner hotspots at the thickness step"
  result: {name: "Stress (Top Section)", instance: "L1M1", derived: "Von Mises"}
  deformation: {enabled: false}
  legend: {visible: true, mode: auto, levels: 12, title: "von Mises, top fibre (psi)"}
  parts: {show: all}
  camera: {std_view: Front, up_axis: "+Z", fit: visible_parts}
  probes:
    - {type: node, id: 68, part: "PSHELL PID_3", result: "Stress (Top Section)", derived: "Von Mises",
       expected_cax: 51986, label: "Max vM (nodal) 52.0 ksi"}
    - {type: node, id: 40, part: "PSHELL PID_3", result: "Stress (Top Section)", derived: "Von Mises",
       expected_cax: 51986, label: "Antisymmetric twin 52.0 ksi"}
  notes:
    - {part: "PSHELL PID_3", node: 8, text: ["Elem 15 corner: 53.99 ksi (element)", "below 0.10 → 0.24 step, Z = 2.58"]}
    - {part: "PSHELL PID_3", node: 106, text: ["Elem 127 corner: 53.99 ksi (element)"]}
    - {part: "PSHELL PID_1", node: 175, text: ["PSHELL 1 max 4.66 ksi"]}
  secondary_viewpoints:
    - name: "07b_Max_Principal"
      result: {name: "Stress (Top Section)", instance: "L1M1", derived: "Max Principal"}
      probes: [{type: node, id: 8, part: "PSHELL PID_3", expected_cax: 44734,
                label: "Max σ1 nodal 44.7 ksi · element 56.95 ksi"}]
    - name: "07c_PSHELL3_only"
      parts: {show_only: ["PSHELL PID_3"]}
      result: {name: "Stress (Top Section)", instance: "L1M1", derived: "Von Mises"}
  animation: none
```

---

## Slide 8 — 7 · Engineering Validation — Hand Calculations
<!-- slide: 8 | id: hand-calcs | type: table+chart | role: validation -->

### Slide content
**Subtitle:** St-Venant torsion of the PSHELL 3 strip: b = 2.0 in, t = 0.10 in, L = 2.6 in

| Quantity | Hand calc | FE | Δ |
|---|---|---|---|
| J = b·t³/3 | 6.67e-4 in⁴ | — | — |
| τ max = T·t / J | 30.0 ksi | 30.30 ksi | 1.0 % |
| σ vM = √3·τ | 52.0 ksi | 50.8–52.5 ksi | ≤ 2 % |
| θ with E = 1.0e6 | 2.07 rad | 1.76 rad | 15 %* |
| θ with E = 1.0e7 | ≈ 0.21 rad | — | — |

- \* The FE is stiffer because the thickness step at Z = 2.8 restrains warping.
- The hand calculation reproduces the FE stress within 1%, so the model behaves as built. The excess flexibility comes from the material card, not the mesh or BCs.
- **Chart (2D, not a viewpoint):** twist R3 along Z; dotted line = corrected modulus estimate.

### Viewpoint
```yaml
viewpoint:
  name: "08_HandCalc_Shear_PSHELL3"
  purpose: "In-plane shear field of the 0.10 in strip to compare with τ = T·t/J = 30 ksi"
  result: {name: "Stress (Top Section)", instance: "L1M1", derived: "ZX"}
  deformation: {enabled: false}
  legend: {visible: true, mode: user, user_min: -31000, user_max: 31000, title: "τzx top fibre (psi), in-plane shear of the X-Z plate"}
  parts: {show_only: ["PSHELL PID_3"]}
  camera: {std_view: Front, up_axis: "+Z", fit: visible_parts}
  probes:
    - {type: node, id: 62, part: "PSHELL PID_3", result: "Stress (Top Section)", derived: "ZX",
       expected_cax: 30003, label: "Far-field in-plane shear ≈ 30 ksi (hand calc 30.0)"}
  notes:
    - {part: "PSHELL PID_3", node: 1, text: ["J = 6.67e-4 in⁴", "τ = 200 × 0.1 / J = 30.0 ksi"]}
  animation: none
  caveat: "PSHELL 3 lies in the global X-Z plane (Y = 0.822), so the in-plane shear is the ZX component in global axes (XY in the native element frame). Global XY is ~0 there."
```

---

## Slide 9 — Margins of Safety
<!-- slide: 9 | id: margins | type: table+callout | role: key-result -->

### Slide content
**Subtitle:** Against the material card stress limits, no factor of safety applied

| Check | Applied | Limit | MS = Limit / Applied − 1 |
|---|---|---|---|
| Max principal (tension), corner | 56.95 ksi | ST 42 ksi | −0.26 |
| Min principal (compression), corner | −56.95 ksi | SC 40 ksi | −0.30 |
| von Mises vs ST, peak | 53.99 ksi | 42 ksi | −0.22 |
| von Mises vs ST, far field | ≈ 52 ksi | 42 ksi | ≈ −0.19 |
| Max in-plane shear | 30.30 ksi | SS 38 ksi | +0.25 |

**Callout (warning) — Assumption:** The OP2 does not say whether ST/SC/SS are yield or ultimate values. The shear check passes only against SS. If these are ultimate values for a 6061-T6-class alloy (yield ≈ 35 ksi tension, ≈ 20 ksi shear), the strip has already yielded and an elastic-plastic solution is needed.

### Viewpoint
```yaml
viewpoint:
  name: "09_Margins_Exceedance"
  purpose: "Only regions above the 42 ksi limit are coloured"
  result: {name: "Stress (Top Section)", instance: "L1M1", derived: "Von Mises"}
  deformation: {enabled: false}
  legend: {visible: true, mode: user, user_min: 42000, user_max: 54000, filter_out_of_range: true,
           title: "von Mises above ST = 42 ksi (psi)", note: "below-range regions shown in no-result colour"}
  parts: {show: all}
  camera: {std_view: Iso, up_axis: "+Z", fit: visible_parts}
  probes:
    - {type: node, id: 68, part: "PSHELL PID_3", result: "Stress (Top Section)", derived: "Von Mises",
       expected_cax: 51986, label: "MS = 42/52.0 − 1 = −0.19"}
  notes: []
  animation: none
```

---

## Slide 10 — 8 · Risks and Limitations
<!-- slide: 10 | id: risks | type: risk-list | role: summary -->

### Slide content
| Level | Risk |
|---|---|
| HIGH | Material card error (E = 1e6, G > E): displacements and stiffness off by about 10× |
| HIGH | Linear solution at a large twist (1.87 rad, or ≈ 0.2 rad corrected): geometric nonlinearity ignored |
| HIGH | Stresses exceed the limits, so linear elastic material is invalid beyond yield |
| MED | Corner peaks at the thickness step depend on the mesh: coarse linear triangles, no convergence study |
| MED | No mid-surface offsets at thickness steps, so joint eccentricity is not modelled |
| MED | Single static load case: no fatigue, modal or buckling check of the 0.10 in plate |
| LOW | Point-load application: small local effect, but the load should still be distributed |

### Viewpoint
```yaml
viewpoint:
  name: "10_Risks_Step_Corner"
  purpose: "Zoom on the mesh-dependent corner peak at the 0.10 → 0.24 in step"
  result: {name: "Stress (Top Section)", instance: "L1M1", derived: "Von Mises"}
  deformation: {enabled: false}
  legend: {visible: true, mode: auto, title: "von Mises (psi)"}
  parts: {show: ["PSHELL PID_2", "PSHELL PID_3"], hide: ["PSHELL PID_1"]}
  display: {mode: shaded_with_mesh}
  camera: {std_view: Front, up_axis: "+Z", fit: window,
           zoom_target: {node: 8, part: "PSHELL PID_3"}, note: "zoom so ~4 elements around node 8 fill the view"}
  probes:
    - {type: node, id: 8, part: "PSHELL PID_3", result: "Stress (Top Section)", derived: "Von Mises",
       label: "Step corner: 1 coarse CTRIA3 across the peak"}
  notes: []
  animation: none
```

---

## Slide 11 — 9 · Recommendations
<!-- slide: 11 | id: recommendations | type: numbered-list | role: summary -->

### Slide content
1. **Fix MAT1:** set E = 1.0e7 psi and leave G blank so Nastran derives it from E and ν. Re-run and re-baseline the displacements.
2. **Thicken the 0.10 in plate:** torsional shear scales with 1/t². At t ≈ 0.125 in, vM ≈ 33 ksi; target ≈ 0.15 in for a 1.5 factor of safety. A closed section or return flange also works.
3. **Fillet and refine:** blend the step corners; use ≥ 10 elements across the width with CQUAD4 or quadratic elements.
4. **Mesh convergence study:** at least 3 mesh levels; report the corner peak against element size.
5. **Nonlinear solution:** SOL 400 (or SOL 106 with LGDISP) if the twist stays above ~0.1 rad; add MATS1 plasticity if yield is still exceeded.
6. **Load introduction and cases:** RBE3 or contact at the real fixture; add bending, combined and fatigue load cases.
7. **Reporting:** fix the legend at the allowable so auto-scaling cannot hide an exceedance.

### Viewpoint
```yaml
viewpoint:
  name: "11_Recommendations_PSHELL3"
  purpose: "Isolate the part to be redesigned (thicken, fillet, refine)"
  result: {name: "Stress (Top Section)", instance: "L1M1", derived: "Von Mises"}
  deformation: {enabled: false}
  legend: {visible: true, mode: user, user_min: 0, user_max: 42000, filter_out_of_range: false,
           title: "von Mises (psi), fixed at ST = 42 ksi (rec. 7)"}
  parts: {show: all, transparent: [{part: "PSHELL PID_1", level: 0.7}, {part: "PSHELL PID_2", level: 0.5}]}
  camera: {std_view: Iso, up_axis: "+Z", fit: visible_parts}
  probes: []
  notes:
    - {part: "PSHELL PID_3", node: 54, text: ["Rec 2: t 0.10 → 0.15 in", "vM ∝ 1/t² → ≈ 23 ksi"]}
    - {part: "PSHELL PID_3", node: 8, text: ["Rec 3: fillet + ≥ 10 elements across"]}
  animation: none
```

---

## Slide 12 — 10 · Final Engineering Verdict
<!-- slide: 12 | id: verdict | type: verdict | role: summary -->

### Slide content
**Verdict banner (red):** NO-GO — not acceptable for design sign-off
- **Strength:** the 0.10 in plate exceeds the tension and compression limits by 24–42% over its whole length. Hand calculation confirms this; it does not depend on the mesh.
- **Model validity:** the material card is physically invalid, corrupting displacements and stiffness.
- **Method:** a linear static solution is invalid at the computed rotations.
- **Path forward:** equilibrium, mesh quality and BCs are sound. Fix the material card, thicken the plate and move to a nonlinear solution (recommendations 1, 2 and 5), then re-review.

### Viewpoint
```yaml
viewpoint:
  name: "12_Verdict"
  purpose: "Closing image: critical plate above the limit, true-scale deformation"
  result: {name: "Stress (Top Section)", instance: "L1M1", derived: "Von Mises"}
  deformation: {enabled: true, result: "Displacement", scale: 1.0, uniform: true}
  legend: {visible: true, mode: user, user_min: 0, user_max: 42000, filter_out_of_range: false,
           title: "von Mises (psi), capped at ST = 42 ksi"}
  parts: {show: all}
  camera: {std_view: Iso, up_axis: "+Z", fit: visible_parts}
  probes:
    - {type: node, id: 68, part: "PSHELL PID_3", result: "Stress (Top Section)", derived: "Von Mises",
       expected_cax: 51986, label: "52 ksi > 42 ksi → NO-GO"}
  notes: []
  animation: none
```
