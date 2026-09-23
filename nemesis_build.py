
import bpy, math, numpy as np, json
from mathutils import Vector, Matrix
from pathlib import Path
from math import sin, cos, pi
OUT=Path(__file__).resolve().parent
scene=bpy.data.scenes.new('A3P5 NEMESIS | Industrial study')
bpy.context.window.scene=scene
scene.unit_settings.system='METRIC'
scene.unit_settings.scale_length=1
COL={}
for name in ['01 | Carbon chassis','02 | Independent running gear','03 | Articulated manipulator','04 | Camera and atmospheric mast','05 | Environmental sampling','06 | Electronics and power','07 | Optional linear lift','90 | Studio']:
 c=bpy.data.collections.new(name); scene.collection.children.link(c);COL[name[:2]]=c
current=COL['01']
def collection(k):
 global current
 current=COL[k]
def finish(obj,mat=None,bevel=0,smooth=False):
 current.objects.link(obj)
 if mat: obj.data.materials.append(mat)
 if bevel:
  m=obj.modifiers.new('Machined edge radius','BEVEL');m.width=bevel;m.segments=3
 if smooth and hasattr(obj.data,'polygons'):
  for p in obj.data.polygons:p.use_smooth=True
 return obj
def mesh(name,verts,faces,mat=None,bevel=0,smooth=False):
 d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update()
 o=bpy.data.objects.new(name,d);finish(o,mat,bevel,smooth);return o
def box(name,loc,dims,mat,bevel=.002):
 x,y,z=[v/2 for v in dims]
 v=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
 f=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 o=mesh(name,v,f,mat,bevel);o.location=loc
 uv=o.data.uv_layers.new(name='Physical weave UV')
 for p in o.data.polygons:
  n=p.normal; ax=max(range(3),key=lambda a:abs(n[a])); idx=[i for i in range(3) if i!=ax]
  for li in p.loop_indices:
   co=o.data.vertices[o.data.loops[li].vertex_index].co; a,b=co[idx[0]],co[idx[1]]
   uv.data[li].uv=((a+b)/.032,(a-b)/.032)
 return o
def cyl(name,loc,r,depth,mat,axis=(0,0,1),n=48,bevel=.001):
 v=[(r*cos(2*pi*i/n),r*sin(2*pi*i/n),z) for z in [-depth/2,depth/2] for i in range(n)]
 f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 o=mesh(name,v,f,mat,bevel);o.location=loc;o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler()
 for p in o.data.polygons[2:]:p.use_smooth=True
 return o
def rod(name,a,b,r,mat,n=24):
 a,b=Vector(a),Vector(b);return cyl(name,(a+b)/2,r,(b-a).length,mat,b-a,n)
def beam(name,a,b,w,h,mat,bevel=.002):
 a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(w,h,(b-a).length),mat,bevel);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def ring(name,loc,outer,inner,depth,mat,axis=(0,0,1),n=64):
 vs=[]
 for z,r in [(-depth/2,outer),(depth/2,outer),(-depth/2,inner),(depth/2,inner)]:
  vs += [(r*cos(2*pi*i/n),r*sin(2*pi*i/n),z) for i in range(n)]
 fs=[]
 for i in range(n):
  j=(i+1)%n
  fs += [(i,j,n+j,n+i),(2*n+j,2*n+i,3*n+i,3*n+j),(n+i,n+j,3*n+j,3*n+i),(j,i,2*n+i,2*n+j)]
 o=mesh(name,vs,fs,mat,.0006,True);o.location=loc;o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();return o
def cable(name,pts,r,mat):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=8;d.bevel_depth=r;d.bevel_resolution=3
 s=d.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
 enums=[i.identifier for i in s.bezier_points[0].bl_rna.properties['handle_left_type'].enum_items]
 for p,co in zip(s.bezier_points,pts):
  p.co=co
  if 'AUTO' in enums:p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,d);return finish(o,mat)
def bolt(name,loc,axis=(0,0,1),r=.004):
 loc=Vector(loc);ax=Vector(axis)
 ring(name+' washer',loc,r*1.38,r*.65,.0012,steel,ax,n=24)
 cyl(name+' socket head',loc+ax*.002,r,.004,steel,ax,n=6,bevel=.00035)
 cyl(name+' hex recess',loc+ax*.0041,r*.43,.0003,black,ax,n=6,bevel=0)
def label(name,text,loc,size,mat= None,rot=(pi/2,0,0),align='CENTER'):
 d=bpy.data.curves.new(name,'FONT');d.body=text;d.size=size;d.align_x=align;d.extrude=.00012;d.resolution_u=8
 o=bpy.data.objects.new(name,d);finish(o,mat or white);o.location=loc;o.rotation_euler=rot;return o
