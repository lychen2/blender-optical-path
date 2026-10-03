"""Scene-local render recipes for the comparison example (Blender 5.2+)."""
import bpy
from mathutils import Vector

STYLES = ('matte', 'soft-lab', 'illustrated', 'textbook', 'toon')


def component_contours(scene, objects, style):
    """Fixed-pixel component edges, or subtle cyan splitter edges in Illustrated."""
    scene.render.use_freestyle = True
    scene.render.line_thickness_mode = 'ABSOLUTE'
    scene.render.line_thickness = 1
    settings = bpy.context.view_layer.freestyle_settings
    settings.mode = 'EDITOR'
    settings.use_culling = True
    settings.crease_angle = 2.35
    for line_set in list(settings.linesets):
        settings.linesets.remove(line_set)
    groups = ({'Splitters': ((.12, .35, .39), 1.0)} if style == 'illustrated' else {
        'Optics': ((.008, .008, .008), 1.8),
        'Hardware': ((.008, .008, .008), 1.6),
    })
    collections = {}
    for role, (color, thickness) in groups.items():
        # Selection-only collections: not linked to the scene, so the library
        # instances stay intact and no source geometry is drawn twice.
        collection = bpy.data.collections.new(style + ' contour / ' + role)
        collections[role] = collection
        line_set = settings.linesets.new(role)
        line_set.select_by_collection = True
        line_set.collection = collection
        line_set.collection_negation = 'INCLUSIVE'
        line_set.select_by_edge_types = True
        line_set.select_by_visibility = True
        line_set.visibility = 'VISIBLE'
        for kind in ('silhouette', 'border', 'crease', 'ridge_valley',
                     'suggestive_contour', 'material_boundary', 'contour',
                     'external_contour', 'edge_mark'):
            setattr(line_set, 'select_' + kind,
                    kind in ('silhouette', 'border', 'crease'))
        line_set.linestyle.color = color
        line_set.linestyle.thickness = thickness
    for obj in objects:
        if obj.type != 'MESH' or obj.hide_render:
            continue
        names = ' '.join(slot.material.name.lower()
                         for slot in obj.material_slots if slot.material)
        if ' / color' in names or 'background' in names:
            continue
        if style == 'illustrated':
            if obj.get('figure_material_role') != 'splitter_shell':
                continue
            role = 'Splitters'
        else:
            role = 'Optics' if any(k in names for k in
                                  ('glass', 'prism', 'coating', 'optical', 'substrate')) else 'Hardware'
        collections[role].objects.link(obj)
    scene['component_contours'] = (
        'Subtle cyan splitter edges, 1 px' if style == 'illustrated' else
        'Visible thin black component edges, 1.6–1.8 px; beams excluded')


