# Six optical-figure shading schemes

Choose a coherent scheme after the figure brief. [Visual style](visual-style.md) owns shared role assignments and preview acceptance. `library/style_presets.json` owns style IDs, aliases and default. These recipes specify rendering direction and reusable prompts; `tools/styles.py` owns shared style operations and `examples/shading.py` is a compatibility entry point. Apply materials to scene-local copies.

The default is **Component Pack Studio**. Choose another style for a user reference or purpose: Matte Technical, Soft Lab, Journal Editorial, Textbook White, or Cel / Toon. Physics is not a style prerequisite; ordinary conceptual beams may be artist-authored.

| Scheme | Hardware | Optics | Beams and field |
| --- | --- | --- | --- |
| Component Pack Studio (`component-pack`, default) | Reflective silver barrels and continuous shading | Lit pale-blue glass with surface highlights | Narrow editable beams; light-grey studio field |
| Matte Technical (`matte`) | Dark coated mounts, satin exposed metal | Pale cyan, moderate transmission, visible edges | Thick editable bodies; cool light gray field |
| Soft Lab (`soft-lab`) | Matte dark hardware with broad side highlights | Teal edges, controlled transparent faces | Editable bodies, optional low-opacity bounded scattering; charcoal field |
| Journal Editorial (`illustrated`, alias `journal-editorial`) | Flat three-tone fills and fine grey-teal silhouettes | Translucent teal faces without specular highlights | Narrow editable beams; true white field |
| Textbook White (`textbook`) | Flat neutral colors, thin black component edges | Flat cyan faces | Flat editable beam bodies without outlines or shadows; true white field |
| Cel / Toon (`toon`) | Hard shadow/base/lit bands, fixed glints, calligraphic navy ink | Hard-banded cyan faces with deep-cyan ink | Pale beam cores, no outlines or bloom; flat butter-yellow field |

`pack` is an alias for `component-pack`. IDs and aliases are implemented in `library/style_presets.json`. The pack's local source material parameters are recorded in the preset and described in [style sources](style-sources.md). Do not claim the source biconvex lens object had that material: it has a null material. The default figure uses nonrefractive translucent illustrative glass to preserve the source palette/finish direction and beam readability. Do not embed or copy the user's source `.blend` or assets.

## Shared controls

Artistic Blender material values are not measured optical/material properties. Roughness increases toward matte; low roughness means sharper specular reflection. A coated black mount should not inherit bare-metal values merely because its substrate is aluminum. Remove excessive clearcoat, sharply reflected light panels and uniform all-white reflections before adding surface texture.

Use restrained asymmetric lighting rather than random optical misalignment. Never tilt/decenter lenses, mirrors or posts randomly: this changes the design or mounting interface. Vary camera, labels, illumination and palette instead. Preserve symmetry when meaningful.

Splitter readability benefits from three cues: cube silhouette, visible internal film where needed, and clear incoming/outgoing beam junctions. Use a nonrefractive translucent shell in conceptual illustrations; opacity is editorial, not measured transmission or splitting ratio. Tune the shell against actual background and surface overlap.

Beams are editable illustrative geometry by default. Geometry Nodes `add_beam_nodes` supports tube geometry, authored point radii and the interactive `Radius Scale`. Styling does not calculate propagation. A halo does not establish diffraction or measured scattering.

## 1. Component Pack Studio — default

- Use lit pale-blue glass, reflective silver barrels and controlled soft illumination on a light-grey field. Keep continuous three-dimensional shading.
- The local pack's inspected Lens material uses base color `(0.906751573, 0.970782459, 1.0)`, roughness `0.1`, IOR `1.5`, transmission `1`. These are source-pack settings, not evidence about a null-material lens object. The local source scene uses Cycles, Filmic, and one top area light (171.4524 W, size 1, near `(0.004917, -0.221193, 2.780707)`). The preset's authored lighting is not a claim of exact replication of that source scene.
- The illustration uses a blue display tint `(0.32, 0.58, 0.78)` under real lighting and nonrefractive transparency. Opacity increases toward grazing angles to show lens edges. The source parameters remain recorded separately.
- Keep beam colors restrained and distinct from the neutral studio field. Use narrow envelopes that leave optical edges and junctions visible.

