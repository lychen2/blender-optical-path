"""Headless Blender integration checks for editable Geometry Nodes beam geometry."""
import json
import math
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geometry_nodes import add_beam_nodes


def evaluated_dimensions(obj):
    scene = next(iter(obj.users_scene), bpy.context.scene)
    with bpy.context.temp_override(scene=scene, view_layer=scene.view_layers[0]):
        depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        assert len(mesh.vertices) > 0, 'evaluated beam mesh is empty'
        used = {mesh.materials[polygon.material_index].original for polygon in mesh.polygons}
        assert used == {obj.material_slots[0].material}, 'GN mesh lost its display material'
        coords = [v.co.copy() for v in mesh.vertices]
        return tuple(max(p[i] for p in coords) - min(p[i] for p in coords) for i in range(3)), coords
    finally:
        evaluated.to_mesh_clear()


def near(actual, expected, tolerance=1e-5):
    assert math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance), (actual, expected)


def expect_invalid_without_mutation(args, kwargs):
    scene = kwargs.get('scene') or bpy.context.scene
    before = (len(bpy.data.objects), len(bpy.data.curves), len(bpy.data.node_groups),
              len(bpy.data.materials), len(scene.objects))
    try:
        add_beam_nodes(*args, **kwargs)
    except ValueError:
        pass
    else:
        raise AssertionError('invalid beam input was accepted')
    after = (len(bpy.data.objects), len(bpy.data.curves), len(bpy.data.node_groups),
             len(bpy.data.materials), len(scene.objects))
    assert before == after, (before, after)


# Familiar optical convention: scale_length=.001 means one scene unit per mm.
scene_mm = bpy.context.scene
scene_mm.unit_settings.system = 'METRIC'
scene_mm.unit_settings.scale_length = .001
scene_mm.unit_settings.length_unit = 'MILLIMETERS'
obj = add_beam_nodes([(0, 0, 0), (20, 0, 0)], name='Uniform / mm', radius_mm=2,
                     color=(.05, .65, .18), scene=scene_mm)
assert obj.type == 'CURVE' and obj.data.splines[0].type == 'POLY'
modifier = next((m for m in obj.modifiers if m.type == 'NODES'), None)
assert modifier is not None and modifier.node_group is not None
assert any(n.bl_idname == 'GeometryNodeCurveToMesh' for n in modifier.node_group.nodes)
assert any(n.bl_idname == 'GeometryNodeCurvePrimitiveCircle' for n in modifier.node_group.nodes)
assert obj.get('opl_beam') is True
assert json.loads(obj['points_mm']) == [[0.0, 0.0, 0.0], [20.0, 0.0, 0.0]]
assert json.loads(obj['radii_mm']) == [2.0, 2.0]
dims, _ = evaluated_dimensions(obj)
near(dims[0], 20)
near(dims[1], 4)
near(dims[2], 4)

scale_socket = next(s for s in modifier.node_group.interface.items_tree
                    if s.item_type == 'SOCKET' and s.in_out == 'INPUT' and s.name == 'Radius Scale')
getattr(modifier.properties.inputs, scale_socket.identifier).value = 2.0
# Refresh the modifier's evaluation cache after its 5.2 interface property changes.
modifier.show_viewport = False
modifier.show_viewport = True
obj.update_tag(refresh={'OBJECT', 'DATA', 'TIME'})
bpy.context.view_layer.update()
scaled_dims, _ = evaluated_dimensions(obj)
near(scaled_dims[1], 8)
near(scaled_dims[2], 8)

# Independent authored end radii must make the evaluated ends observably taper.
taper = add_beam_nodes([(0, 0, 0), (10, 0, 0)], name='Tapered', radius_mm=1,
                       radii_mm=[1, 3], scene=scene_mm)
_, taper_coords = evaluated_dimensions(taper)
start_r = max(math.hypot(p.y, p.z) for p in taper_coords if abs(p.x) < 1e-5)
end_r = max(math.hypot(p.y, p.z) for p in taper_coords if abs(p.x - 10) < 1e-5)
near(start_r, 1)
near(end_r, 3)
assert end_r > start_r * 2.9

# Metre-scale scene: 1 mm is 0.001 scene units.
scene_m = bpy.data.scenes.new('Metre convention check')
scene_m.unit_settings.system = 'METRIC'
scene_m.unit_settings.scale_length = 1.0
metre_obj = add_beam_nodes([(0, 0, 0), (20, 0, 0)], name='Uniform / metres', radius_mm=2,
                           scene=scene_m)
metre_dims, _ = evaluated_dimensions(metre_obj)
near(metre_dims[0], .02)
near(metre_dims[1], .004)
near(metre_dims[2], .004)

# Rejections occur before any scene/data mutation.
expect_invalid_without_mutation(([(0, 0, 0), (1, 0, 0)],), {'radius_mm': 0})
expect_invalid_without_mutation(([(0, 0, 0), (1, 0, 0)],), {'radii_mm': [1]})
expect_invalid_without_mutation(([(0, 0, 0), (1, 0, 0)],), {'radii_mm': [1, float('nan')]})
expect_invalid_without_mutation(([(0, 0, 0), (1, 0, 0)],), {'color': (0, 2, 0)})
expect_invalid_without_mutation(([(0, 0, 0), (1, 0, 0)],), {'profile': 'ribbon'})
expect_invalid_without_mutation(([(0, 0, 0), (1, 0, 0)],), {'opacity': 1.1})

print('GEOMETRY_NODES_CHECK_PASSED')
print('Verified editable POLY curve, Curve to Mesh, exposed Radius Scale, tapered endpoints, mm/metre conversion, and mutation-free invalid inputs.')
