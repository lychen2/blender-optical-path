"""Build editable publication illustrations from standard parts and Geometry Nodes.
blender -b --factory-startup --python-exit-code 1 --python tools/paper_scene.py -- --output /new/figure
"""
import argparse
import json
from pathlib import Path
import runpy
import sys
from xml.sax.saxutils import escape, quoteattr

import bpy
from mathutils import Matrix, Vector
from bpy_extras.object_utils import world_to_camera_view

HERE = Path(__file__).resolve().parent
api = runpy.run_path(str(HERE / 'optics.py'))
styles = runpy.run_path(str(HERE / 'styles.py'))
TEMPLATES = ('beam-relay', 'polarimetry', 'microscope')

# Floating figures use reviewed, asset-specific parts. Any unlisted object is
# mechanical or decorative and stays hidden; names match the source asset tree.
FLOATING_PARTS = {
    'assembly/dpss_laser': {
        'Emission indicator', 'End cap seam', 'End cap seam.001',
        'Identification plate', 'Laser resonator housing', 'Output aperture bezel',
        'Power cable strain relief', 'Power connector',
        *(f'Radial thermal dissipation fin{suffix}' for suffix in ('', *(f'.{i:03}' for i in range(1, 17)))),
        'Recessed output window',
    },
    'assembly/biconvex_lens': {'Polished spherical optical element'},
    'assembly/scientific_camera': {
        'C-mount flange', 'C-mount inner thread', 'C-mount inner thread.001',
        'C-mount inner thread.002', 'C-mount inner thread.003', 'C-mount inner thread.004',
        'CMOS active area', 'Camera front plate', 'Scientific camera housing',
        'Sensor ceramic package',
    },
    'assembly/half_wave_plate': {'Birefringent plate'},
    'schematic/linear_polarizer': {
        'Optical disk.002', 'Polarization visual guide', 'Polarization visual guide.001',
        'Polarization visual guide.002', 'Polarization visual guide.003',
        'Polarization visual guide.004',
    },
    'assembly/photodetector': {
        'BNC bayonet collar', 'BNC signal connector', 'Detector aperture',
        'Photodetector enclosure', 'Photosensitive area',
    },
    'schematic/condenser': {
        'Barrel segment.006', 'Barrel segment.007', 'Barrel segment.008',
        'Optical face.002', 'Optical face.003',
    },
    'assembly/microscope_objective': {'RMS10X / manufacturer objective'},
    'schematic/tube_lens': {
        'Barrel segment', 'Barrel segment.001', 'Barrel segment.002',
        'Optical face', 'Optical face.001',
    },
    'schematic/sample_slide': {'Substrate'},
}


def _display_copy(instance, presentation):
    """Copy source assets and hide supports or unreviewed mechanical details."""
    if presentation == 'full':
        return
    source = instance.instance_collection
    target = bpy.data.collections.new(instance.name + ' / presentation')
    target.instance_offset = source.instance_offset
    mapping = {}
    for old in source.all_objects:
        new = old.copy()
        new['opl_source_object_name'] = old.name
        target.objects.link(new)
        mapping[old] = new
    for old, new in mapping.items():
        if old.parent in mapping:
            new.parent = mapping[old.parent]
        ancestry = [old]
        while ancestry[-1].parent:
            ancestry.append(ancestry[-1].parent)
        support = any(item.name.startswith(('THORLABS / standard support assembly',
                                            'Standard support /')) for item in ancestry)
        support = support or new.name.startswith(('Nominal M4 mounting screw',
                                       'Socket cap screw', 'Hex socket rim', 'Socket interior',
                                       'Compact fixed objective plate', 'Objective reducer',
                                       'Objective rear retaining rim', 'Split laser saddle',
                                       'Module mounting adapter'))
        if support:
            new.hide_render = True
            new.hide_viewport = True
        if presentation == 'floating':
            keep = old.name in FLOATING_PARTS.get(instance['opl_asset_id'], set())
            new.hide_render = new.hide_viewport = not keep
    instance.instance_collection = target


