# Visual direction for optical figures

Choose a visual brief before setting up the camera and renderer. The style should explain the optical path at the intended figure size, not decorate it. These anchors guide manual or scripted art direction; they are not automatic presets.

## Set the brief

Record these choices beside the assembly script:

| Field | What to decide |
| --- | --- |
| Style anchor | Editorial scientific figure, simplified 3D schematic, Cycles studio render, technical axonometric, or a supplied reference |
| Composition | View direction, projection, crop and space for post-render annotations |
| Beam treatment | Actual geometry, material, color meaning and where the path begins/ends |
| Surface and light | Key-light direction, softness, background treatment and material emphasis |
| Series rules | Terms and visual encodings to preserve; features that change in each figure |

Use a specific anchor for each new figure. A Nature Photonics-inspired brief means restrained scientific editorial composition, not compliance with that journal's submission rules or imitation of a particular published figure. Blender Cycles is a renderer, not a complete style: specify surfaces, light and camera as well.

## Example directions

| Anchor | Camera and beam | Light, background and material emphasis |
| --- | --- | --- |
| Editorial scientific figure | Compact high-oblique view; thin colored paths with consistent branch colors | Broad upper-left key, warm-white background, matte dark mounts with restrained metallic edges |
| Simplified 3D schematic | Orthographic three-quarter view; flat translucent ribbons through the optical centers | Soft upper-right key, cool pale-gray background, diffuse surfaces with reduced hardware contrast |
| Cycles studio render | Moderate perspective; narrow luminous cores without a fog halo | Large rear-side key, charcoal background, satin metal and controlled glass reflections |
| Technical axonometric | Elevated axonometric view; sparse ray bundles where they explain focusing | Broad front-side key, neutral paper background, pale ceramic-like schematic housings and crisp aperture edges |

Choose one coherent direction. Do not combine all effects. Preserve the native geometry of standard parts; reduce visual clutter with framing, contrast and visibility choices rather than stretching CAD. Material emphasis changes appearance, not claims about the physical material.

## Beam language and construction

Do not use “glowing volumetric” as a stock description. Pick the representation that communicates the path, then describe what is actually rendered:

- **Thin colored path:** a narrow curve for propagation or branch routing, with little or no emission.
- **Translucent ribbon:** a flat or gently shaped strip when a sheet or broad route is useful.
- **Narrow luminous core:** modest emission with no large bloom halo; suitable for a darker scene.
- **Sparse ray bundle:** several distinct rays to communicate convergence or divergence only when the geometry is justified.
- **Restrained scattering cone:** a volumetric illustration when the brief calls for visible scattering; do not imply that an ordinary beam is visible in clean air.

`add_beam` creates a constant-radius schematic curve. Ribbons, bundles and volumes require additional authored geometry or materials. None of these representations calculates wave propagation. Rotate descriptions by changing the actual representation, not by substituting synonyms for the same effect.

## Variation across figures

For successive independent figures, change **key-light direction, background treatment and material emphasis** rather than reusing one lighting rig and palette. Also choose a distinct camera or beam treatment where it improves the explanation. Inspect the previous brief before choosing the next.

For related panels, preserve component names, abbreviations, physical topology, channel-color meanings and annotation typography. Allocate a different visual focus to each panel: overall route, interaction region, or detector-side detail. Vary illumination direction, background value within the agreed palette and which material surfaces carry contrast. Do not rename the same beam or swap color meanings to create novelty.

An example three-panel set:

| Panel | Constant meaning | Distinct visual treatment |
| --- | --- | --- |
| Overview | BS, M1, M2, Detector; green illumination path | High-oblique camera, left key, warm-white field, matte mount silhouettes |
| Beam-splitter detail | Same terms and path colors | Closer lower view, right key, slightly cooler background, glass-interface emphasis |
| Detection detail | Same Detector name and path colors | Detector-facing crop, rear key, pale neutral field, satin housing edges |

Respect a user's locked background, material or lighting specification. For controlled comparisons, identical lighting may be essential; keep the constraint and vary only unconstrained presentation choices. Never alter geometry or data merely to make panels look different.

## Text belongs after rendering

The 3D scene contains hardware and beams, not component names or callouts. Add labels, panel letters, dimensions and leader lines to a separate 2D overlay after the clean render. Use `add_annotation` only to store optional anchor metadata; it does not perform projection or compositing. Gallery captions are browsing aids and must not be copied into the optical scene.

## Review at final size

Check path readability, clipping, occlusion, mirror orientation, support contact and aperture visibility. Reduce bloom, reflections or depth of field if they hide optical relationships. Avoid arbitrary neon colors, excessive gloss, decorative fog and repeated isometric compositions. Verify the small version, not only a zoomed viewport. Preserve the clean render and the editable overlay separately.
