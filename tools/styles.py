"""Scene-local optical rendering presets. Coordinates and light sizes use scene units."""
import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector

PACKAGE = Path(__file__).resolve().parents[1]
CONFIG = json.loads((PACKAGE / 'library/style_presets.json').read_text())
DEFAULT_STYLE = CONFIG['default']
STYLES = tuple(CONFIG['presets'])


def list_styles():
    return [{'id': key, **value, 'default': key == DEFAULT_STYLE}
            for key, value in CONFIG['presets'].items()]


def _local_objects(scene):
    """Detach instance collections and object data before editing their materials."""
    collections = {}
    objects = {}

    def copy_collection(source):
        if source in collections:
            return collections[source]
        target = bpy.data.collections.new(source.name + ' / style copy')
        target.instance_offset = source.instance_offset.copy()
        target['opl_style_copy'] = True
        collections[source] = target
        for old in source.objects:
            if old not in objects:
                new = old.copy()
                if old.data and old.type in ('MESH', 'CURVE'):
                    new.data = old.data.copy()
                objects[old] = new
            target.objects.link(objects[old])
        for child in source.children:
            target.children.link(copy_collection(child))
        return target

    for obj in tuple(scene.objects):
        if obj.instance_collection:
            if not obj.get('opl_style_local'):
                obj.instance_collection = copy_collection(obj.instance_collection)
                obj['opl_style_local'] = True
    pending = list(objects)
    while pending:
        old = pending.pop()
        new = objects[old]
        if old.parent in objects:
            new.parent = objects[old.parent]
        if old.instance_collection:
            known = set(objects)
            new.instance_collection = copy_collection(old.instance_collection)
            pending.extend(set(objects) - known)
    result = set(scene.objects)
    pending = list(result)
    while pending:
        obj = pending.pop()
        if obj.instance_collection:
            children = set(obj.instance_collection.all_objects) - result
            result.update(children)
            pending.extend(children)
    return result


def _role(obj, material):
    explicit = material.get('figure_material_role') or obj.get('figure_material_role')
    if explicit:
        return explicit
    name = material.name.lower()
    if obj.name.startswith(('Laser resonator housing', 'Radial thermal dissipation fin')):
        return 'laser_body'
    if obj.get('opl_beam') or ' / color' in name:
        return 'beam'
    if name.startswith('background') or obj.get('opl_background'):
        return 'background'
    if 'reflective' in name or 'mirror face' in name:
        return 'mirror'
    if any(word in name for word in ('glass', 'prism', 'coating', 'optical', 'substrate', 'lens')):
        return 'optic'
    if any(word in name for word in ('anod', 'black', 'coated', 'mount')):
        return 'coated_mount'
    return 'metal'


