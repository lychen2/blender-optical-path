# Optical preflight, consolidated questions and off-axis tracing

Complete this preflight before assembling the scene. The shared placement and beam APIs draw authored geometry; they do not infer an optical prescription or trace rays.

## Think first

Read the user's request, references and established choices. Build a provisional surface/port table and distinguish supplied facts, consequences of an optical model, missing information and visual choices. Work through propagation direction, lens signs, focal planes, object/image conjugates, pupil planes, branch roles and possible folding surfaces yourself. Evaluate plausible configurations before offering choices. A reference image establishes visible topology and style, not necessarily focal lengths, sensor position, coating spectra or incidence angles.

Identify contradictions and their consequences. Examples include a negative first lens substituted for a specified positive-positive 4f expander, an input chief ray hitting a mirror's back, or the sensor being treated as a focus just because it is a detector. A specified 4f relay does not by itself identify whether the displayed bundle represents collimated illumination or rays from one object point. State that distinction before constructing an envelope.

Resolve information already available from the conversation, component data, drawings or a model calculation without asking the user to repeat it. Research unfamiliar optics before inventing a menu. Treat assumptions that change the optical design as questions, not as reversible styling decisions.

## Ask one complete, purposeful batch

When optical relationships or the design are unclear, ask detailed questions before dependent modeling. Prepare the whole batch first: do not discover one question per render. Use at most four grouped questions in a single questionnaire. Each group has two to four physically meaningful choices and permits a custom answer. Include all currently identifiable blockers in the descriptions or a concise custom-answer prompt. Omit resolved groups; if there are no blockers, proceed.

| Group | Resolve together when unknown |
| --- | --- |
| Optical intent and topology | Beam direction and branches; illumination versus imaging; source wavelengths/polarization; sample interaction; which beam or field the figure represents |
| Prescription and conjugates | Lens signs and focal lengths; telescope/relay membership; object, image, common focal and pupil planes; spacings; sensor offset; source collimation, beam size and required numerical versus schematic fidelity |
| Off-axis geometry and interfaces | Field/chief-ray angles in each arm; decenter/tilt; mirror/splitter ports; recombination angle; detector-plane normal; apertures; grating grooves, incidence, wavelength and orders, when a grating exists |
| Appearance and delivery | Floating versus mechanical mode; compactness/display scale; reference style, camera, palette/background, readable glass, beam body treatment; 2D labels; figure size and deliverables |

Lead each unresolved group with the interpretation already supported by evidence and explain what the answer changes. Recommend an option only if justified. Do not make users choose between arbitrary mutually exclusive alternatives when the actual design may combine them. Do not re-ask established style choices or force a choice of unknown numerical specifications. Offer symbolic or explicitly illustrative parameters where they can meet the requested fidelity, and obtain agreement when that choice changes the optical result.

After the answers, record one coherent design brief beside the assembly script. Resolve contradictory answers before drawing. One batch means all questions knowable now, not a license to invent answers to a genuinely new contradiction. If a new blocker arises from new evidence, explain why it was not resolvable earlier and ask only that blocker. Continue independent material, asset and document work meanwhile.

## Construct the optical model before the display geometry

Define physical/model coordinates separately from display coordinates. Record wavelength, units, media, local element frames, input ray/field definition, apertures and model limitations. A Gaussian beam radius, a geometrical marginal-ray height and a drawn tube radius are different quantities.

For a paraxial thin lens in one transverse direction, use `[h, theta]`: free space gives `h' = h + d*theta`, and a lens gives `theta' = theta - h/f`. Apply the model in both transverse directions where appropriate. For a positive-positive afocal pair with spacing `f1+f2`, collimated input crosses the shared internal focal plane and leaves collimated with diameter ratio `abs(f2/f1)`. A plane-to-plane 4f relay additionally places its object and image planes `f1` before and `f2` after the lenses, with signed transverse magnification `-f2/f1`. Illumination rays and the pencil emitted by an object point traverse the same relay differently; show the requested bundle. A chief ray of an on-axis bundle may stay on-axis throughout while its boundaries converge and diverge.

