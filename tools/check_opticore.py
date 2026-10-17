"""Check the optional OptiCore adapter through Blender's real operator boundary.
blender -b --factory-startup --python-exit-code 1 --python tools/check_opticore.py -- --checkout /path/to/OptiCore
"""
import argparse
from collections import Counter
import math
from pathlib import Path
import runpy
import sys

import bpy

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--checkout', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
api = runpy.run_path(str(HERE / 'optics.py'))
adapter = runpy.run_path(str(HERE / 'opticore_geometry.py'))
# A metre-based existing scene exposes missing mm conversion.
scene = api['new_workspace']('OptiCore integration')
scene.unit_settings.scale_length = 1
scene.cursor.location = (1, -2, 3)
scene.cursor.rotation_euler = (.2, .4, .6)
material = bpy.data.materials.new('Generated lens source')
source_nodes = material.use_nodes
source_color = tuple(material.diffuse_color)
lens = adapter['add_opticore_lens'](args.checkout, scene=scene, material=material,
    position_mm=(15, 20, 100), diameter_mm=25.4, thickness_mm=6,
    radius1_mm=50, radius2_mm=-50)
bpy.context.view_layer.update()
assert not lens.data.validate(), 'Generated lens mesh needed repair'
assert all(math.isclose(a, b, abs_tol=1e-7) for a, b in zip(lens.dimensions, (.006, .0254, .0254)))
assert all(math.isclose(a, b, abs_tol=1e-7) for a, b in zip(lens.location, (.015, .020, .100)))
assert all(abs(angle) < 1e-7 for angle in lens.rotation_euler), 'Cursor rotation must not rotate the optical axis'
vertices = [vertex.co / .001 for vertex in lens.data.vertices]
axis = [vertex.x for vertex in vertices if math.hypot(vertex.y, vertex.z) < 1e-5]
rim = [vertex.x for vertex in vertices if math.isclose(math.hypot(vertex.y, vertex.z), 12.7, abs_tol=1e-4)]
sag = 50 - math.sqrt(50**2 - 12.7**2)
assert math.isclose(max(axis) - min(axis), 6, abs_tol=1e-5)
assert math.isclose(max(rim) - min(rim), 6 - 2*sag, abs_tol=1e-4), 'Expected biconvex profile'
edges = Counter(tuple(sorted((p.vertices[i], p.vertices[(i+1) % len(p.vertices)])))
    for p in lens.data.polygons for i in range(len(p.vertices)))
assert set(edges.values()) == {2}, 'Glass mesh must be closed'
# The documented adapter call omits material; styling must still split faces and rim.
bare_lens = adapter['add_opticore_lens'](args.checkout, scene=scene, position_mm=(60, 20, 100))
api['apply_style'](scene)
assert len(bare_lens.material_slots) == 2, 'Material-free lenses need polished-face and frosted-edge slots'
assert sum(polygon.material_index == 0 for polygon in bare_lens.data.polygons) == 6144
assert sum(polygon.material_index == 1 for polygon in bare_lens.data.polygons) == 96
bare_shader = bare_lens.material_slots[0].material.node_tree.nodes['Principled BSDF']
assert math.isclose(bare_shader.inputs['Roughness'].default_value, .1, abs_tol=1e-6)
shader = next(node for node in lens.material_slots[0].material.node_tree.nodes
              if node.bl_idname == 'ShaderNodeBsdfPrincipled')
assert shader.inputs['Transmission Weight'].default_value == 1
assert shader.inputs['Metallic'].default_value == 0
assert all(value > .9 for value in shader.inputs['Base Color'].default_value[:3])
assert material.use_nodes == source_nodes and tuple(material.diffuse_color) == source_color, 'Source material was modified'
assert lens['opl_geometry_generator'] == 'CodeFHD/OptiCore'
edge_index = next(i for i, slot in enumerate(lens.material_slots)
                  if slot.material.get('figure_material_role') == 'optic_edge')
edge_faces = [polygon for polygon in lens.data.polygons if polygon.material_index == edge_index]
assert len(edge_faces) == 96, 'Only the 96 cylindrical side faces should be frosted'
assert all(abs(polygon.normal.x) < 1e-5 for polygon in edge_faces)
assert all(all(math.isclose(math.hypot(vertices[i].y, vertices[i].z), 12.7, abs_tol=1e-4)
                   for i in polygon.vertices) for polygon in edge_faces)
edge_shader = lens.material_slots[edge_index].material.node_tree.nodes['Principled BSDF']
assert math.isclose(edge_shader.inputs['Roughness'].default_value, .55, abs_tol=1e-6)
assert edge_shader.inputs['Transmission Weight'].default_value == 1
assert math.isclose(shader.inputs['Roughness'].default_value, .1, abs_tol=1e-6)
# An explicitly supplied source shader must survive the editorial material pass.
material.use_nodes = True
material['figure_material_role'] = 'optic'
material['opl_preserve_glass'] = True
source_shader = material.node_tree.nodes.get('Principled BSDF')
source_shader.inputs['Roughness'].default_value = .07
source_shader.inputs['Transmission Weight'].default_value = 1
lens.material_slots[0].material = material
api['apply_style'](scene)
local_shader = lens.material_slots[0].material.node_tree.nodes.get('Principled BSDF')
assert math.isclose(local_shader.inputs['Roughness'].default_value, .07, abs_tol=1e-6)
assert source_shader.inputs['Roughness'].default_value == local_shader.inputs['Roughness'].default_value
assert local_shader.inputs['Transmission Weight'].default_value == 1
print('OPTICORE_CHECK_PASSED', bpy.app.version_string, len(lens.data.vertices), len(lens.data.polygons))
