# Python and Blender MCP

Both interfaces execute the same `bpy` functions. There is no dependency on a particular MCP transport or an Internet connection. Run from the Blender Python console, Text Editor, or a background Blender process. Replace `/path/to/blender-optical-path` with the skill directory on the Blender host.

## Python assembly

For an executable example that saves and renders a new scene, run:

```bash
blender -b --factory-startup --python-exit-code 1 \
  --python /path/to/blender-optical-path/tools/example_scene.py -- --output /chosen/new-example
```

The output directory must not already exist. The script writes `example.blend`, `preview.png` and a structural validation report.

```python
import bpy, runpy
api = runpy.run_path('/path/to/blender-optical-path/tools/optics.py')
scene = api['new_workspace']('Imaging diagram')  # creates a new scene; preserves the old scene
print(api['list_assets']('lens'))
lens = api['place_asset']('assembly/biconvex_lens', (0, 0, 100),
                         name='L1', scene=scene, at_optical_center=True)
camera = api['place_asset']('assembly/scientific_camera', (160, 0, 100),
                           rotation_deg=(0, 0, 180), name='Detector',
                           scene=scene, at_optical_center=True)
api['add_beam_nodes']([(-120, 0, 100), (0, 0, 100), (150, 0, 100)], scene=scene)
api['apply_style'](scene)  # Journal Editorial
# Save to a new path after choosing the destination; saving is an explicit action.
# bpy.ops.wm.save_as_mainfile(filepath='/chosen/output/imaging.blend')
```

This example shows placement, not an image-forming prescription. The camera anchor is a nominal assembly reference; inspect the front aperture and sensor if exact path endpoints matter. `rotation_deg` is XYZ Euler rotation in degrees. Coordinates and beam radii are in millimetres and convert automatically into the target scene's unit scale. `new_workspace` uses millimetres. For an existing metric metre-based scene the instance scale becomes `0.001`, without changing pre-existing objects or scene units.

`add_beam_nodes` defaults to a 2 mm radius and returns an editable POLY curve with a Geometry Nodes tube. Pass `radii_mm=[r0, r1, ...]` for one positive finite radius per point. Adjust **Radius Scale** in the modifier or edit the curve points and their radii. The supported profile is `tube`. `opacity` defaults to `.55`. Use authored widths for ordinary illustrations; these drawing controls require no optical model.

`add_beam` retains the older beveled-curve API and its 3 mm default. Both helpers use millimetres. [Optional quantitative tools](optional-physics.md) can supply calculated radii when requested.

## Complete paper templates

```bash
blender -b --factory-startup --python-exit-code 1 \
  --python tools/paper_scene.py -- --template beam-relay \
  --output /chosen/new-figure
```

Templates are `beam-relay`, `polarimetry`, and `microscope`. Journal Editorial is the default style. Presentation defaults to `floating`, which hides mounts, sample frames and supports. Compact mode retains mounts and hides supports. Full mode retains native assembly dimensions. Display scaling and authored beam widths are recorded in the scene. Outputs are `figure.blend`, `clean.png`, `annotated.svg`, and `scene.json`.

Inside Blender, load `tools/paper_scene.py` with `runpy`. Call `build_scene(template='microscope', style='illustrated')` to create a new scene. Call `write_overlay(scene, '/chosen/annotated.svg', image='clean.png')` after camera framing. The SVG references the rendered image and keeps text editable.

For native CAD use `place_asset('thorlabs/LMR1/M', position_mm=(0,0,0))`. `at_optical_center=True` rejects CAD parts without measured anchors. `place_asset` creates a new instance each time; `load_asset` reuses the already imported source collection. No operation clears the scene or silently saves files.

## Post-render annotations

Render components and beams **without names or 3D text**. Add labels to the rendered image in a separate 2D editor or compositor. Gallery captions are not part of the component assets.

