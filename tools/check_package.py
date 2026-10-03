"""Integration checks for the saved library and shared Python/MCP API.
blender -b --factory-startup --python-exit-code 1 --python tools/check_package.py
"""
import json
from pathlib import Path
import runpy
import bpy
from mathutils import Vector

PACKAGE = Path(__file__).resolve().parents[1]
index = json.loads((PACKAGE/'library/index.json').read_text())
# Exercise appending before opening the library (opening alone only tests reuse).
api = runpy.run_path(str(PACKAGE/'tools/optics.py'))
fresh_scene = api['new_workspace']('Fresh append test')
fresh_obj = api['place_asset']('assembly/microscope_objective', (0,0,100),
                               scene=fresh_scene, at_optical_center=True)
fresh_error_mm = (fresh_obj.matrix_world @ Vector((0,0,100))-Vector((0,0,100))).length
# Blender stores transforms and scale_length as single-precision floats.
assert fresh_error_mm < 1e-4, fresh_error_mm
assert fresh_obj.instance_collection.all_objects
bpy.ops.wm.open_mainfile(filepath=str(PACKAGE/'library/Optical_Components.blend'))
assert len(index['assets']) == 70
assert len({a['id'] for a in index['assets']}) == 70
catalog = (PACKAGE/'library/blender_assets.cats.txt').read_text()
assert all(name in bpy.data.scenes for name in index['scenes'])
checks=[]
support_count=0
for item in index['assets']:
    col=bpy.data.collections[item['collection']]
    assert col.asset_data and col.asset_data.catalog_id in catalog
    assert col.get('opl_asset_id') == item['id']
    assert not col.hide_render
    assert not any(o.type=='FONT' for o in col.all_objects), item['id']
    assert (PACKAGE/'library'/item['source_record']).exists()
    for obj in col.objects:
        if obj.get('mount_height_mm') is not None:
            assert obj['holder_sku']=='PH50_M' and obj['post_sku']=='TR50_M'
            assert obj['post_insertion_mm']>=12
            if item['kind']=='mounted_assembly':
                assert item['anchor_mm']==[0,0,100]
            support_count+=1
    if item['kind']=='mounted_assembly' and any(o.get('mount_height_mm') is not None for o in col.objects):
        for obj in col.objects:
            if obj.name.startswith(('Socket cap screw /','Hex socket rim','Socket interior')):
                center=obj.matrix_world @ (sum((Vector(v) for v in obj.bound_box),Vector())/8)
                assert center.z >= 65, (item['id'],obj.name,tuple(center))
    if item['kind']=='offline_schematic_module':
        assert not any(o.get('support_length_mm') for o in col.objects), item['id']
        if any(o.get('mount_height_mm') is not None for o in col.objects):
            assert any(o.name.startswith('Module mounting adapter') for o in col.objects), item['id']
    if item['id'] in ('assembly/kinematic_mirror', 'assembly/gold_mirror'):
        assert col['mirror_mount_sku'] == 'POLARIS-K1S5'
        assert not any(o.name.startswith('Official optic / KM100') for o in col.all_objects)
        # Evaluate uninstanced source objects in a temporary linked collection.
        active_scene = bpy.context.scene
        active_scene.collection.children.link(col)
        bpy.context.view_layer.update()
        mount = next(o for o in col.all_objects if o.get('mount_source_asset') == 'thorlabs/POLARIS-K1S5')
        from mathutils import Matrix
        transform = Matrix(json.loads(mount['native_to_assembly']))
        native_seat = Vector((25.371151733613, 3.224097397248, 32.026709096853))
        seat = transform @ native_seat
        assert (transform.to_3x3() @ Vector((0,-1,0)) - Vector((0,0,-1))).length < 1e-5
        post = next(o for o in col.all_objects if o.name.startswith('Standard support / TR50_M / 0'))
        bounds = [post.matrix_world @ Vector(v) for v in post.bound_box]
        center = sum(bounds, Vector()) / 8
        assert abs(center.x-seat.x) < 1e-4 and abs(center.y-seat.y) < 1e-4
        assert abs(max(v.z for v in bounds)-seat.z) < 1e-4
        assert abs(seat.z-74.6) < 1e-4
        assert any(o.name.startswith('Nominal M4 mounting screw / head') for o in col.all_objects)
        assert not any(o.name.startswith('Standard support / TR50_M / 1') for o in col.all_objects)
        active_scene.collection.children.unlink(col)
    if item['id'] in ('assembly/biconvex_lens','assembly/biconcave_lens'):
        assert col['lens_mount_sku'] == 'KM100'
        assert not any(o.name.startswith('Official optic / LMR1_M') for o in col.all_objects)
        active_scene=bpy.context.scene
        active_scene.collection.children.link(col);bpy.context.view_layer.update()
        post=next(o for o in col.all_objects if o.name.startswith('Standard support / TR50_M / 0'))
        assert abs(max((post.matrix_world @ Vector(v)).z for v in post.bound_box)-74.6)<1e-4
        assert any(o.get('mount_source_asset')=='thorlabs/KM100' for o in col.all_objects)
        active_scene.collection.children.unlink(col)
    if item['id']=='assembly/microscope_objective':
        assert col['objective_sku']=='RMS10X'
        assert any(o.get('objective_source_asset')=='thorlabs/RMS10X' for o in col.all_objects)
        assert not any(o.name.startswith('Objective satin cylindrical body') for o in col.all_objects)
    checks.append(item['id'])
