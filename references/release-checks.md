# Figure release checks

Use checks appropriate to the requested deliverable. Do not copy a checklist into a success report: record only outcomes actually inspected or commands actually run. A polished image and a structurally valid Blender scene do not establish physical optical performance.

## 1. Illustration and scene checks

For an ordinary conceptual illustration, no prescription, numerical model, optical preflight, or calculated-beam gate is required. Review:

- The visible source-to-detector topology and branch connections match the brief; no unsupported wavelengths, foci, interference or measurement claims were added.
- Components are recognizable, the objective faces the specimen in specimen-imaging depictions, and source provenance is preserved.
- Artist-authored Geometry Nodes beams remain editable, communicate the intended route, and have readable junctions and widths. Treat radii as illustrative, not calculated.
- Component-pack studio is the default unless a reference or user choice overrides it. Inspect optical surface readability, material roles, beam contrast, lighting, composition and cropping.
- Final-size 2D labels, leaders, dimensions and plane markers are legible, correct and separate/editable. Do not invent measurements.
- Any floating display scaling is not confused with native mechanical dimensions. Mechanical illustrations additionally need appropriate mount, seating and clearance review.

Use `tools/validate_layout.py` for structural validation when appropriate. It checks scene structure, not optical validity. Inspect the exported image as well as the scene.

## 2. User-requested physical design

Quantitative verification is required only when physical design or quantitative optical behavior is part of the request. Use appropriate supplied prescriptions and measurements; distinguish actual data from assumptions. Check relevant conjugates, beam/envelope behavior, optical surfaces and ports, propagation direction, splitter/combiner branch assignment, apertures, detector overlap and tolerances. Off-axis, refractive, diffractive or polarization calculations require task-appropriate inputs and methods. Inspect objective front/rear orientation and mechanical interfaces where relevant. A first-order model cannot certify high-NA performance, aberrations or unspecified internal prescriptions.

Save the actual inputs and computed checkpoints with the generated scene or report. State the model scope and limits. Do not say a calculation or interface check passed unless it was executed and its result was inspected. Structural validation is not optical validation.

## 3. Provenance and distribution

Keep source asset identifiers and provenance metadata. Do not show manufacturer branding/model inscriptions in final artwork; retain functional graduations and original source geometry as appropriate. Respect applicable permissions for CAD derivatives; authored-code licensing does not relicense manufacturer geometry.

Check relative documentation links and output paths. Publish only curated examples and requested deliverables, not temporary renders, reports, backups, bytecode or original STEP files. For package changes, run the applicable package check, affected example command and fresh independent-copy check; report actual command results. Review every final style image, not just one representative render. Keep limitations beside the claims they qualify.
