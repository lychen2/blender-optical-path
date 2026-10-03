# Offline system coverage

All entries below use the 70 bundled assets. No network request is needed to draw them. These are component selection guides, not immutable optical-layout templates. Select the required parts and place them individually in the blank workspace. Only a missing specified manufacturer model requires retrieval.

| System | Bundled component choices | Conditions to supply |
| --- | --- | --- |
| Imaging / relay / Fourier plane | Laser or LED source, iris, achromat, convex/concave/cylindrical lens, tube lens, lens tube, cage, spatial-filter pinhole, camera | Focal lengths, spacing and object/image planes; lens meshes are visual geometry, not a paraxial prescription |
| Bright-field microscopy | LED, condenser, sample slide, XY stage, vertical or horizontal objective, tube lens, camera | Magnification, objective conjugate type, NA, working distance and tube-lens pairing |
| Epi/fluorescence microscopy | LED or laser, bandpass filters, dichroic or epi cube, objective, sample stage, emission filter, camera | Actual excitation/emission bands and dichroic orientation; generic filters have no measured spectral response |
| Michelson / Mach–Zehnder / polarization interferometry | Source, beam expander, mirrors, plate or cube splitter, PBS, wave plates, polarizer, delay stage, retroreflector, camera or detector | Arm topology, path lengths, normals, polarization and phase; no interference computation is included |
| Contact / projection / modulator lithography | UV source, shutter, expander/condenser, photomask, objective/tube lens, wafer chuck, XY stage, SLM/DMD, scanner | Illumination wavelength, projection geometry, mask/wafer plane, dose and motion parameters; this is an illustration library, not an exposure system design |

## Useful combinations

For spatial filtering combine a focusing lens or objective with `schematic/pinhole`, followed by a collimating lens. The visible pinhole diameter is nominal and intentionally legible; choose a physical diameter from the actual beam and wavelength for an experimental design.

For an infinity-corrected microscope combine an objective and `schematic/tube_lens`, using the specified focal-length ratio. The bundled native objectives and nominal tube lens do not automatically form a validated manufacturer pairing.

For reflection layouts use individual mirrors and splitters; place their physical surface normals from the prescribed ray directions. The `assembly/pbs_cube` nominal axis is not its diagonal splitting-plane normal. A camera's front aperture points toward the preceding optic.

For photolithography choose `schematic/photomask` and `schematic/wafer_chuck`, or the modulator/scanner assets for a digital projection illustration. SLM, DMD, scan head and UV source are clearly catalogued as generic schematic modules. They have no manufacturer identity or specified calibrated transfer function.

## What each family means

- **18 standard CAD parts:** official geometry, including reviewed unbranded derivatives. Native coordinates and real dimensions are retained. Supports and optical anchors must be measured before use in a new assembly.
- **24 mounted assemblies:** existing nominal optical models with official support/mount geometry where available. Standard post-mounted components now use PH50/M + TR50/M and a 100 mm nominal optical reference. The periscope and mechanical assets keep their special geometry.
- **28 functional modules:** repository-authored, editable nominal geometry for the otherwise missing optical functions. These enable offline diagrams without claiming a specific SKU or manufacturing accuracy.

The directory `library/provenance` records original model sources, mesh/STEP hashes and cleanup reports. Visible gallery labels describe functions only. Original branded CAD remains in the original repository archive, outside the displayed library.
