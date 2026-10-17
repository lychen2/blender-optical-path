# Visual style workflow

This file owns shared visual rules. [Shading presets](shading-presets.md) own individual looks and reusable prompts; [compact composition](compact-floating-prompt.md) owns floating-layout guidance. Optical decisions belong in the brief or optional physical-design analysis, not in a material preset.

## 1. Set a visual brief

Default to **floating optics** and **Component Pack Studio** (`component-pack`) unless the user chooses otherwise. Hide mounts and supports in floating; use compact for mounts or full for mechanical assemblies. Record presentation mode, final figure size, composition/camera, component prominence, material roles, beam/channel encoding, lighting/background and separate 2D-label plan. Manufacturer dimensions remain intact in source assets and mechanical views. Floating display copies can use shorter gaps and enlarged optical symbols; do not present those changes as physical dimensions.

Extract the reference's visual hierarchy and spacing, not just its palette. Make small optics identifiable, keep sources subordinate and let the beam route connect the composition. Use the canvas efficiently while reserving room for nearby labels. Renderer names and journal names are not complete styles: specify actual materials, light and camera.

## 2. Assign material roles before shading

| Role | Preserve across styles | Common failure to reject |
| --- | --- | --- |
| Coated mount | Dark anodized finish; readable aperture | Unassigned white material, bright bare-metal shader |
| Exposed metal/barrel | Restrained satin depth and actual component shape | Uniform oily plastic, clipped reflections, broad black RMS barrel bands (thin Textbook outlines are intentional) |
| Optical surface | Visible tint, edge and aperture | Nearly invisible glass, milky white face, all-purpose black ink ramp |
| Beam | Clear topology and stable channel meaning | Unreadable or disconnected paths, black outlines, washed-out color |
| Background | Clear separation from optics and labels | Large floor shadows, decorative fog, dirty AO, gradient overwhelming the route |

Assign roles explicitly where possible. A blanket shader based on one material or a loose name match can tint the wrong objects. Inspect node inputs and rendered appearance; viewport color alone is insufficient. Copy materials locally rather than changing source CAD for one illustration.

Give the two publication presets distinct material treatments. Studio uses lit glass, reflective metal and continuous shading on a light-grey field. Editorial uses three-tone flat fills and fine silhouette lines on true white. Both use Standard color management and narrow unlit beams. Avoid bloom, particles, vignettes and decorative floor grids.

Optical glass is a readable symbol in an apparatus overview. Lower transmission and moderate reflections when physical transparency erases its shape. Keep the face visible before adding a rim. For splitters, balance a clearly visible tinted shell against the need to see the internal film and beam junction. Use a nonrefractive transparent/surface mixture for an illustrative view. A glass IOR is material- and wavelength-dependent; illustrative opacity is not measured transmission or a splitting ratio.

## 3. Choose a distinct shading recipe

`library/style_presets.json` is authoritative for style IDs, aliases and default. Use these six recipes:

- **Component Pack Studio (`component-pack`, default):** lit pale-blue glass, reflective silver barrels, continuous soft shading and a light-grey field. The locally inspected component-pack lens material's color/finish informs the visual direction; the original biconvex source object has a null material, so do not claim that source glass material was assigned to it. The skill applies nonrefractive translucent illustrative glass for beam readability.
- **Matte Technical (`matte`):** satin/diffuse material separation, soft continuous shading, restrained optical transparency.
- **Soft Lab (`soft-lab`):** dark field, directional highlights and bounded faint beam scattering where useful.
- **Journal Editorial (`illustrated`, alias `journal-editorial`):** true white field, flat grey-teal three-tone fills and fine silhouette contours. Optical faces have no specular highlights. Beams and hidden CAD creases have no contour lines. It replaces the former warm-paper Illustrated recipe.
- **Textbook White (`textbook`):** true white field, flat colors, thin black component edges, no gloss or floor shadows.
- **Cel / Toon (`toon`):** hard shadow/base/lit bands, pale beam cores and calligraphic component edges.

`pack` aliases `component-pack`. `tools/styles.py` owns shared `apply_style`, `list_styles` and `setup_lighting`; `examples/shading.py` remains a compatibility entry point. See [style sources](style-sources.md) for research and local-pack provenance. Do not infer endorsement from visual references.

For style comparisons, hold geometry, camera, framing, topology, labels and channel identities fixed. Confirm variants remain distinguishable at thumbnail size. For a new unrelated figure, vary key light, palette emphasis and view purposefully; preserve locked user/venue conditions. Do not add random optical tilt, decenter or uneven supports to change appearance. Physical symmetry may be required.

## 4. Preserve beam meaning

Conceptual-illustration beams are editable geometry with artist-authored shape and radii; physics is optional. `tools/geometry_nodes.py` provides `add_beam_nodes` for editable tube beams and an interactive `Radius Scale` multiplier. Use point radii to convey topology or emphasis, not as calculated values unless a physical model was requested and performed. Do not claim calculated envelopes, waist sizes, diffraction, scattering or propagation from their appearance.

Start with narrow, crisp beam envelopes. Leave lens edges and splitter junctions visible; increase width only when the figure needs emphasis. Template radii are generally 0.45–2.2 mm in authored display coordinates, with a separate GN multiplier. Beam shaders use unlit color without bloom.

Use consistent channel colors where the brief provides them. Visible hues are approximate display encodings; infrared colors require explicit false-color interpretation. A combined-channel color is not another wavelength. Do not add an unsupported spectrum.

## 5. Preview, correct and preserve the lesson

Inspect the whole composition at intended display width and crops of high-risk regions: small lenses, objective rings, splitter interfaces, beam junctions and crowded labels. Check silhouette and interface readability without overloading the drawing with internal CAD detail. Inspect substrate edges, objective end faces and visible barrel steps where needed. Preserve opaque occlusion and avoid noisy mesh triangulation.

Render optics, hardware and beams without text. Add names, plane markers, dimensions and leaders in a separate editable 2D overlay. Prefer short nearby labels, alternating above/below crowded branches. Dark backgrounds need light text. Avoid long crossing leaders, white text halos on light fields and crowded labels. Provenance belongs in metadata; physical assumptions belong in captions only when a physical model is in scope.

Acceptance: the route reads at final size; optics and important interfaces are visible; black mounts remain dark; each requested style is distinct; no excessive glass transparency or unintended contour appears; labels are legible and collision-free. Apply [release checks](release-checks.md) appropriate to the request. A reusable prompt does not guarantee a first-pass result; inspect previews before delivery.
