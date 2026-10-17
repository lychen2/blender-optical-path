# Generate clear lenses with OptiCore

Use OptiCore when a figure needs a custom lens mesh. Keep library CAD for manufacturer housings and standard parts.

The adapter loads a local checkout in the current Blender process. It does not change Blender preferences or install the add-on globally.

## Reproduce the complex example

Get the tested revision in a directory you control:

```bash
git clone https://github.com/CodeFHD/OptiCore.git /chosen/OptiCore
git -C /chosen/OptiCore checkout f9b0029009846abbf34a0947971dc4c6ba1a21f6
```

From the skill directory, choose a new output directory:

```bash
blender -b --factory-startup --python-exit-code 1 \
  --python examples/dual_wavelength_interferometer.py -- \
  --opticore /chosen/OptiCore --output /chosen/new-dual-figure
```

The example generates four biconvex singlets with OptiCore. Manufacturer objective housings retain their library geometry and reviewed orientation. Beams remain editable Geometry Nodes curves.

Add `--glass-reference "/path/to/Optical components pack V1.blend"` to load its `Lens` material. Without that option, the script reconstructs the inspected shader parameters.

Outputs include the editable `.blend`, `clean.png`, `annotated.svg`, `layout.json` and `trace.json`. Keep the SVG beside `clean.png` when editing labels.

## Use the adapter inside Blender

```python
import runpy
adapter = runpy.run_path('/path/to/blender-optical-path/tools/opticore_geometry.py')
lens = adapter['add_opticore_lens'](
    '/chosen/OptiCore', position_mm=(0, 0, 100),
    diameter_mm=25.4, thickness_mm=6,
    radius1_mm=50, radius2_mm=-50, scene=scene)
api['apply_style'](scene)  # Journal Editorial assigns clear glass.
```

Make the target scene active and use Object mode. The adapter centers the generated mesh, uses local axis +X and converts millimetres to scene units.

These dimensions describe an authored drawing mesh. Replace them with a supplied prescription when optical design is required.

## Geometry and material have separate controls

OptiCore generates surface geometry. Its operator's optical IOR setting does not configure a render material.

Journal Editorial assigns a Principled shader with transmission 1, IOR 1.5, roughness 0.1 and the source's near-white base color. Reflections and refraction reveal the glass shape. Fine contours help edges remain visible on white. Hardware uses restrained face tones.

Inspect the final image after changing camera, light or background. Shader values alone do not determine the rendered appearance.

## Tested boundary

Revision `f9b0029009846abbf34a0947971dc4c6ba1a21f6` generated spherical singlets in Blender 5.2.2 LTS without upstream edits. Checks covered dimensions, biconvex sag, closed edges, millimetre conversion and clear-glass assignment.

Run the optional integration check against the same checkout:

```bash
blender -b --factory-startup --python-exit-code 1 \
  --python tools/check_opticore.py -- --checkout /chosen/OptiCore
```

Other OptiCore operators, doublets, triplets, Zemax import and ray fans have not been exercised by this adapter.

OptiCore is by Johannes Hinrichs (CodeFHD), licensed GPL-3.0-or-later. Its source is fetched separately; see [third-party notices](../THIRD_PARTY_NOTICES.md).
