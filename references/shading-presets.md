# Five optical-figure shading schemes

Choose one coherent scheme after optical preflight. [Visual style](visual-style.md) owns shared role assignments, defaults and preview acceptance. These recipes contain the intended rendering differences and reusable prompts; `examples/shading.py` implements them for the bundled example. Apply materials to scene-local copies. Treat style feedback as a correction to both the prompt and its implementation.

Default to **Matte Technical** for a restrained apparatus figure. The current dual-wavelength example uses this direction. Choose Cel or Illustrated Geometry for stronger abstraction, Textbook White for a clean teaching figure, and Soft Lab only when a dark field helps the paths. Do not ask again when the user has supplied a clear reference or chosen a style.

| Scheme | Hardware | Optics | Beams and field |
| --- | --- | --- | --- |
| Matte Technical | Dark coated mounts, satin exposed metal | Pale cyan, moderate transmission, visible edges | Thick low-emission envelopes; cool light gray field |
| Soft Lab | Matte dark hardware with broad side highlights | Teal edges, controlled transparent faces | Thick bodies with optional low-optical-depth scattering; charcoal field |
| Illustrated Geometry | Warm continuous diffuse shading, selective hardware contours | Soft tinted faces; translucent splitters with fine cyan edges | Thick softly shaded colored bodies; warm paper field |
| Textbook White | Flat neutral colors with thin black component edges | Flat cyan faces; translucent splitters with a visible film | Flat colored bodies without outlines or shadows; true white field |
| Cel / Toon | Two or three broad shading bands | Distinct face and rim tones | Saturated thick paths without bloom; pale neutral field |

## Shared controls

All Principled material ranges below are artistic Blender values, not measured optical/material properties. Roughness increases toward matte; **low roughness means sharper specular reflection**. A coated black mount should not inherit bare-metal values merely because its substrate is aluminum. Remove excessive clearcoat, sharply reflected light panels and uniform all-white reflections before adding surface texture.

Use restrained, asymmetric lighting rather than random optical misalignment. A slight material roughness variation or reduced cosmetic screw detail is acceptable. Never tilt/decenter lenses, mirrors or posts by a random fraction of a degree to avoid a synthetic appearance: this changes the trace or mounting interface. Required symmetry can be physically meaningful; preserve it. Camera choice, unequal label placement and nonuniform illumination can provide visual variety without altering the system.

Color is a channel encoding. Visible wavelengths may use recognizable approximate hues, with sufficient contrast against the field; display RGB is not a spectral measurement. Near-infrared channels such as 780/1064 nm require a stated **false color**, not a claimed visible infrared hue. Keep combined-channel colors consistent and distinguish them from a new wavelength. Avoid showing arbitrary spectra for monochromatic beams.

Splitter readability requires three simultaneous cues: a cube silhouette, its actual internal film plane, and visible incident/reflected/transmitted beam junctions. For Textbook and Illustrated, use low-opacity shells and a slightly stronger film with no physical refraction. Mix a Transparent BSDF with the style's surface shader; these are editorial opacity values, not measured transmission or splitting ratios. Add thin black component edges in Textbook and subtle cyan splitter edges in Illustrated. Check that the shell has neither become opaque nor disappeared at publication width. The example uses per-surface shell/film opacity of 0.09/0.24 in Textbook and 0.26/0.34 in Illustrated; tune for surface overlap and background rather than treating these as universal constants.

Beams remain thick by default. Numerical tracing determines their envelope and position; styling changes their appearance. A physically narrow focus can use a documented display-width floor. Volume scattering illustrates visibility; it does not imply measured aerosol density or diffraction. A halo is not a diffraction calculation.

## 1. Matte Technical — default

- Black coated mounts: Principled base color near charcoal, Metallic `0.05–0.25`, Roughness `0.4–0.6`. Exposed metal: Metallic `0.6–0.8`, Roughness `0.35–0.5`. Keep these separate so every part does not look like the same plastic.
- Readable optical glass: pale cyan base, Transmission Weight `0.15–0.4`, Roughness `0.12–0.25`, modest specular response, darker edge tone if needed. These reduced-transmission settings intentionally emphasize the optic. Use a physical glass model only when its reflections and refraction remain readable at the final size; refractive index depends on material and wavelength (BK7 is approximately 1.517 near the visible d line, not a universal constant).
- Thick beam surfaces: restrained emission around `0.1–0.4` plus a saturated diffuse/base contribution. No default world fog or bloom.
- Broad upper-side key, weaker fill, light cool-gray field, short soft shadows. Keep shadowing from closing lens apertures or graying the whole image.

**Prompt:** Render a compact technical optical figure with separate satin metal and matte coated mounts, readable pale-cyan optical surfaces, thick saturated traced beam envelopes and a light cool-gray field. Use broad directional lighting, restrained reflections and short soft shadows. Preserve all optical alignments. No glass that disappears, whitewashed mounts, fog, glossy plastic or random component tilt.

## 2. Soft Lab

- Hardware Roughness `0.45–0.65`, with coating/metal separation as above. One large side/rear key and a weaker fill; preserve legibility of black parts against charcoal.
- Glass Transmission Weight `0.25–0.55`, with visible edge highlights and no clipped white patches.
- Prefer a thick bounded beam body. Optional Principled Volume or Volume Scatter belongs inside a bounded beam volume, not an opaque world fog. Set scattering by target optical depth `tau = sigma * L`, for example an illustrative `tau ~ 0.01–0.05`, and check the actual rendered path length in scene coordinates. Density numbers are scale-dependent; do not copy `0.01` into both metre and millimetre scenes without testing. Keep exposure fixed while comparing.
- No diffraction claim from a glow or scattering halo.