**Prompt:** Render floating optical elements with lit pale-blue glass, reflective silver barrels and controlled studio light on a light-grey field. Keep continuous material shading and narrow, readable beams. Hide mounts and supports. Preserve optical topology and component proportions. Add labels on a separate editable layer.

## 2. Matte Technical

- Separate dark coated mounts from exposed satin metal; keep material variation controlled.
- Use readable pale-cyan optics with moderate illustrative transparency and thick editable beams.
- Light cool-gray field, broad upper-side key and weaker fill; avoid long floor shadows.

**Prompt:** Render a compact technical optical figure with separate satin metal and matte coated mounts, readable pale-cyan optical surfaces, editable saturated beam bodies and a light cool-gray field. Use broad directional lighting and restrained reflections. Preserve all alignments. No glass that disappears, whitewashed mounts, fog or random component tilt.

## 3. Soft Lab

- Use a charcoal field, matte hardware, broad side/rear key and gentle fill.
- Keep glass edges and components visible against the dark background.
- Optional faint scattering belongs in bounded geometry and is decorative only, not a calculation or measurement. Avoid theatrical world fog and blown-out cores.

**Prompt:** Use a charcoal laboratory-style field, matte hardware, one broad oblique key and a gentle fill. Keep editable beam bodies thick and visible, with only a faint bounded scattering contribution if useful. Preserve optical faces and branch separation. No theatrical fog, blown-out light cores or invisible black components.

## 4. Journal Editorial (`illustrated`)

Use a true white field and unlit three-tone grey-teal fills. A fixed surface-normal direction assigns shadow, base and light tones. Fine 0.7–0.8 px silhouette lines clarify edges. Exclude beam outlines and CAD creases. Glass uses translucent flat fills without specular highlights; studio lamps do not shade this style.

**Prompt:** Draw floating optical elements as a white-field editorial diagram with three flat face tones and fine grey-teal silhouette lines. Hide mounts and supports. Use translucent teal optical faces without glossy highlights. Keep beams narrow and preserve the reference topology. Add concise dark labels on a separate editable layer.

## 5. Textbook White

- Use flat colors with a small face-tone cue for shape readability. Add thin black component edges where they improve separation; exclude beams and hidden CAD triangles. No broad contour ramps, metallic highlights, refraction, texture or floor shadows.
- Verify an exactly white exported field. Use flat cyan optics and clear beam junctions. Add concise dark labels in the separate 2D overlay.

**Prompt:** Render a clean graphic textbook apparatus on an exactly white field. Use flat neutral-gray component colors, slight face-tone cues and thin, complete black component outlines. Use flat cyan optical symbols; keep splitter interfaces readable. Draw editable saturated beams without outlines. Suppress specular reflection, physical glass refraction, broad contour ramps and floor shadows. Add concise dark labels in the separate editable 2D overlay. No unsupported measurements.

## 6. Cel / Toon

- Use hard light/shadow bands from one fixed key, with stable flat-face tones. Keep the key fixed across a comparison.
- Use deep-cyan ink on optics and dark-navy ink on hardware silhouettes. Beams have no outline; optional pale cores are artistic highlights, not calculated modes.
- Use a flat butter-yellow field without floor shadows. Ensure transparent splitter faces remain readable and speckle-free.

**Prompt:** Render a cel-shaded optical apparatus with hard tone bands from one fixed key direction, cool neutral shadows, fixed glints and calligraphic deep-cyan/dark-navy component edges. Keep editable beams saturated with optional narrow pale artistic cores, and no beam outline. Use a flat butter-yellow field and translucent readable splitter surfaces. Preserve topology and component orientation. No bloom, floor shadows, random misalignment or unsupported physical claims.

## Compare before committing a style

Keep topology, framing and channel colors fixed when comparing styles; change materials and lighting only. Inspect the complete image at intended publication size. Verify mounts remain distinct, lens edges are visible, beam junctions and colors remain readable, and no style introduces an unsupported physical interpretation.
