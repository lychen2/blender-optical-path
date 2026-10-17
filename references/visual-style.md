# Visual style workflow

This file owns shared visual rules. [Shading presets](shading-presets.md) own individual looks and reusable prompts; [compact composition](compact-floating-prompt.md) owns floating-layout guidance. Optical decisions belong in the brief or optional physical-design analysis, not in a material preset.

## 1. Set a visual brief

Default to **floating optics** and **Journal Editorial** (`illustrated`) unless the user chooses otherwise. Hide mounts and supports in floating; use compact for mounts or full for mechanical assemblies. Record presentation mode, final figure size, composition/camera, component prominence, material roles, beam/channel encoding, lighting/background and separate 2D-label plan. Manufacturer dimensions remain intact in source assets and mechanical views. Floating display copies can use shorter gaps and enlarged optical symbols; do not present those changes as physical dimensions.

Extract the reference's visual hierarchy and spacing, not just its palette. Make small optics identifiable, keep sources subordinate and let the beam route connect the composition. Use the canvas efficiently while reserving room for nearby labels. Renderer names and journal names are not complete styles: specify actual materials, light and camera.

## 2. Assign material roles before shading

| Role | Preserve across styles | Common failure to reject |
| --- | --- | --- |
| Coated mount | Dark anodized finish; readable aperture | Unassigned white material, bright bare-metal shader |
| Exposed metal/barrel | Restrained satin depth and actual component shape | Uniform oily plastic, clipped reflections, broad black RMS barrel bands (thin Textbook outlines are intentional) |
| Optical surface | Clear glass with visible edges and aperture | Milky white faces, excessive tint, all-purpose black ink ramp |
| Beam | Clear topology and stable channel meaning | Unreadable or disconnected paths, black outlines, washed-out color |
| Background | Clear separation from optics and labels | Large floor shadows, decorative fog, dirty AO, gradient overwhelming the route |

Assign roles explicitly where possible. A blanket shader based on one material or a loose name match can tint the wrong objects. Inspect node inputs and rendered appearance; viewport color alone is insufficient. Copy materials locally rather than changing source CAD for one illustration.

Journal Editorial uses clear glass, restrained hardware face tones and fine neutral silhouettes on white. Use Standard color management and narrow unlit beams. Avoid bloom, particles, vignettes and decorative floor grids.

Use the inspected component pack's clear glass recipe. Preserve user-supplied glass shaders on local copies when requested. Adjust lighting and neutral edge contours when the glass disappears. Inspect refraction at beam junctions and keep the intended route legible. Material settings describe appearance; optical design requires separate inputs and checks.

## 3. Choose a distinct shading recipe

`library/style_presets.json` defines style IDs, aliases and the default.

- **Journal Editorial (`illustrated`, default):** clear glass, neutral hardware face tones, fine silhouettes and a white field.
- **Matte Technical (`matte`):** satin metal, continuous shading and pale-cyan optics.
- **Soft Lab (`soft-lab`):** dark field, directional highlights and bounded faint beam scattering where useful.
- **Textbook White (`textbook`):** white field, flat colors and thin black component edges.
- **Cel / Toon (`toon`):** hard face bands, pale beam cores and calligraphic component edges.

`journal-editorial`, `component-pack` and `pack` alias `illustrated`. `tools/styles.py` provides `apply_style`, `list_styles` and `setup_lighting`. `examples/shading.py` preserves the example entry point. See [style sources](style-sources.md) for figure references and material provenance.

For style comparisons, hold geometry, camera, framing, topology, labels and channel identities fixed. Confirm variants remain distinguishable at thumbnail size. For a new unrelated figure, vary key light, palette emphasis and view purposefully; preserve locked user/venue conditions. Do not add random optical tilt, decenter or uneven supports to change appearance. Physical symmetry may be required.

## 4. Preserve beam meaning

Conceptual-illustration beams are editable geometry with artist-authored shape and radii; physics is optional. `tools/geometry_nodes.py` provides `add_beam_nodes` for editable tube beams and an interactive `Radius Scale` multiplier. Use point radii to convey topology or emphasis, not as calculated values unless a physical model was requested and performed. Do not claim calculated envelopes, waist sizes, diffraction, scattering or propagation from their appearance.

Start with narrow, crisp beam envelopes. Leave lens edges and splitter junctions visible; increase width only when the figure needs emphasis. Template radii are generally 0.45–2.2 mm in authored display coordinates, with a separate GN multiplier. Beam shaders use unlit color without bloom.

Use consistent channel colors where the brief provides them. Visible hues are approximate display encodings; infrared colors require explicit false-color interpretation. A combined-channel color is not another wavelength. Do not add an unsupported spectrum.

## 5. Preview, correct and preserve the lesson

Inspect the whole composition at intended display width and crops of high-risk regions: small lenses, objective rings, splitter interfaces, beam junctions and crowded labels. Check silhouette and interface readability without overloading the drawing with internal CAD detail. Inspect substrate edges, objective end faces and visible barrel steps where needed. Preserve opaque occlusion and avoid noisy mesh triangulation.

Render optics, hardware and beams without text. Add names, plane markers, dimensions and leaders in a separate editable 2D overlay. Prefer short nearby labels, alternating above/below crowded branches. Dark backgrounds need light text. Avoid long crossing leaders, white text halos on light fields and crowded labels. Provenance belongs in metadata; physical assumptions belong in captions only when a physical model is in scope.

Acceptance: the route reads at final size; optics and important interfaces are visible; black mounts remain dark; each requested style is distinct; no excessive glass transparency or unintended contour appears; labels are legible and collision-free. Apply [release checks](release-checks.md) appropriate to the request. A reusable prompt does not guarantee a first-pass result; inspect previews before delivery.