def material(name,color,metal=0,rough=.4,coat=0,emission=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
 p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 p.inputs['Coat Weight'].default_value=coat
 if emission:
  p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 return m
black=material('Anodized graphite | satin',(0.022,.029,.037),.72,.28)
rubber=material('Vulcanized tire rubber',(.016,.021,.023),0,.68)
treadmat=material('Tread faces | molded rubber',(.025,.030,.031),0,.59)
steel=material('Bead blasted stainless steel',(.40,.46,.51),.86,.25)
silver=material('Brushed aluminum | 6061',(.55,.60,.65),.78,.29)
white=material('Ceramic ivory | sensor housings',(.71,.74,.68),.1,.29)
blue=material('Anodized petrol blue',(.012,.23,.33),.65,.27)
cyan=material('Status turquoise',(.006,.55,.32),.1,.25,emission=2)
violet=material('Status violet',(.24,.025,.7),.1,.3,emission=1.8)
red=material('Signal red',(.5,.018,.018),.2,.32)
yellow=material('Safety amber',(.9,.49,.025),.25,.35)
glass=material('Optical coated glass',(.008,.033,.052),.5,.10,coat=.7)
pcb=material('Solder mask | deep green',(.012,.08,.043),.35,.4)
carbon=material('Carbon fiber | diagonal 2x2 twill',(.034,.040,.045),.52,.31,coat=.38)
N=512; yy,xx=np.mgrid[0:N,0:N];u=xx/N*4;v=yy/N*4
warp=((np.floor(u)+np.floor(v))%4)<2
fu=u%1;fv=v%1
ridge=np.where(warp,np.sin(pi*fu)**.4,np.sin(pi*fv)**.4)
fil=np.where(warp,.85+.15*np.cos(fu*pi*18),.85+.15*np.cos(fv*pi*18))
value=(.018+.045*ridge)*fil*np.where(warp,1.,.64)
arr=np.empty((N,N,4),np.float32)
arr[:,:,0]=value;arr[:,:,1]=value*1.08;arr[:,:,2]=value*1.13;arr[:,:,3]=1
im=bpy.data.images.new('Woven carbon | embedded 512',width=N,height=N);im.pixels.foreach_set(arr.ravel());im.pack()
nodes=carbon.node_tree.nodes;links=carbon.node_tree.links
tex=nodes.new('ShaderNodeTexImage');tex.image=im
bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');links.new(tex.outputs['Color'],bs.inputs['Base Color'])
bn=nodes.new('ShaderNodeBump');bn.inputs['Strength'].default_value=.22;bn.inputs['Distance'].default_value=.0003
links.new(tex.outputs['Color'],bn.inputs['Height']);links.new(bn.outputs['Normal'],bs.inputs['Normal'])
print('Initialized materials and organized scene')


collection('01')
box('Lower impact tray',(0,0,.405),(.612,.678,.034),black,.009)
for x in [-.299,.299]:
 box('Carbon side skin',(x,0,.58),(.009,.648,.325),carbon,.003)
 for z in [.422,.742]:
  box('Side edge extrusion',(x,0,z),(.019,.67,.017),black,.003)
 for y in [-.325,.325]:
  box('Vertical corner protector',(x,y,.58),(.022,.023,.33),black,.004)
 for y in [-.285,-.14,0,.14,.285]:
  for z in [.445,.722]:bolt('M4 panel fixing',(x+math.copysign(.007,x),y,z),(math.copysign(1,x),0,0),.0031)
for y in [-.331,.331]:
 box('Front skin' if y<0 else 'Rear skin',(0,y,.58),(.581,.009,.326),carbon,.003)
 for x in [-.265,.265]:
  for z in [.445,.718]:bolt('End panel captive fastener',(x,y+math.copysign(.007,y),z),(0,math.copysign(1,y),0),.0038)
box('Top deck gasket',(0,0,.751),(.598,.662,.010),rubber)
box('Carbon top deck',(0,0,.761),(.603,.667,.012),carbon,.003)
box('Removable right service hatch',(.155,.045,.769),(.277,.46,.004),carbon,.0015)
for x in [.031,.279]:
 for y in [-.155,.252]:bolt('Hatch quarter turn',(x,y,.773),r=.0032)
for y in [-.16,.17]:
 box('Underbody aluminum cross member',(0,y,.398),(.61,.037,.032),silver)
for x in [-.235,.235]:
 box('Internal frame rail',(x,0,.48),(.025,.625,.15),black)
# Reference front badge and restrained equipment typography
box('Front badge rubber seal',(0,-.341,.568),(.361,.012,.228),rubber,.007)
box('Front etched identity plate',(0,-.349,.568),(.349,.004,.218),black,.005)
label('A3P5 raised name','A3P5',(0,-.353,.518),.098,silver)
label('Nemesis subtitle','N E M E S I S',(0,-.354,.488),.018,white)
label('Team name','TEAM AKASH PATHABO',(-.015,-.354,.641),.015,white)
box('Bangladesh flag',(.13,-.354,.637),(.032,.001,.020),pcb,.0001)
cyl('Flag red disc',(.128,-.355,.637),.0065,.001,red,(0,-1,0),32,0)
for x in [-.158,.158]:
 for z in [.477,.658]:bolt('Identity plate screw',(x,-.355,z),(0,-1,0),.0024)
for x in [-.245,.245]:
 cyl('Headlamp mounting neck',(x,-.348,.715),.034,.027,black,(0,-1,0))
 cyl('Sealed worklight housing',(x,-.377,.715),.047,.038,black,(0,-1,0))
 ring('Worklight metal bezel',(x,-.399,.715),.044,.037,.007,steel,(0,-1,0))
 cyl('Dark optical reflector',(x,-.403,.715),.036,.006,glass,(0,-1,0))
 for i in range(6):
  a=2*pi*i/6;xx=x+.023*cos(a);zz=.715+.023*sin(a)
  cyl('Individual lamp reflector',(xx,-.408,zz),.009,.005,silver,(0,-1,0),24)
  cyl('LED emitter',(xx,-.411,zz),.0055,.0015,white,(0,-1,0),24,0)
 cyl('Center lamp emitter',(x,-.411,.715),.007,.002,white,(0,-1,0))
# Side typography in same broad sponsor zone
for sx in [-1,1]:
 rot=(pi/2,0,sx*pi/2)
 label('Side team mark','TEAM AKASH PATHABO',(sx*.307,0,.687),.018,white,rot)
 label('Side rover identity','NEMESIS',(sx*.308,0,.600),.05,silver,rot)
 label('Side mission identifier','A3P5  /  ENVIRONMENTAL ROBOTICS',(sx*.308,0,.567),.012,white,rot)
 label('Side lower serial','FIELD SYSTEM  /  01',(sx*.308,.0,.460),.013,silver,rot)
# Rear access panel and vents
box('Rear service plate',(0,.341,.582),(.425,.011,.243),black,.005)
for x in [-.14,-.12,-.10,-.08,-.06,-.04,-.02,0,.02,.04,.06,.08,.10,.12,.14]:
 box('Rear cooling louver',(x,.349,.619),(.008,.005,.065),rubber,.003)
label('Rear service ID','A3P5 | SERVICE', (0,.350,.534),.026,silver,(pi/2,0,pi))
for x in [-.16,-.08,0,.08,.16]:
 cyl('Rear sealed connector',(x,.352,.484),.012,.014,steel,(0,1,0),32)
 cyl('Rear connector cap',(x,.363,.484),.009,.007,rubber,(0,1,0),32)
# Mast rear blue box from references
box('Blue equipment enclosure',(-.105,.233,.808),(.205,.145,.083),blue,.006)
box('Blue equipment lid',(-.105,.233,.852),(.21,.15,.006),blue,.002)


collection('02')
def tire(name,center):
 prof=[(-.058,.077),(-.063,.089),(-.062,.109),(-.054,.123),(-.044,.130),(.044,.130),(.054,.123),(.062,.109),(.063,.089),(.058,.077)]
 nv=96;vs=[];fs=[]
 for x,r in prof:vs.extend([(x,r*sin(2*pi*i/nv),r*cos(2*pi*i/nv)) for i in range(nv)])
 for j in range(len(prof)-1):
  for i in range(nv):fs.append((j*nv+i,j*nv+(i+1)%nv,(j+1)*nv+(i+1)%nv,(j+1)*nv+i))
 o=mesh(name,vs,fs,rubber,0,True);o.location=center
 return o
wheel_controls=[]
for sx in [-1,1]:
 # Fixed lengthwise side rails outside body
 for z in [.455,.475]:
  beam('Longitudinal suspension spar',(sx*.371,-.467,z),(sx*.371,.467,z),.032,.027,carbon)
 for y in [-.19,.19]:
  beam('Chassis outrigger',(sx*.267,y,.44),(sx*.372,y,.456),.042,.037,silver)
 cyl('Side suspension rotary mount',(sx*.318,0,.458),.044,.039,white,(1,0,0))
 bolt('Suspension pivot lock',(sx*.344,0,.458),(sx,0,0),.009)
 for sy in [-1,1]:
  x=sx*.465;y=sy*.454;z=.143
  tag=('R' if sx>0 else 'L')+('F' if sy<0 else 'R')
  before=set(current.objects)
  # Steering kingpin, reinforced servo carrier
  cyl(tag+' vertical steering barrel',(sx*.386,y,.435),.042,.099,black)
  ring(tag+' bearing collar',(sx*.386,y,.390),.046,.035,.010,steel)
  box(tag+' servo mount',(sx*.386,y,.495),(.092,.073,.012),black)
  box(tag+' blue steering servo',(sx*.386,y,.524),(.061,.041,.045),blue,.003)
  box(tag+' servo cap',(sx*.386,y,.548),(.061,.041,.005),black,.001)
  cyl(tag+' steering horn',(sx*.386,y,.490),.021,.006,silver)
  for dx in [-.037,.037]:
   for dy in [-.024,.024]:bolt(tag+' servo mount screw',(sx*.386+dx,y+dy,.504),r=.0025)
  # Swept C shaped wheel fork in the YZ plane extruded across X
  yz=[(y-.031,.392),(y+.035,.392),(y+.046,.336),(y-.003,.267),(y-.032,.198),(y-.023,.153),(y+.032,.132),(y+.030,.108),(y-.051,.119),(y-.072,.161),(y-.073,.221),(y-.034,.299)]
  vs=[(sx*.386+dx,yy,zz) for dx in [-.019,.019] for yy,zz in yz];n=len(yz)
  fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
  mesh(tag+' forged C steering fork',vs,fs,black,.004)
  # Industrial reinforcing link follows existing yoke
  rod(tag+' polished fork link',(sx*.386,y+.022,.363),(sx*.386,y-.040,.214),.005,steel)
  for yy,zz in [(y,.365),(y-.038,.209),(y,.142)]:
   bolt(tag+' fork pivot',(sx*.410,yy,zz),(sx,0,0),.0045)
  # Axle motor and boot
  cyl(tag+' DC gearbox',(sx*.399,y,z),.035,.090,silver,(1,0,0))
  cyl(tag+' motor end cap',(sx*.356,y,z),.032,.013,black,(1,0,0))
  for aa in range(12):
   a=2*pi*aa/12
   box(tag+' gearbox rib',(sx*.400,y+.033*sin(a),z+.033*cos(a)),(.044,.003,.003),steel,.0003)
  cyl(tag+' wheel axle',(sx*.444,y,z),.017,.080,steel,(1,0,0))
  tire(tag+' continuous molded tire',(x,y,z))
  # Deep repeating chevron tread, compound blocks
  for i in range(40):
   a=2*pi*i/40
   for side in [-1,1]:
    for j in range(3):
     xx=side*(.009+j*.0175);theta=a+j*.020
     ob=box(tag+' chevron lug %02d'%i,(x+xx,y+.132*sin(theta),z+.132*cos(theta)),(.021,.018,.013),treadmat,.002)
     ob.rotation_euler=(-theta,0,side*.26)
  # sidewall bead ribs
  for side in [-1,1]:
   for rr in [.087,.114]:
    ring(tag+' tire sidewall rib',(x+side*.061,y,z),rr+.0018,rr-.0018,.0028,rubber,(1,0,0),96)
  # Five spoke open rim
  outer=x+sx*.064
  ring(tag+' black rim barrel',(x,y,z),.079,.064,.117,black,(1,0,0))
  ring(tag+' machined beadlock',(outer,y,z),.081,.068,.005,steel,(1,0,0))
  ring(tag+' dark beadlock inset',(outer+sx*.003,y,z),.078,.072,.005,black,(1,0,0))
  cyl(tag+' hub',(outer-sx*.013,y,z),.029,.038,black,(1,0,0))
  cyl(tag+' hub center cap',(outer+sx*.009,y,z),.016,.007,silver,(1,0,0),48)
  for i in range(5):
   a=2*pi*i/5
   beam(tag+' sculpted rim spoke',(outer-sx*.005,y+.022*sin(a),z+.022*cos(a)),(outer-sx*.004,y+.071*sin(a+.10),z+.071*cos(a+.10)),.013,.011,black)
  for i in range(12):
   a=2*pi*i/12
   bolt(tag+' beadlock screw',(outer+sx*.005,y+.075*sin(a),z+.075*cos(a)),(sx,0,0),.0016)
  for i in range(5):
   a=2*pi*i/5
   bolt(tag+' hub screw',(outer+sx*.008,y+.023*sin(a),z+.023*cos(a)),(sx,0,0),.002)
  # Wire loom with slack for steering
  cable(tag+' protected motor harness',[(sx*.382,y,.520),(sx*.340,y-.05,.482),(sx*.34,y-.085,.336),(sx*.353,y-.10,.217),(sx*.347,y,.159)],.004,rubber)
  cable(tag+' signal cable',[(sx*.381,y,.531),(sx*.335,y-.025,.524),(sx*.331,y-sy*.13,.481),(sx*.327,sy*.18,.467)],.0018,red)
  ctl=bpy.data.objects.new(tag+' | steering pivot',None);current.objects.link(ctl);ctl.location=(sx*.386,y,.435)
  bpy.context.view_layer.update()
  for ob in set(current.objects)-before-{ctl}:
   world=ob.matrix_world.copy();ob.parent=ctl;ob.matrix_world=world
  ctl['axis']='Local Z steering; wheel geometry editable';wheel_controls.append(ctl)
# Fixed routed side wiring
for sx in [-1,1]:
 cable('Protected side signal backbone',[(sx*.327,-.43,.483),(sx*.321,-.1,.490),(sx*.323,.15,.49),(sx*.35,.42,.492)],.004,rubber)
print('Four wheel assemblies complete')


collection('03')
# Pedestal and yaw bearing
box('Manipulator pedestal foot',(-.08,-.175,.782),(.194,.197,.021),steel,.004)
for x in [-.160,0]:
 for y in [-.253,-.096]:bolt('Pedestal anchor',(x,y,.797),r=.005)
box('Lower stacked arm base',(-.08,-.175,.844),(.17,.178,.106),black,.005)
box('Upper stacked arm base',(-.08,-.175,.911),(.169,.177,.024),black,.003)
ring('Manipulator yaw slewing bearing',(-.08,-.175,.938),.081,.05,.029,steel)
cyl('Yaw top flange',(-.08,-.175,.955),.077,.013,black)
for i in range(8):
 a=i*pi/4;bolt('Yaw ring fastener',(-.08+.067*cos(a),-.175+.067*sin(a),.965),r=.003)
S=Vector((-.08,-.175,1.13));E=Vector((-.08,.203,1.383));W=Vector((-.08,-.520,1.076))
# Upright paired cheek plates
for xx in [-.143,-.017]:
 box('Shoulder upright cheek',(xx,-.175,1.043),(.015,.126,.168),black,.004)
 for yy in [-.219,-.128]:
  for zz in [.987,1.04]:bolt('Shoulder cheek screw',(xx+.010,yy,zz),(1,0,0),.004)
# Joint stack facing +X as in photographs
def arm_joint(name,pos,r=.069):
 cyl(name+' drum',pos,r,.154,black,(1,0,0))
 for dx in [-.081,.081]:
  cyl(name+' faceplate',pos+Vector((dx,0,0)),r*.94,.011,silver,(1,0,0))
  ring(name+' black bearing race',pos+Vector((dx*1.09,0,0)),r*.71,r*.44,.006,black,(1,0,0))
  for i in range(8):
   a=i*pi/4;bolt(name+' flange screw',pos+Vector((dx*1.10,r*.82*sin(a),r*.82*cos(a))),(math.copysign(1,dx),0,0),.0028)
 cyl(name+' gearbox',pos+Vector((.110,0,0)),r*.50,.045,black,(1,0,0))
 cyl(name+' silver gearmotor',pos+Vector((.159,0,0)),r*.39,.060,silver,(1,0,0))
 ring(name+' motor seam',pos+Vector((.170,0,0)),r*.40,r*.365,.002,steel,(1,0,0))
 cyl(name+' motor end cap',pos+Vector((.193,0,0)),r*.365,.007,steel,(1,0,0))
 for yy in [-.013,.013]:
  cyl(name+' terminal',pos+Vector((.199,yy,0)),.003,.007,yellow,(1,0,0),12)
arm_joint('Shoulder',S,.073)
arm_joint('Elbow',E,.061)
# Paired plates maintain triangular folded profile
for dx in [-.068,.068]:
 a=S+Vector((dx,0,0));b=E+Vector((dx,0,0))
 beam('Upper arm structural rail',a,b,.016,.060,black,.004)
 beam('Upper arm carbon inset',a+Vector((math.copysign(.010,dx),0,0)),b+Vector((math.copysign(.010,dx),0,0)),.004,.037,carbon,.001)
 for t in [.25,.75]:
  p=a.lerp(b,t);bolt('Upper arm rail screw',p+Vector((math.copysign(.012,dx),0,0)),(math.copysign(1,dx),0,0),.003)
 # Forearm extends towards wrist without hiding open center
 a=E+Vector((dx,0,0));b=W+Vector((dx,0,0))
 beam('Forearm open cheek rail',a,b,.015,.033,black,.003)
 for t in [.2,.5,.82]:
  p=a.lerp(b,t);bolt('Forearm structural screw',p+Vector((math.copysign(.009,dx),0,0)),(math.copysign(1,dx),0,0),.0027)
for t in [.18,.78]:
 p=E.lerp(W,t);rod('Forearm cross spacer',p+Vector((-.062,0,0)),p+Vector((.062,0,0)),.008,silver)
# Linear actuator visible within fork
a=E.lerp(W,.17)+Vector((0,0,.010));b=E.lerp(W,.88)+Vector((0,0,.010))
mid=a.lerp(b,.65)
rod('Forearm actuator polished body',a,mid,.014,silver)
rod('Forearm actuator piston',mid,b,.007,steel)
ring('Actuator seal',mid,.016,.007,.010,black,b-a)
for p in [a,b]:
 cyl('Actuator clevis pin',p,.012,.054,steel,(1,0,0))
# Visible elbow/shoulder motor cables with protected routes
cable('Elbow red motor lead',[E+Vector((.199,.013,0)),(.16,.18,1.30),(.08,-.03,1.19),(.08,-.15,1.09),(.05,-.07,.947)],.002,red)
cable('Elbow black motor lead',[E+Vector((.199,-.013,0)),(.166,.17,1.28),(.09,-.02,1.18),(.09,-.12,1.08),(.05,-.03,.934)],.002,rubber)
cable('Arm braided supply loom',[(-.16,-.12,.945),(-.174,-.12,1.04),(-.162,.05,1.225),(-.163,.19,1.358),(-.160,-.19,1.208),(-.156,-.47,1.085)],.006,rubber)
for t in [.23,.43,.63,.83]:
 p=E.lerp(W,t)+Vector((-.081,0,0))
 box('Arm harness clip',p,(.015,.015,.015),black,.002)
# Wrist red servo and creamy actuator housing
cyl('Wrist pitch bearing',W,.030,.12,black,(1,0,0))
box('Wrist servo casing',(-.08,-.535,1.077),(.110,.066,.043),red,.005)
box('Wrist adapter plate',(-.08,-.535,1.045),(.122,.075,.009),steel,.002)
box('Gripper ivory motor enclosure',(-.08,-.535,.996),(.079,.064,.090),white,.004)
box('Wrist vertical inspection slot',(-.08,-.568,.999),(.023,.002,.058),black,.001)
box('Wrist slot metal insert',(-.08,-.570,.997),(.010,.002,.043),steel,.001)
box('Gripper black crossbar',(-.08,-.538,.941),(.179,.077,.021),black,.003)
for xx in [-.150,-.010]:
 bolt('Gripper upper pivot',(xx,-.579,.938),(0,-1,0),.006)
 # Four bars make hollow triangular metal finger frames
 outer=Vector((xx,-.538,.931));tip=Vector((-.08+math.copysign(.022,xx+.08),-.542,.828))
 inner=Vector((xx+math.copysign(.027,-.08-xx),-.538,.931))
 beam('Gripper outer link',outer,tip,.013,.009,silver,.0015)
 beam('Gripper inner diagonal',inner,tip,.009,.008,silver,.0012)
 box('Gripper replaceable rubber tip',tip+Vector((0,0,-.002)),(.015,.03,.030),rubber,.002)
cable('Wrist service loop',[(-.11,-.48,1.10),(-.17,-.515,1.10),(-.165,-.57,1.04),(-.117,-.555,1.027)],.0028,rubber)
label('Arm serial','ARM 01',(-.08,-.267,.851),.015,white)
print('Folded manipulator complete')


collection('04')
A=Vector((.207,.253,.781));B=Vector((.207,.548,1.66));D=(B-A).normalized()
box('Mast mounting plinth',A,(.083,.079,.019),silver,.003)
for xx in [.174,.240]:
 for yy in [.224,.282]:bolt('Mast foot anchor',(xx,yy,.795),r=.0033)
rod('Mast swivel socket',A,A+D*.092,.026,silver)
rod('Rear leaning carbon mast',A+D*.075,B,.014,black)
# Thin exposed circuit rail retains original LED strip
for dx in [-.016,.016]:
 beam('Mast metallic edge rail',A+Vector((dx,-.010,0))+D*.08,B+Vector((dx,-.010,0)),.003,.003,steel,.0005)
beam('Mast LED circuit strip',A+D*.09+Vector((0,-.017,0)),B+Vector((0,-.017,0)),.021,.003,pcb,.0006)
for i in range(38):
 p=A.lerp(B,.12+.86*i/37)+Vector((0,-.021,0))
 box('Mast LED board pad',p,(.012,.003,.012),silver,.0005)
 lit=cyan if 3<=i<=11 else violet if 24<=i<=30 else white
 box('Mast status LED',p+Vector((0,-.002,0)),(.007,.002,.007),lit,.0006)
 for dx in [-.006,.006]:
  box('LED resistor',p+Vector((dx,-.001,.006)),(.002,.001,.003),black,.0001)
for t in [.15,.48,.8]:
 p=A.lerp(B,t);ring('Mast clamp',p,.018,.014,.011,silver,D,32)
# Camera head
cyl('Camera head pivot',(B.x,B.y,B.z+.01),.023,.082,black,(1,0,0))
head=Vector((.207,.549,1.723))
box('Mast ivory camera head',head,(.078,.061,.116),white,.005)
box('Head back gasket',head+Vector((0,.031,0)),(.069,.003,.104),rubber,.001)
for yy in [-.017,.004,.025]:
 for zz in [-.03,-.01,.01,.03]:
  cyl('Head side ventilation port',head+Vector((.040,yy,zz)),.0057,.0015,black,(1,0,0),20,0)
ring('Forward camera lens mount',head+Vector((0,-.037,-.006)),.017,.010,.012,steel,(0,-1,0),32)
cyl('Forward camera lens barrel',head+Vector((0,-.054,-.006)),.012,.022,black,(0,-1,0),48)
cyl('Coated camera optic',head+Vector((0,-.067,-.006)),.009,.004,glass,(0,-1,0),48)
cyl('Camera status indicator',head+Vector((.024,-.032,.028)),.0025,.001,cyan,(0,-1,0),16,0)
for xx in [-.03,.03]:
 for zz in [-.047,.047]:bolt('Camera enclosure screw',head+Vector((xx,-.032,zz)),(0,-1,0),.0021)
# antenna and green safety cap
cyl('Antenna SMA connector',head+Vector((0,0,.063)),.007,.013,yellow)
rod('Flexible whip antenna',head+Vector((0,0,.07)),head+Vector((0,0,.225)),.0025,black)
cyl('Green antenna tip',head+Vector((0,0,.223)),.007,.022,cyan)
cable('Mast service loop',[(.207,.26,.79),(.24,.30,.80),(.254,.40,.89),(.22,.34,1.0)],.004,rubber)
# Atmospheric vent cluster and UV window discreetly integrated on rear deck
box('Atmospheric instrument rail',(-.11,.24,.862),(.197,.118,.008),black,.002)
for i,xx in enumerate([-.176,-.112,-.048]):
 cyl(['MQ135 air quality','MQ7 carbon monoxide','MQ4 methane'][i]+' protective can',(xx,.24,.882),.020,.026,steel)
 for a in range(12):
  aa=2*pi*a/12
  rod('Sensor mesh vertical',(xx+.019*cos(aa),.24+.019*sin(aa),.873),(xx+.019*cos(aa),.24+.019*sin(aa),.889),.0007,black,8)
 cyl('Gas sensor mesh top',(xx,.24,.896),.016,.001,black,n=32,bevel=0)
 for j in [-2,-1,0,1,2]:
  rod('Gas mesh lattice',(xx-.013,.24+j*.005,.897),(xx+.013,.24+j*.005,.897),.00045,silver,8)
box('UV sensor window',(-.105,.192,.865),(.029,.019,.004),glass,.001)
label('Atmospheric unit label','AIR / UV / BARO',(-.105,.172,.820),.012,white)
print('Mast and atmospheric package complete')

collection('05')
# two-level cream three-hole sample rack, right longitudinal side
for z in [.401,.451]:
 ob=box('Three position sample rack',(.461,-.162,z),(.135,.256,.015),white,.003)
 # Real machined bores
 for yy in [-.245,-.162,-.079]:
  cut=cyl('Bore cutter',(.461,yy,z),.021,.060,None,n=48)
  mod=ob.modifiers.new('Sample socket','BOOLEAN')
  vals=[i.identifier for i in mod.bl_rna.properties['operation'].enum_items]
  mod.operation=next(v for v in vals if v=='DIFFERENCE');mod.object=cut
  bpy.context.view_layer.objects.active=ob
  bpy.ops.object.modifier_apply(modifier=mod.name)
  bpy.data.objects.remove(cut,do_unlink=True)
for xx in [.414,.506]:
 for yy in [-.273,-.051]:rod('Sample rack spacer',(xx,yy,.405),(xx,yy,.447),.004,silver)
beam('Rack mounting outrigger',(.343,-.164,.453),(.405,-.164,.453),.037,.019,silver)
label('Sample rack index','01     02     03',(.530,-.162,.437),.011,black,(pi/2,0,pi/2))
cable('Water sampling silicone hose',[(.31,-.035,.483),(.379,-.075,.526),(.458,-.015,.55),(.548,-.028,.485),(.539,-.12,.37)],.006,white)
# sample probe stored vertically alongside rack
cyl('pH probe upper housing',(.535,-.10,.398),.009,.091,black)
cyl('pH probe stainless shaft',(.535,-.10,.326),.005,.053,steel)
cyl('pH electrode tip',(.535,-.10,.294),.006,.013,glass)
cable('Water probe signal',[(.535,-.10,.447),(.546,-.05,.49),(.414,.05,.493),(.324,.08,.489)],.0025,rubber)
box('Turbidity optical sample chamber',(.344,.106,.483),(.051,.073,.055),white,.004)
for yy in [.085,.126]:
 cyl('Turbidity optical port',(.372,yy,.487),.010,.010,black,(1,0,0))
# E stop on accessible rear corner
cyl('Emergency stop amber escutcheon',(-.238,.284,.782),.025,.019,yellow)
cyl('Emergency stop mushroom',(-.238,.284,.805),.020,.029,red,bevel=.004)
label('E stop deck legend','STOP',(-.238,.245,.776),.012,white,(0,0,0))
print('Sampling module complete')


collection('06')
# Visible when service deck is hidden; illustrative electronics layout
box('Battery isolating tray',(0,.035,.438),(.365,.282,.018),white,.003)
box('3S battery pack',(-.095,.017,.482),(.16,.227,.074),black,.006)
for yy in [-.05,.08]:
 box('Battery retaining strap',(-.095,yy,.521),(.167,.018,.008),rubber,.002)
label('Battery identification','11.1V / 3S',(-.095,-.062,.527),.015,white,(0,0,0))
box('Regulated logic mezzanine',(.11,.033,.552),(.190,.239,.010),silver)
box('Arduino Mega illustrative PCB',(.101,.025,.564),(.101,.157,.008),blue,.001)
box('Microcontroller package',(.101,.025,.571),(.020,.020,.003),black,.0005)
for sx in [-1,1]:
 for i in range(18):
  box('Controller pin header',(.101+sx*.045,-.039+i*.007,.575),(.007,.004,.013),black,.0005)
box('ESP communication board',(.106,.139,.58),(.071,.038,.006),pcb,.001)
box('Radio module shield',(.099,.14,.586),(.028,.021,.004),steel,.001)
box('Fused power distribution',(-.12,.195,.533),(.135,.058,.013),pcb)
for x in [-.16,-.13,-.10,-.07]:
 box('Blade fuse',(x,.19,.550),(.014,.018,.022),red,.001)
for x in [-.20,.20]:
 box('Motor driver',(x,-.21,.494),(.065,.108,.035),black,.002)
 for i in range(7):box('Driver heat sink fin',(x-.027+i*.009,-.21,.519),(.003,.096,.028),silver,.0005)
cable('High current battery cable',[(-.095,.13,.495),(-.13,.19,.524),(-.18,.23,.54),(-.23,.12,.53)],.005,red)
cable('Battery ground return',[(-.08,.13,.495),(-.08,.2,.515),(.11,.19,.54),(.18,.1,.55)],.005,rubber)
# hidden internals don't need external visibility changes

collection('07')
# Optional photographic configuration, present in photos 2-3
for xx in [.365,.469]:
 rod('Lift polished guide rail',(xx,.188,.33),(xx,.188,1.423),.006,silver)
rod('Lift lead screw',(.417,.188,.32),(.417,.188,1.423),.004,steel)
for z in [.349,1.421]:
 box('Lift end bridge',(.417,.188,z),(.146,.066,.033),silver,.002)
 for xx in [.365,.469]:bolt('Lift tie bolt',(xx,.188,z+.019),r=.004)
box('Lift traveling tool carriage',(.417,.188,.882),(.163,.095,.043),white,.004)
cyl('Lift lower drive motor',(.417,.188,.292),.022,.09,black)
# Linear lift cable chain arch
pts=[(.395,.191,.36),(.395,.20,.8),(.395,.15,1.12),(.395,-.03,1.16),(.395,-.13,.95),(.395,-.10,.80)]
cable('Lift chain spine',pts,.013,rubber)
for i in range(23):
 t=i/22
 yy=.04+.15*cos(pi*t);zz=.79+.37*sin(pi*t)
 box('Articulated cable chain link',(.395,yy,zz),(.033,.022,.018),black,.002)
COL['07'].hide_render=True;COL['07'].hide_viewport=True
COL['07']['configuration']='Optional tower visible in reference photos 2 and 3. Hidden in primary configuration.'

collection('90')
floor=material('Studio graphite',(.105,.123,.143),.15,.51)
box('Studio floor',(0,0,-.027),(200,200,.03),floor,.0)
world=bpy.data.worlds.new('Soft industrial studio');world.use_nodes=True;scene.world=world
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.22,.27,.34,1);bg.inputs['Strength'].default_value=.34
def area(name,loc,target,energy,color,size):
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.color=color;d.shape=next(i.identifier for i in d.bl_rna.properties['shape'].enum_items if i.identifier=='DISK');d.size=size
 o=bpy.data.objects.new(name,d);finish(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
area('Key | large softbox',(2,-3,3.6),(0,0,.8),500,(.83,.92,1),3)
area('Fill | warm reflector',(-2,-1,2.0),(0,0,.75),380,(1,.87,.72),2.7)
area('Rim | overhead strip',(.5,2.3,3.1),(0,0,.95),650,(.68,.83,1),2.1)
area('Front gloss reflection',(0,-2.5,1.1),(0,0,.7),90,(1,1,1),1.6)
def camera(name,loc,target,lens=52):
 d=bpy.data.cameras.new(name);d.lens=lens;d.clip_start=.01;d.clip_end=300
 o=bpy.data.objects.new(name,d);finish(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
cam=camera('01 | HERO - front starboard',(2.7,-3.8,2.3),(0,.025,.92),58)
camera('02 | Rear engineering view',(-2.7,3.4,2.4),(0,.05,.86),55)
camera('03 | Front elevation',(0,-4.5,1.04),(0,0,.95),64)
camera('04 | Starboard elevation',(4.5,0,1.1),(0,0,.94),64)
camera('05 | Arm and deck detail',(1.6,-2.2,1.8),(-.04,-.08,1.06),75)
scene.camera=cam
scene.render.resolution_x=1400;scene.render.resolution_y=1600;scene.render.resolution_percentage=60
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(OUT/'A3P5_Nemesis_preview.png')
scene.render.film_transparent=False
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.image_settings.color_mode=next(i.identifier for i in scene.render.image_settings.bl_rna.properties['color_mode'].enum_items if i.identifier=='RGBA')
scene.view_settings.exposure=.15
bpy.context.view_layer.update()
# Configure user viewport
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':
  s=a.spaces.active;s.region_3d.view_perspective='CAMERA';s.overlay.show_overlays=False;s.shading.type='MATERIAL'
  s.region_3d.view_camera_zoom=0
for o in bpy.context.selected_objects:o.select_set(False)
print('Scene count',len(scene.objects))
print('Wheel positions',[(o.name,tuple(round(v,3) for v in o.matrix_world.translation)) for o in scene.objects if 'continuous molded tire' in o.name])
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'A3P5_Nemesis_Industrial.blend'))


