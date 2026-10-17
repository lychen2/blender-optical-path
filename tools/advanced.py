"""Calculated envelopes, conic/aspheric lens meshes and explicit-axis alignment."""
import json
import math
from pathlib import Path
import runpy

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
api = runpy.run_path(str(HERE / 'optics.py'))
model = runpy.run_path(str(HERE / 'optical_model.py'))


def add_gaussian_beam(wavelength_nm, waist_mm, waist_position_mm, elements, end_mm,
                      origin_mm=(0, 0, 100), direction=(1, 0, 0), samples=121,
                      display_radius_scale=1, display_floor_mm=0, color=(.08, .6, .2),
                      name='Calculated Gaussian envelope', scene=None):
    scene = scene or bpy.context.scene
    origin = api['finite_vector'](origin_mm, 'origin_mm')
    axis = api['finite_vector'](direction, 'direction')
    if axis.length < 1e-9:
        raise ValueError('direction must be nonzero')
    for value, label, positive in ((display_radius_scale, 'display_radius_scale', True),
                                    (display_floor_mm, 'display_floor_mm', False)):
        if isinstance(value, bool) or not math.isfinite(value) or (value <= 0 if positive else value < 0):
            raise ValueError(f'{label} is invalid')
    axis.normalize()
    result = model['gaussian_beam'](wavelength_nm, waist_mm, waist_position_mm, elements, end_mm, samples)
    # Include lens coordinates and segment endpoints, preserving the calculated envelope.
    rows = {row['position_mm']: row for row in result['samples']}
    for point in result['checkpoints']:
        if 'before' in point:
            row = dict(point['before'])
            row['position_mm'] = point['position_mm']
            rows[point['position_mm']] = row
    ordered = [rows[z] for z in sorted(rows)]
    points = [list(origin + axis * row['position_mm']) for row in ordered]
    radii = [max(display_floor_mm, row['radius_mm'] * display_radius_scale) for row in ordered]
    obj = api['add_beam'](points, name, radii[0], color, scene, radii_mm=radii)
    obj['opl_beam'] = True
    obj['diagram_scope'] = result['model_scope']
    obj['optical_model'] = json.dumps(result)
    obj['optical_inputs'] = json.dumps({'wavelength_nm': wavelength_nm, 'waist_mm': waist_mm,
        'waist_position_mm': waist_position_mm, 'elements': elements, 'end_mm': end_mm})
    obj['display_radius_scale'] = display_radius_scale
    obj['display_floor_mm'] = display_floor_mm
    return obj, result


