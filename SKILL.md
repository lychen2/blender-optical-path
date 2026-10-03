---
name: blender-optical-path
description: Build editable Blender optical-path figures from optical topology, aligned components and a deliberate visual style. Use Python or Blender MCP, render hardware and beams without text, and add labels afterward in a separate 2D overlay.
---

# Blender optical path

Turn an optical topology into an editable, readable figure. Establish physical references, assemble hardware and beam paths, choose a visual direction, render without text, then annotate in 2D. The local component library supports this workflow; use verified manufacturer geometry where useful without making the catalog the subject of the figure.

## Start here

Resolve all paths relative to this skill's directory. The package includes its `.blend` and metadata; using it does not require the original repository.

- **Human assembly:** open `library/Optical_Components.blend`. `01 ASSEMBLY GALLERY` displays 24 mounted assemblies, `02 STANDARD PARTS` displays 18 standard CAD parts, `03 FUNCTIONAL MODULES` displays 28 offline accessories, and `04 BUILD HERE` is the workspace. Read [manual assembly](references/manual.md).
- **Python:** load `tools/optics.py` using `runpy.run_path`. Use the same functions from Blender's console, a background script, or the Text Editor. Read [Python and MCP](references/python-mcp.md).
- **Blender MCP:** discover the connected server's scene inspection and Python execution tools. Send the same Python API or the JSON entrypoint `tools/blender_mcp_entry.py`; do not assume a fixed tool prefix. The path must exist on the Blender host.

The gallery arranges individual components for manual copying. It does not require an entire optical-layout template.

## Workflow

1. Establish the optical topology, beam branches, ports and known dimensions. Inspect the existing scene. Choose a visual brief using [visual style](references/visual-style.md): style anchor, camera, beam treatment, key-light direction, background and material emphasis. Keep physical assumptions explicit.
2. Search `library/index.json` or `python tools/thorlabs.py search QUERY` for the function or exact SKU. Prefer verified geometry when appropriate; mounted assemblies mix CAD and illustrative optics. For missing parts use [official CAD search and cleanup](references/thorlabs-workflow.md). New workspaces use metric units with `scale_length=0.001`: one Blender unit is 1 mm. The API accepts millimetres and converts them for an existing metric scene; never change existing scene units as an implicit conversion.
3. Place collection instances by a documented reference. Rebuilt mounted assemblies use 50 mm standard holders/posts and usually have nominal local `(0,0,100)` optical reference and `+X` axis. Bare CAD keeps native coordinates and has **no calibrated optical anchor**. Inspect and measure its aperture/surface before aligning it or attaching support. Periscopes and mechanical assets need their own reference points. Preserve native mesh geometry and source collection hierarchy.
4. Add schematic beam curves in the working scene. **Do not add component names, labels or any 3D text beside the hardware.** Render hardware and beams without text, then add annotations to the rendered image in a separate 2D editor/compositor. Gallery captions are for browsing only; copy component instances without captions. `add_annotation` records metadata for later work and creates no visible text. For a reflecting surface, use incoming/outgoing unit vectors to choose `n ∝ k_in − k_out`, then verify the reflection equation and identify which local axis is the actual surface normal. A PBS cube's splitting-plane normal differs from its nominal axis. Camera apertures face the incoming beam. Keep focal lengths, propagation distances and ray-tracing claims tied to supplied evidence.
5. Save a new `.blend` without overwriting the library. Validate through `tools/validate_layout.py`, inspect a viewport or render, and check optical alignment, occlusion and unwanted markings visually. The validator checks structure, not ray propagation, collision clearance, or branding embedded in arbitrary mesh topology.

## Visual direction

Read [visual-style.md](references/visual-style.md) before composing a figure. Choose a specific anchor such as Nature Photonics-inspired editorial composition, simplified 3D schematic, Cycles studio rendering or technical axonometric. These are art-direction references, not automatic presets or venue endorsements.

- Do not default to “glowing volumetric” beams. Choose an actual thin colored path, translucent ribbon, narrow luminous core, sparse ray bundle or restrained scattering cone as appropriate; describe what is rendered.
- For successive figures, vary key-light direction, background treatment and material emphasis. Use camera and beam variation purposefully, not random decoration. Record the brief beside the assembly script.
- For related figures, keep core terminology, component IDs, optical meaning and beam-channel colors consistent. Assign each panel a distinct visual focus and variation; do not repeat one render recipe.
- Preserve locked user/venue choices and controlled-comparison conditions. Do not change physical geometry or data to manufacture variety. Reduce effects that obscure the path.

## Visible content and geometry

- In gallery captions and post-render 2D annotations, use generic names such as “Mirror mount”, “Quarter-wave plate” and “Camera”. Keep the generated optical scene text-free. Never add visible Thorlabs logos or SKU/model labels. Searchable IDs and source part numbers belong in custom properties and JSON.
- Remove branding only from a derivative. Never delete small faces indiscriminately. Preserve bores, threads, alignment surfaces, optical interfaces and useful scales. Reject a cleanup rule when the source hash, topology, bounds or permitted volume change does not match.
- Do not include an unreviewed branded model in the display gallery. Keep it in the source archive until cleanup and visual inspection finish. Do not invent missing official parts or present generic optics as exact SKU geometry.
- Beam radius and color are illustrative. Native CAD size is retained; mounted optical geometry is nominal. The files do not simulate interference, polarization, diffraction or laser safety.

## Deliver

Return the editable scene and a text-free render, with the assembly script when relevant. If labels are requested, deliver a separate annotated 2D figure and its editable overlay; never render text as part of the 3D optical scene. Report the exact file path and any missing component or unverified optical anchor. Put provenance and cleanup evidence in metadata, not on the figure. Inspect captions and rendered geometry for unwanted manufacturer markings before delivery.

## References and tools

- [Visual-style briefs and series variation](references/visual-style.md)
- [Offline system coverage](references/system-coverage.md)
- [Manual gallery usage](references/manual.md)
- [Python and Blender MCP](references/python-mcp.md)
- [Thorlabs workflow](references/thorlabs-workflow.md)
- `library/index.json`: exact asset IDs, generic names, source metadata and anchor availability.
- `tools/example_scene.py`: save and render a minimal placement example into a new directory.
- `tools/check_package.py`: check the bundled assets and shared API without modifying the library.
- [Third-party asset rights](THIRD_PARTY_NOTICES.md): retain provenance and publish only reviewed derivatives within applicable permission.
