---
name: blender-optical-path
description: Build editable Blender optical-path figures from optical topology, aligned components and a deliberate visual style. Use Python or Blender MCP, render hardware and beams without text, and add labels afterward in a separate 2D overlay.
---

# Blender optical path

Build a source-to-detector apparatus figure through **optical model → display geometry → shading → 2D annotation**. Use the bundled components and shared API; do not substitute a mechanism diagram for the requested apparatus. Resolve paths relative to this skill directory. Explicit user choices override style defaults.

## Defaults and invariants

- **Compact floating optics by default.** Enlarge optical symbols uniformly about their optical anchors and shorten schematic gaps for clarity; record display scale separately. Use full mechanical assemblies when requested, retaining native CAD dimensions and checking interfaces. Preserve source assets through scene-local copies.
- **Thick beam envelopes by default.** Thin paths need an explicit request. Derive focal structure from the agreed optical model; do not invent radii, conjugates or an extra focus at a detector. Default to coaxial operation unless the design says otherwise.
- **Reviewed manufacturer objectives, preferably RMS series.** Preserve object/image-side orientation; never reverse or hand-model an objective to fit a beam cartoon. Prefer compatible KM100 adjustable lens mounts and POLARIS-K1S5 mirror mounts in mechanical views; verify seating and fasteners.
- **No component names or other text in the 3D render.** Add labels in a separate editable 2D overlay. Preserve source provenance in metadata; do not show manufacturer branding/model inscriptions. Preserve functional graduations and original CAD.
- **Model validity, scene validity and visual quality are separate checks.** Do not claim one from another. Do not introduce random optical tilt/decenter to create an imperfect look. Keep actual optical data distinct from illustrative assumptions.

## Six-step workflow

### 1. Understand

Read [optical preflight](references/optical-preflight.md). Inspect the request, reference, existing scene and established choices. Identify topology, beam meaning, lens groups, conjugate planes, direction and physical versus display coordinates. Reason through plausible interpretations yourself before asking questions; source CAD describes shape, not automatically an optical prescription.

### 2. Clarify once

If material decisions remain unresolved, ask one prepared batch covering all currently identifiable optical and style blockers, with up to four grouped questions. Omit information already established. Offer coherent choices, not guesses the user must repair. Continue independent asset work while answers are pending. Record the agreed brief; ask again only for genuinely new contradictions.

### 3. Model the optics

Use the agreed prescription or explicitly accepted symbolic/illustrative model. Calculate conjugates and envelopes before drawing them. Trace actual surface/port geometry, including reflection/transmission, local frames and off-axis fields when required. Save inputs and numerical checkpoints. See preflight for 4f conventions, grating dispersion and model limits. Structural Blender validation does not establish optical validity.

### 4. Assemble

Choose bundled assets via `library/index.json` and place through `tools/optics.py`. Read [Python/MCP](references/python-mcp.md) for scripted work or [manual assembly](references/manual.md) for UI work. Use [official CAD workflow](references/thorlabs-workflow.md) only when an exact requested part is missing. Measure bare-CAD interfaces before alignment; preserve native geometry and source hierarchy. Apply the optical/assembly sections of [required checks](references/release-checks.md), especially coating normals, objective front direction and lens stop contact.

### 5. Style and preview

Read [visual style](references/visual-style.md), which owns the shared visual rules. Choose one [shading recipe and reusable prompt](references/shading-presets.md); use the [compact composition prompt](references/compact-floating-prompt.md) for floating layouts. Assign explicit material roles, not one shader to everything. Inspect a small preview and high-risk details before final rendering. Compare style variants with fixed geometry/camera/channel meaning. When feedback reveals a recurring problem, update the shared visual rule, affected prompt and implementation together; avoid accumulating contradictory patches.

### 6. Verify and deliver

Apply [required checks](references/release-checks.md). Check trace, geometry, materials and final-size labels independently; inspect every style variant. Save a new editable `.blend`, clean render, assembly script and trace inputs/checkpoints; include annotated artwork and editable overlay when requested. Keep limitations beside the claims they qualify. For package changes run `tools/check_package.py`, the affected example CLI and a fresh independent-copy check. Publish only curated documentation assets, useful scripts and provenance, not intermediate renders, reports, bytecode or original STEP files.

## Runtime and resources

- New workspaces use metric `scale_length=0.001`; API inputs are millimetres and convert to existing metric scenes. Never silently reset an existing scene's units.
- Most mounted assemblies have nominal optical anchor `(0,0,100)` and axis `+X`. Bare CAD has no calibrated anchor; other modules have their own ports. Inspect and measure before placement.
- `load_asset` returns `(collection, record)`. Use `place_asset`, `add_beam`, `add_annotation` and `inspect_scene` through the shared API. `add_annotation` stores metadata only; it does not composite labels.
- For MCP, discover an actually connected Blender tool and run `tools/blender_mcp_entry.py` using the documented request/result properties. Do not assume a tool prefix or infer live transport success from local Python execution.
- `library/Optical_Components.blend` contains individual assemblies, standard parts, functional modules and an empty workspace. The gallery is a resource, not a complete layout template. Its captions are browsing aids only.
- [Coverage](references/system-coverage.md) · [Examples and reproduction](examples/README.md) · [Third-party rights](THIRD_PARTY_NOTICES.md). Publish CAD derivatives only within applicable permission after branding review; authored-code licensing does not relicense manufacturer geometry.
