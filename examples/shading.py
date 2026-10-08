"""Scene-local render recipes for the comparison example (Blender 5.2+)."""
import bpy
from mathutils import Vector

STYLES = ('matte', 'soft-lab', 'illustrated', 'textbook', 'toon')

# Cel / Toon: hard tone bands from one fixed key direction,
# cool-shifted shadows, pale beam cores, fixed glints and
# calligraphic ink on a flat butter-yellow field. Surfaces are emission-only,
# so lamps, world light and GI cannot soften the bands.
TOON_KEY = Vector((.547, .378, .747)).normalized()
TOON_GLINT_DIR = Vector((0, -.309, .951)).normalized()
TOON_BANDS = {'optic': (0, .66), 'hardware': (0, .66), 'beam': (0, .95)}
TOON_ACCENT = {'optic': .985, 'hardware': .985, 'beam': .95}


def srgb_to_linear(c):
    return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4


def linear_to_srgb(c):
    c = max(0.0, min(1.0, c))
    return c * 12.92 if c <= .0031308 else 1.055 * c ** (1 / 2.4) - .055


def display_color(r, g, b):
    return tuple(srgb_to_linear(v) for v in (r, g, b)) + (1,)


TOON_FIELD = display_color(1.0, .945, .75)
TOON_INK = {'Optics': display_color(.05, .30, .36),
            'Hardware': display_color(.10, .11, .16)}


def toon_tones(color, role):
    """Shadow, base, lit and accent tones in display space.

    Beams keep their hue: shadows only darken and the accent is a pale core.
    Neutral parts take a cool shadow shift; saturated parts keep their hue.
    """
    base = [linear_to_srgb(v) for v in color[:3]]
    if role == 'beam':
        shadow = [v * .60 for v in base]
        lit = [v + (1 - v) * .30 for v in base]
        accent = [v + (1 - v) * .55 for v in base]
    else:
        weight = .15 if max(base) - min(base) > .45 else .5
        cool = (.62, .72, 1.0)
        shadow = [v * .72 * (1 - weight + weight * t) for v, t in zip(base, cool)]
        luma = .2126 * base[0] + .7152 * base[1] + .0722 * base[2]
        lift = .10 + .30 * luma
        lit = [v + (1 - v) * lift for v in base]
        accent = [v + (1 - v) * .85 for v in base]
    return tuple(display_color(*tone) for tone in (shadow, base, lit, accent))


def toon_surface(material, color, role, shadow_band=True):
    """Constant-ramp N.L bands into Emission plus one hard accent.

    Optics and hardware use a fixed glint direction. Beams project the view
    into their local cross-section to keep cores visible on oblique segments.
    """
    tree = material.node_tree
    nodes, links = tree.nodes, tree.links
    shadow, base, lit, accent = toon_tones(color, role)
    if not shadow_band:
        # Thin translucent shells stay clean instead of mixing a dark band
        # with the field behind them.
        shadow = base
    low, high = TOON_BANDS[role]
    geometry = nodes.new('ShaderNodeNewGeometry')
    n_dot_l = nodes.new('ShaderNodeVectorMath')
    n_dot_l.operation = 'DOT_PRODUCT'
    n_dot_l.inputs[1].default_value = TOON_KEY
    links.new(geometry.outputs['Normal'], n_dot_l.inputs[0])
    remap = nodes.new('ShaderNodeMath')
    remap.operation = 'MULTIPLY_ADD'
    remap.inputs[1].default_value = .5
    remap.inputs[2].default_value = .5
    links.new(n_dot_l.outputs['Value'], remap.inputs[0])
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.interpolation = 'CONSTANT'
    stops = ramp.color_ramp.elements
    stops[0].position, stops[0].color = 0, shadow
    stops[1].position, stops[1].color = .5 + .5 * low, base
    stops.new(.5 + .5 * high).color = lit
    links.new(remap.outputs[0], ramp.inputs['Fac'])
    cel = nodes.new('ShaderNodeEmission')
    links.new(ramp.outputs['Color'], cel.inputs['Color'])
    n_dot_a = nodes.new('ShaderNodeVectorMath')
    n_dot_a.operation = 'DOT_PRODUCT'
    if role == 'beam':
        # Cycles supplies the longitudinal tangent for these beveled curves.
        # Remove the view component along the tube before testing its core.
        tangent = nodes.new('ShaderNodeTangent')
        tangent.direction_type = 'UV_MAP'
        tangent.uv_map = 'UVMap'
        along = nodes.new('ShaderNodeVectorMath')
        along.operation = 'PROJECT'
        links.new(geometry.outputs['Incoming'], along.inputs[0])
        links.new(tangent.outputs['Tangent'], along.inputs[1])
        across = nodes.new('ShaderNodeVectorMath')
        across.operation = 'SUBTRACT'
        links.new(geometry.outputs['Incoming'], across.inputs[0])
        links.new(along.outputs['Vector'], across.inputs[1])
        view = nodes.new('ShaderNodeVectorMath')
        view.operation = 'NORMALIZE'
        links.new(across.outputs['Vector'], view.inputs[0])
        links.new(view.outputs['Vector'], n_dot_a.inputs[1])
    else:
        n_dot_a.inputs[1].default_value = TOON_GLINT_DIR
    links.new(geometry.outputs['Normal'], n_dot_a.inputs[0])
    hard = nodes.new('ShaderNodeMath')
    hard.operation = 'GREATER_THAN'
    hard.inputs[1].default_value = TOON_ACCENT[role]
    links.new(n_dot_a.outputs['Value'], hard.inputs[0])
    spark = nodes.new('ShaderNodeEmission')
    spark.inputs['Color'].default_value = accent
    mix = nodes.new('ShaderNodeMixShader')
    links.new(hard.outputs[0], mix.inputs[0])
    links.new(cel.outputs[0], mix.inputs[1])
    links.new(spark.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], nodes.get('Material Output').inputs['Surface'])


