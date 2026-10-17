"""Exercise publication templates and JSON entry points in Blender.
blender -b --factory-startup --python-exit-code 1 --python tools/check_illustration.py
"""
import json
import math
from pathlib import Path
import runpy
import tempfile
import xml.etree.ElementTree as ET

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
api = runpy.run_path(str(HERE / 'optics.py'))
styles = runpy.run_path(str(HERE / 'styles.py'))


def request(data, scene):
    scene['OPL_MCP_REQUEST'] = json.dumps(data)
    runpy.run_path(str(HERE / 'blender_mcp_entry.py'))
    response = json.loads(scene['OPL_MCP_RESULT'])
    assert response['ok'], response
    return response['result']


original_scene = bpy.context.scene
source, _ = api['load_asset']('assembly/biconvex_lens')
source_slots = {obj: tuple(slot.material for slot in obj.material_slots) for obj in source.all_objects}
source_colors = {slot.material: (tuple(slot.material.diffuse_color), slot.material.use_fake_user)
                 for obj in source.all_objects for slot in obj.material_slots if slot.material}
# A user-owned lamp must survive recipe application.
request({'action': 'build_template', 'resolution': 800}, original_scene)
scene = bpy.context.scene
lamp = bpy.data.objects.new('User light', bpy.data.lights.new('User light', 'AREA'))
scene.collection.objects.link(lamp)
lamp.data.energy = 17
lamp.location = (123, 234, 345)
# Nested collection instances must be restyled on every application.
wrapper = bpy.data.collections.new('Nested source')
nested_source = bpy.data.objects.new('Nested lens', None)
nested_source.instance_type = 'COLLECTION'
nested_source.instance_collection = source
wrapper.objects.link(nested_source)
nested = bpy.data.objects.new('Nested example', None)
nested.instance_type = 'COLLECTION'
nested.instance_collection = wrapper
scene.collection.objects.link(nested)
beam = next(obj for obj in scene.objects if obj.get('opl_beam'))
assert beam.type == 'CURVE' and beam.modifiers[0].type == 'NODES'


def check_material():
    bpy.context.view_layer.update()
    evaluated = beam.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        assert mesh.vertices
        used = {mesh.materials[polygon.material_index].original for polygon in mesh.polygons}
        assert used == {beam.material_slots[0].material}, 'Beam display material diverged from evaluated geometry'
    finally:
        evaluated.to_mesh_clear()


def reachable_nodes(material):
    """Return shader nodes that contribute upstream to Material Output.Surface."""
    tree = material.node_tree
    output = next(node for node in tree.nodes if node.bl_idname == 'ShaderNodeOutputMaterial')
    reachable = set()
    pending = [output.inputs['Surface']]
    while pending:
        socket = pending.pop()
        for link in tree.links:
            if link.to_socket == socket and link.from_node not in reachable:
                reachable.add(link.from_node)
                pending.extend(link.from_node.inputs)
    return output, reachable


def has_link(material, from_node, from_socket, to_node, to_socket):
    return any(link.from_node == from_node and link.from_socket == from_node.outputs[from_socket]
               and link.to_node == to_node and link.to_socket == to_node.inputs[to_socket]
               for link in material.node_tree.links)