# Material refinement and render quality
im=ns['im'] if 'ns' in globals() else im
N=512; yy,xx=np.mgrid[0:N,0:N];u=xx/N*4;v=yy/N*4
warp=((np.floor(u)+np.floor(v))%4)<2
fu=u%1;fv=v%1
ridge=np.where(warp,np.sin(pi*fu)**.5,np.sin(pi*fv)**.5)
fil=np.where(warp,.88+.12*np.cos(fu*pi*18),.88+.12*np.cos(fv*pi*18))
value=(.16+.23*ridge)*fil*np.where(warp,1.,.69)
arr=np.empty((N,N,4),np.float32);arr[:,:,0]=value;arr[:,:,1]=value*1.035;arr[:,:,2]=value*1.07;arr[:,:,3]=1
im.pixels.foreach_set(arr.ravel());im.update();im.pack()
# Introduce fine molded and machined surface roughness
for mat,scale,strength,dist in [(rubber,360,.16,.0006),(treadmat,410,.19,.0007),(black,620,.08,.00015),(silver,800,.1,.00012)]:
 nd=mat.node_tree.nodes;ln=mat.node_tree.links;pr=next(n for n in nd if n.type=='BSDF_PRINCIPLED')
 noise=nd.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=2.
 bm=nd.new('ShaderNodeBump');bm.inputs['Strength'].default_value=strength;bm.inputs['Distance'].default_value=dist
 ln.new(noise.outputs['Fac'],bm.inputs['Height']);ln.new(bm.outputs['Normal'],pr.inputs['Normal'])
