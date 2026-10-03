# Manual assembly

Open `library/Optical_Components.blend` in Blender 5.2 or newer. The delivered file was built with Blender 5.2.2; older versions have not been verified.

## Copy from the gallery

1. Select `01 ASSEMBLY GALLERY`, `02 STANDARD PARTS`, or `03 FUNCTIONAL MODULES` from the scene selector at the top of Blender. Each displayed component is a full-size collection instance; captions are separate objects.
2. Select the component, press **Ctrl+C**, switch to `04 BUILD HERE`, and press **Ctrl+V**. Use **G**, **R**, and the Item panel to position it. Preserve instance scale `(1,1,1)` in this millimetre scene. Gallery instances may have a display rotation; reset rotation with **Alt+R** if a canonical axis is needed.
3. Save As a new `.blend`. Use **Numpad .** to frame a selected component and **Home** to frame everything. Copy multiple components as needed.

Copy only component instances, not the separate gallery captions. Keep your optical scene free of names and 3D text. Render the hardware and beams first, then add labels to a separate 2D overlay in a graphics editor. Object names in the Outliner remain metadata and do not appear in renders.

Collection instances copy the whole assembly. To edit its separate parts, select the instance and use **Object > Apply > Make Instances Real** with hierarchy preservation. Normal duplicate instances share the source geometry; make the realized object's data single-user before changing only one part's mesh or material.

## Asset Browser

Add this skill's `library` directory under **Edit > Preferences > File Paths > Asset Libraries**. Change an editor to **Asset Browser** and choose the added library. Categories separate mounted assemblies, standard parts, and functional modules. Use Append for a self-contained working scene. Collection assets remain usable by their generic names even if a preview thumbnail is not available.

The `.blend` gallery is the main visual picker. A standard-part's SKU is available in collection custom properties and `index.json`; it is not a visible model inscription or caption.

## Height and coordinate conventions

One coordinate unit in the gallery is one millimetre. Post-mounted assemblies use rigid **PH50/M + TR50/M** CAD parts, including the fork and pedestal. Their nominal optical reference is **100 mm**. Holder/post lengths describe separate overlapping parts, not a sum of exposed lengths. The post body is approximately 50.013 mm in the source CAD; insertion is checked during build.

The objective uses a compact fixed square plate and shallow reducer. The plate, reducer and optical barrel are nominal diagram geometry. Its support is the same 50 mm standard pair.

Mechanical assets and the original periscope keep their own references. New schematic accessories with a post also use a 100 mm optical reference and the same unbranded PH50/M + TR50/M CAD supports, pedestal and fork clamp. Their upper functional modules remain nominal diagram geometry. Read each asset's `anchor_mm`, `axis`, and `ports_mm` in `index.json`; native standard CAD has no calibrated optical anchor.

No geometry is stretched to fit a target optical height. Move whole assemblies or choose different post/holder lengths. Before putting a bare CAD optic into a mount, verify its aperture, mounting interface and transform against the drawing. A default native origin is not an optical center.

## Offline scope

The gallery covers common single-pass imaging, relay/Fourier optics, schematic bright-field and fluorescence microscopy, Michelson/Mach–Zehnder arrangements, and contact/projection or modulator-based lithography illustrations. See [system coverage](system-coverage.md) for the component choices and limits. The library supplies the visual hardware; focal prescriptions, coating bands, precision clearances and propagation physics require task-specific input.

Gallery captions use generic functions; they are not intended for the final optical scene. Brand and SKU inscriptions are removed from reviewed derivatives; original CAD and its provenance remain separately archived. Useful angle graduations may remain.
