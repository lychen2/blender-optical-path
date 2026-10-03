"""Build and render a minimal placement example using only this portable bundle.
blender -b --factory-startup --python-exit-code 1 --python tools/example_scene.py -- --output /new/example
This is a placement example, not a validated image-forming prescription.
"""
import argparse
import json
from pathlib import Path
import runpy
import sys

import bpy
from mathutils import Vector

PACKAGE = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New output directory')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f'Choose a new output directory: {output}')
    api = runpy.run_path(str(PACKAGE/'tools/optics.py'))
    scene = api['new_workspace']('Placement example')
    api['place_asset']('assembly/biconvex_lens', (0,0,100),
                       name='L1', scene=scene, at_optical_center=True)
    api['place_asset']('assembly/scientific_camera', (160,0,100),
                       rotation_deg=(0,0,180), name='Detector',
                       scene=scene, at_optical_center=True)
    api['add_beam']([(-120,0,100),(0,0,100),(150,0,100)], scene=scene)
    report = runpy.run_path(str(PACKAGE/'tools/validate_layout.py'))['validate'](scene)
    if report['errors']:
        raise ValueError(report['errors'])
    camera_data = bpy.data.cameras.new('Overview camera')
    camera_data.type = 'ORTHO'
    camera_data.ortho_scale = 420
    camera_data.clip_end = 10000
    camera = bpy.data.objects.new('Overview camera', camera_data)
    scene.collection.objects.link(camera)
    target = Vector((40,0,55))
    camera.location = target + Vector((240,-450,300))
    camera.rotation_euler = (target-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.camera = camera
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'MATERIAL'
    scene.display.shading.show_cavity = True
    scene.display.shading.background_type = 'WORLD'
    scene.world = bpy.data.worlds.new('Example background')
    scene.world.color = (.9,.9,.9)
    scene.view_settings.view_transform = 'Standard'
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    output.mkdir(parents=True)
    scene.render.filepath = str(output/'preview.png')
    bpy.ops.wm.save_as_mainfile(filepath=str(output/'example.blend'))
    bpy.ops.render.render(write_still=True, scene=scene.name)
    (output/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('EXAMPLE_SCENE_PASSED', json.dumps({'output':str(output), **report}))


if __name__ == '__main__':
    main()