def apply_style(scene, style):
    if style not in STYLES:
        raise ValueError(style)
    scene['shading_preset'] = style
    # Materials are copied in this generated scene/file, never saved to library.
    objects = set(scene.objects)
    for obj in scene.objects:
        if obj.instance_collection:
            objects.update(obj.instance_collection.all_objects)
    materials = {}
    for obj in objects:
        if obj.type not in ('MESH', 'CURVE'):
            continue
        for slot in obj.material_slots:
            old = slot.material
            if old is None:
                continue
            if old not in materials:
                materials[old] = old.copy()
            slot.link = 'OBJECT'
            slot.material = materials[old]
    # Explicit roles distinguish the cube body from its internal splitting film.
    # Per-surface alpha is an editorial aid, not a measured optical property.
    if style in ('textbook', 'illustrated'):
        for obj in objects:
            role = obj.get('figure_material_role')
            if role not in ('splitter_shell', 'splitter_interface'):
                continue
            for slot in obj.material_slots:
                if slot.material is None:
                    continue
                original = slot.material
                local = original.copy()
                local['figure_material_role'] = role
                slot.material = local
                materials[local] = local
    for original, material in materials.items():
        if not material.use_nodes:
            material.use_nodes = True
        nodes = material.node_tree.nodes
        shader = nodes.get('Principled BSDF')
        if shader is None:
            continue
        name = original.name
        color = tuple(shader.inputs['Base Color'].default_value)
        beam = name.endswith(' / color')
        glass = any(k in name.lower() for k in ('glass', 'prism', 'coating', 'optical', 'substrate'))
        ground = name == 'Background'
        objective = any(k in name.lower() for k in ('rms', 'objective', 'microscope'))
        if style == 'matte':
            if beam:
                shader.inputs['Roughness'].default_value = .55
                shader.inputs['Emission Strength'].default_value = .15
        elif style == 'soft-lab':
            shader.inputs['Roughness'].default_value = .45 if not glass else .2
            if ground:
                shader.inputs['Base Color'].default_value = (.015, .023, .038, 1)
            if beam:
                shader.inputs['Emission Strength'].default_value = .8
                # Bounded faint volume inside the closed beam surface. Density
                # is tuned for this authored millimetre-coordinate illustration.
                volume = nodes.new('ShaderNodeVolumePrincipled')
                volume.inputs['Density'].default_value = .00025
                volume.inputs['Color'].default_value = color
                material.node_tree.links.new(volume.outputs['Volume'], nodes.get('Material Output').inputs['Volume'])
            elif glass:
                shader.inputs['Emission Color'].default_value = (.09,.3,.36,1)
                shader.inputs['Emission Strength'].default_value = .12
        elif style=='textbook':
            # Flat graphic colors: no specular response, refraction or received
            # shadows. Fine Freestyle edges separate the flat component faces.
            emission=nodes.new('ShaderNodeEmission')
            emission.inputs['Strength'].default_value=1
            if ground:
                emission.inputs['Color'].default_value=(1,1,1,1)
            elif beam:
                emission.inputs['Color'].default_value=color
            else:
                facing=nodes.new('ShaderNodeLayerWeight')
                ramp=nodes.new('ShaderNodeValToRGB')
                ramp.color_ramp.elements[0].color=color
                ramp.color_ramp.elements[1].color=tuple(v*.82 for v in color[:3])+(1,)
                material.node_tree.links.new(facing.outputs['Facing'],ramp.inputs[0])
                material.node_tree.links.new(ramp.outputs[0],emission.inputs['Color'])
            material.node_tree.links.new(emission.outputs[0],nodes.get('Material Output').inputs['Surface'])
        elif style=='illustrated':
            shader.inputs['Metallic'].default_value = .02
            shader.inputs['Roughness'].default_value = .72
            shader.inputs['Transmission Weight'].default_value = .08 if glass else 0
            if ground:
                color = (.82,.73,.56,1)
                shader.inputs['Base Color'].default_value = color
            if beam:
                shader.inputs['Emission Strength'].default_value = .35
            if style=='illustrated' and not ground and not glass and not beam and not objective:
                # Hardware-only edge ink; glass keeps its clear cyan silhouette.
                facing=nodes.new('ShaderNodeLayerWeight')
                ramp=nodes.new('ShaderNodeValToRGB')
                ramp.color_ramp.elements[0].position=.75
                ramp.color_ramp.elements[0].color=color
                ramp.color_ramp.elements[1].position=.96
                ramp.color_ramp.elements[1].color=(.035,.05,.06,1)
                material.node_tree.links.new(facing.outputs['Facing'],ramp.inputs[0])
                material.node_tree.links.new(ramp.outputs[0],shader.inputs['Base Color'])
        elif style=='toon':
            # Cycles-native Toon BSDF; crisp diffuse threshold, no unsupported
            # EEVEE-only Shader-to-RGB nodes in a Cycles scene.
            output=nodes.get('Material Output')
            toon=nodes.new('ShaderNodeBsdfToon');toon.component='DIFFUSE'
            toon.inputs['Color'].default_value=color
            toon.inputs['Size'].default_value=.65
            toon.inputs['Smooth'].default_value=.015
            material.node_tree.links.new(toon.outputs[0],output.inputs['Surface'])
            if not beam and not ground and not objective:
                # View-dependent contour, not a screen-space stroke. Narrow
                # grazing-angle band; cyan edges for optics rather than black.
                facing=nodes.new('ShaderNodeLayerWeight')
                ramp=nodes.new('ShaderNodeValToRGB')
                ramp.color_ramp.elements[0].position=.76
                ramp.color_ramp.elements[0].color=color
                ramp.color_ramp.elements[1].position=.94
                ramp.color_ramp.elements[1].color=(.025,.18,.22,1) if glass else (.025,.035,.045,1)
                material.node_tree.links.new(facing.outputs['Facing'],ramp.inputs[0])
                material.node_tree.links.new(ramp.outputs[0],toon.inputs['Color'])
            if beam or ground:
                emission=nodes.new('ShaderNodeEmission')
                emission.inputs['Color'].default_value=(.8,.84,.88,1) if ground else color
                emission.inputs['Strength'].default_value=2 if ground else .85
                material.node_tree.links.new(emission.outputs[0],output.inputs['Surface'])
        role = material.get('figure_material_role')
        if style in ('textbook', 'illustrated') and role in ('splitter_shell', 'splitter_interface'):
            output = nodes.get('Material Output')
            surface = output.inputs['Surface'].links[0].from_socket
            transparent = nodes.new('ShaderNodeBsdfTransparent')
            mix = nodes.new('ShaderNodeMixShader')
            # Four prism surfaces overlap in some views; a low per-surface
            # opacity keeps the un-refracted internal paths visible.
            shell_opacity, film_opacity = (.09, .24) if style == 'textbook' else (.26, .34)
            mix.inputs[0].default_value = shell_opacity if role == 'splitter_shell' else film_opacity
            if style == 'illustrated' and role == 'splitter_shell':
                shader.inputs['Base Color'].default_value = (.12, .50, .60, 1)
            material.node_tree.links.new(transparent.outputs[0], mix.inputs[1])
            material.node_tree.links.new(surface, mix.inputs[2])
            material.node_tree.links.new(mix.outputs[0], output.inputs['Surface'])
            shader.inputs['Transmission Weight'].default_value = 0
            material['illustrative_surface_opacity'] = mix.inputs[0].default_value
    if style in ('textbook', 'illustrated'):
        component_contours(scene, objects, style)
    bg=scene.world.node_tree.nodes['Background']
    lights=[o for o in scene.objects if o.type=='LIGHT']
    if style=='soft-lab':
        bg.inputs[0].default_value=(.07,.11,.19,1);bg.inputs[1].default_value=.25
        lights[0].location=(200,200,450);lights[0].data.energy*=.7
        lights[1].data.energy*=.18
    elif style=='illustrated':
        bg.inputs[0].default_value=(.85,.8,.69,1);bg.inputs[1].default_value=.65
        lights[0].location=(-200,100,650)
    elif style=='textbook':
        scene.view_settings.view_transform='Standard'
        bg.inputs[0].default_value=(1,1,1,1);bg.inputs[1].default_value=.8
        for light in lights:
            light.data.energy*=.5;light.data.size=1100
    elif style=='toon':
        bg.inputs[1].default_value=.18
        lights[0].data.size=90;lights[0].data.energy*=.45
        lights[1].data.energy*=.06
    target=Vector((100,-55,98) if scene['opl_presentation_mode']=='floating_optics' else (120,-75,45))
    for light in lights:
        light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
    scene['shading_scope']='Illustrative appearance; geometry and channel semantics unchanged'
