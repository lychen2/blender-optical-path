# Dual-wavelength apparatus: presentation and shading

The example uses 17 shared-library instances and renders two presentation modes and five shading schemes. Default: compact floating optics, Matte Technical materials. The mechanical view retains native parts; floating mode uses shorter display distances and larger optical symbols. All names and the image-plane/z markers are added afterward in a 2D SVG.

## Reproduce

From the skill directory, choose a new output directory for each render:

```bash
blender -b --factory-startup --python-exit-code 1 \
  --python examples/dual_wavelength_interferometer.py -- \
  --mode floating --style matte --output /chosen/floating-matte
python examples/annotate_reference.py /chosen/floating-matte /chosen/floating-matte/annotated.svg
rsvg-convert /chosen/floating-matte/annotated.svg -o /chosen/floating-matte/annotated.png
```

`--mode` accepts `floating` (default) or `mechanical`. `--style` accepts `matte` (default), `soft-lab`, `illustrated`, `textbook`, or `toon`. The checked renderer is Blender 5.2.2 Cycles, including its Toon BSDF and Freestyle. Textbook component edges and Illustrated splitter edges require a Blender build with Freestyle support. Use `--mode mechanical --style matte` for the mounted comparison. Run each floating style with unchanged topology and framing for a material comparison.

The script writes `.blend`, `clean.png`, `layout.json` and `trace.json`. The SVG generator embeds its raster and supports an optional `--raster image.webp` for smaller files. Export with `rsvg-convert` or a graphics editor. Do not add intermediate renders, test reports or generated `.blend` copies to the package.

## Optical model and scope

Two channels labeled 647 nm and 485 nm combine at DM. Positive L1 focuses the input; positive L2 recollimates the expanded beam. P precedes NPBS1. The two arms each include an objective and a following positive lens, L3/L4; one arm includes the illuminated specimen. NPBS2 recombines them coaxially toward the camera. The two mirror/splitter paths are checked using normals measured from the actual coating geometry and directions derived from placed neighbors, including the transmitted path from L4 into the camera.

`paraxial_4f.py` verifies normalized ideal thin-lens models. The user-approved illustrative ratios are 1:2 for L1/L2 and 1:1 for each objective/relay pair; these are not the RMS10X imaging magnification. Checks cover the common internal focus, collimated output, beam expansion and the plane-to-plane relay matrix. Run `python examples/paraxial_4f.py` independently. The drawing depicts the illumination envelope, not the ray pencil from one specimen point. A conjugate image-plane marker therefore does not create a focus of the displayed collimated illumination. The camera z offset is unspecified.

The normalized optical coordinates and display coordinates are different. Focal-plane order and beam action are retained, but displayed millimetre spacings are not a lens prescription. The objective-front direction stays toward the specimen. Its manufacturer CAD provides the external shape, not its internal powers, principal planes or high-NA behavior. The ideal two-lens model is an illustrative relation; it does not establish that these housings, distances and a particular tube lens realize a corrected instrument. Both wavelengths use ideal achromatic powers. The finite drawn waist is a display floor, not a diffraction calculation. No fringe pattern, propagation of a specimen field or aberration performance is simulated.

Purple represents the combined channels, not a new wavelength. This topology contains no grating; no dispersion is added. Off-axis tracing applies only when explicitly specified or required by evidence; this example is coaxial within each arm and at recombination.

## Component provenance and mechanics

- The mounted spherical lenses use reviewed KM100 geometry, with the lens bore centered and the correct edge side seated against the annular stop. Native parts are not stretched. The nominal biconcave asset can protrude beyond the pocket; retaining force and compatibility are not certified. This example uses positive lenses only.
- Mirrors use reviewed POLARIS-K1S5 geometry with measured bottom faces seated on native TR50/M posts. M4 socket-head screws are nominal geometry; thread engagement/torque remain unverified.
- Horizontal and vertical objective assets now use reviewed RMS10X manufacturer derivatives. The yellow magnification band colors the original ring surface. No substitute objective barrel is modeled. Adapter plates and the vertical focus stand remain nominal.
- Laser/camera housings, specimen/polarizer modules and some adapters are nominal. Wavelength labels do not identify verified laser products. NPBS geometry reuses the cube shape with an explicitly nominal non-polarizing coating; it is not a claim that a PBS coating is non-polarizing. DM transmission/reflection spectra remain unspecified.
- The breadboard grid is illustrative, not a verified bolt-hole plan. The cylindrical-lens and tube-lens modules retain their distinct nominal housings; they are not silently squeezed into a one-inch mount. Additional stages, unused-port termination, enclosures and an actual instrument prescription require separate design work.

## Rendering boundaries

Materials are copied locally. Textbook White uses flat colors on true white with thin black component edges; beams have no outline. Illustrated retains warm paper and continuous soft shading, with subtle cyan edges on its splitter cubes. Both styles show the internal beam junction through a translucent shell and a stronger film, with no refraction. The current per-surface opacity factors are 0.09/0.24 (shell/film) for Textbook and 0.26/0.34 for Illustrated; overlapping surfaces compound opacity, and these values do not represent physical transmission or splitting ratios. Illustrated edge ramps exclude ordinary glass, beams and RMS objective barrels. Cel shading uses restrained hardware/cyan contours without black beam outlines. Labels are dark on light fields and light on the dark variant. Library CAD, optical layout and channel meanings do not change between styles. The package checker verifies scene structure, native components, selected seating interfaces and APIs; it does not certify the complete optical or mechanical design.