Use ABCD/first-order propagation only within its stated paraxial regime. Use finite-conjugate/objective data or a suitable numerical model when the result depends on thick optics, high NA, aberration or wavelength-dependent power. Manufacturer housing CAD does not provide the internal optical prescription. Identify a microscope objective's front/object side and rear/image or infinity port from its drawing and intended use before placement. In an infinity-corrected specimen-imaging train the front faces the specimen and the rear faces the tube lens. Never rotate the objective backwards to make an illustrative focus fit: a positive thin-lens matrix is direction-agnostic and cannot certify an asymmetric real objective used with changed conjugates. Separate illumination from object-point imaging when their envelopes differ, and flag an inconsistent envelope for correction rather than altering an established physical orientation. A finite drawn waist can avoid a degenerate mesh; mark it as a display floor unless calculated from a Gaussian/wave model. Do not claim diffraction, interference or fringes from geometrical tracing alone.

## Off-axis paths require local 3D geometry

Default to coaxial propagation within each arm and coaxial recombination when neither the request nor evidence specifies otherwise. Do not infer an off-axis carrier from an oblique camera view or a folded path, and do not ask about it again after the user has selected coaxial operation. Treat off-axis tracing as a capability required when the design calls for it, not as an extra feature to insert. Distinguish folded on-axis propagation, a tilted/decentered optical element, an off-axis object field and a relative recombination angle. These are not interchangeable.

Trace chief and marginal rays for each relevant field/wavelength, not only a centerline. Use actual surface intersections in a common world frame, converting to each element's local optical coordinates for its interaction. Intersect a ray `r + t*k` with a plane through `p` with normal `n` using `t = dot(p-r,n)/dot(k,n)`; reject parallel/backward intersections when inappropriate. Apply apertures in the local surface plane.

At a plane mirror, check `k_out = k_in - 2*dot(k_in,n)*n`, the illuminated face and output clearance. Assign transmitted and reflected splitter branches explicitly, including finite-thickness refraction if it matters. At refracting surfaces use Snell's law or a justified local paraxial model, respecting medium indices and total internal reflection. Oblique high-NA focusing cannot be represented by rotating an on-axis cone and calling it a validated trace; sagittal and tangential behavior may differ.

For a grating define groove direction, surface normal, incident wavevector, diffraction order and side of the surface. Enforce tangential wavevector matching along the periodic direction, preserve the groove-parallel component, and choose the physically appropriate normal component; reject non-propagating orders. A scalar grating equation is sufficient only for the declared in-plane convention. Never assume every wavelength is diffracted into one plane under conical incidence. Do not add a spectrum to monochromatic light.

When two arms recombine, verify overlap and relative direction at the intended image/detector plane. If an off-axis carrier is requested, establish the relative angle and detector sampling; do not invent a tilted output or visible fringe pattern. Record unresolved angle/field parameters and ask before dependent tracing.

## Verification and handoff

Save the input prescription, conventions and computed surface checkpoints with the generated scene: positions, directions, ray heights, aperture margins, identified conjugate/focal planes and applicable tolerances. Verify lens-plane continuity, expected magnification/vergence, forward propagation and branch ports. Trace-based claims require executed checks, not a checklist or screenshots alone.

For a compact floating diagram, map the model into display coordinates only after the physical relationships are established. Keep element order, common foci, incidence sides and beam/optic alignment; record compression and component display scale. Do not use compressed display distances to claim focal lengths. A mechanical view uses native CAD dimensions and also needs mounting/clearance checks.

`tools/validate_layout.py` checks scene structure, not optical validity. Its success cannot substitute for the trace. Inspect the final image independently for beam visibility, readable glass, cropping, supports and 2D labels.