api=runpy.run_path(str(PACKAGE/'tools/optics.py'))
original_scenes=set(bpy.data.scenes)
scene=api['new_workspace']('Package integration test')
a=api['place_asset']('assembly/biconvex_lens',(20,30,100),rotation_deg=(0,0,90),scene=scene,at_optical_center=True)
assert (a.matrix_world @ Vector((0,0,100))-Vector((20,30,100))).length<1e-5
b=api['place_asset']('assembly/biconvex_lens',(200,30,100),scene=scene,at_optical_center=True)
assert a.instance_collection==b.instance_collection
scene.unit_settings.scale_length=1
c=api['place_asset']('assembly/kinematic_mirror',(200,0,100),scene=scene,at_optical_center=True)
assert (c.matrix_world @ Vector((0,0,100))-Vector((.2,0,.1))).length<1e-6
assert abs(c.scale.x-.001)<1e-8
api['add_beam']([(0,0,100),(200,0,100)],scene=scene)
envelope=api['add_beam']([(0,0,100),(100,0,100),(200,0,100)],scene=scene,radii_mm=[4,.8,3])
assert all(abs(p.radius*3-r)<1e-5 for p,r in zip(envelope.data.splines[0].points,[4,.8,3]))
for bad in ([1], [1,0,2], [1,float('nan'),2], [1,True,2]):
    try:api['add_beam']([(0,0,0),(1,0,0),(2,0,0)],scene=scene,radii_mm=bad)
    except ValueError:pass
    else:raise AssertionError('Invalid envelope radii accepted')
api['add_annotation']('M1',(200,-20,0),scene=scene)
assert not any(o.type=='FONT' for o in scene.objects)
assert json.loads(scene['opl_post_render_annotations'])[0]['text']=='M1'
for kwargs in [dict(asset_id='bad'),dict(asset_id='thorlabs/LMR1/M',at_optical_center=True),
               dict(asset_id='assembly/biconvex_lens',position_mm=(float('nan'),0,0))]:
    try:api['place_asset'](scene=scene,**kwargs)
    except ValueError:pass
    else:raise AssertionError('Invalid request accepted')
try:api['add_beam']([(0,0,0),(0,0,0)],scene=scene)
except ValueError:pass
else:raise AssertionError('Zero-length beam accepted')
validator=runpy.run_path(str(PACKAGE/'tools/validate_layout.py'))
assert validator['validate'](scene)['status']=='passed'
scene['OPL_MCP_REQUEST']=json.dumps({'action':'add_component','asset_id':'thorlabs/LMR1/M','position_mm':[0,0,0]})
runpy.run_path(str(PACKAGE/'tools/blender_mcp_entry.py'))
assert json.loads(scene['OPL_MCP_RESULT'])['ok']
scene['OPL_MCP_REQUEST']=json.dumps({'action':'add_annotation','text':'Detector'})
runpy.run_path(str(PACKAGE/'tools/blender_mcp_entry.py'))
assert json.loads(scene['OPL_MCP_RESULT'])['result']['text']=='Detector'
assert not any(o.type=='FONT' for o in scene.objects)
font=bpy.data.curves.new('Forbidden test label','FONT')
text_obj=bpy.data.objects.new('Forbidden test label',font)
scene.collection.objects.link(text_obj)
assert validator['validate'](scene)['status']=='failed'
bpy.data.objects.remove(text_obj,do_unlink=True)
bpy.data.curves.remove(font)
scene['OPL_MCP_REQUEST']=json.dumps({'action':'validate'})
runpy.run_path(str(PACKAGE/'tools/blender_mcp_entry.py'))
assert json.loads(scene['OPL_MCP_RESULT'])['result']['status']=='passed'
scene['OPL_MCP_REQUEST']=json.dumps({'action':'bad'})
try:runpy.run_path(str(PACKAGE/'tools/blender_mcp_entry.py'))
except ValueError:pass
else:raise AssertionError('Invalid MCP action accepted')
assert not json.loads(scene['OPL_MCP_RESULT'])['ok']
assert original_scenes.issubset(set(bpy.data.scenes))
report={'status':'passed','blender':bpy.app.version_string,'asset_count':len(checks),
        'fresh_library_append':True,'fresh_placement_error_mm':fresh_error_mm,
        'placement_tolerance_mm':0.0001,
        'standard_support_assemblies_checked':support_count,'asset_catalogs':True,
        'no_font_objects_in_components':True,'mm_and_metre_placement':True,
        'legacy_floating_support_ornaments_removed':True,
        'module_placeholder_supports_replaced':True,
        'source_collection_reuse':True,'non_destructive_workspace':True,
        'invalid_request_rejection':True,'mcp_python_entrypoint':True,
        'live_mcp_transport':'not tested; no connected server exposed'}
report['post_render_annotations_only'] = True
report['polaris_mounts_seated_upright'] = True
report['km100_lens_mounts_and_rms10x_objective'] = True
report['variable_radius_envelope'] = True
print('PACKAGE_CHECK_PASSED '+json.dumps(report))
