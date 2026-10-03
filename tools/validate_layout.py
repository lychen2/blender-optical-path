"""Structural scene checks, not optical simulation or collision checking.
blender -b FILE.blend --python-exit-code 1 --python tools/validate_layout.py
"""
import json
import math

import bpy


def validate(scene=None):
    scene = scene or bpy.context.scene
    errors = []
    if scene.unit_settings.system == 'NONE':
        errors.append('Scene units are unspecified')
    pending = list(scene.objects)
    visited = set()
    while pending:
        obj = pending.pop()
        if obj in visited:
            continue
        visited.add(obj)
        if obj.type == 'FONT':
            errors.append(obj.name + ': 3D text is not allowed; add annotations after rendering')
        if obj.instance_type == 'COLLECTION' and obj.instance_collection:
            pending.extend(obj.instance_collection.all_objects)
    instances = [o for o in scene.objects if o.instance_type == 'COLLECTION']
    for obj in instances:
        if obj.instance_collection is None:
            errors.append(obj.name + ': missing collection')
        elif obj.instance_collection.hide_render:
            errors.append(obj.name + ': source collection hidden from render')
        if not all(math.isfinite(v) for row in obj.matrix_world for v in row):
            errors.append(obj.name + ': nonfinite transform')
        if min(abs(v) for v in obj.scale) < 1e-12:
            errors.append(obj.name + ': zero scale')
    beams = [o for o in scene.objects if o.type == 'CURVE' and 'diagram_scope' in o]
    for obj in beams:
        for spline in obj.data.splines:
            points = spline.points
            if len(points) < 2 or any((a.co-b.co).length < 1e-9 for a, b in zip(points, points[1:])):
                errors.append(obj.name + ': invalid beam segment')
    return {'scene': scene.name, 'status': 'failed' if errors else 'passed',
            'instances': len(instances), 'beams': len(beams), 'errors': errors,
            'scope': 'Units, transforms, collection visibility, no 3D text and nonzero beam segments; no optical alignment or collision solver'}


if __name__ == '__main__':
    report = validate()
    print(json.dumps(report, indent=2))
    if report['errors']:
        raise RuntimeError('; '.join(report['errors']))