# Tread groove articulation with narrower raised faces
for ob in COL['02'].objects:
 if 'chevron lug' in ob.name:
  for ve in ob.data.vertices:ve.co.y*=.55
# Remove floor edge from background; contact at wheel sole
bpy.data.objects['Studio floor'].scale=(10,10,1)
bpy.data.objects['Studio floor'].location.z=-.016
# More generous subject framing
cam.location=(2.25,-3.15,2.00);cam.rotation_euler=(Vector((0,.04,.98))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=58
scene.camera=cam
scene.cycles.samples=48;scene.cycles.use_denoising=True
prefs=bpy.context.preferences.addons['cycles'].preferences
types=[v[0] for v in prefs.get_device_types(bpy.context)]
for typ in ['OPTIX','CUDA','ONEAPI']:
 if typ not in types:continue
 try:
  prefs.compute_device_type=typ;prefs.get_devices()
  devices=[d for d in prefs.devices if d.type==typ]
  if devices:
   for d in prefs.devices:d.use=(d.type==typ)
   scene.cycles.device='GPU';print('Rendering device',[d.name for d in devices]);break
 except Exception:pass
else:scene.cycles.device='CPU';print('Rendering on CPU')
scene.render.engine='CYCLES'
scene.render.resolution_percentage=60
scene.render.filepath=str(OUT/'A3P5_Nemesis_preview.png')
print('Refined materials')


# Physical twill runs diagonally on each sheet, matching reference wrap.
for ob in scene.objects:
 if ob.type=='MESH' and ob.data.uv_layers and any(m==carbon for m in ob.data.materials):
  uv=ob.data.uv_layers.active
  for p in ob.data.polygons:
   ax=max(range(3),key=lambda a:abs(p.normal[a]));idx=[i for i in range(3) if i!=ax]
   for li in p.loop_indices:
    co=ob.data.vertices[ob.data.loops[li].vertex_index].co
    uv.data[li].uv=(co[idx[0]]/.020,co[idx[1]]/.020)
value=(.095+.205*ridge)*fil*np.where(warp,1.,.67)
arr[:,:,0]=value;arr[:,:,1]=value*1.035;arr[:,:,2]=value*1.07
im.pixels.foreach_set(arr.ravel());im.update();im.pack()
pr=next(n for n in carbon.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
pr.inputs['Metallic'].default_value=.30;pr.inputs['Roughness'].default_value=.38;pr.inputs['Coat Weight'].default_value=.22
# Continuous photographic backdrop
collection('90')
fp=next(n for n in floor.node_tree.nodes if n.type=='BSDF_PRINCIPLED');fp.inputs['Base Color'].default_value=(.038,.050,.064,1);fp.inputs['Roughness'].default_value=.54
points=[(1.5+3*sin(i*pi/48),3*(1-cos(i*pi/48))) for i in range(25)]
points.append((4.5,40))
verts=[(x,y,z-.001) for x in [-100,100] for y,z in points];n=len(points)
faces=[(i,i+1,n+i+1,n+i) for i in range(n-1)]
mesh('Seamless studio cyclorama',verts,faces,floor,0,True)
for ob in COL['90'].objects:
 if ob.type=='CAMERA':ob.data.clip_end=10000
# Wheel roll pivots, retain steering pivots and exact transforms
collection('02')
for ctl in wheel_controls:
 tag=ctl.name[:2];sx=1 if tag[0]=='R' else -1;sy=-1 if tag[1]=='F' else 1
 roll=bpy.data.objects.new(tag+' | wheel spin',None);current.objects.link(roll);roll.location=(sx*.465,sy*.454,.143)
 bpy.context.view_layer.update();mw=roll.matrix_world.copy();roll.parent=ctl;roll.matrix_world=mw
 for ob in list(ctl.children):
  if any(t in ob.name for t in ['continuous molded tire','chevron lug','tire sidewall','rim barrel','beadlock','rim spoke','hub','center cap']):
   mw=ob.matrix_world.copy();ob.parent=roll;ob.matrix_world=mw
 roll['axis']='Local X = wheel rolling axis'
# Arm articulation pivots for presentation posing
collection('03')
def pivot(name,loc,parent=None):
 ob=bpy.data.objects.new(name,None);current.objects.link(ob);ob.location=loc
 bpy.context.view_layer.update()
 if parent:
  mw=ob.matrix_world.copy();ob.parent=parent;ob.matrix_world=mw
 return ob
yaw=pivot('CTRL | Arm yaw',(-.08,-.175,.939))
shoulder=pivot('CTRL | Shoulder pitch',S,yaw)
elbow=pivot('CTRL | Elbow pitch',E,shoulder)
wrist=pivot('CTRL | Wrist pitch',W,elbow)
yaw['axis']='Z';shoulder['axis']='X';elbow['axis']='X';wrist['axis']='X'
for ob in list(current.objects):
 if ob.type=='EMPTY':continue
 nm=ob.name
 if any(t in nm for t in ['pedestal','stacked arm base','Pedestal','Arm serial','Yaw ring']):continue
 parent=yaw
 if nm.startswith('Upper arm'):parent=shoulder
 if nm.startswith('Elbow') or nm.startswith('Forearm') or nm.startswith('Actuator'):parent=elbow
 if nm.startswith('Wrist') or nm.startswith('Gripper'):parent=wrist
 mw=ob.matrix_world.copy();ob.parent=parent;ob.matrix_world=mw
# Inspectable custom metadata
scene['Reference basis']='Six supplied photographs; no measured drawings. Primary photo configuration with optional lift separately organized.'
scene['Scale status']='Estimated metric proportions; visual product model, not dimensioned fabrication CAD.'
scene['Solar panel']='User clarified none.'
scene['Articulation']='Four steering pivots, four wheel rolling pivots and arm pose pivots. Cable curves are static and can be edited for large pose changes.'
scene['Mission hardware']='Sensor and internal electronics placements are design packaging interpretations from supplied mission description.'
# Final photographic settings
scene.camera=cam;scene.render.resolution_x=1600;scene.render.resolution_y=1900;scene.render.resolution_percentage=100
scene.cycles.samples=96;scene.cycles.use_denoising=True
scene.render.filepath=str(OUT/'A3P5_Nemesis_Hero.png')
bpy.context.view_layer.update()
print('Polish complete')


# Consolidate repeating tire lugs into one editable mesh per wheel.
# Keeps the modeled geometry and substantially reduces object overhead.
collection('02');bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
for tag in ['LF','LR','RF','RR']:
 obs=[ob for ob in list(COL['02'].objects) if ob.name.startswith(tag+' chevron lug')]
 verts=[];faces=[]
 for ob in obs:
  ev=ob.evaluated_get(deps);me=ev.to_mesh();off=len(verts)
  verts += [tuple(ob.matrix_world@v.co) for v in me.vertices]
  faces += [tuple(off+i for i in p.vertices) for p in me.polygons]
  ev.to_mesh_clear()
 if obs:
  out=mesh(tag+' | molded chevron tread mesh',verts,faces,treadmat,0)
  ctl=bpy.data.objects.get(tag+' | wheel spin');bpy.context.view_layer.update();mw=out.matrix_world.copy();out.parent=ctl;out.matrix_world=mw
  for ob in obs:bpy.data.objects.remove(ob,do_unlink=True)
# Reframe complete rover with floor margin
target=Vector((0,.04,.91))
cam.location=target+(cam.location-target)*1.105
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
scene.camera=cam
# Embedded reference photographs (image editor) and original mission brief.
ref_paths=[str(OUT/'manuscript/research/prototype_photos'/f'prototype_{i:02d}.jpg') for i in range(1,5)]
for i,path in enumerate(ref_paths):
 img=bpy.data.images.load(path,check_existing=True);img.name='REFERENCE %02d | Original rover'%(i+1);img.pack();img.use_fake_user=True
brief=(OUT/'docs/rover-design-brief.md').read_text(encoding='utf-8')
txt=bpy.data.texts.new('SOURCE | Nemesis mission brief');txt.write(brief)
notes="""# A3P5 NEMESIS — Blender model

## Open
Open A3P5_Nemesis_Industrial.blend. The active scene is A3P5 NEMESIS | Industrial study.
The materials, carbon weave and four distinct reference photos are packed into the file.
Five named cameras are included for hero, rear, front, side and arm-detail views.

## Reference and scale
Photo-based visual reconstruction with industrial finishing. Approximate overall dimensions:
1.086 m wide × 1.190 m long × 1.953 m high.
Dimensions and hidden construction are estimated from photographs, not measured fabrication drawings.
The user confirmed there is no solar panel.

## Configurations
The main configuration follows photos 1, 4, 5 and 6.
Collection 07 | Optional linear lift contains the tall side lift from photos 2–3.
It is hidden in the viewport and rendering by default. Enable both visibility settings to show it.

## Editing and posing
Collections 01–06 separate the chassis, running gear, arm, mast, sampling equipment and internals.
Each corner has a named steering pivot (Z axis) and wheel-spin pivot (X axis).
The arm has CTRL pivots for yaw (Z), shoulder (X), elbow (X) and wrist (X).
Cable curves are static; reshape them after large pose changes.
Repeated tire treads are consolidated per wheel for easier interaction. Their geometry remains editable.

## Mission equipment
Camera and antenna mast, work lights, air-sensor protective cans, UV window,
pH probe and turbidity sample chamber represent the supplied environmental mission description.
Collection 06 contains illustrative battery, fused distribution, motor drivers and controller packaging.
Hide the deck and body skins to inspect it.
Added sensor and concealed electronics layouts are design interpretations, not verified original internals.
The source mission brief is embedded as a Blender text block.
This is a visual 3D asset; navigation software, sensor simulation and validated engineering are not included.

## Finish
Diagonal carbon twill, aluminum and steel surfaces, rubber tires, motor details,
panel seams, captive fasteners, protected wire routes and removable equipment housings.

Created for Blender 4.3.2. Render engine: Cycles.
"""
(OUT/'README_Nemesis.md').write_text(notes,encoding='utf-8')
doc=bpy.data.texts.new('READ ME | Model and controls');doc.write(notes)
scene.cycles.samples=64
scene.render.filepath=str(OUT/'A3P5_Nemesis_Hero.png')
bpy.context.view_layer.update()
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':
  a.spaces.active.region_3d.view_perspective='PERSP'
  a.spaces.active.region_3d.view_rotation=cam.rotation_euler.to_quaternion()
  a.spaces.active.region_3d.view_location=(0,.04,.91)
  a.spaces.active.region_3d.view_distance=3.1
  a.spaces.active.overlay.show_overlays=False
  a.spaces.active.shading.type='MATERIAL'
print('Final object count',len(scene.objects))


# Complete concealed instrument packaging from mission brief.
collection('06')
box('PMS7003 particulate sensor housing',(0,.265,.637),(.072,.060,.022),blue,.0015)
box('Particulate airflow plenum',(0,.305,.637),(.085,.023,.029),black,.002)
for x in [-.023,0,.023]:
 cyl('Particulate intake duct',(x,.321,.637),.006,.010,black,(0,1,0),24)
box('BMP180 pressure and temperature PCB',(-.19,.245,.687),(.023,.028,.003),pcb,.0005)
box('BMP180 metal sensor cap',(-.19,.245,.691),(.007,.009,.004),steel,.0004)
box('FlySky compatible RC receiver package',(.21,.247,.682),(.047,.075,.026),black,.002)
cable('Receiver internal antenna',[(.218,.282,.69),(.22,.30,.712),(.11,.302,.713),(.05,.297,.715)],.001,rubber)
label('PMS package label','PMS7003',(0,.26,.650),.009,white,(0,0,0))
# Restore polished camera view in Blender.
scene.camera=cam
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':
  sp=a.spaces.active;sp.camera=cam
  if hasattr(sp,'use_local_camera'):sp.use_local_camera=True
  sp.region_3d.view_perspective='CAMERA';sp.region_3d.view_camera_zoom=-12
  sp.overlay.show_overlays=False;sp.shading.type='MATERIAL';a.tag_redraw()
bpy.context.view_layer.update()
scene['Delivered preview']='A3P5_Nemesis_Hero.png | 1600 x 1900'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'A3P5_Nemesis_Industrial.blend'))
print('FINAL',len(scene.objects),'objects')
print('PACKED REFERENCES',[(im.name,bool(im.packed_file)) for im in bpy.data.images if im.name.startswith('REFERENCE')])
print('DELIVERABLES',[(p.name,p.stat().st_size) for p in OUT.iterdir() if p.name in ['A3P5_Nemesis_Industrial.blend','A3P5_Nemesis_Hero.png','README_Nemesis.md']])


