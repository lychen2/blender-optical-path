# Optional physical modeling and upstream tools

Ordinary conceptual illustrations do not require optical modeling. Add quantitative physics only when requested, with suitable inputs, executed checks and explicit model limits. The local parametric lens helper is not an optical prescription, and a numerical helper's presence does not mean a calculation was performed.

## Local optional capabilities

- `tools/advanced.py` provides `add_lens` for sampled conic/aspheric geometry and `add_gaussian_beam` for calculated Gaussian envelopes. Its lens geometry does not infer a manufacturer prescription, focal length or aberrations. Display scaling/floor parameters are separate from the calculated beam model.
- `tools/optical_model.py` provides ideal scalar paraxial/ABCD and Gaussian-beam calculations, paraxial ray tracing, ideal Jones waveplate/polarizer/Stokes operations, and lossless isotropic dielectric Fresnel coefficients. Its declared limits include homogeneous air, ideal thin lenses and no coatings, absorption, apertures, aberrations, vector focusing or measured component prescriptions. It is not a Blender (`bpy`) module.
- `tools/geometry_nodes.py` `add_beam_nodes` creates editable tube-beam geometry with artist-authored radii and interactive `Radius Scale`; it is not a physics solver.

## Calculate an ideal beam without Blender

Load the numerical module with ordinary Python. Lengths are millimetres; wavelengths are nanometres.

```python
import runpy
model = runpy.run_path('/path/to/blender-optical-path/tools/optical_model.py')
result = model['gaussian_beam'](
    wavelength_nm=500, waist_mm=.1, waist_position_mm=0,
    elements=[{'position_mm': 100, 'focal_length_mm': 50}],
    end_mm=200, samples=81)
print(result['checkpoints'])
```

Each sample contains position, radius, curvature and Gouy angle. Lens checkpoints contain values before and after each lens. Infinite curvature uses `None`. Elements must be sorted within the waist-to-end interval.

`abcd_system(elements, start_mm, end_mm)` returns a 2×2 matrix. `trace_paraxial_ray(height_mm, angle_rad, elements, start_mm, end_mm)` returns propagation checkpoints. Jones helpers accept two complex amplitudes. `fresnel(n1, n2, incidence_deg)` returns power coefficients and the total-internal-reflection state.

## Add geometry or align an explicit axis in Blender

```python
import runpy
advanced = runpy.run_path('/path/to/blender-optical-path/tools/advanced.py')
lens = advanced['add_lens'](
    diameter_mm=25.4, thickness_mm=6,
    radius1_mm=40, radius2_mm=-40,
    conic1=-1, asphere1=[1e-6], scene=scene)
residuals = advanced['align_component'](
    lens.name, target_mm=(0, 0, 100), toward_mm=(100, 0, 100),
    local_axis=(1, 0, 0), local_anchor_mm=(0, 0, 0), scene=scene)
```

Create `scene` with the [shared API](python-mcp.md). Lens geometry uses local axis `+X`. Surface radii are signed; `None` creates a plane. Aspheric coefficients start at A4, then A6; A4 has units mm⁻³.

Alignment uses an explicit native-coordinate anchor and local axis. Align a root object; the helper preserves scale and reports anchor and angular residuals. Library collection instances use their documented native-millimetre anchors. User geometry needs an anchor in its own local coordinates.

`add_gaussian_beam` accepts the numerical beam inputs plus `origin_mm`, `direction`, `display_radius_scale` and `display_floor_mm`. The origin defines longitudinal coordinate zero. The returned object stores calculated results and display settings separately. It uses the legacy beveled curve; authored paper-template beams use Geometry Nodes.

## Upstream emulator: blender-optics-simulator

Repository: [emircbngl/blender-optics-simulator](https://github.com/emircbngl/blender-optics-simulator), version `v0.31.0`. Its documented facade is `optical_alignment_sim/optics_api.py`, with functions `build_example`, `get_state`, `inspect_beam`, `set_param`, `trace_beam`, and `render`. The project describes a Blender optical-alignment simulator; the facade/API and repository's scope are upstream claims, not verified behavior here. Project-reported counts of 341/618 are not a test suite result and must not be represented as one. License: GPL-3.0-or-later. This skill does not bundle or install it, and no adapter is promised.

## Upstream OptiCore

Repository: [CodeFHD/OptiCore](https://github.com/CodeFHD/OptiCore), version `2.0`. Repository metadata reports Blender `4.2.5`; its README reports testing with Blender `4.2.1` (these are different version claims). License: GPL-3.0-or-later. It documents operator-oriented workflows rather than a stable public API for this skill. No bundling, installation, compatibility guarantee or adapter is promised.

## Use and reporting

Before relying on any external addon, verify its present version, license compatibility, Blender/runtime compatibility, installation and behavior in the actual environment. Do not install it without explicit authorization. Do not claim plugin installation, tests, integration or API behavior unless verified. Keep optional models and upstream projects out of the default conceptual illustration path.