def add_lens(diameter_mm=25.4, thickness_mm=6, radius1_mm=40, radius2_mm=-40,
             conic1=0, conic2=0, asphere1=None, asphere2=None,
             radial_segments=24, angular_segments=96, position_mm=(0, 0, 100),
             name='Parametric lens', scene=None):
    """Sample exact conic sag plus even terms A4, A6, ...; local optical axis is +X.

    Positive radii have centres toward +X. Coefficients use millimetres: A4 is mm^-3.
    This creates a tessellated surface, not a manufacturer prescription or a trace.
    """
    scene = scene or bpy.context.scene
    position = api['finite_vector'](position_mm, 'position_mm')
    factor = api['units'](scene)
    for number in (diameter_mm, thickness_mm, conic1, conic2):
        if isinstance(number, bool) or not isinstance(number, (int, float)) or not math.isfinite(number):
            raise ValueError('Lens dimensions and conics must be finite numbers')
    if diameter_mm <= 0 or thickness_mm <= 0:
        raise ValueError('Lens diameter and thickness must be positive')
    if type(radial_segments) is not int or not 2 <= radial_segments <= 512:
        raise ValueError('radial_segments must be an integer from 2 to 512')
    if type(angular_segments) is not int or not 12 <= angular_segments <= 512:
        raise ValueError('angular_segments must be an integer from 12 to 512')
    for radius in (radius1_mm, radius2_mm):
        if radius is not None and (isinstance(radius, bool) or not math.isfinite(radius) or radius == 0):
            raise ValueError('Surface radius must be finite and nonzero; use null for a plane')
    coefficients = [list(asphere1 or []), list(asphere2 or [])]
    if any(isinstance(a, bool) or not isinstance(a, (int, float)) or not math.isfinite(a)
           for values in coefficients for a in values):
        raise ValueError('Asphere coefficients must be finite numbers')

    def sag(r, radius, conic, values):
        c = 0 if radius is None else 1 / radius
        radicand = 1 - (1 + conic) * c * c * r * r
        if radicand < 0:
            raise ValueError('Aperture exceeds the real conic surface domain')
        return c * r * r / (1 + math.sqrt(radicand)) + sum(a * r ** (4 + 2 * i) for i, a in enumerate(values))

    radii = [diameter_mm / 2 * i / radial_segments for i in range(radial_segments + 1)]
    fronts = [-thickness_mm / 2 + sag(r, radius1_mm, conic1, coefficients[0]) for r in radii]
    backs = [thickness_mm / 2 + sag(r, radius2_mm, conic2, coefficients[1]) for r in radii]
    if any(a >= b for a, b in zip(fronts, backs)):
        raise ValueError('Lens surfaces intersect within the sampled aperture; increase thickness or reduce aperture')
    vertices, faces = [], []
    sides = []
    for surface_index, xs in enumerate((fronts, backs)):
        center = len(vertices)
        vertices.append((xs[0], 0, 0))
        rings = []
        for r, x in zip(radii[1:], xs[1:]):
            ring = []
            for j in range(angular_segments):
                angle = 2 * math.pi * j / angular_segments
                ring.append(len(vertices))
                vertices.append((x, r * math.cos(angle), r * math.sin(angle)))
            rings.append(ring)
        surface_faces = []
        for j in range(angular_segments):
            k = (j + 1) % angular_segments
            surface_faces.append((center, rings[0][j], rings[0][k]))
        for inner, outer in zip(rings, rings[1:]):
            for j in range(angular_segments):
                k = (j + 1) % angular_segments
                surface_faces.append((inner[j], outer[j], outer[k], inner[k]))
        faces.extend(tuple(reversed(face)) if surface_index == 0 else face for face in surface_faces)
        sides.append(rings[-1])
    for j in range(angular_segments):
        k = (j + 1) % angular_segments
        faces.append((sides[0][j], sides[0][k], sides[1][k], sides[1][j]))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    material = bpy.data.materials.new(name + ' / optical glass')
    material.use_nodes = True
    shader = material.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (.90675, .97078, 1, 1)
    shader.inputs['Roughness'].default_value = .1
    shader.inputs['Transmission Weight'].default_value = 1
    shader.inputs['IOR'].default_value = 1.5
    material['figure_material_role'] = 'optic'
    mesh.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = polygon.index < len(faces) - angular_segments
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    obj.location = position * factor
    obj.scale = (factor,) * 3
    obj['figure_material_role'] = 'optic'
    obj['optical_axis_local'] = '+X'
    obj['lens_prescription_mm'] = json.dumps({'diameter': diameter_mm, 'center_thickness': thickness_mm,
        'radius1': radius1_mm, 'radius2': radius2_mm, 'conic1': conic1, 'conic2': conic2,
        'asphere1': coefficients[0], 'asphere2': coefficients[1], 'edge_thickness': backs[-1] - fronts[-1]})
    obj['geometry_scope'] = 'Sampled conic/aspheric surfaces; no aberration, focal length or material dispersion inference'
    return obj


def align_component(object_name, target_mm, toward_mm, local_axis=(1, 0, 0),
                    local_anchor_mm=(0, 0, 0), scene=None):
    """Align an explicit native-mm anchor and axis; preserve object scale."""
    scene = scene or bpy.context.scene
    obj = scene.objects.get(object_name)
    if obj is None:
        raise ValueError(f'Object is not in this scene: {object_name}')
    if obj.parent:
        raise ValueError('Align a root object; parent transforms require an explicit assembly solution')
    target = api['finite_vector'](target_mm, 'target_mm') * api['units'](scene)
    toward = api['finite_vector'](toward_mm, 'toward_mm') * api['units'](scene)
    axis = api['finite_vector'](local_axis, 'local_axis')
    anchor = api['finite_vector'](local_anchor_mm, 'local_anchor_mm')
    if (toward - target).length < 1e-9 or axis.length < 1e-9:
        raise ValueError('Alignment requires nonzero local and target directions')
    obj.rotation_mode = 'QUATERNION'
    # The current scaled local axis accounts for signed object scales.
    scaled_axis = Vector(tuple(axis[i] * obj.scale[i] for i in range(3)))
    obj.rotation_quaternion = scaled_axis.rotation_difference(toward - target)
    bpy.context.view_layer.update()
    obj.location += target - obj.matrix_world @ anchor
    bpy.context.view_layer.update()
    actual_anchor = obj.matrix_world @ anchor
    actual_axis = (obj.matrix_world.to_3x3() @ axis).normalized()
    error = (actual_anchor - target).length / api['units'](scene)
    angle = actual_axis.angle((toward - target).normalized())
    return {'object': obj.name, 'anchor_error_mm': error, 'axis_error_rad': angle,
            'scope': 'Explicit anchor/axis alignment; no inferred CAD ports or optimization'}