# Comprehensive cable routing revision requested by the user.
import bpy,math
from mathutils import Vector
from math import sin,cos,pi
for o in list(scene.objects):
 if o.type=='CURVE' or o.name.startswith('Arm harness clip') or o.name.startswith('Articulated cable chain link'):
  bpy.data.objects.remove(o,do_unlink=True)
if '08' not in COL:
 c=bpy.data.collections.new('08 | Secured wiring and connectors');scene.collection.children.link(c);COL['08']=c
collection('08')
sleeve=material('Black braided cable sleeving',(.008,.011,.013),.1,.52)
def attach(ob,parent):
 if parent:
  bpy.context.view_layer.update();mw=ob.matrix_world.copy();ob.parent=parent;ob.matrix_world=mw
 return ob
def harness(name,pts,r=.004,parent=None,mat=None):
 ob=cable('WIRE | '+name,pts,r,mat or sleeve)
 attach(ob,parent);ob['routing']='Terminated and supported; static presentation routing'
 return ob
def gland(name,pos,axis=(1,0,0),r=.008,parent=None):
 p=Vector(pos);a=Vector(axis).normalized();before=set(current.objects)
 cyl('CONNECTOR | '+name+' nut',p,r*1.25,.006,steel,a,n=6,bevel=.0007)
 cyl('CONNECTOR | '+name+' boot',p+a*.006,r,.014,black,a,n=32,bevel=.001)
 for t in [.003,.007,.011]:
  ring('CONNECTOR | '+name+' grip',p+a*t,r*1.09,r*.90,.0015,rubber,a,24)
 for o in set(current.objects)-before:attach(o,parent)
 return p+a*.012