def _surface(material, color, roughness=.5, metallic=0, transmission=0, ior=1.5, emission=0, opacity=1, unlit=False, edge_opacity=None, edge_color=None):
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    shader = nodes.new('ShaderNodeBsdfPrincipled')
    shader.inputs['Base Color'].default_value = (*color[:3], 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['IOR'].default_value = ior
    shader.inputs['Transmission Weight'].default_value = transmission
    shader.inputs['Emission Color'].default_value = (*color[:3], 1)
    shader.inputs['Emission Strength'].default_value = emission
    output = nodes.new('ShaderNodeOutputMaterial')
    surface = shader.outputs['BSDF']
    if unlit:
        channel = nodes.new('ShaderNodeEmission')
        channel.inputs['Color'].default_value = (*color[:3], 1)
        channel.inputs['Strength'].default_value = 1 + emission
        surface = channel.outputs[0]
    if edge_color is not None:
        facing = nodes.new('ShaderNodeLayerWeight')
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = .12
        ramp.color_ramp.elements[0].color = (*color[:3], 1)
        ramp.color_ramp.elements[1].position = .78
        ramp.color_ramp.elements[1].color = (*edge_color, 1)
        material.node_tree.links.new(facing.outputs['Facing'], ramp.inputs[0])
        target = channel.inputs['Color'] if unlit else shader.inputs['Base Color']
        material.node_tree.links.new(ramp.outputs['Color'], target)
    if opacity < 1:
        transparent = nodes.new('ShaderNodeBsdfTransparent')
        mix = nodes.new('ShaderNodeMixShader')
        mix.inputs[0].default_value = opacity
        if edge_opacity is not None:
            facing = nodes.new('ShaderNodeLayerWeight')
            ramp = nodes.new('ShaderNodeMapRange')
            ramp.inputs['From Min'].default_value = 0
            ramp.inputs['From Max'].default_value = 1
            ramp.inputs['To Min'].default_value = opacity
            ramp.inputs['To Max'].default_value = edge_opacity
            material.node_tree.links.new(facing.outputs['Facing'], ramp.inputs['Value'])
            material.node_tree.links.new(ramp.outputs['Result'], mix.inputs[0])
        material.node_tree.links.new(transparent.outputs[0], mix.inputs[1])
        material.node_tree.links.new(surface, mix.inputs[2])
        surface = mix.outputs[0]
    material.node_tree.links.new(surface, output.inputs['Surface'])
    material.diffuse_color = (*color[:3], 1)


def _frost_lens_edge(obj):
    """Assign rough glass only to the cylindrical rim of known singlet meshes."""
    if obj.type != 'MESH':
        return
    if obj.get('opl_geometry_generator') == 'CodeFHD/OptiCore':
        axis = 0
    elif obj.name.startswith('Polished spherical optical'):
        axis = 2
    else:
        return
    if any(slot.material and slot.material.get('figure_material_role') == 'optic_edge'
           for slot in obj.material_slots):
        return
    radial = [index for index in range(3) if index != axis]
    vertices = obj.data.vertices
    center = [(min(vertex.co[i] for vertex in vertices) + max(vertex.co[i] for vertex in vertices)) / 2
              for i in radial]
    radii = [sum((vertex.co[i] - value)**2 for i, value in zip(radial, center))**.5
             for vertex in vertices]
    radius = max(radii)
    sides = [polygon for polygon in obj.data.polygons
             if abs(polygon.normal[axis]) < 1e-4 and
             all(abs(radii[index] - radius) < radius * 1e-5 for index in polygon.vertices)]
    if not sides:
        return
    # A geometry-only OptiCore call has no slots. Reserve slot zero for its faces.
    if not obj.material_slots:
        polished = bpy.data.materials.new('Lens / polished optical faces')
        polished['figure_material_role'] = 'optic'
        obj.data.materials.append(polished)
    edge = bpy.data.materials.new('Lens / frosted cylindrical edge')
    edge['figure_material_role'] = 'optic_edge'
    _surface(edge, CONFIG['presets']['illustrated']['lens_color'], roughness=.55,
             transmission=1, ior=1.5)
    index = len(obj.data.materials)
    obj.data.materials.append(edge)
    for polygon in sides:
        polygon.material_index = index
    obj['opl_frosted_edge_faces'] = len(sides)


def apply_style(scene=None, style=DEFAULT_STYLE):
    scene = scene or bpy.context.scene
    style = CONFIG['aliases'].get(style, style)
    if style not in STYLES:
        raise ValueError(f'Unknown style: {style}; choose from {STYLES}')
    objects = _local_objects(scene)
    recipe = CONFIG['presets'][style]
    scene.render.use_freestyle = False
    for obj in objects:
        for slot in obj.material_slots:
            current = slot.material
            if current is None:
                continue
            source_name = current.get('opl_style_source', current.name)
            source = current.get('opl_style_source_material') or bpy.data.materials.get(source_name)
            if source is not None:
                slot.link = 'OBJECT'
                slot.material = source
    # Every application starts with source colors, so changing styles is reversible.
    if style != 'illustrated':
        legacy = runpy.run_path(str(PACKAGE / 'tools/graphic_styles.py'))
        setup_lighting(scene, style=style)
        scene['opl_presentation_mode'] = scene.get('opl_presentation_mode', 'floating_optics')
        for obj in objects:
            for slot in obj.material_slots:
                if slot.material:
                    source = slot.material
                    local = source.copy()
                    local['opl_style_source'] = source.name
                    local['opl_style_source_material'] = source
                    local['figure_material_role'] = _role(obj, source)
                    slot.material = local
        legacy['apply_legacy_style'](scene, style, objects)
    else:
        for obj in objects:
            _frost_lens_edge(obj)
        materials = {}
        for obj in objects:
            if obj.type not in ('MESH', 'CURVE'):
                continue
            for slot in obj.material_slots:
                old = slot.material
                if old is None:
                    continue
                role = _role(obj, old)
                key = (old, role)
                if key not in materials:
                    local = old.copy()
                    local['opl_style_source'] = old.name
                    local['opl_style_source_material'] = old
                    materials[key] = local
                    shader = old.node_tree.nodes.get('Principled BSDF') if old.use_nodes else None
                    color = tuple(shader.inputs['Base Color'].default_value) if shader else tuple(old.diffuse_color)
                    options = {}
                    if role == 'beam':
                        # Preserve the original channel through repeated style changes.
                        color = tuple(old.get('opl_channel_color', color))
                        local['opl_channel_color'] = color
                        options = {'emission': recipe['beam_emission'], 'unlit': True,
                                   'opacity': old.diffuse_color[3]}
                    elif role == 'background':
                        color = recipe['field']
                        options = {'roughness': 0, 'ior': 1.45}
                    elif role == 'optical_coating':
                        color = (.8, .8, .8)
                        options = {'opacity': .18, 'roughness': .1, 'metallic': 1, 'ior': 1.45}
                    elif role == 'optic_edge':
                        color = recipe['lens_color']
                        options = {'roughness': .55, 'transmission': 1, 'ior': 1.5}
                    elif role in ('splitter_shell', 'splitter_interface', 'optic'):
                        # Use the inspected pack's near-white transmissive Lens recipe.
                        color = recipe['lens_color']
                        options = {'roughness': recipe['lens_roughness'],
                                   'transmission': recipe['lens_transmission'],
                                   'ior': recipe['lens_ior']}
                    elif role == 'mirror':
                        color = (.8, .8, .8)
                        options = {'roughness': 0, 'metallic': 1, 'ior': 1.45}
                    elif role == 'laser_body':
                        color = (.295690566, .295690566, .295690566)
                        options = {'roughness': .362318814, 'metallic': 1, 'ior': 1.45}
                    elif role == 'coated_mount':
                        color = (.031059653, .031059653, .031059653)
                        options = {'roughness': .369565219, 'ior': 1.45}
                    else:
                        neutral = max(color[:3]) - min(color[:3]) < .2
                        if neutral and max(color[:3]) > .25:
                            # Source pack: Objective rough / Objective shiny.
                            rough = 'satin' in old.name.lower() or 'rough' in old.name.lower()
                            color = (1, 1, 1) if rough else (.8, .8, .8)
                            options = {'roughness': .3 if rough else .1, 'metallic': 1, 'ior': 1.45}
                        else:
                            options = {'roughness': .5, 'ior': 1.45}
                    if not (role == 'optic' and old.get('opl_preserve_glass')):
                        _surface(local, color, **options)
                    local['figure_material_role'] = role
                slot.link = 'OBJECT'
                slot.material = materials[key]
        setup_lighting(scene, style)
    # GN Set Material references must follow scene-local display materials.
    for obj in objects:
        if obj.get('opl_beam') and obj.material_slots:
            for modifier in obj.modifiers:
                if modifier.type == 'NODES' and modifier.node_group:
                    for node in modifier.node_group.nodes:
                        if node.bl_idname == 'GeometryNodeSetMaterial':
                            node.inputs['Material'].default_value = obj.material_slots[0].material
    scene['opl_applied_style'] = style
    scene['shading_preset'] = style
    scene['shading_scope'] = 'Illustrative display materials; physical calculations are optional'
    return {'style': style, 'changed': True, 'description': recipe['description']}


def setup_lighting(scene=None, style=DEFAULT_STYLE, target_mm=(0, 0, 100), span_mm=500):
    """Create or update owned studio lamps; preserve user lamps and scene units."""
    scene = scene or bpy.context.scene
    style = CONFIG['aliases'].get(style, style)
    if style not in STYLES:
        raise ValueError(f'Unknown style: {style}')
    if scene.unit_settings.system == 'NONE':
        raise ValueError('Configure Metric units before setting up an optical studio')
    factor = .001 / scene.unit_settings.scale_length
    target = Vector(target_mm) * factor
    span = float(span_mm) * factor
    if span <= 0:
        raise ValueError('span_mm must be positive')
    recipe = CONFIG['presets'].get(style, CONFIG['presets'][DEFAULT_STYLE])
    world = bpy.data.worlds.new('OPL studio')
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs[0].default_value = (*recipe.get('field', (.92, .935, .95)), 1)
    bg.inputs[1].default_value = recipe.get('world_strength', .65)
    if style == 'illustrated':
        # Camera sees a clean page; other rays retain the pack's dark world.
        camera_field = world.node_tree.nodes.new('ShaderNodeBackground')
        camera_field.name = 'Camera field'
        camera_field.inputs['Color'].default_value = (1, 1, 1, 1)
        camera_field.inputs['Strength'].default_value = 1
        paths = world.node_tree.nodes.new('ShaderNodeLightPath')
        mix = world.node_tree.nodes.new('ShaderNodeMixShader')
        world.node_tree.links.new(paths.outputs['Is Camera Ray'], mix.inputs[0])
        world.node_tree.links.new(bg.outputs[0], mix.inputs[1])
        world.node_tree.links.new(camera_field.outputs[0], mix.inputs[2])
        world.node_tree.links.new(mix.outputs[0], world.node_tree.nodes['World Output'].inputs['Surface'])
    scene.world = world
    # Scale the inspected pack's metre-scale studio to this drawing's span.
    # Its one square area light is 171.4524 W, size 1 m, at z=2.7807 m.
    lights = (
        ('OPL broad overhead key', (.004917 / 4.5, -.221193 / 4.5, 2.780707 / 4.5),
         171.452407837 / 4.5**2, 1 / 4.5),
        ('OPL soft fill', (-.3, -.55, .4), 171.452407837 / 4.5**2 * .35, .45),
    ) if style == 'illustrated' else (
        ('OPL broad overhead key', (.15, -.25, 1.5), 220, 1.5),
        ('OPL soft fill', (-.6, -.8, .8), 80, 1.2),
    )
    for obj in scene.objects:
        if obj.get('opl_studio_light'):
            obj.hide_render = obj.hide_viewport = obj['opl_studio_light'] not in {light[0] for light in lights}
        if obj.get('opl_studio_backdrop'):
            obj.hide_render = obj.hide_viewport = style != 'illustrated'
    for name, offset, energy, size in lights:
        obj = next((o for o in scene.objects if o.get('opl_studio_light') == name), None)
        if obj is None:
            data = bpy.data.lights.new(name, 'AREA')
            obj = bpy.data.objects.new(name, data)
            scene.collection.objects.link(obj)
        obj['opl_studio_light'] = name
        obj.location = target + Vector(offset) * span
        obj.rotation_euler = (0, 0, 0) if style == 'illustrated' and name == 'OPL broad overhead key' else (target - obj.location).to_track_quat('-Z', 'Y').to_euler()
        obj.data.shape = 'SQUARE'
        obj.data.energy = energy * span * span
        obj.data.size = size * span
    if style == 'illustrated':
        _studio_backdrop(scene, target, span)
    for obj in scene.objects:
        if any(slot.material and _role(obj, slot.material) == 'background' for slot in obj.material_slots):
            obj.visible_camera = style != 'illustrated'
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.cycles.transmission_bounces = 12
    scene.cycles.transparent_max_bounces = 16
    scene.view_settings.view_transform = 'Filmic' if style == 'illustrated' else 'AgX'
    scene.view_settings.look = 'Medium High Contrast' if style == 'illustrated' else 'None'
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    return {'style': style, 'lights': len(lights), 'span_mm': span_mm}


def _studio_backdrop(scene, target, span):
    """Add an editable curved studio wall above the existing reflective floor."""
    import math
    backdrop = next((obj for obj in scene.objects if obj.get('opl_studio_backdrop')), None)
    if backdrop is not None:
        return
    # Match the source pack's seamless sweep; orient it behind the apparatus.
    behind = Vector((0, 1, 0))
    if scene.camera:
        behind = target - scene.camera.location
        behind.z = 0
        behind.normalize()
    right = Vector((behind.y, -behind.x, 0))
    grounds = [obj for obj in scene.objects if any(slot.material and
               _role(obj, slot.material) == 'background' for slot in obj.material_slots)]
    floor = min(((obj.matrix_world @ Vector(corner)).z for obj in grounds for corner in obj.bound_box),
                default=target.z - .2 * span)
    radius = .5 * span
    profile = [(span + radius * math.sin(angle), floor + radius * (1 - math.cos(angle)))
               for angle in (i * math.pi / 48 for i in range(25))]
    if not grounds:
        profile.insert(0, (-4 * span, floor))
    profile.append((span + radius, floor + 3 * span))
    vertices = [tuple(Vector((target.x, target.y, z)) + behind * distance + right * side * 4 * span)
                for distance, z in profile for side in (-1, 1)]
    faces = [(2*i, 2*i+1, 2*i+3, 2*i+2) for i in range(len(profile)-1)]
    mesh = bpy.data.meshes.new('OPL seamless studio sweep')
    mesh.from_pydata(vertices, [], faces)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    backdrop = bpy.data.objects.new('OPL seamless studio sweep', mesh)
    backdrop['opl_studio_backdrop'] = True
    backdrop['opl_background'] = True
    scene.collection.objects.link(backdrop)
    material = bpy.data.materials.new('OPL studio sweep / source Backplane')
    material['figure_material_role'] = 'background'
    _surface(material, (1, 1, 1), roughness=0, ior=1.45)
    mesh.materials.append(material)