for style in ('matte', 'soft-lab', 'textbook', 'toon', 'textbook', 'journal-editorial', 'matte', 'illustrated', 'pack'):
    request({'action': 'apply_style', 'style': style}, scene)
    check_material()
    nested_copy = next(obj for obj in nested.instance_collection.objects if obj.instance_collection)
    optic = next(obj for obj in nested_copy.instance_collection.all_objects
                 if any(slot.material and 'glass' in slot.material.name.lower() for slot in obj.material_slots))
    material = next(slot.material for slot in optic.material_slots if slot.material)
    assert material.get('opl_style_source_material'), 'Nested material was not processed'
    if style == 'textbook':
        assert any(node.bl_idname == 'ShaderNodeEmission' for node in material.node_tree.nodes)
        assert all(not lineset.linestyle.thickness_modifiers.get('Ink pen')
                   for lineset in scene.view_layers[0].freestyle_settings.linesets)
    if style in ('journal-editorial', 'pack'):
        output, reachable = reachable_nodes(material)
        assert {node.bl_idname for node in reachable} == {'ShaderNodeBsdfPrincipled'}, (
            'Clear lens must use real glass without a colored emission or opacity layer')
        principled = next(iter(reachable))
        assert has_link(material, principled, 'BSDF', output, 'Surface')
        assert principled.inputs['Transmission Weight'].default_value == 1
        assert principled.inputs['Metallic'].default_value == 0
        assert math.isclose(principled.inputs['Roughness'].default_value, .1, abs_tol=1e-6)
        assert principled.inputs['IOR'].default_value == 1.5
        assert all(math.isclose(actual, expected, abs_tol=1e-6) for actual, expected in zip(
            principled.inputs['Base Color'].default_value[:3], (.906751573, .970782459, 1)))
        assert not scene.render.use_freestyle
        assert scene.view_settings.view_transform == 'Filmic'
        assert scene.view_settings.look == 'Medium High Contrast'
        assert scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value == 0
        assert scene['opl_applied_style'] == 'illustrated'
        hardware = next(slot.material for obj in nested_copy.instance_collection.all_objects
                        for slot in obj.material_slots if slot.material
                        and slot.material.get('figure_material_role') == 'coated_mount')
        _, hardware_nodes = reachable_nodes(hardware)
        assert {node.bl_idname for node in hardware_nodes} == {'ShaderNodeBsdfPrincipled'}
        assert next(iter(hardware_nodes)).inputs['Emission Strength'].default_value == 0
        # The reference's floor and curved wall must participate in actual lighting.
        backdrop = next(obj for obj in scene.objects if obj.get('opl_studio_backdrop'))
        _, backdrop_nodes = reachable_nodes(backdrop.material_slots[0].material)
        assert {node.bl_idname for node in backdrop_nodes} == {'ShaderNodeBsdfPrincipled'}
        assert not backdrop.hide_render and not backdrop.visible_camera
        assert backdrop.visible_glossy and backdrop.visible_transmission
        assert scene.world.node_tree.nodes.get('Camera field')
        edge = next(slot.material for slot in optic.material_slots if slot.material
                    and slot.material.get('figure_material_role') == 'optic_edge')
        _, edge_nodes = reachable_nodes(edge)
        edge_shader = next(node for node in edge_nodes if node.bl_idname == 'ShaderNodeBsdfPrincipled')
        assert math.isclose(edge_shader.inputs['Roughness'].default_value, .55, abs_tol=1e-6)
        edge_indices = [i for i, slot in enumerate(optic.material_slots) if slot.material == edge]
        assert len(edge_indices) == 1, 'Repeated styling must not add edge slots'
        edge_faces = [polygon for polygon in optic.data.polygons if polygon.material_index == edge_indices[0]]
        assert len(edge_faces) == optic['opl_frosted_edge_faces'] == 128
        assert all(abs(polygon.normal.z) < 1e-4 for polygon in edge_faces)
        owned_lights = [obj for obj in scene.objects if obj.get('opl_studio_light') and not obj.hide_render]
        assert len(owned_lights) == 2
        key = next(obj for obj in owned_lights if obj['opl_studio_light'] == 'OPL broad overhead key')
        fill = next(obj for obj in owned_lights if obj['opl_studio_light'] == 'OPL soft fill')
        assert math.isclose(fill.data.energy / key.data.energy, .35, abs_tol=1e-6)
    assert lamp.data.energy == 17 and tuple(lamp.location) == (123, 234, 345)
assert scene['opl_applied_style'] == 'illustrated'
assert styles['DEFAULT_STYLE'] == 'illustrated'
for obj, materials in source_slots.items():
    assert tuple(slot.material for slot in obj.material_slots) == materials, obj.name
for material, (color, fake_user) in source_colors.items():
    assert tuple(material.diffuse_color) == color, material.name
    assert material.use_fake_user == fake_user, material.name
assert not any(obj.type == 'FONT' for obj in scene.objects)
assert request({'action': 'validate'}, scene)['errors'] == []
assert request({'action': 'inspect'}, scene)['beams'][0]['geometry_nodes']
listed = request({'action': 'list_styles'}, scene)
assert len(listed) == 5
assert [style['id'] for style in listed if style['default']] == ['illustrated']
# A thin coating over a glass substrate must not become a second refracting solid.
coating = bpy.data.objects.new('Dichroic coating', bpy.data.meshes.new('Coating mesh'))
scene.collection.objects.link(coating)
coating['figure_material_role'] = 'optical_coating'
coating.data.materials.append(next(iter(source_colors)))
request({'action': 'apply_style'}, scene)
_, coating_nodes = reachable_nodes(coating.material_slots[0].material)
assert {node.bl_idname for node in coating_nodes} == {
    'ShaderNodeMixShader', 'ShaderNodeBsdfTransparent', 'ShaderNodeBsdfPrincipled'}
