"""Shared, non-destructive bpy operations for the UI, Python console and MCP.

Load with runpy.run_path(...); functions do not require UI selection or operators.
All public coordinates are in millimetres, converted to the current scene units.
"""
import gzip
import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

PACKAGE = Path(__file__).resolve().parents[1]
LIBRARY = PACKAGE / 'library' / 'Optical_Components.blend'
INDEX = PACKAGE / 'library' / 'index.json'


def finite_vector(value, name):
    if len(value) != 3 or any(isinstance(v, bool) or not isinstance(v, (int, float))
                              or not math.isfinite(v) for v in value):
        raise ValueError(f'{name} must contain three finite numbers')
    return Vector(value)


def units(scene):
    if scene.unit_settings.system == 'NONE':
        raise ValueError('Set scene units first: use new_workspace() or configure Metric units')
    return .001 / scene.unit_settings.scale_length


def list_assets(query=''):
    records = json.loads(INDEX.read_text())['assets']
    query = query.casefold()
    return [a for a in records if query in json.dumps(a).casefold()]


def asset_record(asset_id):
    return next((a for a in list_assets() if a['id'] == asset_id), None)


def load_asset(asset_id):
    record = asset_record(asset_id)
    if record is None:
        raise ValueError(f'Unknown asset ID: {asset_id}; use list_assets()')
    # Use a stable ID, not Blender's potentially suffixed name.
    for col in bpy.data.collections:
        if col.get('opl_asset_id') == asset_id and col.library is None:
            return col, record
    with bpy.data.libraries.load(str(LIBRARY), link=False) as (source, target):
        if record['collection'] not in source.collections:
            raise ValueError(f'Missing collection in library: {record["collection"]}')
        target.collections = [record['collection']]
    return target.collections[0], record


def new_workspace(name='Optical workspace'):
    scene = bpy.data.scenes.new(name)
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = .001
    scene.unit_settings.length_unit = 'MILLIMETERS'
    scene['diagram_scope'] = 'Editable optical schematic; beam paths are authored curves.'
    if bpy.context.window:
        bpy.context.window.scene = scene
    return scene


def place_asset(asset_id, position_mm=(0, 0, 0), rotation_deg=(0, 0, 0),
                name=None, scene=None, at_optical_center=False):
    """Place at native base origin, or at a documented assembly optical reference.

    CAD origins remain native. Optical reference points are nominal schematic
    anchors, not calibrated interface locations. Mechanical/CAD assets reject
    optical-center placement until their anchors are measured.
    """
    scene = scene or bpy.context.scene
    position = finite_vector(position_mm, 'position_mm')
    rotation = finite_vector(rotation_deg, 'rotation_deg')
    factor = units(scene)
    record = asset_record(asset_id)
    if record is None:
        raise ValueError(f'Unknown asset ID: {asset_id}')
    if at_optical_center and record['anchor_mm'] is None:
        raise ValueError(f'{asset_id} has no measured optical anchor; use native-origin placement')
    col, record = load_asset(asset_id)
    from mathutils import Euler
    rot = Euler(tuple(math.radians(x) for x in rotation), 'XYZ').to_matrix().to_4x4()
    anchor = Vector(record['anchor_mm']) if at_optical_center else Vector((0, 0, 0))
    obj = bpy.data.objects.new(name or record['label'], None)
    obj.instance_type = 'COLLECTION'
    obj.instance_collection = col
    obj.matrix_world = (Matrix.Translation(position * factor) @ rot
                        @ Matrix.Scale(factor, 4) @ Matrix.Translation(-anchor + col.instance_offset))
    obj.empty_display_size = 10
    obj['opl_asset_id'] = asset_id
    obj['part_number'] = record.get('sku', '')
    obj['placement_reference'] = 'nominal optical reference' if at_optical_center else 'native origin'
    obj['source'] = record['provenance']
    scene.collection.objects.link(obj)
    return obj


def add_beam(points_mm, name='Beam', radius_mm=3, color=(.05, .65, .18), scene=None,
             radii_mm=None):
    scene = scene or bpy.context.scene
    points = [finite_vector(p, 'point') for p in points_mm]
    if len(points) < 2 or any((a-b).length < 1e-9 for a, b in zip(points, points[1:])):
        raise ValueError('Beam needs at least two points and no zero-length segment')
    if not math.isfinite(radius_mm) or radius_mm <= 0:
        raise ValueError('radius_mm must be positive and finite')
    radii = list(radii_mm) if radii_mm is not None else [radius_mm] * len(points)
    if len(radii) != len(points) or any(isinstance(r, bool) or not isinstance(r, (int, float))
                                       or not math.isfinite(r) or r <= 0 for r in radii):
        raise ValueError('radii_mm must contain one positive finite radius per point')
    rgb = finite_vector(color, 'color')
    if any(v < 0 or v > 1 for v in rgb):
        raise ValueError('Color channels must be between 0 and 1')
    factor = units(scene)
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = radius_mm * factor
    curve.bevel_resolution = 3
    spline = curve.splines.new('POLY')
    spline.points.add(len(points)-1)
    curve.use_fill_caps = True
    for p, co, radius in zip(spline.points, points, radii):
        p.co = (* (co * factor), 1)
        p.radius = radius / radius_mm
    material = bpy.data.materials.new(name + ' / color')
    material.diffuse_color = (*rgb, 1)
    material.use_nodes = True
    shader = material.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*rgb, 1)
    shader.inputs['Emission Color'].default_value = (*rgb, 1)
    shader.inputs['Emission Strength'].default_value = .4
    curve.materials.append(material)
    obj = bpy.data.objects.new(name, curve)
    scene.collection.objects.link(obj)
    obj['radii_mm'] = json.dumps(radii)
    obj['diagram_scope'] = 'Authored schematic envelope; no ray tracing or propagation calculation'
    return obj


