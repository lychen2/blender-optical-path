---
name: blender-optical-path
description: Build editable Blender optical-path illustrations from a brief topology, component-library assets, editable beam geometry, deliberate styling, and a separate 2D annotation layer. Use Python or Blender MCP when available; physics-based modeling is optional unless the user asks for a physical design.
---

# Blender optical path

Create a **pure paper illustration by default**, not a simulated or certified instrument. The ordinary path is **brief topology → Thorlabs/library components → editable Geometry Nodes beams → style → separate editable 2D labels → visual and scene checks**. Keep all scene geometry editable. Do not invent a prescription, numerical optical parameters, or physics claims to complete a conceptual figure. Explicit user choices override defaults.

## Defaults and invariants

- **Default presentation: floating optics.** Hide mounts, retaining rings, sample frames, support posts and bases. Retain optical elements and recognizable functional source/detector housings. Choose `compact` for mounts without supports, or `full` for native mechanical assemblies.
- **Default look: Journal Editorial.** Use `illustrated` or `journal-editorial`: Cycles-rendered clear glass, reflective metal and softly lit housings, using the component pack’s materials, Filmic view and studio environment. Keep the camera background free of floor shadows. Add rough glass only to the cylindrical nonoptical lens edges. Use the inspected component pack's near-white `Lens` shader: transmission 1, IOR 1.5, roughness 0.1. Preserve an explicitly supplied glass shader on local copies. `component-pack` and `pack` are compatibility aliases for `illustrated`. See [shading presets](references/shading-presets.md) and [material sources](references/style-sources.md).
- **Illustrative beams by default.** Make editable beam bodies with `tools/geometry_nodes.py` `add_beam_nodes`; use artist-authored radii and the interactive `Radius Scale`. They communicate route, branches and visual emphasis, not calculated propagation. Do not represent them as physically calculated unless the user requests a physical design and the relevant model/checks are actually performed.
- **Use real library/CAD parts where helpful.** Browse `library/index.json`, including Thorlabs components and standard parts. Preserve native source geometry and provenance. Scale floating display copies only for legibility; retain native CAD dimensions for mechanical views and verify mechanical interfaces when those matter.
- **Objective orientation remains meaningful.** In specimen-imaging usage, objective front/object side faces the specimen; rear/infinity port faces the tube/relay lens. Confirm from the drawing and scene axis. Do not reverse an objective to make an illustrative beam fit.
- **No text in the 3D render.** Add labels, dimensions and leaders later in a separate editable 2D overlay. `add_annotation` records intent only; it does not create or composite visible text.
- **Separate scene and visual checks from optical validity.** An ordinary conceptual illustration needs no numerical prescription, optical preflight, or quantitative beam check. If a user requests physical design, quantitative optics and applicable mechanical interfaces become part of that task; do not claim validation without executed evidence.
- **Keep provenance honest.** Distinguish sourced CAD, authored geometry, display scaling and conceptual assumptions. Do not show manufacturer branding/model inscriptions in the final art; retain source metadata and observe applicable reuse permissions.

## Workflow

1. **Brief the topology.** Identify components, source-to-detector route, branches, beam/channel meanings, presentation mode, reference style, figure size and requested deliverables. Ask only about a genuine ambiguity that blocks the requested illustration or physical design. For a conceptual figure, use clear symbolic choices rather than requesting unavailable optical prescriptions. See [brief and optional physical design](references/optical-preflight.md).
2. **Assemble components.** Choose assets from `library/index.json`; use [Python/MCP](references/python-mcp.md) for scripted work or [manual assembly](references/manual.md) for UI work. Use exact manufacturer CAD only when requested or needed. For custom lens meshes, use the optional [OptiCore adapter](references/opticore.md) with an explicit local checkout. Assign the glass shader separately. Preserve native dimensions and source hierarchy. Check objective orientation and mechanical interfaces when applicable. See [official CAD workflow](references/thorlabs-workflow.md) when an exact requested part is missing.
3. **Draw editable beams.** Add Geometry Nodes beam geometry from the chosen topology using `tools/geometry_nodes.py` `add_beam_nodes`. Set point radii deliberately and tune with `Radius Scale`. For a conceptual figure, the radii are artist-authored, not inferred from the optics. Beam geometry can be tubes; do not promise unverified profile options.
4. **Style and compose.** Apply a named style through `tools/styles.py` (`apply_style`, `list_styles`, `setup_lighting`); `examples/shading.py` is a compatibility entry point. Available styles and aliases are in `library/style_presets.json`. Use the recipe and reference links below. Inspect a preview and high-risk details before final rendering.
5. **Annotate separately.** Render components and beams without text; add labels in a distinct editable 2D layer after rendering. Choose final positions, type size, leaders and dimensions at the target image size. Do not invent measurements.
6. **Check and deliver.** Inspect the rendered image at intended final size and verify scene structure as appropriate. Preserve edited `.blend`, assets/scripts and provenance as requested. For a physical-design task, also run appropriate quantitative and interface checks and report their actual results. See [release checks](references/release-checks.md).

## Optional technical modeling

Physics is an incremental, opt-in layer rather than a prerequisite for ordinary conceptual illustration. If requested, distinguish physical coordinates from display coordinates and use inputs and calculations appropriate to the design. `tools/advanced.py` contains parametric conic/aspheric lens geometry and calculated Gaussian-beam helpers; `tools/optical_model.py` contains ideal ABCD/paraxial, Gaussian, Jones and Fresnel calculations with explicit limitations. These capabilities do not turn CAD into a prescription, certify an instrument, or imply that a calculation was run. See [optional physics and upstream tools](references/optional-physics.md).

## Runtime and resources

- New workspaces use metric `scale_length=0.001`; API inputs are millimetres and convert to existing metric scenes. Never silently reset an existing scene's units.
- Many mounted assemblies have nominal optical anchor `(0,0,100)` and axis `+X`; bare CAD has no calibrated anchor unless documented. Inspect and measure before placement.
- `load_asset` returns `(collection, record)`. Use `place_asset`, `add_beam`, `add_annotation` and `inspect_scene` through the shared API. `add_annotation` stores metadata only; it does not composite labels.
- For MCP, discover an actually connected Blender tool and use `tools/blender_mcp_entry.py` with its documented request/result properties. Do not assume a tool prefix or infer live transport success from local Python execution.
- `library/Optical_Components.blend` contains individual assemblies, standard parts, functional modules and an empty workspace. The gallery is a resource, not a complete layout template.
- [Coverage](references/system-coverage.md) · [Examples and reproduction](examples/README.md) · [Third-party rights](THIRD_PARTY_NOTICES.md). Publish CAD derivatives only within applicable permission after branding review; authored-code licensing does not relicense manufacturer geometry.