def clamp(name,p,tangent=(0,1,0),radius=.004,mount=None,parent=None):
 p=Vector(p);a=Vector(tangent).normalized();before=set(current.objects)
 ring('CLAMP | '+name,p,radius+.0017,radius+.0002,.006,black,a,24)
 if mount is not None:
  mt=Vector(mount);beam('CLAMP | '+name+' saddle foot',p,mt,.008,.006,black,.0007)
  # Small captive screw set into the mounting face
  if (p-mt).length>.0001:
   normal=(p-mt).normalized()
   cyl('CLAMP | '+name+' screw',mt+normal*.001,.0023,.002,steel,normal,n=6,bevel=.0003)
 for o in set(current.objects)-before:attach(o,parent)
def terminal_pair(name,pos,axis=(1,0,0),parent=None):
 p=Vector(pos);axis=Vector(axis);before=set(current.objects)
 # Insulated boot bridges the original two motor terminals.
 box('CONNECTOR | '+name+' molded terminal boot',p,(.021,.039,.022),black,.004)
 for o in set(current.objects)-before:attach(o,parent)
 return p
# Frame trunks, branched connections and compact corner loops.
for sx in [-1,1]:
 side='R' if sx>0 else 'L'
 p=gland(side+' chassis bulkhead',(sx*.307,0,.489),(sx,0,0),.009)
 trunkx=sx*.350
 harness(side+' chassis-to-rail feed',[p,(sx*.333,0,.489),(trunkx,0,.481)],.005)
 box('WIRE | '+side+' rail distribution junction',(trunkx,0,.480),(.025,.043,.022),black,.003)
 harness(side+' clipped rail backbone',[(trunkx,-.417,.481),(trunkx,-.22,.481),(trunkx,0,.481),(trunkx,.22,.481),(trunkx,.417,.481)],.0045)
 for yy in [-.35,-.23,-.10,.10,.23,.35]:
  clamp(side+' rail P clip',(trunkx,yy,.481),radius=.0045,mount=(sx*.360,yy,.473))
 for sy in [-1,1]:
  y=sy*.454;tag=side+('F' if sy<0 else 'R');ctl=bpy.data.objects.get(tag+' | steering pivot')
  # Branch box rests on the inner face of the fixed spar.
  box('CONNECTOR | '+tag+' corner distribution',(trunkx,sy*.417,.481),(.022,.028,.020),black,.003)
  # Signal boot enters the inward-facing side of the blue steering unit.
  q=gland(tag+' steering servo',(sx*.386,y-sy*.021,.526),(0,-sy,0),.0045,ctl)
  harness(tag+' steering service bend',[(trunkx,sy*.416,.482),(sx*.350,y-sy*.056,.494),(sx*.369,y-sy*.053,.517),q],.003,ctl)
  clamp(tag+' steering loop fixed anchor',(trunkx,sy*.416,.482),(0,sy,0),.003,(sx*.360,sy*.416,.476))
  clamp(tag+' servo strain relief',(sx*.379,y-sy*.049,.521),(sx*.3,-sy,.3),.003,(sx*.386,y-sy*.026,.510),ctl)
  # Motor feed follows the inward rear face of the C fork.
  q0=gland(tag+' fork feed',(sx*.360,y-.009,.443),(-sx,0,0),.005,ctl)
  q1=gland(tag+' axle motor',(sx*.348,y-.003,.148),(-sx,0,0),.0055,ctl)
  pts=[q0,(sx*.355,y+.014,.406),(sx*.359,y+.029,.354),(sx*.359,y+.010,.315),(sx*.359,y-.019,.270),(sx*.359,y-.050,.219),(sx*.350,y-.050,.175),q1]
  harness(tag+' fork motor loom',pts,.0035,ctl)
  for yy,zz in [(y+.026,.358),(y-.010,.287),(y-.049,.217)]:
   clamp(tag+' fork loom retainer',(sx*.359,yy,zz),(0,-.4,-1),.0035,(sx*.369,yy,zz),ctl)
  # Short external connection between backbone and sealed fork feed.
  harness(tag+' steering-axis power loop',[(trunkx,sy*.417,.478),(sx*.333,y-sy*.033,.472),(sx*.333,y-.012,.453),q0],.0035,ctl)