def component_contours(scene, objects, style):
    """Fixed-pixel component edges: thin black (Textbook), calligraphic
    role-colored ink (Toon), or subtle cyan splitter edges (Illustrated).

    This pass does not guarantee complete feature-edge coverage. Callers must
    include required components, including visible nanostructures. Inspect
    bevels, CAD end-face circles and barrel steps in the render. Add selected
    source-geometry curves for missing boundaries; retain opaque occlusion.
    Tune width after coverage is complete. Exclude CAD triangulation.
    """
    scene.render.use_freestyle = True
    scene.render.line_thickness_mode = 'ABSOLUTE'
    scene.render.line_thickness = 1
    settings = bpy.context.view_layer.freestyle_settings
    settings.mode = 'EDITOR'
    settings.use_culling = True
    settings.crease_angle = 2.35
    for line_set in list(settings.linesets):
        settings.linesets.remove(line_set)
    if style == 'illustrated':
        groups = {'Splitters': ((.12, .35, .39), 1.0)}
    elif style == 'toon':
        groups = {'Optics': (TOON_INK['Optics'][:3], 2.8),
                  'Hardware': (TOON_INK['Hardware'][:3], 3.4)}
    else:
        groups = {'Optics': ((.008, .008, .008), 1.8),
                  'Hardware': ((.008, .008, .008), 1.6)}
    # Toon hardware keeps outer silhouettes only; CAD creases would knot.
    edge_kinds = {'Hardware': ('silhouette', 'border')} if style == 'toon' else {}
    collections = {}
    for role, (color, thickness) in groups.items():
        # Selection-only collections: not linked to the scene, so the library
        # instances stay intact and no source geometry is drawn twice.
        collection = bpy.data.collections.new(style + ' contour / ' + role)
        # Freestyle's selection reference does not retain an unlinked collection.
        collection.use_fake_user = True
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
                    kind in edge_kinds.get(role, ('silhouette', 'border', 'crease')))
        line_set.linestyle.color = color
        line_set.linestyle.thickness = thickness
        if style == 'toon':
            # Calligraphic ink: stroke width follows the stroke direction.
            line_set.linestyle.caps = 'ROUND'
            pen = line_set.linestyle.thickness_modifiers.new('Ink pen', 'CALLIGRAPHY')
            pen.orientation = .79
            pen.thickness_min, pen.thickness_max = thickness * .7, thickness * 1.5
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
    scene['component_contours'] = {
        'illustrated': 'Subtle cyan splitter edges, 1 px',
        'toon': 'Calligraphic ink 2–5 px: deep-cyan optics, dark-navy hardware silhouettes; beams excluded',
    }.get(style, 'Visible thin black component edges, 1.6–1.8 px; beams excluded')


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
    if style in ('textbook', 'illustrated', 'toon'):
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
            # Emission-only cel surfaces: skip mesh-light sampling of CAD faces.
            material.cycles.emission_sampling='NONE'
            if ground:
                emission=nodes.new('ShaderNodeEmission')
                emission.inputs['Color'].default_value=TOON_FIELD
                emission.inputs['Strength'].default_value=1
                material.node_tree.links.new(emission.outputs[0],nodes.get('Material Output').inputs['Surface'])
            else:
                # Objective barrels keep their native ring color in the bands.
                role='beam' if beam else 'optic' if glass else 'hardware'
                toon_surface(material,color,role,material.get('figure_material_role')!='splitter_shell')
        role = material.get('figure_material_role')
        if style in ('textbook', 'illustrated', 'toon') and role in ('splitter_shell', 'splitter_interface'):
            output = nodes.get('Material Output')
            surface = output.inputs['Surface'].links[0].from_socket
            transparent = nodes.new('ShaderNodeBsdfTransparent')
            mix = nodes.new('ShaderNodeMixShader')
            # Four prism surfaces overlap in some views; a low per-surface
            # opacity keeps the un-refracted internal paths visible.
            shell_opacity, film_opacity = {'textbook': (.09, .24), 'illustrated': (.26, .34),
                                           'toon': (.30, .42)}[style]
            mix.inputs[0].default_value = shell_opacity if role == 'splitter_shell' else film_opacity
            if style == 'illustrated' and role == 'splitter_shell':
                shader.inputs['Base Color'].default_value = (.12, .50, .60, 1)
            material.node_tree.links.new(transparent.outputs[0], mix.inputs[1])
            material.node_tree.links.new(surface, mix.inputs[2])
            material.node_tree.links.new(mix.outputs[0], output.inputs['Surface'])
            shader.inputs['Transmission Weight'].default_value = 0
            material['illustrative_surface_opacity'] = mix.inputs[0].default_value
    if style in ('textbook', 'illustrated', 'toon'):
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
        # Flat field; Standard keeps the authored band colors exact.
        scene.view_settings.view_transform='Standard'
        scene.cycles.use_denoising=False
        # Deterministic splitter transparency: no Russian-roulette speckle.
        scene.cycles.min_transparent_bounces=scene.cycles.transparent_max_bounces
        bg.inputs[0].default_value=TOON_FIELD;bg.inputs[1].default_value=1
        scene['toon_recipe']=('Emission-only N.L bands from fixed key '+str(tuple(round(v,3) for v in TOON_KEY))
                              +'; fixed glint and camera-facing beam core; no lamps or GI')
    target=Vector((100,-55,98) if scene['opl_presentation_mode']=='floating_optics' else (120,-75,45))
    for light in lights:
        light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
    scene['shading_scope']='Illustrative appearance; geometry and channel semantics unchanged'
