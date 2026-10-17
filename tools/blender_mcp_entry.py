"""Execute inside Blender through Python or an MCP Python-execution tool."""
import json
import runpy
from pathlib import Path
import bpy

HERE = Path(__file__).resolve().parent
api = runpy.run_path(str(HERE / 'optics.py'))


def execute(request, scene):
    if not isinstance(request, dict):
        raise ValueError('OPL_MCP_REQUEST must be a JSON object')
    action = request.get('action', 'inspect')
    if action == 'list_assets':
        return api['list_assets'](request.get('query', ''))
    if action == 'list_styles':
        return api['list_styles']()
    if action == 'apply_style':
        return api['apply_style'](scene, request.get('style', 'illustrated'))
    if action == 'build_template':
        paper = runpy.run_path(str(HERE / 'paper_scene.py'))
        target = paper['build_scene'](request.get('template', 'beam-relay'),
            request.get('style', 'illustrated'), request.get('presentation', 'floating'),
            request.get('resolution', 1500))
        return api['inspect_scene'](target)
    if action == 'export_overlay':
        runpy.run_path(str(HERE / 'paper_scene.py'))['write_overlay'](
            scene, request['output'], request.get('image', 'clean.png'))
        return {'output': request['output']}
    if action == 'inspect':
        return api['inspect_scene'](scene)
    if action == 'new_workspace':
        target = api['new_workspace'](request.get('name', 'Optical workspace'))
        return {'scene': target.name, 'units': 'millimetres'}
    if action == 'add_component':
        obj = api['place_asset'](request['asset_id'], request.get('position_mm', [0, 0, 0]),
                                request.get('rotation_deg', [0, 0, 0]), request.get('name'),
                                scene, request.get('at_optical_center', False))
        return {'object': obj.name, 'asset_id': obj['opl_asset_id'], 'location': list(obj.location)}
    if action == 'add_beam':
        obj = api['add_beam'](request['points_mm'], request.get('name', 'Beam'),
                              request.get('radius_mm', 3), request.get('color', [.05, .65, .18]), scene,
                              radii_mm=request.get('radii_mm'))
        return {'object': obj.name, 'points': len(request['points_mm'])}
    if action == 'add_beam_nodes':
        obj = api['add_beam_nodes'](request['points_mm'], request.get('name', 'Beam'),
            request.get('radius_mm', 2), request.get('color', [.05, .65, .18]), scene,
            request.get('radii_mm'), request.get('profile', 'tube'), request.get('opacity', .55))
        return {'object': obj.name, 'editable': 'Geometry Nodes'}
    if action in ('add_lens', 'align_component', 'add_gaussian_beam'):
        advanced = runpy.run_path(str(HERE / 'advanced.py'))
        kwargs = dict(request.get('parameters', {}))
        kwargs['scene'] = scene
        if action == 'add_gaussian_beam':
            obj, calculation = advanced[action](**kwargs)
            return {'object': obj.name, 'calculation': calculation}
        result = advanced[action](**kwargs)
        return result if isinstance(result, dict) else {'object': result.name}
    if action == 'calculate':
        model = runpy.run_path(str(HERE / 'optical_model.py'))
        function = request['function']
        if function not in ('gaussian_beam', 'abcd_system', 'trace_paraxial_ray', 'fresnel',
                            'waveplate', 'polarizer', 'stokes'):
            raise ValueError('Unknown optical calculation: ' + str(function))
        kwargs = dict(request.get('parameters', {}))
        if function in ('waveplate', 'polarizer', 'stokes'):
            # JSON represents Jones components as [real, imaginary] pairs.
            kwargs['jones'] = tuple(complex(*value) if isinstance(value, list) else complex(value)
                                    for value in kwargs['jones'])
        value = model[function](**kwargs)
        if function in ('waveplate', 'polarizer'):
            value = [[z.real, z.imag] for z in value]
        return value
    if action in ('add_annotation', 'add_label'):
        return api['add_annotation'](request['text'], request.get('position_mm', [0, 0, 0]),
                                      request.get('size_mm', 5), scene)
    if action == 'validate':
        validator = runpy.run_path(str(HERE / 'validate_layout.py'))
        return validator['validate'](scene)
    raise ValueError('Unknown action: ' + str(action))


scene = bpy.context.scene
try:
    request = json.loads(scene.get('OPL_MCP_REQUEST', '{}'))
    result = {'ok': True, 'action': request.get('action', 'inspect') if isinstance(request, dict) else None,
              'result': execute(request, scene)}
except Exception as error:
    scene['OPL_MCP_RESULT'] = json.dumps({'ok': False, 'error': str(error)})
    print('OPL_MCP_RESULT ' + scene['OPL_MCP_RESULT'])
    raise
scene['OPL_MCP_RESULT'] = json.dumps(result, ensure_ascii=False)
print('OPL_MCP_RESULT ' + scene['OPL_MCP_RESULT'])