def build_scene(template='beam-relay', style='illustrated', presentation='floating',
                resolution=1500):
    if template not in TEMPLATES:
        raise ValueError(f'Unknown template: {template}')
    if presentation not in ('compact', 'full', 'floating'):
        raise ValueError('presentation must be compact, full or floating')
    if type(resolution) is not int or resolution < 320:
        raise ValueError('resolution must be an integer of at least 320 pixels')
    canonical = styles['CONFIG']['aliases'].get(style, style)
    if canonical not in styles['STYLES']:
        raise ValueError(f'Unknown style: {style}')
    nodes = runpy.run_path(str(HERE / 'geometry_nodes.py'))
    scene = api['new_workspace']('Paper illustration / ' + template)
    scene['opl_presentation_mode'] = {
        'full': 'full_mechanical_assembly',
        'compact': 'compact_optics_with_mounts',
        'floating': 'floating_optics',
    }[presentation]
    scene['diagram_scope'] = 'Conceptual publication illustration; authored beam widths and display spacing'
    scene['beam_width_meaning'] = 'Illustrative channel envelope; radii are drawing controls in millimetres'
    placed = []

    def place(asset, x, label, angle=0, size=1):
        position = Vector((x, 0, 100))
        obj = api['place_asset'](asset, position, (0, 0, angle), label, scene, True)
        _display_copy(obj, presentation)
        if presentation != 'full':
            obj.matrix_world = Matrix.Translation(position) @ Matrix.Scale(size, 4) @ Matrix.Translation(-position) @ obj.matrix_world
        obj['display_scale'] = size if presentation != 'full' else 1
        placed.append(obj)
        api['add_annotation'](label, (x, 0, 175), scene=scene)
        return obj

    place('assembly/dpss_laser', -250, 'Laser', size=.65)
    if template == 'beam-relay':
        place('assembly/biconvex_lens', -130, 'L1', size=1.25)
        place('assembly/biconvex_lens', 20, 'L2', size=1.25)
        place('schematic/sample_slide', 145, 'Sample')
        place('assembly/scientific_camera', 265, 'Camera', 180, .72)
        xs, radii = [-235, -130, -55, 20, 145, 265], [1.4, 1.4, .45, 2.2, 2.2, 2.2]
        color = (.025, .34, .25)
    elif template == 'polarimetry':
        place('assembly/half_wave_plate', -100, 'HWP', size=1.2)
        place('schematic/linear_polarizer', 55, 'P', size=1.2)
        place('assembly/photodetector', 235, 'Detector', 180)
        xs, radii = [-235, -100, 55, 235], [1.5, 1.5, 1.5, 1.5]
        color = (.58, .075, .045)
    else:
        place('schematic/condenser', -130, 'Condenser', size=1.15)
        place('schematic/sample_slide', -20, 'Sample')
        place('assembly/microscope_objective', 65, 'Objective', 180, 1.2)
        place('schematic/tube_lens', 175, 'Tube lens', size=1.15)
        place('assembly/scientific_camera', 310, 'Camera', 180, .72)
        xs, radii = [-235, -130, -20, 65, 175, 310], [2.2, 2.2, .6, 2.2, 2.2, .75]
        color = (.045, .22, .5)
    nodes['add_beam_nodes']([(x, 0, 100) for x in xs], name='Editable channel',
        radius_mm=1.5, radii_mm=radii, color=color, opacity=.78, scene=scene)
    # Ground remains optional: clean transparent output also supports journal page layouts.
    mesh = bpy.data.meshes.new('Studio field')
    mesh.from_pydata([(-3000, -3000, -8), (3000, -3000, -8), (3000, 3000, -8), (-3000, 3000, -8)], [], [(0, 1, 2, 3)])
    ground = bpy.data.objects.new('Studio field', mesh)
    scene.collection.objects.link(ground)
    material = bpy.data.materials.new('Background')
    material.diffuse_color = (.92, .935, .95, 1)
    material['figure_material_role'] = 'background'
    mesh.materials.append(material)
    target = Vector((20, 0, 72 if presentation == 'full' else 100))
    camera_data = bpy.data.cameras.new('Paper overview')
    camera_data.type = 'ORTHO'
    camera_data.ortho_scale = 720
    camera_data.clip_end = 10000
    camera = bpy.data.objects.new('Paper overview', camera_data)
    scene.collection.objects.link(camera)
    camera.location = target + Vector((220, -650, 390))
    camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = camera
    scene.render.resolution_x = resolution
    scene.render.resolution_y = round(resolution * .43)
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    styles['apply_style'](scene, style)
    return scene


def write_overlay(scene, output, image='clean.png'):
    """Project metadata into editable SVG text; no Blender FONT objects."""
    scene.view_layers[0].update()
    width = scene.render.resolution_x * scene.render.resolution_percentage / 100
    height = scene.render.resolution_y * scene.render.resolution_percentage / 100
    factor = api['units'](scene)
    dark = scene.get('opl_applied_style') == 'soft-lab'
    color = '#f2f5fa' if dark else '#202c38'
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width:g}" height="{height:g}" viewBox="0 0 {width:g} {height:g}">',
             f'<image xlink:href={quoteattr(str(image))} width="{width:g}" height="{height:g}"/>',
             f'<g id="labels" font-family="Arial, Helvetica, sans-serif" font-size="{max(14, width / 75):g}" fill="{color}" text-anchor="middle">']
    for record in json.loads(scene.get('opl_post_render_annotations', '[]')):
        point = world_to_camera_view(scene, scene.camera, Vector(record['position_mm']) * factor)
        parts.append(f'<text x="{point.x * width:.2f}" y="{(1 - point.y) * height:.2f}">{escape(record["text"])}</text>')
    parts.extend(['</g>', '</svg>'])
    Path(output).write_text('\n'.join(parts) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New output directory')
    parser.add_argument('--template', choices=TEMPLATES, default='beam-relay')
    parser.add_argument('--style', choices=(*styles['STYLES'], *styles['CONFIG']['aliases']), default=styles['DEFAULT_STYLE'])
    parser.add_argument('--presentation', choices=('compact', 'full', 'floating'), default='floating')
    parser.add_argument('--resolution', type=int, default=1500)
    parser.add_argument('--samples', type=int, default=48)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    out = args.output.resolve()
    if out.exists():
        raise FileExistsError(f'Choose a new output directory: {out}')
    if args.samples < 1:
        raise ValueError('samples must be positive')
    scene = build_scene(args.template, args.style, args.presentation, args.resolution)
    validation = runpy.run_path(str(HERE / 'validate_layout.py'))['validate'](scene)
    if validation['errors']:
        raise ValueError(validation['errors'])
    out.mkdir(parents=True)
    scene.cycles.samples = args.samples
    scene.render.filepath = str(out / 'clean.png')
    write_overlay(scene, out / 'annotated.svg')
    (out / 'scene.json').write_text(json.dumps({'template': args.template, 'style': args.style,
        'presentation': args.presentation, 'scope': scene['diagram_scope'],
        'beam_width_meaning': scene['beam_width_meaning'], 'validation': validation,
        'scene': api['inspect_scene'](scene)}, indent=2) + '\n')
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'figure.blend'))
    bpy.ops.render.render(write_still=True, scene=scene.name)
    print('PAPER_SCENE_PASSED ' + str(out))


if __name__ == '__main__':
    main()
