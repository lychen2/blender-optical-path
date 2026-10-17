"""Editable, publication-oriented beam geometry built from authored curve data."""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


# Keep the public millimetre convention aligned with tools/optics.py without
# importing its unrelated asset-library dependencies.
def _units(scene):
    if scene.unit_settings.system == 'NONE':
        raise ValueError('Set scene units first: configure Metric units')
    return .001 / scene.unit_settings.scale_length


def _finite_vector(value, name):
    try:
        if len(value) != 3 or any(isinstance(v, bool) or not isinstance(v, (int, float))
                                  or not math.isfinite(v) for v in value):
            raise ValueError
    except (TypeError, ValueError):
        raise ValueError(f'{name} must contain three finite numbers') from None
    return tuple(float(v) for v in value)


def _positive(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f'{name} must be positive and finite')
    return float(value)


def _make_material(name, rgb, opacity):
    material = bpy.data.materials.new(name + ' / color')
    material.diffuse_color = (*rgb, opacity)
    material.use_nodes = True
    shader = material.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*rgb, 1)
    shader.inputs['Emission Color'].default_value = (*rgb, 1)
    shader.inputs['Emission Strength'].default_value = .4
    shader.inputs['Alpha'].default_value = opacity
    if opacity < 1:
        material.surface_render_method = 'DITHERED'
    material['figure_material_role'] = 'beam'
    return material


def _geometry_group(name, circle_radius_scene, material):
    group = bpy.data.node_groups.new(name + ' / Geometry', 'GeometryNodeTree')
    group.interface.new_socket(name='Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    scale = group.interface.new_socket(name='Radius Scale', in_out='INPUT', socket_type='NodeSocketFloat')
    scale.default_value = 1.0
    scale.min_value = 0.0
    scale.max_value = 100.0
    scale.description = 'Interactive multiplier for the authored per-point beam radii'
    group.interface.new_socket(name='Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')

    nodes = group.nodes
    links = group.links
    inp = nodes.new('NodeGroupInput')
    inp.location = (-600, 100)
    out = nodes.new('NodeGroupOutput')
    out.location = (400, 100)
    radius = nodes.new('GeometryNodeInputRadius')
    radius.location = (-600, -180)
    multiply = nodes.new('ShaderNodeMath')
    multiply.operation = 'MULTIPLY'
    multiply.location = (-350, -160)
    links.new(radius.outputs['Radius'], multiply.inputs[0])
    links.new(inp.outputs['Radius Scale'], multiply.inputs[1])
    circle = nodes.new('GeometryNodeCurvePrimitiveCircle')
    circle.location = (-100, -220)
    circle.inputs['Resolution'].default_value = 16
    circle.inputs['Radius'].default_value = circle_radius_scene
    to_mesh = nodes.new('GeometryNodeCurveToMesh')
    to_mesh.location = (160, 100)
    to_mesh.inputs['Fill Caps'].default_value = True
    links.new(inp.outputs['Geometry'], to_mesh.inputs['Curve'])
    links.new(circle.outputs['Curve'], to_mesh.inputs['Profile Curve'])
    links.new(multiply.outputs[0], to_mesh.inputs['Scale'])
    assign = nodes.new('GeometryNodeSetMaterial')
    assign.location = (380, 100)
    assign.inputs['Material'].default_value = material
    links.new(to_mesh.outputs['Mesh'], assign.inputs['Geometry'])
    links.new(assign.outputs['Geometry'], out.inputs['Geometry'])
    out.location = (600, 100)
    return group


def add_beam_nodes(points_mm, name='Beam', radius_mm=2, color=(.05, .65, .18), scene=None,
                   radii_mm=None, profile='tube', opacity=.55):
    """Create an editable poly-curve beam with Geometry Nodes tube geometry.

    ``points_mm`` and radii are millimetres. Tube profile is the supported
    profile; it is rotationally symmetric, so it has no orientation dependency.
    ``Radius Scale`` on the modifier multiplies all authored point radii.
    """
    scene = scene or bpy.context.scene
    points = [_finite_vector(p, 'point') for p in points_mm]
    if len(points) < 2 or any((Vector(a) - Vector(b)).length < 1e-9
                              for a, b in zip(points, points[1:])):
        raise ValueError('Beam needs at least two points and no zero-length segment')
    base_radius = _positive(radius_mm, 'radius_mm')
    radii = list(radii_mm) if radii_mm is not None else [base_radius] * len(points)
    if len(radii) != len(points):
        raise ValueError('radii_mm must contain one positive finite radius per point')
    radii = [_positive(r, 'radius') for r in radii]
    rgb = _finite_vector(color, 'color')
    if any(v < 0 or v > 1 for v in rgb):
        raise ValueError('Color channels must be between 0 and 1')
    if profile != 'tube':
        raise ValueError("profile must be 'tube'")
    if isinstance(opacity, bool) or not isinstance(opacity, (int, float)) or not math.isfinite(opacity) or not 0 <= opacity <= 1:
        raise ValueError('opacity must be finite and between 0 and 1')
    factor = _units(scene)

    # All input validation is complete before creating Blender datablocks.
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 1
    spline = curve.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for point, co, point_radius in zip(spline.points, points, radii):
        point.co = (*(component * factor for component in co), 1)
        point.radius = point_radius / base_radius
    material = _make_material(name, rgb, float(opacity))
    curve.materials.append(material)
    obj = bpy.data.objects.new(name, curve)
    scene.collection.objects.link(obj)
    group = _geometry_group(name, base_radius * factor, material)
    modifier = obj.modifiers.new(name + ' / Geometry Nodes', 'NODES')
    modifier.node_group = group
    # Group interface socket identifiers are stable within this group.
    radius_socket = next(s for s in group.interface.items_tree
                         if s.item_type == 'SOCKET' and s.in_out == 'INPUT' and s.name == 'Radius Scale')
    getattr(modifier.properties.inputs, radius_socket.identifier).value = 1.0
    obj['opl_beam'] = True
    obj['figure_material_role'] = 'beam'
    obj['points_mm'] = json.dumps(points, allow_nan=False)
    obj['radii_mm'] = json.dumps(radii, allow_nan=False)
    obj['profile'] = profile
    obj['diagram_scope'] = 'Authored schematic envelope; no ray tracing or propagation calculation'
    return obj