assert next(node for node in coating_nodes if node.bl_idname == 'ShaderNodeMixShader').inputs[0].default_value < .2
with tempfile.TemporaryDirectory(prefix='opl-overlay-') as directory:
    output = Path(directory) / 'figure.svg'
    request({'action': 'export_overlay', 'output': str(output), 'image': 'figure "draft" & final.png'}, scene)
    root = ET.parse(output).getroot()
    assert root.find('{http://www.w3.org/2000/svg}image').get('{http://www.w3.org/1999/xlink}href') == 'figure "draft" & final.png'
    texts = root.findall('.//{http://www.w3.org/2000/svg}text')
    assert [t.text for t in texts] == ['Laser', 'L1', 'L2', 'Sample', 'Camera']
    assert all(0 < float(t.attrib['x']) < 800 and 0 < float(t.attrib['y']) < 344 for t in texts)
    assert len({t.attrib['y'] for t in texts}) > 1

# Optional geometry runs only when explicitly requested through this same boundary.
lens_result = request({'action': 'add_lens', 'parameters': {'name': 'Test asphere',
    'position_mm': [0, 70, 100], 'conic1': -1, 'asphere1': [1e-6]}}, scene)
lens = scene.objects[lens_result['object']]
assert lens.type == 'MESH' and len(lens.data.polygons) > 100
assert not lens.data.validate()
alignment = request({'action': 'align_component', 'parameters': {'object_name': lens.name,
    'target_mm': [20, 70, 100], 'toward_mm': [20, 170, 100]}}, scene)
