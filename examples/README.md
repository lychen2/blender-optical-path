# Paper figures and dual-wavelength apparatus

## Generate a paper figure

```bash
blender -b --factory-startup --python-exit-code 1 \
  --python tools/paper_scene.py -- --template beam-relay \
  --output /chosen/new-paper-figure
```

Choose `beam-relay`, `polarimetry` or `microscope`. Defaults are floating optics and Journal Editorial: Cycles glass and metal, soft studio lighting and a shadow-free camera background.

Floating hides mounts, sample frames and supports. Choose `compact` for mounts without supports, or `full` for native assemblies.

Outputs are `figure.blend`, `clean.png`, `annotated.svg` and `scene.json`. Edit component transforms, curve points and **Radius Scale** in the blend. Keep the SVG beside `clean.png` to edit labels.

[Relay preview](../docs/examples/paper-editorial.svg). Reproduce it with `--resolution 1400 --samples 48`. Template beam widths are authored drawing controls.

## Generate the complex dual-wavelength figure

```bash
blender -b --factory-startup --python-exit-code 1 \
  --python examples/dual_wavelength_interferometer.py -- \
  --output /chosen/new-dual-figure
```

The example uses 17 library components, two input channels and two recombined arms. Defaults are `--mode floating --style illustrated`.

The script writes `dual_wavelength_interferometer.blend`, `clean.png`, `annotated.svg`, `layout.json` and `trace.json`. The SVG references the adjacent clean image. Render its labels with:

```bash
rsvg-convert /chosen/new-dual-figure/annotated.svg \
  -o /chosen/new-dual-figure/annotated.png
```

Use `--mode mechanical` for native assemblies. Other styles are `matte`, `soft-lab`, `textbook` and `toon`. The [shading guide](../references/shading-presets.md) describes them.

### OptiCore lenses and source glass

The [complex preview](../docs/examples/dual-editorial.svg) uses OptiCore for four singlet lens meshes. Pass a local checkout:

```bash
blender -b --factory-startup --python-exit-code 1 \
  --python examples/dual_wavelength_interferometer.py -- \
  --opticore /path/to/OptiCore --output /chosen/new-opticore-figure
```

Add `--glass-reference "/path/to/Optical components pack V1.blend"` to use its `Lens` material. Otherwise the script reconstructs the inspected glass recipe.

The adapter loads OptiCore in the current process. It assigns glass separately from geometry. Generated mesh parameters describe the drawing; they do not infer a manufacturer prescription.

See [OptiCore setup and tested revision](../references/opticore.md). The saved blend can reopen without OptiCore because it contains the generated mesh.

## Optical topology and model

Channels labeled 647 nm and 485 nm combine at DM. L1 and L2 form the illustrative expander. P precedes NPBS1. Each arm contains an objective and a following lens, L3 or L4. One arm contains the sample. NPBS2 recombines both arms toward the camera.

The script checks mirror and splitter directions from actual coating normals and neighboring component positions. Purple represents combined channels. The topology has no grating or spectral-dispersion stage.

`paraxial_4f.py` checks normalized thin-lens relations: 1:2 for L1/L2 and 1:1 for each objective/relay pair. Those ratios differ from the RMS10X manufacturer's imaging magnification.

The drawing uses compressed display distances and a finite waist floor. The envelope illustrates illumination, not a ray pencil from one sample point. It does not simulate interference, aberrations or high-NA objective behavior. Run `python examples/paraxial_4f.py` for the independent normalized checks.

## Component provenance

Manufacturer objective geometry retains its reviewed orientation: object side toward the sample, rear port toward the relay lens. The yellow band follows the original ring surface.

Library lens mounts and mirrors retain reviewed native geometry in mechanical mode. OptiCore lenses use authored dimensions and carry generator metadata. Optical surfaces, standard mounts and source assets remain separate.

Laser and camera housings, sample and polarizer modules, and some adapters are nominal. Wavelength labels do not identify verified laser products. NPBS uses a cube-shaped derivative with an unspecified coating. DM spectra remain unspecified.

Breadboard holes and fasteners illustrate mounting. They do not establish thread engagement, clearances or a build-ready instrument.

## Editing and rendering

All default beams are editable Geometry Nodes curves. Change point radii or **Radius Scale** to adjust their width. Labels remain in the separate SVG.

Materials are scene-local copies. Journal Editorial uses the component pack’s glass, metal and housing shaders with Filmic color management. Cylindrical lens edges use rough glass. The reflective floor and curved wall affect lighting but remain invisible to the camera. Inspect lens edges, beam junctions and labels at final size after changing the camera or lighting.