# Arm motor cables are kept close to the metal cheeks and gearboxes.
yaw=bpy.data.objects.get('CTRL | Arm yaw');elbow=bpy.data.objects.get('CTRL | Elbow pitch');wrist=bpy.data.objects.get('CTRL | Wrist pitch')
S=Vector((-.08,-.175,1.13));E=Vector((-.08,.203,1.383));W=Vector((-.08,-.520,1.076))
terminal_pair('elbow motor',(.133,.203,1.380),parent=elbow)
terminal_pair('shoulder motor',(.133,-.175,1.127),parent=yaw)
for tag,p,par in [('elbow',E,elbow),('shoulder',S,yaw)]:
 for dy,mt in [(.013,red),(-.013,black)]:
  harness(tag+' short terminal tail',[p+Vector((.199,dy,0)),p+Vector((.208,dy,0)),p+Vector((.213,dy,-.005))],.0018,par,mt)
q=gland('arm pedestal harness',(.006,-.12,.887),(1,0,0),.009)
box('WIRE | shoulder junction',(.007,-.112,1.040),(.024,.031,.047),black,.003)
harness('elbow motor along upper rail',[(.138,.203,1.374),(.141,.178,1.351),(.083,.167,1.343),(.006,.153,1.350),(.006,.075,1.300),(.006,-.024,1.234),(.011,-.096,1.183),(.015,-.130,1.151),(.014,-.127,1.088),(.016,-.112,1.049)],.0036,yaw)
for t in [.22,.46,.72]:
 p=S.lerp(E,t)+Vector((.086,0,-.002))
 clamp('upper arm motor loom',p,E-S,.0036,p+Vector((-.014,0,0)),yaw)
harness('shoulder motor branch',[(.137,-.175,1.120),(.140,-.154,1.103),(.117,-.116,1.087),(.045,-.110,1.073),(.016,-.112,1.049)],.0036,yaw)
clamp('shoulder motor branch',(.080,-.112,1.080),(1,0,.2),.0036,(.065,-.124,1.093),yaw)
harness('arm upright to pedestal',[(.016,-.112,1.049),(.015,-.112,1.009),(.020,-.118,.970),(.026,-.122,.925),q],.005,yaw)
for zz in [1.01,.974]:
 clamp('upright cable retainer',(.016,-.112,zz),(0,0,1),.005,(.002,-.112,zz),yaw)
# Main forearm loom runs behind the port-side rails; deliberate joint bend.
q0=gland('forearm supply base',(-.169,-.15,.887),(-1,0,0),.008)
q1=gland('wrist servo input',(-.137,-.52,1.079),(-1,0,0),.005,wrist)
harness('arm port-side supply',[q0,(-.177,-.145,.927),(-.163,-.14,1.009),(-.160,-.11,1.139),(-.160,.046,1.264),(-.160,.183,1.361),(-.159,.237,1.390),(-.159,.217,1.417),(-.161,.172,1.388),(-.162,.06,1.342),(-.162,-.10,1.273),(-.162,-.29,1.192),(-.162,-.454,1.122),q1],.0045,yaw)
for t in [.22,.43,.65,.85]:
 p=E.lerp(W,t)+Vector((-.081,0,.017))
 clamp('forearm loom saddle',p,W-E,.0045,p+Vector((.014,0,-.017)),yaw)
for t in [.28,.62]:
 p=S.lerp(E,t)+Vector((-.080,0,.010))
 clamp('port upper rail loom',p,E-S,.0045,p+Vector((.014,0,-.010)),yaw)
q2=gland('gripper actuator input',(-.121,-.535,1.010),(-1,0,0),.0045,wrist)
harness('wrist anchored flex loop',[q1,(-.158,-.526,1.067),(-.157,-.543,1.039),(-.144,-.543,1.017),q2],.003,wrist)
clamp('wrist servo loop anchor',(-.154,-.526,1.068),(0,0,1),.003,(-.138,-.526,1.068),wrist)
clamp('wrist actuator loop anchor',(-.138,-.541,1.019),(1,0,0),.003,(-.119,-.541,1.019),wrist)
# Fixed mast loom: rear face clear of LEDs, sealed at both ends.
A=Vector((.207,.253,.781));B=Vector((.207,.548,1.66));D=(B-A).normalized()
qa=gland('mast deck feed',(.251,.258,.775),(0,0,1),.0075)
qb=gland('camera head underside',(.210,.567,1.665),(0,0,-1),.0055)
pts=[qa,(.248,.272,.814),(.229,.294,.845),(.220,.298,.879)]
pts += [A.lerp(B,t)+Vector((.011,.016,0)) for t in [.2,.4,.6,.8,.95]]
pts += [qb]
harness('mast protected rear loom',pts,.0038)
clamp('mast loop deck anchor',(.246,.278,.823),(0,.4,1),.0038,(.234,.276,.812))
for t in [.16,.36,.57,.78,.94]:
 p=A.lerp(B,t)+Vector((.011,.016,0))
 clamp('mast rear loom retainer',p,D,.0038,A.lerp(B,t))
# Probe signal is dressed along the existing sampling bracket.
qp=gland('pH probe signal',(.535,-.10,.442),(0,0,1),.004)
qi=gland('water quality data',(.307,.083,.511),(1,0,0),.006)
harness('pH probe secured signal',[qp,(.535,-.10,.472),(.531,-.055,.481),(.526,-.008,.486),(.462,.035,.486),(.390,.064,.492),qi],.0028)
for p,mt in [((.535,-.105,.473),(.519,-.105,.451)),((.531,-.055,.481),(.518,-.055,.455)),((.451,.04,.487),(.44,.04,.475)),((.377,.067,.494),(.371,.067,.476))]:
 clamp('sample probe lead',p,(0,1,0),.0028,mt)
# Fluid hose stows in a fixed quick-disconnect, with no dangling hose end.
qh=gland('turbidity fluid outlet',(.373,.126,.487),(1,0,0),.006)
box('CONNECTOR | sampling hose stow bracket',(.517,-.248,.450),(.021,.025,.026),black,.002)
qt=gland('sampling hose stow coupler',(.517,-.248,.466),(0,0,1),.0065)
harness('clipped sampling fluid hose',[qh,(.421,.105,.494),(.505,.015,.492),(.534,-.058,.484),(.534,-.157,.480),qt],.0045,mat=white)
for yy in [-.075,-.177]:
 clamp('sample hose edge clip',(.534,yy,.482),(0,1,0),.0045,(.518,yy,.451))
# Short instrumentation wires enter their housing from below.
for xx in [-.176,-.112,-.048]:
 qg=gland('gas sensing module', (xx,.24,.867),(0,0,-1),.0038)
 harness('gas sensor base jumper',[qg,(xx,.24,.850)],.0025)
# Hidden power wiring terminates at actual modeled distribution packages.
qpos=gland('battery positive',(-.095,.132,.492),(0,1,0),.005)
qneg=gland('battery negative',(-.074,.132,.492),(0,1,0),.005)
qf=gland('fused distribution input',(-.164,.166,.541),(0,-1,0),.005)
box('WIRE | common ground bus',(-.065,.205,.547),(.027,.023,.017),black,.002)
qg=gland('ground bus input',(-.066,.190,.550),(0,-1,0),.005)
harness('fused battery positive',[qpos,(-.096,.164,.500),(-.14,.172,.529),qf],.0045,mat=red)
harness('battery ground return',[qneg,(-.072,.164,.507),(-.066,.174,.534),qg],.0045)
clamp('battery positive strain relief',(-.109,.168,.510),(1,0,1),.0045,(-.109,.155,.503))
clamp('battery return strain relief',(-.068,.17,.523),(0,0,1),.0045,(-.068,.153,.518))
# RC aerial terminates in a secured insulated radiator, not a loose wire.
box('WIRE | receiver antenna dielectric mount',(.045,.296,.711),(.034,.014,.008),white,.001)
harness('receiver coax to fixed aerial',[(.218,.282,.686),(.219,.298,.698),(.160,.299,.709),(.08,.298,.713),(.045,.296,.713)],.0015)
for x in [.10,.17]:
 clamp('receiver aerial clip',(x,.299,.711),(1,0,0),.0015,(x,.302,.702))
print('External and internal cable harnesses rebuilt with connectors and clips')


