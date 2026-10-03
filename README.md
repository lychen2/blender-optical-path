# Blender Optical Path

An agent skill for building **editable optical-path figures in Blender**: define the topology, align components, choose a visual direction, render a clean scene, and annotate the image in 2D.

Use it for imaging, microscopy, interferometry and lithography illustrations. Work through Blender Python, a connected Blender MCP server, or manual assembly. Local components support the workflow; the deliverable is your optical figure, not a catalog of parts.

![Compact floating optical layout with component labels](docs/examples/floating-matte.webp)

**Example: dual-wavelength optical apparatus.** Seventeen library components, reviewed RMS10X objective geometry, three positive-positive 4f groups and separate 2D labels. Beam envelopes follow a normalized paraxial illumination model with illustrative ratios; the objective housings do not supply an internal optical prescription. Spacing, nominal coatings and adapters do not constitute a build-ready design.

[Reproduce and inspect the model](examples/README.md) · [Editable labeled SVG](docs/examples/floating-matte.svg) · [Assembly script](examples/dual_wavelength_interferometer.py)

## Floating or mechanical

The same topology supports compact floating optics or mounted apparatus views. Floating mode enlarges optical symbols and compresses spacing; mechanical mode retains native component dimensions. These are presentation comparisons, not dimensional overlays.

| Floating optics — default | Mechanical assembly |
| --- | --- |
| ![Floating optical elements](docs/examples/floating-matte.webp) | ![Mounted apparatus](docs/examples/mechanical-matte.webp) |

[Full-size mechanical figure](docs/examples/mechanical-matte.webp) · [Editable mechanical SVG](docs/examples/mechanical-matte.svg)

## Five shading choices

The floating views below hold component placement, camera and channel colors fixed. Materials and lighting change; labels remain separate 2D artwork. Purple denotes the combined channels, not a third wavelength. The image-plane marker denotes a conjugate plane; the depicted collimated illumination does not focus there. The axial offset z is illustrative and unnumbered.

| Style | Preview |
| --- | --- |
| **Matte Technical** — restrained metal and readable glass | ![Matte Technical](docs/examples/floating-matte.webp) |
| **Soft Lab** — dark field and softly illuminated paths | ![Soft Lab](docs/examples/floating-soft-lab.webp) |
| **Illustrated Geometry** — warm soft shading and translucent cyan splitters | ![Illustrated Geometry](docs/examples/floating-illustrated.webp) |
| **Textbook White** — flat white field and thin black component edges | ![Textbook White](docs/examples/floating-textbook.webp) |
| **Cel / Toon** — stepped shading and selective cyan/gray contours | ![Cel shading](docs/examples/floating-toon.webp) |

[Material recipes and prompts](references/shading-presets.md) · [Compact composition prompt](references/compact-floating-prompt.md). Every preview links to a local file; editable SVGs with the same basenames are in `docs/examples/`.

![Six-step workflow: understand, clarify once, model the optics, assemble, style and preview, verify and deliver](docs/workflow.svg)

