# Optical-figure shading

**Journal Editorial** is the default. It combines transparent glass, restrained hardware, fine neutral contours and a white background.

[Visual style](visual-style.md) covers composition and readability. `library/style_presets.json` defines style IDs, aliases and the default. `tools/styles.py` applies materials to scene-local copies.

## Journal Editorial

Use `illustrated` or `journal-editorial`.

- Use the component pack's clear `Lens` shader for optical glass: transmission 1, IOR 1.5 and roughness 0.1.
- Use neutral hardware with three restrained face tones. Preserve dark source and detector housings.
- Use fine neutral silhouettes, approximately 0.7–0.8 px. Exclude beam outlines and hidden CAD creases.
- Keep the background white. Broad area lights provide glass reflections; hardware face tones remain stable.
- Draw narrow editable beams with consistent channel colors. Add concise labels in a separate SVG layer.

Glass base color is `(0.906751573, 0.970782459, 1.0)`, from the inspected source material. Reflections, refraction and edge contours reveal its shape. See [material provenance](style-sources.md#local-component-pack-glass).

**Prompt:** Draw a floating optical apparatus on white with clear glass, restrained neutral hardware and fine silhouettes. Keep component proportions and optical topology. Use narrow colored beams and separate editable labels.

## Other rendering options

| Style | Hardware | Optics | Field |
| --- | --- | --- | --- |
| Matte Technical (`matte`) | Dark coated mounts and satin metal | Pale cyan, moderate transmission | Cool light gray |
| Soft Lab (`soft-lab`) | Dark surfaces with broad side highlights | Teal edges and transparent faces | Charcoal |
| Textbook White (`textbook`) | Flat neutral colors and thin black edges | Flat cyan symbols | White |
| Cel / Toon (`toon`) | Hard bands, fixed glints and bold ink | Banded cyan faces | Butter yellow |

`component-pack` and `pack` are compatibility aliases for `illustrated`.

### Matte Technical

Separate coated mounts from exposed satin metal. Use broad directional lighting and restrained reflections. Preserve alignments and apertures.

**Prompt:** Render a technical optical figure with satin metal, dark mounts, readable pale-cyan optical surfaces and editable beam bodies on light gray.

### Soft Lab

Use a broad side or rear key with a weaker fill. Keep glass and dark hardware visible. Any decorative scattering stays inside bounded beam geometry.

**Prompt:** Render an optical apparatus on charcoal with matte hardware, broad side highlights and readable colored beams. Preserve component faces and branch separation.

### Textbook White

Use flat neutral hardware and cyan optical symbols. Thin black edges clarify components; exclude beams, hidden triangles and floor shadows.

**Prompt:** Draw a white-field textbook apparatus with flat neutral hardware, cyan optics and thin black component edges. Add labels separately.

### Cel / Toon

Use hard shadow, base and light bands from a fixed key direction. Beams may have pale artistic cores. Use calligraphic component edges.

**Prompt:** Draw a cel-shaded optical apparatus with fixed hard face tones, cyan optics and dark component ink on butter yellow. Keep beams free of outlines.

## Inspect the rendered figure

Keep geometry, camera and channel identities fixed during style comparisons. Inspect glass edges, splitter junctions, objective barrels and labels at final size.

Correct lighting or contour coverage when transparent glass disappears. Preserve the selected material's character and keep beam routes readable. Do not tilt optics to create highlights.
