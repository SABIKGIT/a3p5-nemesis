from pathlib import Path
import json, html, math
from PIL import ImageFont
from matplotlib.font_manager import FontProperties, findfont
R=Path(__file__).resolve().parent
D=[]
for f in ['canva_revision_spec_01_07.json','canva_revision_spec_08_14.json']:
 D.extend(json.loads((R/f).read_text(encoding='utf-8'))['diagrams'])
D.sort(key=lambda d:int(d['diagram_id']))
COLORS={'data':'#155C92','control':'#A95700','feedback':'#704CA0','power':'#B43131','physical':'#535E65'}
X=[55,670,1285]; W=520
font=ImageFont.truetype(findfont(FontProperties(family='DejaVu Sans')),40)
bold=ImageFont.truetype(findfont(FontProperties(family='DejaVu Sans',weight='bold')),42)
parts=[]; audit=[]
def esc(s):return html.escape(str(s))
def div(cls,x,y,w,h,extra='',content=''):
 return f'<div class="{cls}" style="left:{x:.1f}px;top:{y:.1f}px;width:{w:.1f}px;height:{h:.1f}px;{extra}">{content}</div>'
def rect(x,y,w,h,color,rounding=0):
 return div('shape',x,y,max(.1,w),max(.1,h),f'background:{color};border-radius:{rounding}px;')
def line_segment(a,b,kind,under=False):
 x1,y1=a;x2,y2=b
 if abs(x1-x2)<.1 and abs(y1-y2)<.1:return ''
 if abs(x1-x2)>.1 and abs(y1-y2)>.1:raise ValueError('Non-orthogonal line')
 color='#ffffff' if under else COLORS[kind]
 thick=14 if under else (8 if kind=='power' else 5)
 horizontal=abs(y1-y2)<.1
 lo=min(x1,x2) if horizontal else min(y1,y2);length=abs(x2-x1) if horizontal else abs(y2-y1)
 def segment(pos,ln,offset=0,sz=thick):
  return rect(pos,y1-sz/2+offset,ln,sz,color) if horizontal else rect(x1-sz/2+offset,pos,sz,ln,color)
 if under:return segment(lo,length)
 if kind=='physical':return segment(lo,length,-4,3)+segment(lo,length,4,3)
 if kind in ['control','feedback']:
  dash,gap=(15,9) if kind=='control' else (5,8)
  return ''.join(segment(lo+t,min(dash,length-t)) for t in range(0,math.ceil(length),dash+gap))
 return segment(lo,length)
def arrowhead(point,prev,kind):
 x,y=point;px,py=prev;c=COLORS[kind]
 if x>px:glyph='▶';xx=x-25;yy=y-16
 elif x<px:glyph='◀';xx=x;yy=y-16
 elif y>py:glyph='▼';xx=x-15;yy=y-25
 else:glyph='▲';xx=x-15;yy=y-6
 return div('arrowhead',xx,yy,30,32,f'color:{c};font-family:Arial;font-size:29px;line-height:32px;text-align:center;',glyph)
def arrow(points,kind,tag=None,tag_position=None,head=True):
 out=''.join(line_segment(a,b,kind,True) for a,b in zip(points,points[1:]))
 out+=''.join(line_segment(a,b,kind) for a,b in zip(points,points[1:]))
 if head:out+=arrowhead(points[-1],points[-2],kind)
 if tag:
  seg=max(zip(points,points[1:]),key=lambda ab:abs(ab[0][0]-ab[1][0])+abs(ab[0][1]-ab[1][1]))
  a,b=seg;tx,ty=tag_position or ((a[0]+b[0])/2,(a[1]+b[1])/2)
  out+=div('edge-tag',tx-19,ty-19,38,38,f'border:2px solid {COLORS[kind]};color:{COLORS[kind]};',esc(tag))
 return out
def wrap_title(t):
 words=t.split();lines=[];line=''
 for w in words:
  trial=(line+' '+w).strip()
  if bold.getlength(trial)>470 and line:lines.append(line);line=w
  else:line=trial
 if line:lines.append(line)
 return lines
