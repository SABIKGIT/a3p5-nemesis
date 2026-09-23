import bpy, math, random
from pathlib import Path
from mathutils import Vector
from math import pi
if 'NEMESIS' not in bpy.app.driver_namespace:
 raise RuntimeError('Run nemesis_build.py before this script in the same Blender process; see docs/reproduce.md.')
ns=bpy.app.driver_namespace['NEMESIS']
base=bpy.data.scenes['A3P5 NEMESIS | Industrial study']
out=Path(__file__).resolve().parent
out.mkdir(parents=True,exist_ok=True)
base_colls=[c for c in base.collection.children if c.name[:2] in ['01','02','03','04','05','06','08']]
box,cyl,rod,ring,label,camera,area,material=[ns[n] for n in ['box','cyl','rod','ring','label','camera','area','material']]
concrete=material('Mission | pale concrete',(0.39,0.43,0.45),rough=.85)
pavement=material('Mission | ground',(0.16,0.19,0.20),rough=.93)
paint=material('Mission | muted teal',(0.028,0.17,0.20),metal=.2,rough=.44)
clay=material('Mission | terracotta rubble',(0.25,0.12,0.07),rough=.94)
water=material('Mission | sample water',(0.015,0.17,0.21),rough=.16,coat=.5)
plastic=material('Mission | vessel translucent',(0.37,0.58,0.63),rough=.20,coat=.4)
white=ns['white'];silver=ns['silver'];black=ns['black'];yellow=ns['yellow'];cyan=ns['cyan']
missions=[]
def new_scene(name,camloc,target,lens=52):
 s=bpy.data.scenes.new(name)
 s.world=base.world.copy();s.world.name=name+' | ambient'
 for c in base_colls:s.collection.children.link(c)
 c=bpy.data.collections.new(name+' | environment');s.collection.children.link(c)
 ns['scene']=s;ns['current']=c
 s.render.engine='CYCLES';s.cycles.samples=40;s.cycles.use_denoising=True
 s.render.resolution_x=1800;s.render.resolution_y=1250;s.render.resolution_percentage=100
 s.render.image_settings.file_format='PNG';s.render.film_transparent=False
 s.view_settings.view_transform=base.view_settings.view_transform
 s.view_settings.look=base.view_settings.look
 box(name+' | ground',(0,0,-.027),(12,12,.05),pavement,.002)
 area(name+' | sky softbox',(1,-2,5),(0,0,.6),1500,(.86,.93,1),5)
 area(name+' | side reflection',(-3,-.5,2.5),(0,0,.8),950,(1,.85,.68),3)
 area(name+' | rim',(0,3,3),(0,0,1),1400,(.75,.92,1),3)
 cam=camera(name+' | camera',camloc,target,lens);s.camera=cam
 s['evidence']='Conceptual Blender mission illustration; no physical mission results.'
 s['preserved_layout']='Original chassis, wheel, manipulator, mast and managed wiring positions retained.'
 missions.append(s)
 return s
# Air-quality inspection: stationary observation beside industrial piping.
s=new_scene('M01 | Industrial air monitoring',(2.7,-3.7,2.35),(0,.14,.86),55)
box('M01 | backdrop wall',(0,2.1,1.25),(6,.18,2.5),concrete,.02)
for x in [-1.7,-1.35,1.15]:
 rod('M01 | process pipe',(x,1.86,.2),(x,1.86,2.15),.065,silver)
 for z in [.38,1.2,2.0]:ring('M01 | pipe flange',(x,1.86,z),.09,.064,.035,black)
rod('M01 | cross-pipe',(-1.7,1.86,1.95),(1.3,1.86,1.95),.06,silver)
for x,y in [(-1.05,.72),(-1.45,.65)]:
 cyl('M01 | sealed drum',(x,y,.35),.20,.7,paint)
 for z in [.08,.62]:ring('M01 | drum bead',(x,y,z),.207,.195,.025,silver)
for x in [-.8,.8]:box('M01 | sampling boundary stripe',(x,-.05,.001),(.035,1.6,.003),yellow,.001)
label('M01 | inspection area sign','ENVIRONMENTAL INSPECTION',(0,1.988,1.6),.12,black)
# Water: pH probe tip submerged at original stowed mounting position into raised sample vessel.
s=new_scene('M02 | Water sample assessment',(1.8,-2.4,1.35),(.13,-.07,.71),64)
s['sample_access']='Illustrative staged vessel beneath fixed pH probe; automated deployment is not demonstrated.'
box('M02 | sampling plinth',(.72,-.1,.065),(.50,.40,.13),concrete,.015)
box('M02 | spill tray',(.61,-.1,.138),(.29,.25,.014),silver,.006)
ring('M02 | open sample vessel',(.535,-.10,.226),.071,.064,.17,plastic)
cyl('M02 | vessel base',(.535,-.10,.145),.067,.007,plastic)
cyl('M02 | water surface below probe',(.535,-.10,.235),.063,.128,water)
for z in [.19,.22,.25,.28]:
 rod('M02 | volume marking',(.596,-.124,z),(.598,-.096,z),.0015,white)