def add_annotation(body, position_mm=(0, 0, 0), size_mm=5, scene=None):
    """Record a 2D post-render annotation without creating a 3D text object.

    Optical components and beams stay free of labels in the Blender scene. The
    returned record can be used by a compositor or graphics editor after the
    render. Positions are millimetres in the scene's optical reference frame.
    """
    scene = scene or bpy.context.scene
    point = finite_vector(position_mm, 'position_mm')
    if not isinstance(body, str) or not body.strip():
        raise ValueError('Annotation text must be nonempty')
    if not math.isfinite(size_mm) or size_mm <= 0:
        raise ValueError('size_mm must be positive and finite')
    key = 'opl_post_render_annotations'
    records = json.loads(scene.get(key, '[]'))
    record = {'text': body.strip(), 'position_mm': list(point), 'size_mm': size_mm,
              'placement': 'add after render; no Blender FONT object'}
    records.append(record)
    scene[key] = json.dumps(records, ensure_ascii=False)
    return record


# Compatibility name: it records post-render data and never creates 3D text.
add_label = add_annotation


def import_cad(mesh_path, label=None):
    """Import the mesh interchange emitted by thorlabs.py; native mm retained.

    The returned collection is unlinked: place it by instance after inspecting
    its coordinate frame. No automated optical-axis inference is performed.
    """
    path = Path(mesh_path).resolve()
    with gzip.open(path, 'rt') as stream:
        data = json.load(stream)
    if data.get('units') != 'mm' or not data.get('solids'):
        raise ValueError('CAD interchange must have units=mm and nonempty solids')
    # Validate at the external file boundary before creating Blender datablocks.
    for solid in data['solids']:
        vertices, faces = solid['vertices'], solid['faces']
        for vertex in vertices:
            finite_vector(vertex, 'CAD vertex')
        if not vertices or not faces:
            raise ValueError('CAD solid is empty')
        for face in faces:
            if len(face) != 3 or any(type(i) is not int or i < 0 or i >= len(vertices) for i in face):
                raise ValueError('Invalid CAD triangle index')
        # Rounded legacy tessellations can collapse triangle corners. Do not emit
        # these zero-area polygons; retain a count on the derivative collection.
        valid = [face for face in faces if len(set(face)) == 3 and
                 (Vector(vertices[face[1]]) - Vector(vertices[face[0]])).cross(
                     Vector(vertices[face[2]]) - Vector(vertices[face[0]])).length > 1e-12]
        solid['dropped_degenerate_triangles'] = len(faces) - len(valid)
        solid['faces'] = valid
    col = bpy.data.collections.new(label or 'Thorlabs / ' + data['sku'])
    root = bpy.data.objects.new(data['sku'] + ' / native origin', None)
    col.objects.link(root)
    material = bpy.data.materials.get('CAD / neutral') or bpy.data.materials.new('CAD / neutral')
    material.diffuse_color = (.13, .16, .20, 1)
    for i, solid in enumerate(data['solids']):
        mesh = bpy.data.meshes.new(f'{data["sku"]} / solid {i}')
        mesh.from_pydata(solid['vertices'], [], solid['faces'])
        mesh.update()
        mesh.materials.append(material)
        obj = bpy.data.objects.new(mesh.name, mesh)
        obj.parent = root
        col.objects.link(obj)
    col['dropped_degenerate_triangles'] = sum(s['dropped_degenerate_triangles'] for s in data['solids'])
    col['part_number'] = data['sku']
    col['manufacturer'] = 'Thorlabs'
    col['source_sha256'] = data.get('source_sha256', '')
    col['label_treatment'] = 'reviewed engraving removal' if data.get('lettering_removed') else 'source geometry retained'
    col['coordinate_frame'] = 'Native STEP coordinates in mm; optical axis uncalibrated'
    col['source_step'] = data['source']
    col.asset_mark()
    col.asset_data.description = f'Thorlabs {data["sku"]}; native STEP millimetres; optical anchor uncalibrated'
    col.use_fake_user = True
    return col


def inspect_scene(scene=None):
    scene = scene or bpy.context.scene
    return {'scene': scene.name, 'unit_system': scene.unit_settings.system,
            'scale_length': scene.unit_settings.scale_length,
            'instances': [{'name': o.name, 'asset_id': o.get('opl_asset_id'),
                           'collection': o.instance_collection.name,
                           'position_scene_units': list(o.location)}
                          for o in scene.objects if o.instance_type == 'COLLECTION' and o.instance_collection],
            'objects': len(scene.objects)}