for d in D:
 did=d['diagram_id'];special=did=='12'; ys=[180,590] if special else [185,620];H=300 if special else 340
 nodes={n['id']:{**n,'x':X[n['column']-1],'y':ys[n['row']-1]} for n in d['nodes']}
 content=div('page-title',55,28,1750,63,'',esc(d['page_header']))
 subtitle=d.get('subtitle','Proposed functional architecture')
 if did=='14':subtitle='External fixed-station benchmark and future rover validation'
 content+=div('subtitle',55,103,1750,45,'',esc('A3P5 NEMESIS  |  '+subtitle))
 paths=[]; reverse_pairs={(e['from'],e['to']) for e in d['edges']}
 cross=0;far=0
 port_counts={1:0,2:0,3:0}
 def port(col):
  offsets=[0,-65,65,-130,130,-195,195]
  k=port_counts[col];port_counts[col]+=1
  assert k<len(offsets),(did,col,'ports exhausted')
  return X[col-1]+W/2+offsets[k]
 diagonal_count=sum(a['row']!=b['row'] and a['column']!=b['column'] for e in d['edges'] for a,b in [(nodes[e['from']],nodes[e['to']])])
 guards={'Healthy and enabled':('A','Health + enable'),'Mission and pose valid':('B','Mission + pose valid'),'Fault or timeout':('C','Fault / timeout'),'Recoverable fault':('D','Recoverable fault'),'Critical fault or takeover':('E','Fault / takeover'),'Limits unmet':('F','Limits unmet'),'Clear fault and reset':('G','Clear fault + reset'),'Emergency input':('H','Emergency input'),'Physical release and reset':('I','Release + reset')}
 if did=='02':
  cy=ys[0]+H/2;bottom=ys[0]+H;top2=ys[1];mid=(bottom+top2)/2
  paths=[([(X[0]+W,cy),(X[1],cy)],'power',None), ([(X[1]+W,cy),(X[2],cy)],'power',None), ([(X[1]+W/2,bottom),(X[1]+W/2,mid),(X[0]+W/2,mid),(X[0]+W/2,top2)],'power',None), ([(X[1]+W/2,bottom),(X[1]+W/2,top2)],'power',None), ([(X[1]+W/2,bottom),(X[1]+W/2,mid),(X[2]+W/2,mid),(X[2]+W/2,top2)],'power',None)]
 else:
  for k,e in enumerate(d['edges']):
   a=nodes[e['from']];b=nodes[e['to']];ar,br=a['row'],b['row'];ac,bc=a['column'],b['column']
   opp=(e['to'],e['from']) in reverse_pairs; off=(22 if ac<bc or (ac==bc and ar<br) else -22) if opp else 0
   kind=e['type'];tag=guards[e['label']][0] if special else None
   if ar==br and abs(ac-bc)==1:
    y=a['y']+H/2+off
    pts=[(a['x']+W if ac<bc else a['x'],y),(b['x'] if ac<bc else b['x']+W,y)]
   elif ac==bc and ar!=br:
    x=port(ac)
    pts=[(x,a['y']+H if ar<br else a['y']),(x,b['y'] if ar<br else b['y']+H)]
   elif ar==br:
    far+=1; up=ar==1;lane=154 if up else (ys[1]+H+18)
    pya=a['y'] if up else a['y']+H;pyb=b['y'] if up else b['y']+H
    xa=port(ac);xb=port(bc)
    pts=[(xa,pya),(xa,lane),(xb,lane),(xb,pyb)]
   else:
    cross+=1;lane=ys[0]+H+(ys[1]-ys[0]-H)*cross/(diagonal_count+1)
    xa=port(ac);xb=port(bc)
    pts=[(xa,a['y']+H if ar<br else a['y']),(xa,lane),(xb,lane),(xb,b['y'] if ar<br else b['y']+H)]
   paths.append((pts,kind,tag))
 # Custom routing separates guarded state and data partition paths.
 custom={}
 special_file=R/'canva_special_routes.json'
 if special_file.exists():
  records=json.loads(special_file.read_text(encoding='utf8'))
  custom=records.get(did,{})
 if custom:
  for route in custom['routes']:content+=arrow(route['points'],route['type'],route.get('tag'),route.get('tag_position'),route.get('head',True))
  for dot in custom.get('dots',[]):
   xx,yy=dot['point'];rr=dot.get('radius',7)
   content+=rect(xx-rr,yy-rr,rr*2,rr*2,COLORS[dot.get('type','control')],rr)
 else:
  for points,kind,tag in paths:content+=arrow(points,kind,tag)
 if did=='02':
  for xx in [X[1]+W/2]:content+=rect(xx-7,mid-7,14,14,COLORS['power'],7)
 for n in nodes.values():
  lines=n['body'].splitlines();tl=wrap_title(n['title'])
  assert len(lines)<=4 and len(tl)<=2,(did,n)
  assert max(font.getlength(t) for t in lines)<=470,(did,n['id'],'body overflow')
  titleh=len(tl)*47
  needed=24+titleh+13+len(lines)*45.2+22
  assert needed<=H,(did,n['id'],'height overflow',needed,H)
  boxcontent=f'<h2>{"<br>".join(esc(t) for t in tl)}</h2><p>{"<br>".join(esc(t) for t in lines)}</p>'
  content+=div('node',n['x'],n['y'],W,H,'',boxcontent)
  audit.append({'diagram':did,'node':n['id'],'body_lines':len(lines),'body_max_px':round(max(font.getlength(t) for t in lines),1),'used_height_px':round(needed,1),'available_height_px':H})
 if special:
  content+=div('legend-heading',55,924,1750,44,'','LEGEND  ·  Dashed arrows show guarded state transitions')
  short=[guards[k] for k in guards]
  for i,(key,label) in enumerate(short):
   xx=55+(i%3)*595;yy=978+(i//3)*51
   content+=div('guard-key',xx,yy,540,45,'',f'<b>{key}</b>  {esc(label)}')
  foot='Dots join H emergency-input branches. Proposed transitions; emergency interruption is independent of software.'
  content+=div('footnote',55,1141,1750,46,'',esc(foot))
 else:
  content+=div('legend-heading',55,987,1750,43,'','LEGEND  ·  Arrow direction indicates the direction of the link')
  for i,leg in enumerate(d['legend']):
   xx=55+(i%2)*905;yy=1044+(i//2)*57
   content+=arrow([(xx,yy+19),(xx+78,yy+19)],leg['type'])
   content+=div('legend-text',xx+103,yy-4,750,48,'',esc(leg['meaning']))
  foot='Functional links require verification. Crossings without a junction dot are not connected.'
  if did=='02':foot='Parallel load branches; dots mark common supply junctions. Returns and pinouts are omitted.'
  if did=='14':foot='External benchmark results do not calibrate the rover. No test-to-training feedback is permitted.'
  content+=div('footnote',55,1162,1750,35,'',esc(foot))
 notes={'diagram_id':did,'figure_number':d['manuscript_figure_number'],'edge_definitions':d['edges'],'legend':d['legend'],'limitations':d['limitations']}
 parts.append(f'<section class="page" data-document-role="page" data-label="{esc(d["page_header"])}" data-speaker-notes="{esc(json.dumps(notes,ensure_ascii=False))}">{content}</section>')
css='''*{box-sizing:border-box}html,body{margin:0;padding:0;background:#d9e0e6;font-family:Arial,sans-serif;color:#132b3d}.page{position:relative;width:1860px;height:1200px;overflow:hidden;background:#fff;margin:0 0 40px}.shape,.arrowhead,.node,.page-title,.subtitle,.legend-heading,.legend-text,.footnote,.guard-key,.edge-tag{position:absolute}.page-title{font-size:48px;line-height:1.12;font-weight:700;white-space:nowrap}.subtitle{font-size:32px;color:#51606a;line-height:1.2}.node{border:2px solid #7c94a4;border-radius:7px;background:#f4f8fb;padding:23px 24px;box-shadow:none}.node h2{font-size:42px;line-height:47px;font-weight:700;margin:0 0 13px;color:#163c54}.node p{font-size:40px;line-height:45.2px;margin:0;color:#172b39}.legend-heading{font-size:34px;line-height:1.2;font-weight:700;color:#304b5a}.legend-text{font-size:40px;line-height:1.1;white-space:nowrap;color:#243b49}.footnote{font-size:29px;line-height:1.15;color:#4e5d66}.guard-key{font-size:40px;line-height:1.05;white-space:nowrap}.guard-key b{color:#a95700}.edge-tag{font-size:27px;line-height:34px;text-align:center;font-weight:bold;background:white;border-radius:50%;z-index:2}.node{z-index:3}'''
output=R/'A3P5_Canva_Figures_With_Legends.html'
output.write_text('<!doctype html><html><head><meta charset="utf-8"><title>A3P5 NEMESIS Figures and Legends</title><style>'+css+'</style></head><body>'+''.join(parts)+'</body></html>',encoding='utf-8')
(R/'canva_legend_layout_audit.json').write_text(json.dumps({'pages':14,'canvas':[1860,1200],'nodes':audit,'status':'Local source preflight; Canva import and native export verification pending'},indent=2),encoding='utf-8')
print(output)
print('Pages',len(parts),'nodes',len(audit),'bytes',output.stat().st_size)
