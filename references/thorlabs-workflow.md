# Standard part search, download, cleanup and use

Use bundled assets offline by default. Connect to suppliers only when the user specifies a missing model or requests a library expansion. Manufacturer specifications govern model selection; a similar appearance does not establish compatibility.

## Choose a part

Search locally with `python tools/thorlabs.py search lens`, a generic function, or an exact SKU. `library/index.json` distinguishes official CAD, mixed mounted assemblies and nominal schematic modules. The gallery uses generic visible names; the index and collection properties retain the original manufacturer model.

For a specified new model, check the manufacturer's current product page and drawing. Record aperture and outer diameter, wavelength/coating band, focal length or magnification, working distance/NA, mounting thread and required adapters. For objectives distinguish infinity-corrected vs finite-conjugate and the required tube lens. For splitters distinguish polarization, coating and transmission/reflection convention. A STEP solid does not supply a validated optical prescription.

Supplier search order:

| Source | Entry point | Use |
| --- | --- | --- |
| Thorlabs | https://www.thorlabs.com/navigation.cfm?guide_id=10 | First choice for mounts, supports, optical elements and imaging hardware |
| Edmund Optics | https://www.edmundoptics.com/category/optical-components/1019/ | Alternative optical elements and imaging components |
| OptoSigma | https://www.optosigma.com/us_en/c/3d-cad-data | Alternative optical and positioning hardware |
| Zemax resources | https://www.zemax.com/resources/3d-model-library | User-supplied discovery link; verify current destination and whether the file is optical data or mechanical CAD |
| TraceParts | https://www.traceparts.com/zh-cn/search/optical-components | Supplier CAD catalog; verify publisher, revision and reuse terms against the original manufacturer |

These are discovery entry points, not a claim that every model is free, currently available or retrievable without an account. Follow current supplier links, retain provenance and respect model-specific reuse terms. The bundled assets do not depend on these sites being reachable.

## Exact-SKU official download

```bash
python tools/thorlabs.py download LMR1/M --output /chosen/cad-sources
```

The helper validates the exact SKU using the official product GraphQL API, selects STEP and CAD PDF assets, checks HTTPS host and file signatures, and records URLs, hashes and retrieval time. It refuses an existing product directory. The endpoint is an upstream interface and may change: if it fails, use the product page's CAD tab, save the original file and equivalent metadata, and report the failure. Never invent a download URL or silently substitute a similar SKU. Existing repository archives can be reused without another network request.

Official regional redirects preserve POST requests for HTTP 307/308. Allowed hosts cover `thorlabs.com`, `thorlabschina.cn` and `thorlabscms.cn` and their subdomains. Regional media requests can time out; retry into a new destination after a failed transfer. The bundled assets work offline. Downloaded originals are for local inspection; do not publish them with visible branding or model inscriptions.

## Tessellation

Use **normal Python with build123d**, not Blender's bundled Python, for STEP operations. Create a dedicated virtual environment and install `build123d` there.

```bash
/path/to/cad-python tools/thorlabs.py convert /chosen/cad-sources/LMR1_M/source.step \
  --sku LMR1/M --output /chosen/cad-sources/LMR1_M/original.mesh.json.gz
```

The output preserves native millimetres, solid order, the source hash and a default 0.06 mm tessellation tolerance. Check the CAD drawing for dimensions and coordinate frame before aligning it. Solids or shells can be tessellated; an invalid BRep is rejected. Do not convert an optical design file into an assumed mechanical solid.

## Remove visible branding on a derivative

Inspect the exact STEP revision, identify engraved branding and SKU faces, and create a reviewed rules JSON:

```json
{
  "source_sha256": "SHA256_OF_THE_INSPECTED_STEP",
  "solid_count": 1,
  "solids": {
    "0": {
      "face_count": 238,
      "remove_faces": [27, 28],
      "max_volume_added_mm3": 5
    }
  }
}
```

The face list above is a **schema example**, not a usable cleanup prescription. Inspect the actual file; never copy guessed face indices. Preserve functional angle ticks, bores and mating surfaces. Logo removal must not erase provenance metadata.

```bash
/path/to/cad-python tools/thorlabs.py clean /chosen/source.step \
  --rules /chosen/reviewed-rules.json --output /chosen/visualization/unbranded.step
/path/to/cad-python tools/thorlabs.py convert /chosen/visualization/unbranded.step \
  --sku LMR1/M --output /chosen/visualization/unbranded.mesh.json.gz
```

The cleanup checks source hash, solid/face counts, valid BRep, bounds within 0.001 mm and a reviewed permitted volume increase. It exports a new STEP and a `.cleanup.json` report. The converter records whether an adjacent successful cleanup report matches the input hash. Original source files remain untouched.

Shell-based CAD needs a separate reviewed face-replacement method, not the solid defeaturing command: replace the engraved planar wall, preserve other structural faces and check bounds. Volume checks are not applicable to open shells. Existing reviewed cleanup reports are included in `library/provenance`.

## Import and register

Inside Blender:

```python
import runpy, bpy
api = runpy.run_path('/path/to/blender-optical-path/tools/optics.py')
col = api['import_cad']('/chosen/visualization/unbranded.mesh.json.gz', 'Standard part / Lens mount')
obj = bpy.data.objects.new('Lens mount', None)
obj.instance_type, obj.instance_collection = 'COLLECTION', col
bpy.context.scene.collection.objects.link(obj)
# Native geometry is in mm. For a metre scene, set obj.scale = (.001, .001, .001).
```

Inspect the imported part from several views before admitting it to the unbranded gallery. `import_cad` validates mesh indices and drops/counts degenerate triangles; it cannot infer branding or a physical optical anchor. Assign a generic caption, catalogue category and backend SKU. Save as a new asset-library `.blend` next to its metadata. To make it searchable through the bundled API, add an index record and store its `opl_asset_id` on the collection, or maintain it as a separate local library.

Record native optical center/axis only after measuring the relevant surface or aperture against CAD. Assemble supporting hardware with rigid transforms. Do not stretch standard CAD or alter units to make a part fit. Review a preview for remaining marks before sharing. Keep component names out of the 3D optical scene; add requested labels to the rendered image afterward. Shared STEP files must be reviewed derivatives without branding or model inscriptions, and sharing must remain within the applicable permission.
