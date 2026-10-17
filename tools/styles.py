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


def _surface(material, color, roughness=.5, metallic=0, transmission=0, ior=1.5, emission=0, opacity=1, unlit=False, edge_opacity=None, edge_color=None, graphic=False):
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
    if graphic:
        geometry = nodes.new('ShaderNodeNewGeometry')
        direction = nodes.new('ShaderNodeVectorMath')
        direction.operation = 'DOT_PRODUCT'
        direction.inputs[1].default_value = Vector((-.35, -.45, .82)).normalized()
        material.node_tree.links.new(geometry.outputs['Normal'], direction.inputs[0])
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.interpolation = 'CONSTANT'
        ramp.color_ramp.elements[0].position = 0
        ramp.color_ramp.elements[0].color = tuple(v * .62 for v in color[:3]) + (1,)
        ramp.color_ramp.elements[1].position = .25
        ramp.color_ramp.elements[1].color = (*color[:3], 1)
        ramp.color_ramp.elements.new(.72).color = tuple(v + (1 - v) * .18 for v in color[:3]) + (1,)
        material.node_tree.links.new(direction.outputs['Value'], ramp.inputs[0])
        material.node_tree.links.new(ramp.outputs['Color'], channel.inputs['Color'])
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
    if style not in ('component-pack', 'illustrated'):
        legacy = runpy.run_path(str(PACKAGE / 'tools/graphic_styles.py'))
        setup_lighting(scene, style='component-pack')
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
                        options = {'roughness': .85, 'unlit': True}
                    elif role in ('splitter_shell', 'splitter_interface', 'optic'):
                        color = recipe.get('lens_display_color', recipe['lens_color'])
                        shell = role == 'splitter_shell'
                        if style == 'component-pack':
                            options = {'opacity': .16 if shell else .48,
                                       'edge_opacity': .86, 'roughness': recipe['lens_roughness'],
                                       'ior': recipe['lens_ior'], 'metallic': .08,
                                       'edge_color': (.13, .30, .46)}
                        else:
                            options = {'opacity': .22 if shell else .56,
                                       'unlit': True, 'graphic': True}
                        # Transparency is nonrefractive so authored beam routes remain visible.
                    elif role == 'mirror':
                        color = (.68, .76, .82) if style == 'component-pack' else (.32, .55, .59)
                        options = {'roughness': .16, 'metallic': .85} if style == 'component-pack' else {'unlit': True, 'graphic': True}
                    elif role == 'coated_mount':
                        color = (.035, .045, .055) if style == 'component-pack' else (.10, .14, .17)
                        options = {'roughness': .35, 'metallic': .32} if style == 'component-pack' else {'unlit': True, 'graphic': True}
                    else:
                        neutral = max(color[:3]) - min(color[:3]) < .2
                        if neutral and max(color[:3]) > .25:
                            color = (.40, .44, .48) if style == 'component-pack' else (.48, .53, .56)
                        options = {'roughness': recipe['metal_roughness'], 'metallic': .7} if style == 'component-pack' else {'unlit': True, 'graphic': True}
                    _surface(local, color, **options)
                    local['figure_material_role'] = role
                slot.link = 'OBJECT'
                slot.material = materials[key]
        setup_lighting(scene, style)
        if style == 'illustrated':
            runpy.run_path(str(PACKAGE / 'tools/graphic_styles.py'))['component_contours'](scene, objects, style)
        else:
            scene['component_contours'] = 'Lit glass and satin metal; no graphic outlines'
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
    scene.world = world
    # Energy scales with squared scene-coordinate distance, matching Blender lamps.
    for name, offset, energy, size in (
        ('OPL broad overhead key', (.15, -.25, 1.5), 220, 1.5),
        ('OPL soft fill', (-.6, -.8, .8), 80, 1.2),
    ):
        obj = next((o for o in scene.objects if o.get('opl_studio_light') == name), None)
        if obj is None:
            data = bpy.data.lights.new(name, 'AREA')
            obj = bpy.data.objects.new(name, data)
            scene.collection.objects.link(obj)
        obj['opl_studio_light'] = name
        obj.location = target + Vector(offset) * span
        obj.rotation_euler = (target - obj.location).to_track_quat('-Z', 'Y').to_euler()
        obj.data.energy = energy * span * span * (.18 if style == 'component-pack' else 0 if style == 'illustrated' else 1)
        obj.data.size = size * span
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.cycles.transmission_bounces = 12
    scene.cycles.transparent_max_bounces = 16
    scene.view_settings.view_transform = 'Standard' if style in ('component-pack', 'illustrated') else 'AgX'
    scene.view_settings.exposure = 0
    return {'style': style, 'lights': 2, 'span_mm': span_mm}
