import bpy, json, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
reports=[]
for file in [root/'A3P5_Nemesis_Industrial.blend',root/'manuscript/blender/A3P5_Nemesis_Mission_Studies.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(file),load_ui=False)
 reports.append({'file':file.relative_to(root).as_posix(),'objects':len(bpy.data.objects),'scenes':len(bpy.data.scenes),'images':[{'name':im.name,'packed':bool(im.packed_file),'filepath':im.filepath} for im in bpy.data.images],'texts':[{'name':t.name,'characters':len(t.as_string())} for t in bpy.data.texts],'libraries':[x.filepath for x in bpy.data.libraries]})
(root/'verification/blender_input_inventory.json').write_text(json.dumps(reports,indent=2),encoding='utf8')
print('BLENDER_INVENTORY_DONE')
