"""Normalize asset paths in these repository copies; geometry is verified unchanged.
Run with Blender --background --factory-startup --python scripts/prepare_blender_distribution.py.
"""
import bpy, json, hashlib, array, struct, re
from pathlib import Path
root=Path(__file__).resolve().parents[1]

def geometry_signature():
 h=hashlib.sha256()
 for mesh in sorted(bpy.data.meshes,key=lambda x:x.name):
  h.update(mesh.name.encode())
  coords=array.array('f',[0.0])*(len(mesh.vertices)*3);mesh.vertices.foreach_get('co',coords);h.update(coords.tobytes())
  indexes=array.array('i',[0])*len(mesh.loops);mesh.loops.foreach_get('vertex_index',indexes);h.update(indexes.tobytes())
  counts=array.array('i',[0])*len(mesh.polygons);mesh.polygons.foreach_get('loop_total',counts);h.update(counts.tobytes())
 for obj in sorted(bpy.data.objects,key=lambda x:x.name):
  h.update(obj.name.encode());h.update(struct.pack('<16d',*(v for row in obj.matrix_world for v in row)))
  h.update(str([x.name for x in obj.material_slots]).encode())
 return h.hexdigest()

reports=[]
for file in [root/'A3P5_Nemesis_Industrial.blend',root/'manuscript/blender/A3P5_Nemesis_Mission_Studies.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(file),load_ui=False)
 bpy.context.preferences.filepaths.save_version=0
 before=geometry_signature();images=[]
 for image in bpy.data.images:
  match=re.match(r'REFERENCE (\d+)',image.name)
  if match:
   source=root/'manuscript/research/prototype_photos'/('prototype_%02d.jpg'%int(match[1]))
   packed_bytes=bytes(image.packed_file.data) if image.packed_file else source.read_bytes()
   if image.packed_file:image.unpack(method='REMOVE')
   image.filepath=bpy.path.relpath(str(source),start=str(file.parent)).replace(chr(92),'/')
   image.pack(data=packed_bytes,data_len=len(packed_bytes))
   assert hashlib.sha256(bytes(image.packed_file.data)).digest()==hashlib.sha256(packed_bytes).digest()
   for packed in image.packed_files:packed.filepath=image.filepath
  images.append({'name':image.name,'packed':bool(image.packed_file),'filepath':image.filepath})
 for screen in bpy.data.screens:
  for area in screen.areas:
   for space in area.spaces:
    if space.type=='FILE_BROWSER' and space.params:
     space.params.directory=b'/'*max(2,len(space.params.directory))
     space.params.directory=b'//'
 for scene in bpy.data.scenes:
  if scene.render.filepath:scene.render.filepath='//'+Path(scene.render.filepath.replace('\\','/')).name
 for text in bpy.data.texts:
  if text.name.startswith('SOURCE |'):
   text.clear();text.write((root/'docs/rover-design-brief.md').read_text(encoding='utf8'));text.name='SOURCE | Public rover design brief'
  elif text.name.startswith('READ ME'):
   content=text.as_string().replace('original mission brief','public design brief').replace('Original mission brief','Public design brief')
   text.clear();text.write(content)
 assert geometry_signature()==before
 bpy.ops.wm.save_as_mainfile(filepath=str(file))
 bpy.ops.wm.open_mainfile(filepath=str(file),load_ui=False)
 assert geometry_signature()==before
 assert all(not re.match(r'[A-Za-z]:',im.filepath) for im in bpy.data.images)
 reports.append({'file':file.relative_to(root).as_posix(),'geometry_sha256':before,'objects':len(bpy.data.objects),'scenes':len(bpy.data.scenes),'images':images,'geometry_unchanged_after_save_reload':True,'changes':['repository-relative reference-image and render paths; packed image bytes preserved; saved file-browser location cleared','public design brief replaces superseded embedded mission brief'],'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
(root/'verification/blender_distribution.json').write_text(json.dumps(reports,indent=2),encoding='utf8')
print('BLENDER_DISTRIBUTION_PASS',len(reports))
