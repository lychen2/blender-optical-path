"""Reference-inspired dual-wavelength, dual-arm mechanical optical layout.
blender -b --factory-startup --python-exit-code 1 --python examples/dual_wavelength_interferometer.py -- --output /new/output
Uses the bundled component API. Geometry is nominal; wavelengths identify the
reference channels, not verified laser SKUs, coatings or a build-ready design.
"""
import argparse
import json
import math
from pathlib import Path
import runpy
import sys
import bpy
from mathutils import Matrix, Vector
from bpy_extras.object_utils import world_to_camera_view

PACKAGE=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--mode',choices=['floating','mechanical'],default='floating')
    parser.add_argument('--style',choices=['matte','soft-lab','illustrated','textbook','toon'],default='matte')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    out=args.output.resolve()
    if out.exists():raise FileExistsError('Use a new output directory')
    out.mkdir(parents=True)
    api=runpy.run_path(str(PACKAGE/'tools/optics.py'))
    trace=runpy.run_path(str(Path(__file__).with_name('paraxial_4f.py')))['prescription']()
    (out/'trace.json').write_text(json.dumps(trace,indent=2)+'\n')
    scene=api['new_workspace']('Dual-wavelength mechanical layout')
    scene['opl_presentation_mode']='floating_optics' if args.mode=='floating' else 'full_mechanical_assembly'
    scene['scope']='Positive-positive 4f illumination model; normalized focal ratios, schematic spacing, coaxial recombination'
    scene['style']='Editorial laboratory apparatus; cool ivory field, upper-right soft key, satin metal, thick violet beam bodies'
    nodes={};placed=[]
    # Schematic spacing and display magnification apply only to floating mode.
    xmap=[(-320,-245),(-279,-216.3),(-240,-170),(-168,-115),(-98,-60),
          (-30,-5),(48,55),(125,115),(205,180),(298,265),(390,335),
          (490,410),(510,428),(543.6,457.32),(550,465)]
    def point(p):
        x,y,z=p
        if args.mode!='floating':return (x,y,z)
        for (a,b),(c,d) in zip(xmap,xmap[1:]):
            if a<=x<=c:
                x=b+(x-a)*(d-b)/(c-a);break
        return (x,y*.76,z)
    def place(key,asset,x,y,angle=0):
        pos=point((x,y,100))
        o=api['place_asset'](asset,pos,rotation_deg=(0,0,angle),name=key,scene=scene,at_optical_center=True)
        if args.mode=='floating':
            scale=.7 if 'laser' in asset else 1.5 if 'objective' in asset else 1.2 if 'camera' in asset else 1.75
            o.matrix_world=Matrix.Translation(Vector(pos)) @ Matrix.Scale(scale,4) @ Matrix.Translation(-Vector(pos)) @ o.matrix_world
            o['display_scale']=scale;o['scale_scope']='Schematic display enlargement; not physical dimensions'
        nodes[key]=pos;placed.append(o);return o
    def mat(name,rgb,metal=0,rough=.4,trans=0):
        m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
        s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*rgb,1)
        s.inputs['Metallic'].default_value=metal;s.inputs['Roughness'].default_value=rough
        s.inputs['Transmission Weight'].default_value=trans;s.inputs['IOR'].default_value=1.45
        return m
    # All standard supports stay unscaled. Two physical laser housings, not arrows.
    place('647 nm source','assembly/dpss_laser',-320,0)
    place('485 nm source','assembly/dpss_laser',-320,-125)
    place('M1','assembly/kinematic_mirror',-240,-125,135)
    place('DM','assembly/kinematic_mirror',-240,0,-45)
    # Replace only the front surface of a local duplicate with a nominal dichroic.
    def local_copy(instance,name):
        src=instance.instance_collection;col=bpy.data.collections.new(name);mapping={}
        col.instance_offset=src.instance_offset
        for old in src.all_objects:
            new=old.copy();col.objects.link(new);mapping[old]=new
        for old,new in mapping.items():
            if old.parent in mapping:new.parent=mapping[old.parent]
        instance.instance_collection=col
        return col
    dichroic=local_copy(placed[-1],'DM / standard mount with nominal dichroic')
    glass=mat('Dichroic / nominal coating',(.23,.63,.61),.15,.2,.4)
    for o in dichroic.all_objects:
        if o.name.startswith(('Mirror glass substrate','Reflective coated face')):
            o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(glass)
    place('L1','assembly/biconvex_lens',-168,0)
    place('L2','assembly/biconvex_lens',-98,0)
    place('P','schematic/linear_polarizer',-30,0)
    # Cube halves and mounting hardware are reused; coating is a nominal NPBS,
    # not a claim that a PBS SKU has non-polarizing optical properties.
    def npbs(key,x,y):
        o=place(key,'assembly/pbs_cube',x,y,90)
        col=local_copy(o,key+' / nominal NPBS on standard support')
        o['optical_role']='Nominal non-polarizing splitter; coating unspecified'
        o['derived_geometry']='PBS-shaped cube, not the source optical coating'
        for part in col.all_objects:
            if part.name.startswith('PBS prism half'):
                part['figure_material_role']='splitter_shell'
            if 'Polarizing dielectric interface' in part.name:
                part['figure_material_role']='splitter_interface'
                part.data=part.data.copy();part.data.materials.clear();part.data.materials.append(glass)
                part.name=key+' nominal splitting interface'
        return o
    npbs('NPBS1',48,0)
    place('M2','assembly/kinematic_mirror',48,-170,45)
    # Manufacturer object side faces the specimen/upstream; rear infinity port
    # faces L3/L4. Never reverse an asymmetric objective to fit a beam cartoon.
    # The normalized thin-lens envelope does not validate internal conjugates
    # or aberrations of this manufacturer objective.
    place('Specimen','schematic/sample_slide',125,-170)
    place('Objective 1','assembly/microscope_objective',205,0,180)
    place('Objective 2','assembly/microscope_objective',205,-170,180)
    for objective in placed[-2:]:
        # RMS assembly +X points toward the front/object side. It must point
        # upstream here; this is independent of the illustrative lens matrix.
        assert (objective.matrix_world.to_3x3() @ Vector((1,0,0))).normalized().dot(Vector((-1,0,0))) > .9999
    place('L3','assembly/biconvex_lens',298,0)
    place('L4','assembly/biconvex_lens',298,-170)
    place('M3','assembly/kinematic_mirror',390,0,225)
    npbs('NPBS2',390,-170)
    place('Color CMOS camera','assembly/scientific_camera',550,-170,180)
    # Editorial glass: clear silhouette at README size, not measured transmission.
    lens_material=mat('Readable pale cyan optical glass',(.14,.52,.59),.08,.27,.18)
    for instance in placed:
        if instance['opl_asset_id'] not in ('assembly/biconvex_lens','assembly/biconcave_lens'):
            continue
        col=local_copy(instance,instance.name+' / editorial glass')
        for obj in col.all_objects:
            if obj.name.startswith('Polished spherical optical'):
                obj.data=obj.data.copy();obj.data.materials.clear();obj.data.materials.append(lens_material)
    # An image plane is an annotation, not another floating physical plate.
    nodes['Image plane']=point((490,-170,100))
    nodes['z distance']=point((510,-170,60))
    def beam(name,pts,color,r=2,radii=None):
        factor=1.4 if args.mode=='floating' else 1
        return api['add_beam']([point(p) for p in pts],name=name,radius_mm=r*factor,color=color,scene=scene,
                               radii_mm=[v*factor for v in radii] if radii else None)
    beam('647 nm',[(-279,0,100),(-240,0,100)],(.78,.035,.025))
    beam('485 nm',[(-279,-125,100),(-240,-125,100),(-240,0,100)],(.04,.24,.8))
    violet=(.47,.06,.66)
    # Trace in normalized optical coordinates, then map its surface/focus
    # stations to authored display coordinates. No mm prescription is inferred.
    expander, upper, lower=trace['pairs']
    waist_floor=.35  # Display aid, not a diffraction calculation.
    in_radius=2
    out_radius=in_radius*expander['diameter_ratio']
    focus_x=-168+70*expander['f1']/(expander['f1']+expander['f2'])
    beam('4f expander',[(-240,0,100),(-168,0,100),(focus_x,0,100),(-98,0,100),(48,0,100)],
         violet,radii=[in_radius,in_radius,waist_floor,out_radius,out_radius])
    for name,y,model in [('Reference arm',0,upper),('Specimen arm',-170,lower)]:
        fx=205+93*model['f1']/(model['f1']+model['f2'])
        start=[(48,0,100)] if y==0 else [(48,0,100),(48,y,100)]
        end=[(390,0,100),(390,-170,100)] if y==0 else [(390,y,100)]
        points=start+[(205,y,100),(fx,y,100),(298,y,100)]+end
        radii=[out_radius]*len(start)+[out_radius,waist_floor,out_radius*model['diameter_ratio']]+[out_radius*model['diameter_ratio']]*len(end)
        beam(name,points,violet,radii=radii)
    # Coaxial collimated illumination remains collimated across the conjugate
    # image plane and the illustrative z offset. It is not a point-source pencil.
    beam('Coaxial output',[(390,-170,100),(490,-170,100),(543.6,-170,100)],violet,r=out_radius)
    scene['beam_model']='Paraxial positive-positive 4f illumination, derived from trace.json; display distances compressed independently'
    trace['display']={'lens_stations_mm':{'L1':-168,'L2':-98,'Objective':205,'L3_L4':298},
                      'focus_stations_mm':[focus_x,251.5], 'waist_radius_floor_mm':waist_floor,
                      'coordinates':'Authored display coordinates, not physical focal distances',
                      'image_plane':'Conjugate sample-plane marker; not a focus of the displayed illumination bundle',
                      'folded_arms':'Post-relay optical distances mapped separately to the common displayed image plane'}
    (out/'trace.json').write_text(json.dumps(trace,indent=2)+'\n')
    # Read actual optical-face geometry; derive input and output vectors from
    # adjacent placed components rather than re-testing authored Euler angles.
    port_checks=[]
    for key,previous,following in [('M1','485 nm source','DM'),('DM','M1','L1'),
            ('M2','NPBS1','Specimen'),('M3','L3','NPBS2'),
            ('NPBS1','P','M2'),('NPBS2','M3','Color CMOS camera')]:
        inst=next(o for o in placed if o.name==key)
        col=inst.instance_collection
        scene.collection.children.link(col);bpy.context.view_layer.update()
        face_obj=next(o for o in col.all_objects if
                      ('nominal splitting interface' in o.name if key.startswith('NPBS')
                       else o.name.startswith('Reflective coated face')))
        polygon=max(face_obj.data.polygons,key=lambda p:p.area)
        transform=inst.matrix_world @ Matrix.Translation(-col.instance_offset) @ face_obj.matrix_world
        normal=(transform.to_3x3().inverted().transposed() @ polygon.normal).normalized()
        kin=(Vector(nodes[key])-Vector(nodes[previous])).normalized()
        kout=(Vector(nodes[following])-Vector(nodes[key])).normalized()
        error=(kin-2*kin.dot(normal)*normal-kout).length
        assert error<1e-5,(key,error,list(normal))
        check={'component':key,'measured_world_normal':list(normal),
               'incoming':list(kin),'reflected':list(kout),'reflection_error':error}
        if key.startswith('NPBS'):
            prev,next_name=('P','Objective 1') if key=='NPBS1' else ('L4','Color CMOS camera')
            tin=(Vector(nodes[key])-Vector(nodes[prev])).normalized()
            tout=(Vector(nodes[next_name])-Vector(nodes[key])).normalized()
            assert (tin-tout).length<1e-5,key
            check['transmission_direction_error']=(tin-tout).length
            check['transmitted_input']=prev
            check['transmitted_output']=next_name
        port_checks.append(check)
        scene.collection.children.unlink(col)
    trace['measured_surface_ports']=port_checks
    (out/'trace.json').write_text(json.dumps(trace,indent=2)+'\n')
    # Light-grey breadboard with sparse shallow recesses avoids a decorative grid.
    boardmat=mat('Anodized breadboard',(.59,.65,.68),.35,.48)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(125,-80,-7))
    board=bpy.context.object;board.name='Breadboard';board.dimensions=(990,330,14)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);board.data.materials.append(boardmat)
    b=board.modifiers.new('Board edges','BEVEL');b.width=3;b.segments=3
    holemat=mat('Mounting grid / shallow recess',(.15,.19,.21),.2,.7)
    # Shared mesh keeps the editable scene compact; not full threaded-hole CAD.
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=2.2,depth=.1,location=(0,0,-.08))
    prototype=bpy.context.object;prototype.name='Mounting-grid recess';prototype.data.materials.append(holemat)
    for x in range(-350,601,25):
        for y in range(-225,76,25):
            q=prototype.copy();q.data=prototype.data;scene.collection.objects.link(q);q.location=(x,y,.02)
    bpy.data.objects.remove(prototype,do_unlink=True)
    if args.mode=='floating':
        # Reviewed selections for these particular assets, not a generic classifier.
        for instance in placed:
            col=local_copy(instance,instance.name+' / floating optics')
            asset=instance['opl_asset_id']
            for o in col.all_objects:
                if o.type!='MESH':continue
                n=o.name
                if asset in ('assembly/biconvex_lens','assembly/biconcave_lens'):
                    keep=n.startswith('Polished spherical optical')
                elif asset=='assembly/kinematic_mirror':
                    keep=n.startswith(('Mirror glass substrate','Reflective coated face'))
                elif asset=='assembly/pbs_cube':
                    keep=n.startswith('PBS prism') or 'nominal splitting interface' in n
                elif asset=='schematic/linear_polarizer':
                    keep=n.startswith(('Optical disk','Polarization visual guide'))
                elif asset=='schematic/sample_slide':keep=n.startswith('Substrate')
                else:
                    keep=not n.startswith(('THORLABS /','Standard support /','Split laser saddle',
                        'Compact fixed objective plate','Objective reducer','Objective rear retaining rim'))
                    if n.startswith(('Hex socket rim','Socket cap screw','Socket interior')):
                        keep=False
                o.hide_render=not keep;o.hide_viewport=not keep
        board.hide_render=True
        for o in scene.objects:
            if o.name.startswith('Mounting-grid recess'):o.hide_render=True
    world=bpy.data.worlds.new('Cool ivory studio');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs[0].default_value=(.84,.87,.91,1)
    world.node_tree.nodes['Background'].inputs[1].default_value=.6;scene.world=world
    groundmat=mat('Background',(.86,.88,.89),0,.85)
    bpy.ops.mesh.primitive_plane_add(size=20000,location=(0,0,-15));bpy.context.object.data.materials.append(groundmat)
    data=bpy.data.cameras.new('Overview');camera=bpy.data.objects.new('Overview',data);scene.collection.objects.link(camera)
    target=Vector((100,-55,98) if args.mode=='floating' else (120,-75,45))
    camera.location=target+Vector((140,-890,810) if args.mode=='floating' else (310,-890,720))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO';data.ortho_scale=850 if args.mode=='floating' else 1110;data.clip_end=20000;scene.camera=camera
    def light(name,pos,energy,size):
        d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size
        o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=pos;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
    light('Upper-right soft key',(380,100,700),13000000,700)
    light('Front fill',(-250,-450,500),6500000,650)
    scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=True
    width,height=2100,(820 if args.mode=='floating' else 1050)
    scene.render.resolution_x=width;scene.render.resolution_y=height;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.render.filepath=str(out/'clean.png')
    runpy.run_path(str(Path(__file__).with_name('shading.py')))['apply_style'](scene,args.style)
    bpy.context.view_layer.update()
    # Source collection objects are evaluated through a temporary link for
    # inspection only; instance sources remain unchanged.
    checked=runpy.run_path(str(PACKAGE/'tools/validate_layout.py'))['validate'](scene)
    assert checked['status']=='passed',checked
    assert len(placed)==17,len(placed)
    anchors={}
    for name,p in nodes.items():
        v=world_to_camera_view(scene,camera,Vector(p));anchors[name]=[round(v.x*width,2),round((1-v.y)*height,2)]
    meta={'anchors_px':anchors,'image_size':[width,height],'style':args.style,'mode':scene['opl_presentation_mode'],'scope':scene['scope'],
          'components':[{'name':o.name,'asset_id':o['opl_asset_id'],'display_scale':o.get('display_scale',1)} for o in placed],
          'mechanical_parts':'Native PH50/M + TR50/M, pedestal and fork clamp where present in library assemblies',
          'limitations':['Reference supplies no dimensions, objective prescription, coatings or sensor conjugate.','Laser housings are generic, not verified 647/485 nm products.','NPBS coating and dichroic are nominal derivatives; standard mounts and supports retained.','Envelope derived from a normalized paraxial model; display distances are not an optical prescription. No internal objective tracing or interference simulation.','Breadboard grid is schematic and does not establish screw-hole fit.','POLARIS-K1S5 uses measured bottom mounting faces with nominal M4 fasteners; thread engagement is unverified.'],
          'beam_model':scene['beam_model'],
          'validation':checked}
    (out/'layout.json').write_text(json.dumps(meta,indent=2)+'\n')
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'dual_wavelength_interferometer.blend'))
    bpy.ops.render.render(write_still=True)
    print('MECHANICAL_LAYOUT_PASSED',len(placed))

if __name__=='__main__':main()
