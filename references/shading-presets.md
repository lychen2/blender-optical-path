# Five optical-figure shading schemes

Choose one coherent scheme after optical preflight. [Visual style](visual-style.md) owns shared role assignments, defaults and preview acceptance. These recipes contain the intended rendering differences and reusable prompts; `examples/shading.py` implements them for the bundled example. Apply materials to scene-local copies. Treat style feedback as a correction to both the prompt and its implementation.

Default to **Matte Technical** for a restrained apparatus figure. The current dual-wavelength example uses this direction. Choose Cel or Illustrated Geometry for stronger abstraction, Textbook White for a clean teaching figure, and Soft Lab only when a dark field helps the paths. Do not ask again when the user has supplied a clear reference or chosen a style.

| Scheme | Hardware | Optics | Beams and field |
| --- | --- | --- | --- |
| Matte Technical | Dark coated mounts, satin exposed metal | Pale cyan, moderate transmission, visible edges | Thick low-emission envelopes; cool light gray field |
| Soft Lab | Matte dark hardware with broad side highlights | Teal edges, controlled transparent faces | Thick bodies with optional low-optical-depth scattering; charcoal field |
| Illustrated Geometry | Warm continuous diffuse shading, selective hardware contours | Soft tinted faces; translucent splitters with fine cyan edges | Thick softly shaded colored bodies; warm paper field |
| Textbook White | Flat neutral colors with thin black component edges | Flat cyan faces; translucent splitters with a visible film | Flat colored bodies without outlines or shadows; true white field |
| Cel / Toon | Hard shadow/base/lit bands, fixed glints, calligraphic navy ink | Hard-banded cyan faces with deep-cyan ink | Pale camera-facing beam cores, no outlines or bloom; flat butter-yellow field |

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

Cel / Toon uses hard lighting bands, crisp highlights and variable-width ink to give the apparatus a cel-animation appearance.

- Use emission-only bands: `Geometry.Normal · key` through a constant-interpolation ColorRamp into Emission. Place the fixed key direction so broad light/shadow boundaries are visible on barrels and lenses. Keep flat faces away from band thresholds.
- Use shadow, base and lit tones. Neutral shadows shift cool; beam tones retain their channel colors. Optics and hardware add a hard glint from a fixed direction. For beam cores, subtract the view component along the curve tangent, normalize, then compare with the surface normal. This keeps the pale stripe visible on oblique segments.
- In EEVEE, Diffuse BSDF → Shader to RGB → constant ColorRamp → Emission is an alternative. Shader to RGB is EEVEE-only. The emission recipe above is tested in Cycles.
- Draw Freestyle silhouette and border ink with a fixed pixel width and a calligraphy thickness modifier, about 2–5 px at 2100 px: deep cyan on optics, dark navy on hardware. Beams have no outline. Do not use facing-ratio rims; they blacken lens faces and objective barrels.
- Use a flat butter-yellow field with no floor shadow. Splitter shells use pale tones to keep the internal junction readable. In Cycles, setting `min_transparent_bounces = transparent_max_bounces` suppresses Russian-roulette noise through stacked transparent faces.

**Prompt:** Render a cel-shaded optical apparatus. Use emission-only hard tone bands from one fixed key direction, with clear light/shadow boundaries on objective barrels, laser housings and lenses. Shift neutral shadows cool. Give traced beams pale camera-facing cores, and give glass and metal crisp fixed glints. Draw calligraphic deep-cyan ink on optics and dark-navy ink on hardware silhouettes, with no beam outlines. Use a flat butter-yellow field. Keep translucent splitter shells pale, with a visible internal film and beam junction. Preserve the manufacturer objective shape and native ring color, and keep the camera and optical geometry fixed. No soft gradients, bloom, floor shadows or 3D lettering.

**Acceptance:** At a 700–900 px preview width the figure reads as cel animation and is clearly different from Textbook White and Illustrated. Horizontal and oblique beam segments show pale cores at resolvable widths; focal waists remain visible. Objective barrels and laser housings show hard light/shadow boundaries. Flat faces have stable tones. Beams have no outline; splitter shells, films and junctions are readable and speckle-free. No lost focal waist, blackened optics or muddy splitter.

## Compare before committing a style

Keep trace, topology, framing and channel colors fixed when comparing shading schemes; change materials and lighting only. A later floating/mechanical composition comparison may change display scale, but should be labeled accordingly. Inspect both full resolution and the actual publication width. Verify black mounts remain black, lens edges are visible, beam colors retain saturation, focal structure remains legible and neither highlights nor shadows dominate.
