# Blender Optical Path

An agent skill for drawing optical setups in Blender. Describe a layout, and the agent models the beam path, places and aligns the components, renders the scene, and adds labels in a separate 2D layer. You get an editable `.blend`, a text-free render and a labeled SVG.

Typical subjects: imaging and microscopy paths, interferometers, lithography setups.

[中文说明](README.zh-CN.md)

https://github.com/user-attachments/assets/b63bad65-843b-46b2-bf64-ec6e713d0830

![Compact floating optical layout with component labels](docs/examples/floating-matte.webp)

The example is a dual-wavelength apparatus built from 17 library components. Two channels (647 nm and 485 nm) merge at a dichroic mirror, split into two objective arms, and recombine before the camera.

[Reproduce the example](examples/README.md) · [Editable labeled SVG](docs/examples/floating-matte.svg) · [Assembly script](examples/dual_wavelength_interferometer.py)

## Two views

Floating optics is the default: optical elements without mounts, enlarged and placed closer together for a compact figure. Mechanical assembly shows the full hardware at native CAD dimensions.

| Floating optics | Mechanical assembly |
| --- | --- |
| ![Floating optical elements](docs/examples/floating-matte.webp) | ![Mounted apparatus](docs/examples/mechanical-matte.webp) |

[Editable mechanical SVG](docs/examples/mechanical-matte.svg)

## Five shading styles

Same layout and camera, different materials and lighting. Purple marks the combined beam.

| Style | Preview |
| --- | --- |
| **Matte Technical**: restrained metal, readable glass | ![Matte Technical](docs/examples/floating-matte.webp) |
| **Soft Lab**: dark field, softly lit beams | ![Soft Lab](docs/examples/floating-soft-lab.webp) |
| **Illustrated Geometry**: warm soft shading, translucent cyan splitters | ![Illustrated Geometry](docs/examples/floating-illustrated.webp) |
| **Textbook White**: white field, thin black edges | ![Textbook White](docs/examples/floating-textbook.webp) |
| **Cel / Toon**: hard light/shadow bands, bright beam cores, bold ink | ![Cel shading](docs/examples/floating-toon.webp) |

Recipes and prompts: [shading presets](references/shading-presets.md) · [compact composition](references/compact-floating-prompt.md) · [visual style](references/visual-style.md)

## Workflow

![Six-step workflow: understand, clarify once, model the optics, assemble, style and preview, verify and deliver](docs/workflow.svg)

1. **Understand**: read the request and work out the topology and beam path.
2. **Clarify once**: ask any open questions together, in a single round.
3. **Model the optics**: compute conjugate planes and beam envelopes.
4. **Assemble**: place and align components from the bundled library.
5. **Style and preview**: choose a shading style and check a small preview.
6. **Verify and deliver**: check the result and export the files.

[Editable workflow diagram](docs/workflow.excalidraw) (opens in [Excalidraw](https://excalidraw.com))

## Install

Requires Blender 5.2 or later; tested with 5.2.2 LTS. For pi:

```bash
git clone https://github.com/lychen2/blender-optical-path.git \
  ~/.pi/agent/skills/blender-optical-path
```

Run `/reload`, then `/skill:blender-optical-path`. For other agents, copy the whole folder into the skill directory and load [`SKILL.md`](SKILL.md).

Example request:

> Draw an editable Michelson interferometer. Use a simplified 3D schematic with a high oblique camera, thick colored beam bodies, a white background and matte mounts. Render without text; add BS, M1, M2 and Detector in a separate 2D overlay afterward.

Include the topology, any known dimensions and the target figure size.

## Defaults

- Labels live in a separate 2D layer, so the 3D render stays text-free and you can edit labels without re-rendering.
- Beams are drawn as thick colored bodies. Ask if you want thin lines.

## Python and MCP

Inside Blender:

```python
import runpy
api = runpy.run_path('/path/to/blender-optical-path/tools/optics.py')
scene = api['new_workspace']('Optical diagram')
api['place_asset']('assembly/biconvex_lens', (0, 0, 100),
                   scene=scene, at_optical_center=True)
api['add_beam']([(-100, 0, 100), (100, 0, 100)], scene=scene)
```

Positions are in millimetres. To try a minimal scene from the command line, pass a new output directory:

```bash
blender -b --factory-startup --python-exit-code 1 \
  --python tools/example_scene.py -- --output /chosen/new-example
```

The directory receives the `.blend`, a PNG preview and a short report.

With a Blender MCP server connected, `tools/blender_mcp_entry.py` runs the same API from JSON requests. See the [API and MCP reference](references/python-mcp.md).

## Component library

`library/Optical_Components.blend` holds 70 components: 24 mounted assemblies, 18 manufacturer CAD parts and 28 schematic modules. Open it to browse, or place parts by id through the API. Part ids and sources are listed in `library/index.json` and `library/provenance/`.

- [Manual assembly](references/manual.md)
- [Supported systems](references/system-coverage.md)
- [Adding a part from official CAD](references/thorlabs-workflow.md)

## Package checks

```bash
blender -b --factory-startup --python-exit-code 1 \
  --python tools/check_package.py
```

`tools/validate_layout.py` checks a saved layout.

## License

Code and documentation are released under the [MIT License](LICENSE). Manufacturer CAD keeps its original terms; see [third-party notices](THIRD_PARTY_NOTICES.md).
