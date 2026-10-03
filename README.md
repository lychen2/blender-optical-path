# Blender Optical Path

An agent skill for building **editable optical-path figures in Blender**: define the topology, align components, choose a visual direction, render a clean scene, and annotate the image in 2D.

Use it for imaging, microscopy, interferometry and lithography illustrations. Work through Blender Python, a connected Blender MCP server, or manual assembly. Local components support the workflow; the deliverable is your optical figure, not a catalog of parts.

![Optical figure workflow](docs/workflow.svg)

[Editable workflow diagram](docs/workflow.excalidraw) — import into [Excalidraw](https://excalidraw.com).

## Install and start

Requires **Blender 5.2+**; checked with 5.2.2 LTS. Clone this repository into your agent's skill directory. For Pi:

```bash
git clone https://github.com/lychen2/blender-optical-path.git \
  ~/.pi/agent/skills/blender-optical-path
```

Run `/reload`, then invoke `/skill:blender-optical-path`. For another agent, install the **whole folder** in its skill directory and load [`SKILL.md`](SKILL.md). Keep the scripts and bundled resources together. The local workflow needs no network access; Blender MCP requires a separately connected server.

Example request:

> Draw an editable Michelson interferometer. Use a simplified 3D schematic with a high oblique camera, thin colored beam paths, a white background and matte mounts. Render without text; add BS, M1, M2 and Detector in a separate 2D overlay afterward.

Specify the topology, known dimensions and intended figure size. If exact optics are unknown, the skill should preserve that uncertainty rather than invent an optical prescription.

## How the skill works

1. **Define the path.** Establish component order, beam branches, input/output ports and known optical constraints.
2. **Assemble and align.** Place components by measured or documented references. Keep standard CAD at native dimensions; verify mirror normals and aperture orientation.
3. **Choose a visual direction.** Select a style anchor, camera, beam treatment, lighting, background and material emphasis. Prefer readable geometry over decorative effects.
4. **Render without text.** Keep component names, panel letters and callouts out of the 3D scene. Check the render for blocked paths, floating parts and unwanted inscriptions.
5. **Annotate in 2D.** Add labels to the rendered image in a separate editable overlay. Deliver the `.blend`, clean render, assembly script and annotated figure when requested.

**No names beside components in the 3D render.** Outliner names and provenance remain metadata. Browsing captions are separate from component assets. `add_annotation` records post-render intent; it does not create a text object or composite an overlay.

## Visual direction, not one default look

Choose a distinct anchor for each new figure. These are art-direction references, not claims of journal endorsement or automatic render presets.

| Anchor | Useful visual choices |
| --- | --- |
| Nature Photonics-inspired editorial figure | Compact composition, restrained palette, clear spatial hierarchy and generous space for 2D labels |
| Simplified 3D schematic | Orthographic view, matte surfaces, thin beam paths and limited mechanical detail |
| Blender Cycles studio render | Physically based surfaces, broad soft illumination, controlled glass reflections and subtle contact shadows |
| Technical axonometric | Precise silhouettes, desaturated hardware, directional path cues and minimal depth effects |

Do not reuse “glowing volumetric” for every beam. Choose the actual representation: a thin colored path, translucent ribbon, narrow luminous core, sparse ray bundle or a restrained scattering cone. Some require additional geometry or materials; the bundled beam helper creates a curve, not a volume simulation.

For successive figures, vary **light direction, background treatment and material emphasis**. For related panels, keep component names, abbreviations, beam-channel colors and optical meaning consistent, while assigning each panel a distinct visual change. Approved user or venue constraints take precedence over variation.

The [visual-style guide](references/visual-style.md) gives reusable briefs, controlled variation rules and review criteria. Record choices beside the assembly script so revisions can reproduce them.

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
