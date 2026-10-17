# Briefing a figure; optional optical preflight

For an ordinary conceptual illustration, establish the visible topology and presentation—not a numerical prescription. The default route is a concise brief, library components, editable artist-authored beams, styling, separate 2D labels, then visual/scene checks. No optical calculation or preflight gate is required unless the user asks for physical design or quantitative optical behavior.

## Brief the illustration

Identify what is actually shown: source, optics, branches, sample or interaction, detector, beam directions, and any channel or polarization distinctions the user supplied. Also note presentation (floating or mechanical), reference/style, final image size, annotations and deliverables. Work from conversation, reference images, scene and component metadata before asking. Ask only a focused question when an unresolved choice prevents a clear illustration or conflicts with an explicit requirement. Offer a symbolic choice when numerical details are not needed; do not demand focal lengths, wavelengths or coating data for an ordinary conceptual figure.

A reference image can establish visible topology and style, but does not establish hidden optical prescriptions. Do not add unrequested foci, spectra, diffraction, interference, scattering, or fringe patterns. Beam shape/width may be chosen artistically for legibility, clearly understood as an illustration.

## Components and orientation

Use bundled assets from `library/index.json` by default; consult [manual assembly](manual.md) and [Python/MCP](python-mcp.md). Select standard parts where visible and useful. Keep provenance and native CAD dimensions. Enlarge or reposition floating display copies only with awareness that these are display changes, not mechanical dimensions. Mechanical depictions require suitable mount, seating and clearance checks.

Preserve objective orientation. For specimen imaging, the objective front/object side faces the specimen and its rear/infinity side faces the tube or relay lens. Use the source drawing and measured scene axis to identify the sides; never rotate an objective backward merely to match an illustrative beam.

## When physical design is requested

Only when the user requests physical design, calculated beams, quantitative performance, or a physically constrained layout, establish and record the necessary physical inputs: wavelength/media, element prescription or justified model, coordinate frames, input beam/field, apertures, conjugates and applicable tolerances. Resolve actual contradictions before claiming a physical result. Manufacturer housing CAD does not provide an internal optical prescription. Use a model appropriate to the task and state its limits. ABCD/first-order propagation is paraxial; ideal Gaussian, Jones and Fresnel helpers have explicit assumptions. Higher-NA, thick, aberrated, dispersive, or off-axis behavior may require additional data and methods.

For example, a thin lens in one transverse direction maps `[h, theta]` to `theta' = theta - h/f`, and free space maps `h' = h + d*theta`. These are useful only when their paraxial assumptions match the requested analysis. A positive-positive afocal pair with spacing `f1+f2` has diameter ratio `abs(f2/f1)` for collimated input; a plane-to-plane 4f relay has object/image planes `f1` before and `f2` after the lenses and signed transverse magnification `-f2/f1`. Such facts do not establish the user's prescription. A detector does not by itself imply a focus.

If off-axis physics is explicitly in scope, define local element frames, chief/marginal rays, actual surface ports, incidence sides and branch interactions. Check actual mirror/splitter geometry, refraction where relevant, grating order/periodicity when a grating exists, and arm overlap at the specified plane. Do not infer an off-axis carrier from a camera view. Do not claim a trace from a schematic line or a geometry validator.

## Verification and handoff

For a conceptual figure, visually review the component route, beam readability, glass and boundaries, framing/cropping, annotation legibility, and objective orientation. Run structural checks when appropriate; they do not establish optical validity.

For a physical-design task, preserve the inputs, conventions, executed calculations and relevant checkpoints with the scene. Verify applicable conjugates, propagation, branch ports, clearances and tolerances. Report exactly which checks ran and remaining unknowns. A compact display layout may shorten gaps or enlarge symbols only after the physical relationships are established; record display changes separately from physical dimensions.
