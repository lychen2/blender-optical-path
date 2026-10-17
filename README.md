# Blender Optical Path

An agent skill for drawing optical setups in Blender. Describe a layout, and the agent draws editable beams, places library components, renders the scene, and adds a separate 2D label layer. You get an editable `.blend`, a text-free render and a labeled SVG.

Typical subjects: imaging and microscopy paths, interferometers, lithography setups.

[中文说明](README.zh-CN.md)

https://github.com/user-attachments/assets/b63bad65-843b-46b2-bf64-ec6e713d0830

![Journal Editorial dual-wavelength optical path with clear glass](docs/examples/dual-editorial.webp)

The dual-wavelength example combines 17 components, editable Geometry Nodes beams and separate SVG labels. The preview uses OptiCore meshes for four clear singlet lenses. The default floating view hides mounts and supports.

[Generate a figure](examples/README.md) · [Editable SVG](docs/examples/dual-editorial.svg) · [Example script](examples/dual_wavelength_interferometer.py)

## Three presentation modes

Paper templates default to `floating`: optical elements and necessary source/detector housings, without mounts or supports. Choose `compact` to retain recognizable mounts, or `full` for native assembly dimensions and supports.

The [dual-wavelength example](examples/dual_wavelength_interferometer.py) retains its `floating` and `mechanical` modes. It depicts 17 components and two illustrative wavelength channels. [Labeled floating view](docs/examples/dual-editorial.svg) · [Mechanical view](docs/examples/mechanical-matte.svg).

## Journal Editorial by default

**Journal Editorial** (`illustrated`, alias `journal-editorial`) combines clear glass, restrained three-tone hardware, fine contours and a white field. Glass follows the inspected component pack's `Lens` material. [Material source](references/style-sources.md#local-component-pack-glass).

[Simple relay SVG](docs/examples/paper-editorial.svg). Purple marks the combined channels. Additional rendering options are described in the [shading guide](references/shading-presets.md).

Recipes and prompts: [shading presets](references/shading-presets.md) · [compact composition](references/compact-floating-prompt.md) · [visual style](references/visual-style.md)

## Workflow

1. Describe the topology, channels and target figure size.
2. Place library components, including reviewed Thorlabs hardware.
3. Draw editable Geometry Nodes beams with authored radii.
4. Apply a style and inspect the rendered composition.
5. Add editable labels in a separate SVG layer.
6. Check scene structure and readability at final size.

Ordinary paper illustrations need no optical prescription. [Quantitative modeling](references/optional-physics.md) is available when the task requires it.

## Install

Requires Blender 5.2 or later; tested with 5.2.2 LTS. For pi:

```bash
git clone https://github.com/lychen2/blender-optical-path.git \
  ~/.pi/agent/skills/blender-optical-path
```

Run `/reload`, then `/skill:blender-optical-path`. For other agents, copy the whole folder into the skill directory and load [`SKILL.md`](SKILL.md).

Example request:

> Draw an editable Michelson interferometer with floating optics, clear glass, narrow colored beam envelopes and a white background. Use a high oblique camera. Add BS, M1, M2 and Detector in a separate SVG.

Include the topology, any known dimensions and the target figure size.

## Defaults

- Labels live in a separate 2D layer, so the 3D render stays text-free and you can edit labels without re-rendering.
- Paper templates use narrow editable beam envelopes with authored point radii. Adjust **Radius Scale** in Geometry Nodes to change their width.

## Python and MCP

Inside Blender:

```python
import runpy
api = runpy.run_path('/path/to/blender-optical-path/tools/optics.py')
scene = api['new_workspace']('Optical diagram')
api['place_asset']('assembly/biconvex_lens', (0, 0, 100),
                   scene=scene, at_optical_center=True)
api['add_beam_nodes']([(-100, 0, 100), (100, 0, 100)], scene=scene)
api['apply_style'](scene)  # Journal Editorial
```

Positions are in millimetres. Generate a complete paper-figure template in a new output directory:

```bash
blender -b --factory-startup --python-exit-code 1 \
  --python tools/paper_scene.py -- --output /chosen/new-figure
```

The directory receives `figure.blend`, `clean.png`, `annotated.svg` and `scene.json`. Templates: `beam-relay`, `polarimetry`, `microscope`. Use `--presentation compact` for mounts without supports, `floating` for optical symbols, or `full` for native assemblies. Use `--style illustrated` for Journal Editorial. Adjust **Radius Scale** in the beam's Geometry Nodes modifier.

`tools/example_scene.py` retains the minimal assembly example. Paper templates require no numerical input.

For OptiCore lens meshes, pass a local checkout to the complex example:

```bash
blender -b --factory-startup --python-exit-code 1 \
  --python examples/dual_wavelength_interferometer.py -- \
  --opticore /path/to/OptiCore --output /chosen/new-dual-figure
```

The adapter loads OptiCore in that Blender process. Glass materials are assigned separately. See [reproduction and source-material options](examples/README.md#opticore-lenses-and-source-glass).

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

Run `tools/check_illustration.py` in Blender for template, style, SVG and optional-entry checks. Run `tools/check_geometry_nodes.py` for editable-beam geometry. Run `python tools/check_optical_model.py` for optional numerical helpers.

`tools/validate_layout.py` checks a saved layout.

## License

Code and documentation are released under the [MIT License](LICENSE). Manufacturer CAD keeps its original terms; see [third-party notices](THIRD_PARTY_NOTICES.md).