`add_annotation('L1', position_mm=(0,0,100), scene=scene)` optionally records intent in the scene's `opl_post_render_annotations` JSON property. It creates no visible object. The position is a world-space anchor in millimetres, not a pixel position; `size_mm` is a legacy size hint, not a rendered font size. Choose final pixel positions and font sizes after rendering. The compatibility name `add_label` now has the same metadata-only behavior. Neither function renders or composites an overlay. The paper-template `write_overlay` helper projects these anchors into editable SVG text. Inspect label positions at final size.

## MCP

The common [Blender MCP](https://github.com/ahujasid/blender-mcp) exposes Python execution, scene inspection and viewport capture. Discover the actual tools on the connected server; prefixes and schemas vary. Use the code field of its Python execution tool:

```python
import bpy, json, runpy
bpy.context.scene['OPL_MCP_REQUEST'] = json.dumps({
    'action': 'add_component',
    'asset_id': 'assembly/kinematic_mirror',
    'position_mm': [100, 0, 100],
    'rotation_deg': [0, 0, 45],
    'at_optical_center': True,
    'name': 'M1'
})
runpy.run_path('/path/to/blender-optical-path/tools/blender_mcp_entry.py')
print(bpy.context.scene.get('OPL_MCP_RESULT'))
```

The request property and response JSON avoid reliance on shell quoting. For `new_workspace` the result is written to the original scene where the request was set; the returned scene name identifies the newly active scene. For more complex placement, directly execute the Python example instead of using the wrapper. Run on Blender's main thread.

| Action | Input fields | Result |
| --- | --- | --- |
| `list_assets` | Optional `query` | Matching index records |
| `inspect` / `validate` | None | Scene inventory / structural checks |
| `new_workspace` | Optional `name` | New millimetre scene name |
| `add_component` | `asset_id`, optional `position_mm`, `rotation_deg`, `name`, `at_optical_center` | Created object name |
| `add_beam` | `points_mm`, optional `radius_mm` (default 3 mm), `radii_mm`, `color`, `name` | Created beam object name |
| `add_annotation` | `text`, optional `position_mm`, `size_mm` | Post-render annotation record; no 3D text |
| `add_beam_nodes` | `points_mm`, optional `radius_mm`, `radii_mm`, `color`, `name`, `profile`, `opacity` | Editable Geometry Nodes beam |
| `list_styles` | None | Available recipes and default |
| `apply_style` | Optional `style` | Applied scene-local recipe |
| `build_template` | Optional `template`, `style`, `presentation`, `resolution` | New scene inventory |
| `export_overlay` | `output`, optional `image` | SVG path; writes the requested file |
| `add_lens`, `align_component`, `add_gaussian_beam` | `parameters` matching the function in `tools/advanced.py` | Geometry, alignment residuals, or calculated envelope |
| `calculate` | `function`, `parameters` matching `tools/optical_model.py` | Optional numerical result |

For `calculate`, available functions are `gaussian_beam`, `abcd_system`, `trace_paraxial_ray`, `waveplate`, `polarizer`, `stokes`, and `fresnel`. JSON represents each complex Jones component as `[real, imaginary]`; waveplate and polarizer results use the same representation.

For `build_template`, the result stays on the requesting scene, while Blender activates the newly created scene. Subsequent actions operate on that active scene.

Mutating calls are not idempotent: inspect the result after a timeout before retrying, so repeated MCP calls do not create duplicate components. Exceptions set an error result and propagate to the MCP tool. Native scene operations remain available for moving, rotating and deleting specific instances.

A local path must be accessible to the Blender process. If the MCP server runs on another computer, install the entire skill folder there and use that host's path. Do not put large mesh arrays into a tool request; append the bundled `.blend` collection through `optics.py`.

## Validation and rendering

```bash
blender -b /chosen/output/imaging.blend --python-exit-code 1 \
  --python /path/to/blender-optical-path/tools/validate_layout.py
```

Check a viewport capture or render after construction. The structural validator checks units, finite transforms, visible source collections, absence of 3D text (including collection instances) and nonzero beam segments. It does not prove optical alignment, valid imaging conjugates, collision clearance, or absence of unknown embedded branding. Verify those visually and against the specified design.

Runtime compatibility is verified with Blender's Python execution path. A live MCP transport test requires a connected server; the package does not configure or start a server itself.