assert alignment['anchor_error_mm'] < 1e-4 and alignment['axis_error_rad'] < 1e-4
assert (lens.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized().y > .999
calculation = request({'action': 'add_gaussian_beam', 'parameters': {'wavelength_nm': 500,
    'waist_mm': .1, 'waist_position_mm': 0, 'elements': [], 'end_mm': 100,
    'origin_mm': [0, 70, 100], 'display_radius_scale': 10, 'samples': 11}}, scene)
assert math.isclose(calculation['calculation']['samples'][0]['radius_mm'], .1)
stokes = request({'action': 'calculate', 'function': 'stokes',
    'parameters': {'jones': [[1, 0], [0, 0]]}}, scene)
assert stokes == [1, 1, 0, 0], stokes
waveplate = request({'action': 'calculate', 'function': 'waveplate', 'parameters': {
    'jones': [[1, 0], [0, 0]], 'retardance_rad': math.pi, 'angle_deg': 45}}, scene)
assert math.isclose(sum(v*v for v in waveplate[0]), 0, abs_tol=1e-12)
assert math.isclose(sum(v*v for v in waveplate[1]), 1)
extra_beam = request({'action': 'add_beam_nodes', 'points_mm': [[0, 90, 100], [50, 90, 100]],
    'name': 'JSON beam', 'radii_mm': [1, 3]}, scene)
assert scene.objects[extra_beam['object']].type == 'CURVE'
with tempfile.TemporaryDirectory(prefix='opl-style-save-') as directory:
    path = str(Path(directory) / 'style.blend')
    bpy.ops.wm.save_as_mainfile(filepath=path)
    bpy.ops.wm.open_mainfile(filepath=path)
    scene = bpy.context.scene
    beam = next(obj for obj in scene.objects if obj.name == 'Editable channel')
    request({'action': 'apply_style', 'style': 'illustrated'}, scene)
    request({'action': 'apply_style', 'style': 'component-pack'}, scene)
    check_material()
# Presentation modes operate on copied collections; native source visibility must
# remain untouched across each build. Copies carry source names for assertions,
# avoiding Blender's globally suffixed object names.
paper = runpy.run_path(str(HERE / 'paper_scene.py'))
expected_modes = {
    'compact': 'compact_optics_with_mounts',
    'floating': 'floating_optics',
    'full': 'full_mechanical_assembly',
}
for template in paper['TEMPLATES']:
    default_scene = paper['build_scene'](template, resolution=320)
    assert default_scene['opl_applied_style'] == 'illustrated'
    assert default_scene['opl_presentation_mode'] == expected_modes['floating'], (
        f'{template}: build_scene default should be floating')
    default_instances = [obj for obj in default_scene.objects if obj.get('opl_asset_id')]
    assert all(any(part.get('opl_source_object_name') for part in obj.instance_collection.all_objects)
               for obj in default_instances), (
        f'{template}: default build should use floating presentation copies')
    original_flags = {}
    for mode in ('full', 'compact', 'floating'):
        presentation_scene = paper['build_scene'](template, presentation=mode, resolution=320)
        assert presentation_scene['opl_presentation_mode'] == expected_modes[mode]
        instances = {obj['opl_asset_id']: obj for obj in presentation_scene.objects
                     if obj.get('opl_asset_id')}
        assert instances
        visible_by_asset = {}
        for asset_id, instance in instances.items():
            source, _ = api['load_asset'](asset_id)
            original_flags.setdefault(asset_id, {obj.name: (obj.hide_render, obj.hide_viewport)
                for obj in source.all_objects})
            collection = instance.instance_collection
            if mode == 'full':
                # Full mode deliberately uses the original native collection.
                visible_by_asset[asset_id] = {
                    obj.name for obj in source.all_objects
                    if obj.type == 'MESH' and not obj.hide_render and not obj.hide_viewport
                }
            else:
                visible_by_asset[asset_id] = {
                    obj.get('opl_source_object_name')
                    for obj in collection.all_objects
                    if obj.type == 'MESH' and obj.get('opl_source_object_name')
                    and not obj.hide_render and not obj.hide_viewport
                }
            assert visible_by_asset[asset_id], f'{template}/{mode}/{asset_id}: no visible meshes'
            if mode == 'compact':
                support_names = {obj.name for obj in source.all_objects
                                 if obj.name.startswith('Standard support /')}
                assert not (visible_by_asset[asset_id] & support_names), (
                    f'{template}/{asset_id}: compact retained support posts')
                if asset_id == 'assembly/half_wave_plate':
                    assert {'Rotating graduated bezel', 'Rotation bearing insert'} <= visible_by_asset[asset_id], (
                        'Compact polarimetry must retain recognizable waveplate mount parts')
            if mode == 'floating':
                allowed = paper['FLOATING_PARTS'].get(asset_id, set())
                if asset_id == 'assembly/microscope_objective':
                    assert allowed == {'RMS10X / manufacturer objective'}
                    assert visible_by_asset[asset_id] == allowed, (
                        'Floating microscope objective must retain only the RMS10X optic')
                assert visible_by_asset[asset_id] <= allowed, (
                    f'{template}/{asset_id} floating mechanical meshes: '
                    f'{sorted(visible_by_asset[asset_id] - allowed)}')
                expected = allowed & {obj.name for obj in source.all_objects if obj.type == 'MESH'}
                assert visible_by_asset[asset_id] == expected, (
                    f'{template}/{asset_id} floating parts differ: '
                    f'expected {sorted(expected)}, got {sorted(visible_by_asset[asset_id])}')
                if asset_id == 'assembly/dpss_laser':
                    all_fins = {obj.name for obj in source.all_objects
                                if obj.name.startswith('Radial thermal dissipation fin')}
                    assert len(all_fins) == 17 and all_fins <= visible_by_asset[asset_id], (
                        f'Floating laser should retain all 17 native cooling fins; got {sorted(all_fins)}')
        if mode == 'full':
            full_visible = visible_by_asset
            if template == 'microscope':
                objective = instances['assembly/microscope_objective']
                assert tuple(round(v, 6) for v in objective.rotation_euler) == (0.0, 0.0, round(-math.pi, 6)), (
                    'Reviewed RMS10X orientation changed')
        elif mode == 'compact':
            compact_visible = visible_by_asset
        else:
            floating_visible = visible_by_asset
    assert any(full_visible[asset_id] != compact_visible[asset_id] for asset_id in full_visible), (
        f'{template}: compact should hide supports relative to full')
    assert any(floating_visible[asset_id] != compact_visible[asset_id] for asset_id in full_visible), (
        f'{template}: floating should differ from compact')
    for asset_id in full_visible:
        assert compact_visible[asset_id] <= full_visible[asset_id], (
            f'{template}/{asset_id}: compact exposed parts hidden in full')
    for asset_id, flags in original_flags.items():
        source, _ = api['load_asset'](asset_id)
        assert {obj.name: (obj.hide_render, obj.hide_viewport) for obj in source.all_objects} == flags, (
            f'{template}/{asset_id}: source asset hide flags changed')

print('ILLUSTRATION_CHECK_PASSED')