box('M02 | water channel',(1.75,.5,.13),(1.20,4,.26),concrete,.025)
box('M02 | water channel surface',(1.75,.5,.267),(.90,4,.006),water,.001)
for y in [.7,1.3]:
 cyl('M02 | reserve sample bottle',(.80,y,.10),.052,.19,white)
 cyl('M02 | bottle cap',(.80,y,.204),.054,.021,paint)
# Small vial pickup at gripper, preserves existing wrist and cable geometry.
s=new_scene('M03 | Lightweight sample handling',(1.65,-2.65,1.62),(-.03,-.18,.82),64)
cyl('M03 | gripped sample vial',(-.08,-.542,.804),.014,.105,white)
cyl('M03 | sample cap in jaws',(-.08,-.542,.853),.016,.015,paint)
box('M03 | sample label',(-.080,-.558,.796),(.022,.001,.039),yellow,.001)
box('M03 | pickup bench',(-.08,-.76,.695),(.55,.44,.028),silver,.01)
for x in [-.31,.15]:
 for y in [-.94,-.58]:rod('M03 | bench leg',(x,y,0),(x,y,.682),.014,black)
for x in [-.24,.10]:
 cyl('M03 | spare vial',(x,-.82,.769),.022,.115,white)
 cyl('M03 | spare cap',(x,-.82,.83),.025,.018,paint)
# Disaster visual inspection. Small debris kept away from wheel contacts; not a traversability demonstration.
s=new_scene('M04 | Disaster reconnaissance',(2.6,-3.8,2.3),(0,.1,.82),56)
random.seed(51)
for i in range(36):
 x=random.uniform(-2.1,2.1);y=random.uniform(.8,2.5)
 o=box('M04 | loose masonry',(x,y,random.uniform(.05,.13)),(random.uniform(.1,.4),random.uniform(.12,.27),random.uniform(.07,.22)),clay,.015)
 o.rotation_euler[2]=random.uniform(-pi,pi)
for x in [-1.8,1.9]:box('M04 | damaged pillar',(x,1.6,.9),(.25,.35,1.8),concrete,.025)
o=box('M04 | fallen structural beam',(0,2.1,.44),(3.1,.23,.24),concrete,.02);o.rotation_euler[1]=.18
rod('M04 | exposed conduit',(-1.7,1.47,.65),(-.85,1.0,.12),.018,silver)
# Patrol with proposed compact navigation sensors; original arm/mast retained.
s=new_scene('M05 | Proposed autonomous patrol',(2.7,-3.8,2.8),(0,.1,.80),56)
s['proposed_additions']='Deck LiDAR + humidity pod + mast depth camera. These have not been verified on the physical prototype.'
box('M05 | lidar foot',(-.22,.085,.78),(.085,.09,.025),silver)
cyl('M05 | proposed compact LiDAR',(-.22,.085,.838),.045,.088,black)
ring('M05 | lidar optical band',(-.22,.085,.841),.046,.043,.019,paint)
box('M05 | proposed RH pod',(-.242,.241,.802),(.047,.060,.055),white,.005)
for y in [.22,.23,.24,.25]:box('M05 | RH vent',(-.242,y,.831),(.033,.003,.002),black,.001)
box('M05 | proposed depth-camera bracket',(.207,.536,1.616),(.115,.043,.025),silver)
box('M05 | proposed depth camera',(.207,.511,1.627),(.11,.035,.035),black,.005)
for x in [.167,.247]:cyl('M05 | depth camera lens',(x,.49,1.63),.010,.010,ns['glass'],axis=(0,-1,0))
for y in [-1.65,-1.35,-1.05,-.75,.8,1.1,1.4]:box('M05 | planned route segment',(.02,y,.006),(.035,.14,.009),cyan,.002)
for x,y in [(-1.15,.3),(1.20,1.2)]:
 box('M05 | obstacle crate',(x,y,.32),(.45,.45,.64),paint,.02)
 for z in [.05,.60]:box('M05 | crate frame',(x,y,z),(.48,.48,.04),silver)
# Orthographic sheet camera, shared model and light ground.
s=new_scene('M06 | Engineering overview',(2.8,-3.6,2.5),(0,.04,.95),55)
s.camera.data.type='ORTHO';s.camera.data.ortho_scale=2.55
s.render.resolution_x=1550;s.render.resolution_y=1600
s['evidence']='Photo-based geometric reconstruction; dimensions are estimates, not a metrological scan.'
# Context-specific detail camera for immersion view.
ns['scene']=bpy.data.scenes['M02 | Water sample assessment'];ns['current']=bpy.data.collections['M02 | Water sample assessment | environment']
cam=camera('M02 | Probe immersion detail',(1.15,-.72,.72),(.52,-.10,.32),72)
# Put the finished source in a separate file; approved industrial file remains unchanged.
for s in missions:s.render.filepath=str(out/(s.name[:3]+'_mission.png'))
bpy.context.window.scene=bpy.data.scenes['M01 | Industrial air monitoring']
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'A3P5_Nemesis_Mission_Studies.blend'))
ns['scene']=base;ns['current']=ns['COL']['08']
print('Created mission scenes:',[(s.name,len(s.objects)) for s in missions])