# Tighten shoulder loom against motor underside with a real mounting contact.
collection('08')
for ob in list(COL['08'].objects):
 if ob.name=='WIRE | shoulder motor branch' or ob.name.startswith('CLAMP | shoulder motor branch'):
  bpy.data.objects.remove(ob,do_unlink=True)
harness('shoulder motor branch',[(.137,-.175,1.120),(.139,-.177,1.098),(.110,-.173,1.097),(.060,-.164,1.091),(.030,-.137,1.078),(.016,-.112,1.049)],.0036,yaw)
clamp('shoulder motor underside',(.080,-.169,1.093),(1,0,.12),.0036,(.080,-.168,1.107),yaw)

# Functional-looking cable carrier for the optional lift.
collection('07')
chainpts=[]
for i in range(21):chainpts.append(Vector((.395,.222,.389+i*(1.12-.389)/20)))
for i in range(1,13):
 a=pi*i/12;chainpts.append(Vector((.395,.157+.065*cos(a),1.12+.065*sin(a))))
for i in range(1,8):chainpts.append(Vector((.395,.092,1.12-i*(1.12-.894)/7)))
chainpts.append(Vector((.395,.145,.882)))
harness('lift internal flexible loom',chainpts,.005)
for i in range(0,len(chainpts)-1):
 p=chainpts[i].lerp(chainpts[i+1],.5);v=chainpts[i+1]-chainpts[i]
 for dx in [-.014,.014]:
  ob=box('WIRE | lift carrier cheek',p+Vector((dx,0,0)),(.006,.018,v.length*.9),black,.001)
  ob.rotation_euler=v.to_track_quat('Z','Y').to_euler()
 rod('WIRE | lift carrier cross pin',p+Vector((-.016,0,0)),p+Vector((.016,0,0)),.0025,steel,12)
box('CONNECTOR | lift fixed carrier bracket',(.395,.212,.386),(.043,.032,.028),black,.003)
box('CONNECTOR | lift carriage carrier bracket',(.395,.143,.884),(.043,.027,.026),black,.003)
for z,y in [(.393,.222),(.891,.145)]:
 bolt('Lift cable carrier anchor',(.395,y,z),r=.003)
# Field sensor and control supply harnesses hidden below body skins.
collection('08')
for name,pts in [
 ('regulated logic supply',[(-.066,.211,.550),(-.035,.217,.550),(.035,.212,.568),(.085,.151,.582)]),
 ('MCU signal trunk',[(.101,.089,.574),(.143,.103,.577),(.168,.176,.611),(.196,.221,.680)]),
 ('particle sensor cable',[(.101,.09,.574),(.101,.185,.598),(.055,.227,.626),(.035,.249,.638)]),
 ('barometric sensor cable',[(-.18,.241,.686),(-.155,.223,.681),(-.132,.21,.65),(-.095,.205,.550)])
]:
 harness(name,pts,.0025)
 for p in [pts[0],pts[-1]]:
  box('CONNECTOR | '+name+' plug',p,(.009,.012,.008),black,.001)
# Update notes and persist the latest deliverables.
notes=(OUT/'README_Nemesis.md').read_text(encoding='utf-8')
notes += """
## Wiring revision
Collection 08 organizes the secured harnesses and connectors.
Cable runs follow the arm rails, steering forks, mast and chassis spars.
The model includes connector boots, sealed glands, P-clamps, clipped tubing,
short colored motor tails, and controlled bends at moving assemblies.
The optional lift has a supported cable carrier with fixed and moving end brackets.
Cable placement was visually checked in the displayed pose; curves remain static when posing.
"""
(OUT/'README_Nemesis.md').write_text(notes,encoding='utf-8')
t=bpy.data.texts.get('READ ME | Model and controls');t.clear();t.write(notes)
scene['Wiring revision']='Clipped and connector-terminated harnesses. Localized service bends at moving joints. Static presentation cable curves.'
scene.camera=cam
scene.render.resolution_x=1600;scene.render.resolution_y=1900;scene.render.resolution_percentage=100;scene.cycles.samples=64
scene.render.filepath=str(OUT/'A3P5_Nemesis_Hero.png')
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'A3P5_Nemesis_Industrial.blend'))
print('Saved managed harness revision:',len([o for o in scene.objects if o.type=='CURVE']),'cable and hose curves')
print('Clamps',len([o for o in scene.objects if o.name.startswith('CLAMP |') and 'screw' not in o.name and 'foot' not in o.name]))


collection('90')
detail=camera('06 | Managed wiring close-up',(1.48,-.86,1.67),(.025,-.07,1.075),74)
# Render a close view first so the cable connections can be inspected.
scene.camera=detail
scene.render.resolution_x=1320;scene.render.resolution_y=1180;scene.render.resolution_percentage=100
scene.cycles.samples=48
scene.render.filepath=str(OUT/'A3P5_Nemesis_Wiring_Detail.png')
print('Cable-detail view ready')


# Route the probe lead along the sample-rack rear edge and the frame.
collection('08')
for o in list(COL['08'].objects):
 if o.name=='WIRE | pH probe secured signal' or o.name.startswith('CLAMP | sample probe lead'):
  bpy.data.objects.remove(o,do_unlink=True)
qp=Vector((.535,-.10,.454));qi=Vector((.319,.083,.511))
harness('pH probe secured signal',[qp,(.535,-.10,.472),(.531,-.059,.474),(.488,-.049,.464),(.415,-.049,.464),(.392,-.046,.492),(.357,-.044,.498),(.348,-.020,.49),(.348,.059,.49),qi],.0028)
for p,mt,tan in [
 ((.535,-.105,.473),(.519,-.105,.451),(0,1,0)),
 ((.488,-.049,.464),(.488,-.049,.455),(1,0,0)),
 ((.415,-.049,.464),(.415,-.049,.455),(1,0,0)),
 ((.348,.043,.49),(.356,.043,.478),(0,1,0))
]:clamp('sample probe lead',p,tan,.0028,mt)
# Clamp alignment QA: snap each collar to the cable centerline, and each
# mounting foot into the nearest supporting rover surface.
from mathutils.geometry import interpolate_bezier
from mathutils.bvhtree import BVHTree
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
segments=[]
for o in scene.objects:
 if o.type!='CURVE':continue
 for spl in o.data.splines:
  ps=spl.bezier_points
  for a,b in zip(ps,list(ps)[1:]):
   pp=interpolate_bezier(a.co,a.handle_right,b.handle_left,b.co,18)
   pp=[o.matrix_world@p for p in pp]
   for aa,bb in zip(pp,pp[1:]):
    if (bb-aa).length>1e-7:segments.append((aa,bb,o.data.bevel_depth))
def nearest_wire(p):
 best=None
 for a,b,r in segments:
  d=b-a;t=max(0,min(1,(p-a).dot(d)/d.length_squared));q=a+t*d
  if best is None or (q-p).length<best[0]:best=((q-p).length,q,d.normalized(),r)
 return best
# Build one acceleration structure of the actual support geometry.
vv=[];ff=[]
for o in scene.objects:
 if o.type!='MESH' or not any(c.name[:2] in ['01','02','03','04','05','06','07'] for c in o.users_collection) or o.name.startswith(('WIRE |','CONNECTOR |','CLAMP |')):continue
 ev=o.evaluated_get(deps);me=ev.to_mesh();off=len(vv);vv += [o.matrix_world@v.co for v in me.vertices];ff += [tuple(off+i for i in p.vertices) for p in me.polygons];ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(vv,ff,all_triangles=False)
# Preserve each existing name and parent while correcting its collar and foot.
collars=[o for o in list(scene.objects) if o.name.startswith('CLAMP |') and 'saddle foot' not in o.name and 'screw' not in o.name]
fixed=0
for ob in collars:
 name=ob.name;par=ob.parent;p=ob.matrix_world.translation.copy();closest=nearest_wire(p)
 if not closest or closest[0]>.025:continue
 _,q,tan,r=closest
 # Blender suffixes occur after the base name; find matching foot and screw.
 base=name; suffix=''
 if len(name)>4 and name[-4]=='.' and name[-3:].isdigit():base=name[:-4];suffix=name[-4:]
 foot=bpy.data.objects.get(base+' saddle foot'+suffix)
 screw=bpy.data.objects.get(base+' screw'+suffix)
 if foot:
  zz=max(v.co.z for v in foot.data.vertices);mt=foot.matrix_world@Vector((0,0,zz));hit=bvh.find_nearest(mt)
  if hit:
   mount=hit[0];n=(q-mount).normalized() if (q-mount).length>.001 else hit[1]
   mount_inside=mount-n*.001
   footname=foot.name;bpy.data.objects.remove(foot,do_unlink=True)
   new=beam(footname,q,mount_inside,.008,.006,black,.0007);attach(new,par)
   if screw:
    screwname=screw.name;bpy.data.objects.remove(screw,do_unlink=True)
    new=cyl(screwname,mount+n*.0012,.0023,.002,steel,n,n=6,bevel=.0003);attach(new,par)
 bpy.data.objects.remove(ob,do_unlink=True)
 new=ring(name,q,r+.0017,r+.0002,.006,black,tan,24);attach(new,par);new['attachment_checked']=True
 fixed+=1
bpy.context.view_layer.update()
scene['Cable clamp QA']='Collars aligned to evaluated cable centerlines; mounting feet terminate inside the nearest rover support surfaces.'
print('Aligned collars and supporting mounts:',fixed)
scene.camera=cam;scene.render.resolution_x=1600;scene.render.resolution_y=1900;scene.cycles.samples=64;scene.render.filepath=str(OUT/'A3P5_Nemesis_Hero.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'A3P5_Nemesis_Industrial.blend'))

# Keep live construction helpers for the mission-scene builder in this session.
bpy.app.driver_namespace['NEMESIS']=globals()
