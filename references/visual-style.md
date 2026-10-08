# Visual style workflow

This file owns the shared visual rules. [Shading recipes](shading-presets.md) own individual looks and reusable prompts; [compact composition](compact-floating-prompt.md) owns floating-layout guidance. Optical decisions belong in [preflight](optical-preflight.md), not in a material preset.

## 1. Set a visual brief

Start from the agreed optical model and answered preferences. Default to compact floating optics and Matte Technical styling when no reference overrides them. Ask about unresolved optical and visual choices together, not one question after each render.

Record presentation mode, final figure size, composition/camera, component prominence, material roles, beam/channel encoding, lighting/background and 2D-label plan beside the script. Manufacturer dimensions remain intact in source assets and mechanical views. Floating display copies can use shorter gaps and enlarged optical symbols; recheck their optical anchors after scaling.

Extract the reference's visual hierarchy and spacing, not just its palette. Make small optics identifiable, keep sources subordinate and let the beam route connect the composition. Use the canvas efficiently while reserving room for nearby labels. Renderer names and journal names are not complete styles: specify actual materials, light and camera.

## 2. Assign material roles before shading

| Role | Preserve across styles | Common failure to reject |
| --- | --- | --- |
| Coated mount | Dark anodized finish; readable aperture | Unassigned white material, bright bare-metal shader |
| Exposed metal/barrel | Restrained satin depth and actual component shape | Uniform oily plastic, clipped reflections, broad black RMS barrel bands (thin Textbook outlines are intentional) |
| Optical surface | Visible tint, edge and aperture; actual film plane | Nearly invisible glass, milky white face, all-purpose black ink ramp |
| Beam | Calculated envelope, thick body, stable channel meaning | Unchanged tube through focusing optics, black outlines, washed-out color |
| Background | Clear separation from optics and labels | Large floor shadows, decorative fog, dirty AO, gradient overwhelming the route |

Assign roles explicitly where possible. A blanket shader based on one material or a loose name match can tint the wrong objects. Inspect node inputs and rendered appearance; viewport color alone is insufficient. Copy materials locally rather than changing source CAD for one illustration.

Optical glass is a readable symbol in an apparatus overview. Lower transmission and moderate reflections when physical transparency erases its shape. Keep the face visible before adding a rim. For splitters, balance a clearly visible tinted shell against the need to see the internal film and beam junction; edge strokes alone do not rescue an almost invisible cube. Use a nonrefractive transparent/surface mixture for this illustrative view. A glass IOR is material- and wavelength-dependent; illustrative opacity is not measured transmission or a splitting ratio.

## 3. Choose a distinct shading recipe

Use [five shading recipes](shading-presets.md). Their differences must come from more than a changed background:

- **Matte Technical:** satin/diffuse material separation, soft continuous shading, restrained optical transparency.
- **Soft Lab:** dark field, directional highlights and bounded faint beam scattering where useful.
- **Illustrated Geometry:** warm paper field, muted continuous volume shading, selective hardware contours; no black glass, beam or objective-barrel outline. PBS shells may use a slightly stronger cyan edge cue so the split/merge junction remains visible.
- **Textbook White:** true white field, flat lighting-independent or near-flat colors, thin black component edges, no gloss, no floor shadows. Exclude beams from the contour pass.
- **Cel / Toon:** hard shadow/base/lit bands from one fixed key, pale beam cores, fixed glints and calligraphic ink (deep cyan on optics, dark navy on hardware) on a flat butter-yellow field; no beam outline or facing-ratio rim.

For a style comparison, hold geometry, camera, framing, optical topology, labels and channel identities fixed. Confirm the variants remain distinguishable at thumbnail size. For a new unrelated figure, vary key light, palette emphasis and view purposefully; preserve any locked user/venue conditions. Do not add random optical tilt, decenter or uneven supports to remove a synthetic appearance. Physical symmetry may be required.

## 4. Preserve beam meaning

Default to thick beam envelopes. Thin single-line paths require an explicit request. Use the preflight model for expansion, convergence, shared foci, recollimation and dispersion. The on-axis chief ray can remain straight while envelope boundaries focus. A finite drawn waist can be a documented display floor; it is not automatically a calculated diffraction waist.

`add_beam` draws a curve with constant radius or per-vertex `radii_mm`; it does not derive optical behavior. Ribbons, outlined bundles and bounded scattering volumes require additional authored geometry/materials. A scattered halo does not establish diffraction or measured air scattering.

Use consistent channel colors. Visible hues are approximate display encodings, and infrared wavelengths require explicit false colors. A combined-channel color is not another wavelength. Do not add a spectrum without spectral input and a dispersive element.

## 5. Preview, correct and preserve the lesson

Before final resolution, inspect the entire composition at its intended display width and crops of high-risk regions: small lenses, objective rings, splitter interfaces, focal waists and crowded labels. For outlines, inspect grazing angles; a Layer Weight ramp is not a fixed-pixel contour and can blacken faces if reversed or applied indiscriminately. Check edge coverage before adjusting line width. Inspect substrate edges, individual nanostructures, lens rims, objective end faces and barrel steps. Silhouettes and borders alone can miss closed-mesh creases, bevels and CAD seams. Include required objects and edge types. Add selected source-mesh edges or verified CAD circular sections where automatic detection misses necessary boundaries. Preserve opaque occlusion and exclude internal triangulation. Check continuity through transparent beams. Reduce heavy strokes while retaining coverage.

When feedback reveals a recurring visual error, make three linked changes: generalize the rule here (or refine its existing owner), update the affected recipe's reusable prompt/acceptance criteria, and correct its implementation. Keep the generic prompt reusable across other apparatus layouts; put asset-specific selections in the example script. Rerender affected styles and inspect actual artifacts before declaring the issue solved. Remove obsolete or conflicting instructions instead of appending another exception.

Render optics/hardware/beams without text. Add names, plane markers, dimensions and leaders in a separate editable 2D overlay. Prefer short nearby labels, alternating above/below crowded branches. Dark backgrounds need light text. Avoid long crossing leaders, white text halos on light fields and crowded image-plane/z labels. Source provenance belongs in metadata; relevant physical assumptions belong in captions or the example documentation.

Acceptance: the path reads at final size; optics and coating planes are visible; black mounts remain dark; thin black Textbook component edges separate adjacent flat faces; PBS shells stay translucent enough to reveal the beam junction and their interface remains identifiable; Illustrated PBS edges stay cyan rather than black; no excessive glass transparency or unintended contour; each requested style has a distinct shading treatment; labels are legible and collision-free. Apply [release checks](release-checks.md) for physical interfaces and packaging. A prompt improves repeatability but does not guarantee a first-pass result; iterate on previews before delivery.
