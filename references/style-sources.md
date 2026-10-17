# Visual style sources and provenance

Journal Editorial uses the component pack’s glass, metal, lighting and Filmic view with scientific-figure composition. The sources below record the material settings and visual references.

## Inspected scientific figures

- Nature (2023), “Density-wave ordering in a unitary Fermi gas with photon-mediated interactions,” Fig. 1a. DOI: [10.1038/s41586-023-06018-3](https://doi.org/10.1038/s41586-023-06018-3); PMC: [PMC10284702](https://pmc.ncbi.nlm.nih.gov/articles/PMC10284702/).
- Nature Communications (2021), “Ultrafast high-harmonic nanoscopy of magnetization dynamics,” Fig. 1a. DOI: [10.1038/s41467-021-26594-0](https://doi.org/10.1038/s41467-021-26594-0); PMC: [PMC8566501](https://pmc.ncbi.nlm.nih.gov/articles/PMC8566501/).
- Science Advances (2021), “Parallel, linear, and subnanometric 3D tracking of microparticles with Stereo Darkfield Interferometry,” Figs. 1A–C. DOI: [10.1126/sciadv.abe3902](https://doi.org/10.1126/sciadv.abe3902); PMC: [PMC7864575](https://pmc.ncbi.nlm.nih.gov/articles/PMC7864575/). This is evidence from *Science Advances*; flagship *Science* figures were not inspected.
- Scientific Reports (2020), “Motion-picture recording of ultrafast behavior of polarized light incident at Brewster's angle,” Figs. 4a–c. DOI: [10.1038/s41598-020-64714-w](https://doi.org/10.1038/s41598-020-64714-w); PMC: [PMC7203257](https://pmc.ncbi.nlm.nih.gov/articles/PMC7203257/).
- Scientific Reports (2020), “A compact single channel interferometer to study vortex beam propagation through scattering layers,” Fig. 1a. DOI: [10.1038/s41598-019-56795-z](https://doi.org/10.1038/s41598-019-56795-z); PMC: [PMC6962366](https://pmc.ncbi.nlm.nih.gov/articles/PMC6962366/).
- Scientific Reports (2018), “Fast stabilization of a high-energy ultrafast OPA with adaptive lenses,” Fig. 1. DOI: [10.1038/s41598-018-32182-y](https://doi.org/10.1038/s41598-018-32182-y); PMC: [PMC6156574](https://pmc.ncbi.nlm.nih.gov/articles/PMC6156574/).
- Scientific Reports (2025), “Large tolerance for incidence angle in Terahertz parametric detection,” Figs. 1a–f. DOI: [10.1038/s41598-025-06264-7](https://doi.org/10.1038/s41598-025-06264-7); PMC: [PMC12218185](https://pmc.ncbi.nlm.nih.gov/articles/PMC12218185/).

These figures use sparse geometry, consistent visual channels, clear subsystem grouping and multi-panel detail. Apply those techniques while preserving the drawing's topology and meaning.

## Local component-pack glass

The material reference is `Optical components pack V1.blend`, inspected in Blender 5.2.2. The skill records its shader settings; the user's source file and geometry are not bundled.

The `Lens` material uses a Principled shader with base color `(0.906751573, 0.970782459, 1.0)`, metallic 0, roughness 0.1, IOR 1.5 and transmission 1. The inspected biconvex object has an empty material slot. The `Lens` datablock supplies the material reference independently of that object.

The source scene uses Cycles, Filmic, Medium High Contrast and a zero-strength world. Its square top area light is 171.4524 W, size 1, near `(0.004917, -0.221193, 2.780707)`. The white `Backplane` is a curved reflective studio surface, roughness 0 and IOR 1.45.

The default scales that studio to the figure and adds a weak broad front fill. The floor and curved wall remain visible to indirect rays but hidden from the camera. This preserves material reflections without lower floor shadows.

Hardware recipes use `Objective rough` (white metal, roughness 0.3), `Objective shiny` (0.8 metal, roughness 0.1), and `Laser body` (0.29569 metal, roughness 0.36232). Dark housings use the pack’s near-black finish. Cylindrical lens edges use a separate rough-glass material, roughness 0.55.

The complex preview uses four OptiCore biconvex meshes and the source `Lens` material. OptiCore revision `f9b0029009846abbf34a0947971dc4c6ba1a21f6` was executed in Blender 5.2.2. See [reproduction details](opticore.md).