[Editable workflow diagram](docs/workflow.excalidraw) — import into [Excalidraw](https://excalidraw.com).

## Install and start

Requires **Blender 5.2+**; checked with 5.2.2 LTS. Clone this repository into your agent's skill directory. For Pi:

```bash
git clone https://github.com/lychen2/blender-optical-path.git \
  ~/.pi/agent/skills/blender-optical-path
```

Run `/reload`, then invoke `/skill:blender-optical-path`. For another agent, install the **whole folder** in its skill directory and load [`SKILL.md`](SKILL.md). Keep the scripts and bundled resources together. The local workflow needs no network access; Blender MCP requires a separately connected server.

Example request:

> Draw an editable Michelson interferometer. Use a simplified 3D schematic with a high oblique camera, thick colored beam bodies, a white background and matte mounts. Render without text; add BS, M1, M2 and Detector in a separate 2D overlay afterward.

Specify the topology, known dimensions and intended figure size. If exact optics are unknown, the skill should preserve that uncertainty rather than invent an optical prescription.

## Choose the mechanical detail

The skill defaults to **floating optics**. It asks a consolidated set of questions only when unresolved optical or style choices materially change the result:

| Mode | What appears |
| --- | --- |
| Full mechanical assembly | Optical components with mounts, posts, holders, bases and fork clamps; suited to apparatus layouts |
| Floating optics | Optical surfaces without support hardware, retaining recognizable laser/objective/camera housings where useful; suited to compact conceptual views |

A real-setup request uses full mechanical assembly. Source CAD and mechanical dimensions are preserved; floating views may uniformly enlarge display copies and use shorter schematic spacings. Mechanical detail alone does not make an optical design build-ready. Visibility and material edits operate on scene-local copies.

## How the skill works

1. **Understand.** Read the reference and establish topology, ports, direction and physical versus display coordinates.
2. **Clarify once.** Resolve remaining optical and style decisions in one prepared batch; record the agreed brief.
3. **Model the optics.** Calculate conjugates and beam envelopes from the agreed model. Save inputs, numerical checkpoints and assumptions.
4. **Assemble.** Place reviewed components by measured or documented references. Preserve native CAD dimensions; check coating normals, objective direction and seating. Record floating display transforms separately.
5. **Style and preview.** Choose role-based materials, lighting and camera. Inspect a small render without text. When feedback reveals a recurring issue, update the shared rule, prompt and implementation together.
6. **Verify and deliver.** Check optical validity, assembly and final-size labels independently. Add a separate editable 2D overlay; deliver the `.blend`, clean render, assembly script and model checkpoints.

**No names beside components in the 3D render.** Outliner names and provenance remain metadata. Browsing captions are separate from component assets. `add_annotation` records post-render intent; it does not create a text object or composite an overlay.

## Visual direction, not one default look

Choose a distinct anchor for each new figure. These are art-direction references, not claims of journal endorsement or automatic render presets.

| Anchor | Useful visual choices |
| --- | --- |
| Nature Photonics-inspired editorial figure | Compact composition, restrained palette, clear spatial hierarchy and generous space for 2D labels |
| Simplified 3D schematic | Orthographic view, matte surfaces, thick beam bodies and limited mechanical detail |
| Blender Cycles studio render | Physically based surfaces, broad soft illumination, controlled glass reflections and subtle contact shadows |
| Technical axonometric | Precise silhouettes, desaturated hardware, directional path cues and minimal depth effects |

**Beams are thick by default; thin single-line paths require an explicit user request.** Choose a visibly wide colored body, translucent ribbon, broad beam envelope or restrained scattering cone without adding automatic glow or fog. Some require additional geometry or materials; the bundled beam helper creates a curve, not a volume simulation.

For successive figures, vary **light direction, background treatment and material emphasis**. For related panels, keep component names, abbreviations, beam-channel colors and optical meaning consistent, while assigning each panel a distinct visual change. Approved user or venue constraints take precedence over variation.

The [visual-style guide](references/visual-style.md) gives reusable briefs, controlled variation rules and review criteria. [Optical preflight](references/optical-preflight.md) and [release checks](references/release-checks.md) require geometry-derived port checks, conjugate reasoning and final-size visual inspection. Record choices beside the assembly script so revisions can reproduce them.

## Build through Python or MCP

Inside Blender:

```python
import runpy
api = runpy.run_path('/path/to/blender-optical-path/tools/optics.py')
scene = api['new_workspace']('Optical diagram')
api['place_asset']('assembly/biconvex_lens', (0, 0, 100),
                   scene=scene, at_optical_center=True)
api['add_beam']([(-100, 0, 100), (100, 0, 100)], scene=scene)
```

Positions are millimetres. The API converts into the target metric scene without changing its units, preserves existing scenes, and does not save automatically. Bare CAD has no calibrated optical anchor; inspect its aperture before aligning it.

For a minimal placement example, run from the skill directory:

```bash
blender -b --factory-startup --python-exit-code 1 \
  --python tools/example_scene.py -- --output /chosen/new-example
```

This writes an editable scene, a text-free PNG and a structural report into a **new** directory. It uses a simple Workbench preview, not a finished optical prescription or an implementation of every style above.

Blender MCP executes the same API or the JSON wrapper in `tools/blender_mcp_entry.py`. The package does not start an MCP server. [API and MCP reference](references/python-mcp.md).

## Component resources

The bundled `.blend` contains 70 reusable assets: mounted assemblies, manufacturer CAD and schematic accessories. Open `library/Optical_Components.blend` to browse, or place components through the API. Bundled parts work offline.

- [Manual assembly and coordinates](references/manual.md)
- [System coverage and limits](references/system-coverage.md)
- [Missing parts: official CAD search and reviewed cleanup](references/thorlabs-workflow.md)

Geometry categories and source records are retained in `library/index.json` and `library/provenance`. Native CAD, mixed assemblies and nominal schematic modules are distinguished. Manufacturer-derived geometry is a supporting resource, not a new optical specification. No original STEP files are included.

## Check and deliver

```bash
blender -b --factory-startup --python-exit-code 1 \
  --python tools/check_package.py
```

Checks cover inventory, supports, fresh appending, metric placement, invalid input rejection, the MCP Python wrapper and the text-free scene rule. Output goes to the terminal rather than the library. Use `tools/validate_layout.py` for a saved layout, then inspect the render.

Structural checks do not prove optical alignment, collision clearance or freedom from unknown mesh-embedded markings. The skill does not simulate diffraction, interference or image formation. Live MCP transport is not covered by the local checks.

## License and assets

Authored code, documentation and workflow illustrations use the [MIT License](LICENSE). Manufacturer-derived geometry is excluded from that license and retains its original rights. See [third-party notices](THIRD_PARTY_NOTICES.md). Publish or transfer CAD only within the applicable permission and only after reviewing derivatives for unwanted branding and model inscriptions.
