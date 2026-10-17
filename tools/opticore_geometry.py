"""Optional OptiCore lens adapter. Load a local checkout; do not install an add-on."""
import importlib.util
import json
import math
from pathlib import Path
import sys

import bpy

_MODULE = '_opl_opticore'


def load_opticore(checkout):
    """Register only the upstream lens operator in the current Blender process."""
    checkout = Path(checkout).expanduser().resolve()
    if not (checkout / 'bl_optics/lens.py').is_file():
        raise FileNotFoundError(f'Expected an OptiCore checkout: {checkout}')
    module = sys.modules.get(_MODULE)
    if module is None:
        spec = importlib.util.spec_from_file_location(
            _MODULE, checkout / '__init__.py', submodule_search_locations=[str(checkout)])
        module = importlib.util.module_from_spec(spec)
        sys.modules[_MODULE] = module
        spec.loader.exec_module(module)
        bpy.utils.register_class(module.OBJECT_OT_add_lens)
    elif Path(module.__file__).parent != checkout:
        raise ValueError('Use one OptiCore checkout per Blender process')
    return module


def add_opticore_lens(checkout, name='OptiCore lens', position_mm=(0, 0, 100),
                      diameter_mm=25.4, thickness_mm=6, radius1_mm=50,
                      radius2_mm=-50, scene=None, material=None):
    """Create an editable biconvex singlet, centered at position_mm, with local +X axis.

    Dimensions describe drawing geometry, not an inferred optical prescription.
    OptiCore supplies mesh geometry; the material is assigned separately.
    """
    scene = scene or bpy.context.scene
    values = (diameter_mm, thickness_mm, radius1_mm, radius2_mm, *position_mm)
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError('Lens parameters must be finite')
    if diameter_mm <= 0 or thickness_mm <= 0 or radius1_mm <= 0 or radius2_mm >= 0:
        raise ValueError('Use positive size, positive front radius and negative rear radius')
    aperture = diameter_mm / 2
    if aperture >= min(radius1_mm, -radius2_mm):
        raise ValueError('Aperture must fit both spherical surfaces')
    sag = sum(abs(radius) - math.sqrt(radius * radius - aperture * aperture)
              for radius in (radius1_mm, radius2_mm))
    if thickness_mm <= sag:
        raise ValueError('Center thickness must keep a positive lens edge')
    if bpy.context.scene != scene:
        raise ValueError('Make the target scene active before using the OptiCore operator')
    if bpy.context.mode != 'OBJECT':
        raise ValueError('Use Object mode before generating an OptiCore lens')
    load_opticore(checkout)
    result = bpy.ops.mesh.add_lens(makedoublet='1', ltype1='rotational', ltype2='rotational',
        RY1=radius1_mm, RY2=radius2_mm, lensradius=aperture,
        centerthickness1=thickness_mm, num1=32, num2=96,
        align='WORLD', location=(0, 0, 0), rotation=(0, 0, 0),
        shade_smooth=True, addrayfan=False)
    if result != {'FINISHED'}:
        raise RuntimeError(f'OptiCore lens generation failed: {result}')
    obj = bpy.context.active_object
    obj.name = name
    # Upstream uses raw Blender coordinates and places surface 1 at the origin.
    # Center the actual generated axial bounds before converting mm to scene units.
    factor = .001 / scene.unit_settings.scale_length
    axial = [vertex.co.x for vertex in obj.data.vertices]
    center = (min(axial) + max(axial)) / 2
    for vertex in obj.data.vertices:
        vertex.co.x -= center
        vertex.co *= factor
    obj.location = tuple(value * factor for value in position_mm)
    obj.data.materials.clear()
    if material is not None:
        obj.data.materials.append(material)
    obj['figure_material_role'] = 'optic'
    obj['opl_geometry_generator'] = 'CodeFHD/OptiCore'
    obj['opl_geometry_source'] = 'https://github.com/CodeFHD/OptiCore'
    obj['opl_geometry_parameters_mm'] = json.dumps({
        'diameter': diameter_mm, 'center_thickness': thickness_mm,
        'radius1': radius1_mm, 'radius2': radius2_mm})
    obj['opl_geometry_scope'] = 'Authored illustration dimensions; no optical prescription inferred'
    obj['opl_axis'] = '+X'
    return obj
