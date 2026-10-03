# Required optical-figure checks

Apply these checks before accepting a scene or publishing an example. A visually plausible render and a structurally valid Blender scene are insufficient evidence of correct optics. Record actual outcomes beside generated scenes; do not copy unperformed checks into a success report.

## 1. Optical relationships and ports

Complete [optical preflight](optical-preflight.md) before rendering. Resolve all identifiable design and style uncertainties in one prepared question batch. Preserve answered choices. Default to coaxial operation unless the design specifies otherwise.

Define lens signs, object/image planes, shared foci, relay groups and the displayed beam's meaning. Positive-positive 4f expansion must not become a negative-first-lens telescope. Calculate illumination envelopes and conjugates from the agreed model; do not fit arbitrary radii to a pretty path. A detector does not automatically imply a converging input beam. Keep display scale separate from physical focal distances. Show grating dispersion only for present wavelengths and physically allowed orders with an explicit convention.

For **each splitter and combiner independently**:

- Inspect the internal coating/interface polygon, not the cube outline or its nominal asset axis. Transform its normal into world coordinates using the inverse transpose of the full object/parent/instance transform.
- Derive incident and output directions from the actual upstream/downstream port positions. Do not use manually typed vectors that merely repeat the design angles.
- Verify the reflected port with `k_out = k_in - 2(k_in·n)n`. Check the actual transmitted port separately, accounting for refraction/finite thickness when relevant. Check forward intersections, coating location and port overlap.
- For recombination, verify which incoming arm transmits and which reflects into the camera direction. A correct splitter orientation does not establish a correct combiner orientation; parallel-looking cubes may require different rotations depending on the incoming vectors.
- Do not confuse PBS and NPBS optical behavior. Reusing cube geometry does not establish coating/polarization properties. Record nominal coatings and polarization assumptions explicitly.

Use geometry-derived normals in executable checks. An angle assertion that uses the same hard-coded angle as placement cannot detect a mismatched internal film or reversed input direction. Run these checks after placement changes and before every release render.

## 2. Objective orientation and provenance

Use reviewed manufacturer objective CAD, preferably RMS-series assets; do not hand-model replacement barrels. Recolor native ring surfaces only, preserving provenance and truthful magnification. Manufacturer housing geometry is not an internal lens prescription.

In specimen-imaging usage, the front/object side faces the specimen and the rear/infinity port faces the following tube/relay lens. Check this using the measured model axis and specimen position. Never reverse the objective to fit an idealized beam cone. An ABCD result alone does not validate conjugates, NA or aberrations of a real asymmetric objective. Document departures from intended use and require a justified design, not a cosmetic rotation.

## 3. Mounting and lens seating

For mechanically shown spherical lenses, prefer compatible KM100 adjustable mounts; POLARIS-K1S5/KS1 require their own interface checks. Use POLARIS-K1S5 as the standard mirror preference. Fixed miniature holders do not replace alignment capability. Tip/tilt adjustment is not XY translation. Keep genuine catalog parts unchanged and do not force incompatible barrels into one-inch mounts.

Measure optic bore center, optical surface axis, pocket opening direction, annular stop and clamping face. Check radial centering **and axial seating**. Put the correct side of the lens edge against the stop; centering bounding boxes can leave a lens outside the pocket or intersecting its shoulder. Check edge thickness, clear aperture, retention and protrusion independently. Do not silently scale source CAD to fit. Record unresolved contact, retention and thread issues.

Orient the actual mounting face toward the post. Verify post contact and hole-axis alignment using geometry, not the mount's lowest decorative feature. Distinguish threaded holes from M4 clearance/counterbore interfaces, and use appropriate nominal fasteners with honest limits. Do not hide an inverted mount with an invented spacer. Black anodized KM100 hardware must have an explicit dark coated material, not Blender's unassigned white default.

## 4. Material roles and readable images

Assign shading by semantic role: coated mount, metal barrel, lens, splitter, beam, background. Inspect material nodes, not just viewport diffuse colors. Glass should remain identifiable at the final output width. Avoid full transparency that erases lens faces and reflected light that turns dark mounts white.

Textbook flat colors need thin black component edges to separate silhouettes and necessary creases; exclude beams and hidden mesh edges. For Textbook and Illustrated splitters, confirm that the tinted cube shell, internal film and split/merge beam junction are all readable. Use a nonrefractive transparent/surface blend, with enough shell opacity to remain recognizable at publication width. Illustrated may use subtle cyan splitter edges. Illustrated contour treatments must not put black ramps on lenses, splitter cubes, beams or RMS barrels. Use mild surface shading for objective bodies and preserve the colored magnification ring. In toon mode, use restrained hardware contours and cyan optical contours; keep beams free of black outlines. Review grazing-angle effects at the actual camera because a facing ramp is not a fixed-width silhouette stroke.

Never add random optical tilt or decenter to make the image feel less synthetic. Vary lighting, finish, camera and overlay placement. Preserve genuine symmetry when required. Infrared colors are false-color encodings. Scattering/glow is not a diffraction calculation.

## 5. Deliverable and distribution check

Render 3D geometry without text; add component names and dimensions only in a separate editable 2D overlay. Inspect captions, short labels, leaders and plane markers at the final display size. Keep text legible on dark variants. Avoid labels colliding with the image-plane/z region.

Show only final curated examples in README. When comparing styles, keep topology, framing and channel meaning fixed. A floating/mechanical comparison may change display spacing and component scale; state this near the comparison. Check every final image, not just one representative render.

Run `tools/check_package.py` on the modified library, test the actual example CLI and optical-model checks, and exercise a fresh independent package copy. Inspect relative links and tracked files. Keep STEP originals, test logs, old renders, backups, cached bytecode and duplicated example `.blend` outputs out of the public package. Preserve useful source provenance and scripts. State unresolved optical/mechanical limits beside the example, without claiming structural checks verify an instrument design.
