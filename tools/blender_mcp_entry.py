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
                              request.get('radius_mm', .6), request.get('color', [.05, .65, .18]), scene)
        return {'object': obj.name, 'points': len(request['points_mm'])}
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