**Prompt:** Use a charcoal laboratory-style field, matte hardware, one broad oblique key and a gentle fill. Keep the traced beam envelopes thick and visible, with only a faint bounded scattering contribution if necessary. Preserve optical faces and branch separation. No theatrical fog, blown-out light cores or invisible black components.

## 3. Illustrated Geometry

- Preserve real objective CAD and essential optical silhouettes; suppress cosmetic detail in display copies. Never substitute a hand-built objective barrel.
- Principled Metallic `0–0.15`, Roughness `0.55–0.75`, small palette of muted hardware colors. Use local shadowing sparingly, not a blanket dirty AO layer.
- Tinted optical faces with gentle diffuse shading; **exclude lenses, splitter prisms, beams and RMS objective barrels from dark contour ramps**. Retain continuous soft shading on the metal barrel and the native colored ring. Use translucent splitter shells with a visible film and subtle cyan edge strokes. Optional dark contours belong only to selected non-optical hardware silhouettes, not every screw or internal triangle.
- Thick flat colored beam envelopes, no volume scattering. A very subtle hand-drawn character can belong in the 2D overlay, not jittered optical boundaries.

**Prompt:** Produce a warm-paper technical illustration with continuous soft volume shading, muted matte hardware and selective subtle contours on non-optical housings. Keep lenses visibly cyan with no black ink border. Show splitter cubes as translucent cyan shells with subtle cyan edges and a slightly stronger internal film; keep the beam junction visible without refraction. Shade the manufacturer-derived objective barrel smoothly in neutral gray and preserve its colored ring; do not darken its silhouette into a thick black rim. Draw traced beams as thick softly shaded color bodies without outlines. Use a directional soft key and small shadows for depth. Keep the reference camera and optical geometry fixed. This style must read as a softly shaded illustration, not the flat white Textbook preset.

**Acceptance:** Warm paper plus continuous surface shading; clean cyan optics; no dark patches at lens centers or objective edges; dark contours only on non-optical housing details. Translucent splitter cubes retain cyan boundaries, a visible film and readable internal beam junctions.

## 4. Textbook White

- Flat, lighting-independent colors or an emission-based graphic shader with a small normal-based tonal variation (`~10–20%`) for shape readability. Add thin black strokes to component silhouettes and necessary creases, including optics and objective barrels; exclude beams and hidden CAD triangles. Use fixed-pixel lines rather than broad view-angle contour ramps. No metallic highlights, refraction, texture or floor shadows. Emission here implements flat color; it does not imply a glowing object.
- Pure-white composited field, verified in the exported pixels. Do not rely on changing world strength or a gray diffuse floor to approximate white.
- Clear flat cyan optics, neutral gray hardware and the original magnification-ring color. Use translucent splitter shells and a slightly stronger film so the internal split/merge junction stays visible. Thick solid-color beam envelopes, no fog, no bloom. Use a tested display transform for the chosen palette; keep channel identity unchanged.
- Nearby dark 2D labels, few leaders, consistent typography and generous separation between paths and text.

**Prompt:** Render a clean graphic textbook apparatus on an exactly white field. Use flat neutral-gray component colors with a slight face-tone cue and thin black component outlines. Use flat cyan optical symbols and translucent cyan splitter shells with a visible internal film. Keep split/merge beam junctions visible. Preserve the real objective silhouette and its magnification ring. Draw thick solid-color traced beams without outlines. Suppress specular reflection, physical glass refraction, broad contour ramps, surface texture and all floor shadows. Add concise dark labels in the separate 2D overlay. Keep geometry and framing fixed. The image should read as a crisp flat diagram and be visibly different from the warm, continuously shaded Illustrated preset.

**Acceptance:** White exported background, virtually no surface gloss or directional shadow, thin black component outlines and no beam outlines. Adjacent flat faces remain distinct; the splitter shell, film and internal beam junction are all visible. Clearly different from Illustrated at a 700–900 px preview width.

## 5. Cel / Toon

- Use two or three diffuse tone bands with a broad lighting direction. Avoid a thick black outline on every edge.
- In EEVEE, an optional node path is Diffuse BSDF → Shader to RGB → ColorRamp with constant interpolation → Emission. Shader to RGB is engine-specific and is not a portable Cycles toon pipeline. Set separate ramps for hardware, optics and beam roles; do not quantize everything to identical colors.
- For Cycles use a tested Toon BSDF setup or a composited lighting pass. Verify engine/node support before promising identical results across engines.
- Optical glass uses a readable tinted face with a restrained deep-cyan silhouette cue, not black ink. Other hardware can use a fine dark-gray contour. Preserve the manufacturer objective shape and ring; use soft gray barrel shading without a broad black outline. Thick beams have no black outline or scattering. Keep floor shadows absent or subordinate so contours, not shadows, separate components.

**Prompt:** Create a restrained cel-shaded optical apparatus with discrete diffuse tone bands, fine dark-gray contours on hardware and fine deep-cyan contours on optical silhouettes. Keep lens faces readable, not black-rimmed. Preserve the manufacturer objective shape, smoothly shaded barrel and native ring color. Give traced beam bodies a solid saturated color with no black outline. Use a pale shadow-free field and preserve the fixed camera/optical geometry. No broad black objective rims, tangled internal outlines, heavy ground shadows, bloom or 3D lettering.

**Acceptance:** Clearly stepped shading and legible silhouettes; fine role-specific contour cues; no lost focal waist, blackened optics or dark floor shadow competing with the path.

## Compare before committing a style

Keep trace, topology, framing and channel colors fixed when comparing shading schemes; change materials and lighting only. A later floating/mechanical composition comparison may change display scale, but should be labeled accordingly. Inspect both full resolution and the actual publication width. Verify black mounts remain black, lens edges are visible, beam colors retain saturation, focal structure remains legible and neither highlights nor shadows dominate.
