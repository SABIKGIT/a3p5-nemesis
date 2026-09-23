import bpy,json,time
from pathlib import Path
out=Path(__file__).resolve().parent
out.mkdir(parents=True,exist_ok=True)
log=[]
for s in bpy.data.scenes:
 if s.name.startswith('M0'):
  s.render.filepath=str(out/Path(s.render.filepath.replace('\\','/')).name)
  s.render.threads_mode='FIXED';s.render.threads=8
  t=time.time();bpy.context.window.scene=s
  bpy.ops.render.render(write_still=True,scene=s.name)
  log.append({'scene':s.name,'file':s.render.filepath,'seconds':time.time()-t})
  (out/'render_log.json').write_text(json.dumps(log,indent=2))
s=bpy.data.scenes['M02 | Water sample assessment'];s.camera=bpy.data.objects['M02 | Probe immersion detail'];s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.filepath=str(out/'M02_probe_detail.png')
bpy.context.window.scene=s;bpy.ops.render.render(write_still=True,scene=s.name)
(out/'render_complete.txt').write_text('All six mission views and probe detail rendered.')

s=bpy.data.scenes["M03 | Lightweight sample handling"];s.camera=bpy.data.objects["M03 | Gripper task detail"];s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.filepath=str(out/"M03_gripper_detail.png")
bpy.context.window.scene=s;bpy.ops.render.render(write_still=True,scene=s.name)
