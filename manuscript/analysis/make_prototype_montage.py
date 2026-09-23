from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from matplotlib.font_manager import FontProperties, findfont
import hashlib,json
base=Path(__file__).resolve().parents[1]
src=base/'research'/'prototype_photos'
out=base/'figures'/'prototype_views.png'
W=1800; margin=40; gutter=40; cell_w=840; photo_h=1180; label_h=160
H=2*(photo_h+label_h)+2*margin+gutter
canvas=Image.new('RGB',(W,H),'white')
draw=ImageDraw.Draw(canvas)
font=ImageFont.truetype(findfont(FontProperties(family='DejaVu Sans',weight='bold')),60)
labels=[['(a) Front oblique'],['(b) Alternate configuration'],['(c) Manipulator and','optional lift'],['(d) Elevated deck view']]
records=[]
for i,lines in enumerate(labels):
 p=src/f'prototype_{i+1:02d}.jpg'
 before=hashlib.sha256(p.read_bytes()).hexdigest()
 original=Image.open(p).convert('RGB')
 ratio=min(cell_w/original.width,photo_h/original.height)
 size=(round(original.width*ratio),round(original.height*ratio))
 im=original.resize(size,Image.Resampling.LANCZOS)
 x=margin+(i%2)*(cell_w+gutter);y=margin+(i//2)*(photo_h+label_h+gutter)
 px=x+(cell_w-im.width)//2;py=y+(photo_h-im.height)//2
 canvas.paste(im,(px,py))
 draw.rectangle((px,py,px+im.width-1,py+im.height-1),outline=(195,199,202),width=2)
 linegap=10; text_h=len(lines)*65+(len(lines)-1)*linegap
 ly=y+photo_h+18
 bounds=[]
 for line in lines:
  box=draw.textbbox((0,0),line,font=font);tw=box[2]-box[0]
  assert tw<=cell_w-12,(line,tw)
  tx=x+(cell_w-tw)//2
  draw.text((tx,ly),line,font=font,fill=(24,32,39),stroke_width=0)
  bbox=draw.textbbox((tx,ly),line,font=font)
  assert bbox[0]>=x and bbox[2]<=x+cell_w and bbox[3]<=y+photo_h+label_h
  bounds.append(bbox);ly+=65+linegap
 after=hashlib.sha256(p.read_bytes()).hexdigest()
 assert before==after
 records.append({'source':str(p),'source_size':original.size,'source_sha256':before,'placed_size':size,'photo_box':[px,py,px+im.width,py+im.height],'labels':lines,'label_bounds':bounds,'source_unchanged':before==after,'crop':'none','photo_edit':'proportional fit only; full image retained'})
canvas.save(out,dpi=(300,300),optimize=True)
manifest={'output':str(out),'dimensions':[W,H],'layout':'2x2','label_font':'Arial Bold','label_pixels':60,'recommended_print_max_height_inches':5.5,'sources':records}
(base/'figures'/'prototype_views_provenance.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'saved':str(out),'size':canvas.size,'labels_fit':True,'all_source_hashes_unchanged':all(r['source_unchanged'] for r in records)}))
