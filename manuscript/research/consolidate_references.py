from pathlib import Path
import json,re,csv,hashlib,datetime,urllib.request,urllib.parse,time,html,unicodedata
R=Path(__file__).resolve().parent
CACHE=R/'verified_reference_metadata';CACHE.mkdir(exist_ok=True)
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def clean(x):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',str(x)))).strip()
def doi(x):return str(x or '').lower().strip().removeprefix('https://doi.org/').removeprefix('doi:')
def yearof(m):
 for f in ['published','published-print','published-online','issued']:
  try:return m[f]['date-parts'][0][0]
  except:pass
 return None
sources=[]
for fn in ['mobility_sources.json','sensing_sources.json']:
 for x in load(R/fn)['sources']:sources.append((fn,x))
for x in load(R/'context_sources.json'):sources.append(('context_sources.json',x))
sources.append(('template_metadata.xml',{'id':'T01','title':'An Adaptive Suspension System for Planetary Rovers','authors':['G. Reina','M. Foglia'],'year':2010,'venue':'IFAC Proceedings Volumes','doi':'10.3182/20100906-3-IT-2019.00036','url':'https://www.sciencedirect.com/science/article/pii/S147466701635056X','source_type':'research article','read_depth':'Saved Elsevier API core metadata; publisher abstract and author institutional bibliography checked.','supports':'Variable wheel-camber suspension proposed for conventional rocker-type planetary rover suspensions.','caution':'Nemesis does not incorporate or validate the paper’s variable-camber linkage.'}))
for x in load(R/'additional_reference_sources.json'):sources.append(('additional_reference_sources.json',x))
for x in load(R/'sensing_sources_supplement.json'):sources.append(('sensing_sources_supplement.json',x))
sources.append(('liosam_source.json',load(R/'liosam_source.json')))
for origin,x in sources:
 if x['id']=='M03':
  x['audit_correction']='The original audit paired a 2021 arXiv title with a different journal title. The journal DOI/title/abstract were independently verified; no equivalence to arXiv:2105.06501 is asserted.'
  x['title']='A general update rule for Lyapunov-based adaptive control of mobile robots with wheel slip'
  x['url']='https://doi.org/10.1002/acs.3747'
  x['read_depth']='Publisher-deposited journal abstract and Crossref metadata independently read; earlier preprint association corrected.'
  x['supports']='Family of Lyapunov-based adaptive kinematic controllers for a differential-drive robot with longitudinal/lateral slip; assessed with numerical simulations.'
  x['caution']='Differential-drive model and numerical evaluation are not evidence of Nemesis slip compensation; preprint/journal equivalence is unverified.'
merged={}
for origin,x in sources:
 k=doi(x.get('doi')) or x.get('url') or x.get('source_url')
 assert k,(origin,x)
 if k not in merged:merged[k]={'source_ids':[],'source_audits':[],'source_files':[],'doi':doi(x.get('doi')),'title':x['title'],'authors':x.get('authors',[]),'year':x.get('year'),'venue':x.get('venue') or x.get('journal',''),'url':x.get('url') or x.get('source_url'),'source_type':x.get('source_type') or x.get('type') or ('official institutional page' if x['id'] in ['M15','M16'] else 'research article')}
 r=merged[k];r['source_ids'].append(x['id']);r['source_files'].append(origin);r['source_audits'].append({'source_id':x['id'],'audit_correction':x.get('audit_correction'),'read_depth':x.get('read_depth') or x.get('read_scope'),'supports':x.get('supports') or x.get('claim_supported') or x.get('use'),'limitations':x.get('caution') or x.get('limitations') or x.get('limit')})
 if not r['authors'] and x.get('authors'):r['authors']=x['authors']
# Reuse raw census records before issuing new public requests.
rawindex={}
for p in (R/'raw_crossref').glob('Q*.json'):
 if p.name.endswith('.request.json'):continue
 for x in load(p)['message']['items']:rawindex.setdefault(doi(x.get('DOI')),(x,str(p.relative_to(R))))
request_log=load(R/'reference_metadata_request_log.json') if (R/'reference_metadata_request_log.json').exists() else []
for i,r in enumerate(merged.values(),1):
 d=r['doi'];m=None;provider=None;origin=None
 if d and d in rawindex:m,origin=rawindex[d];provider='Crossref archived census'
 elif d:
  datacite=d.startswith('10.24432/')
  provider='DataCite' if datacite else 'Crossref'
  url=('https://api.datacite.org/dois/' if datacite else 'https://api.crossref.org/v1/works/')+urllib.parse.quote(d,safe='')
  p=CACHE/(hashlib.sha256(d.encode()).hexdigest()[:16]+'.json')
  if p.exists():raw=p.read_bytes();origin=str(p.relative_to(R))
  else:
   start=datetime.datetime.now(datetime.timezone.utc).isoformat()
   for attempt in range(3):
    try:
     req=urllib.request.Request(url,headers={'User-Agent':'Nemesis-reference-audit/1.0','Accept':'application/json'})
     with urllib.request.urlopen(req,timeout=60) as response:raw=response.read();status=response.status
     p.write_bytes(raw);origin=str(p.relative_to(R))
     request_log.append({'doi':d,'url':url,'started_utc':start,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':status,'raw_file':origin,'sha256':hashlib.sha256(raw).hexdigest()});break
    except Exception as e:
     if attempt==2:request_log.append({'doi':d,'url':url,'error':str(e)});raw=None
     else:time.sleep(3*(attempt+1))
   time.sleep(1.1)
  if raw:
   doc=json.loads(raw)
   if datacite:
    a=doc['data']['attributes'];m={'DOI':a['doi'],'title':[z['title'] for z in a['titles']],'author':[{'given':z.get('givenName'),'family':z.get('familyName'),'name':z.get('name')} for z in a['creators']],'published':{'date-parts':[[a['publicationYear']]]},'container-title':['UCI Machine Learning Repository'],'publisher':a.get('publisher',''),'type':'dataset','URL':a.get('url')}
   else:m=doc['message']
 if m:
  assert doi(m.get('DOI'))==d,(d,m.get('DOI'))
  r['metadata_title']=clean(' '.join(m.get('title',[])))
  r['metadata_year']=yearof(m)
  r['journal']=clean(' '.join(m.get('container-title',[])))
  r['authors_structured']=m.get('author',[])
  metadata_authors=[' '.join(filter(None,[a.get('given'),a.get('family')])) or a.get('name','') for a in m.get('author',[])]
  if metadata_authors:r['authors']=metadata_authors
  if not r['year']:r['year']=r['metadata_year']
  if not r['venue']:r['venue']=clean(' '.join(m.get('container-title',[])))
  for f,source in [('volume','volume'),('issue','issue'),('pages','page'),('article_number','article-number'),('publisher','publisher')]:r[f]=m.get(source)
  t1=set(re.findall(r'[a-z0-9]+',r['title'].lower()));t2=set(re.findall(r'[a-z0-9]+',r['metadata_title'].lower()))
  r['title_token_overlap']=round(len(t1&t2)/max(1,min(len(t1),len(t2))),3)
  r['metadata_verification']={'status':'DOI resolved and title compared','provider':provider,'raw_file':origin,'title_matches_at_least_0_7':r['title_token_overlap']>=.7}
  r['metadata_discrepancies']=[]
  if r['metadata_year'] is not None and r['metadata_year']!=r['year']:r['metadata_discrepancies'].append(f"Source audit citation year {r['year']} retained; deposited publication year {r['metadata_year']}.")
 else:r['metadata_verification']={'status':'Primary-source audit; no DOI supplied' if not d else 'Primary-source audit; API lookup unavailable','provider':None}
 print(i,len(merged),r['source_ids'],r['metadata_verification']['status'],flush=True)
 # Persist a checkpoint so the provenance survives an interruption.
 (R/'reference_metadata_request_log.json').write_text(json.dumps(request_log,indent=2),encoding='utf-8')
# Correct publisher metadata name-part parsing using the authors' linked preprint.
for r in merged.values():
 if r['doi']=='10.1109/tro.2021.3075644':
  r['deposited_authors_structured']=r.get('authors_structured',[])
  r['authors_structured']=[{'given':'Carlos','family':'Campos'},{'given':'Richard','family':'Elvira'},{'given':'Juan J.','family':'Gómez Rodríguez'},{'given':'José M. M.','family':'Montiel'},{'given':'Juan D.','family':'Tardós'}]
  r['authors']=[' '.join([a['given'],a['family']]) for a in r['authors_structured']]
  r['metadata_discrepancies'].append('Author name parts corrected against the authors’ arXiv record, which explicitly links this journal DOI: https://arxiv.org/abs/2007.11898. Original deposited name parts are preserved.')

# Stable keys use author/year plus identifier hash; aliases retain original audit IDs.
def surname(r):
 if r.get('authors_structured'):
  a=r['authors_structured'][0]
  if a.get('family'):return a['family']
 a=r['authors'][0] if r['authors'] else 'Unknown'
 if 'Winsen' in a:return 'Winsen'
 if a in ['DFRobot','Bosch Sensortec','Analog Devices']:return a
 if 'Joint Committee for Guides in Metrology' in a:return 'JCGM'
 if 'Geological Survey' in a:return 'USGS'
 if 'National Institute' in a:return 'NIST'
 return a.split()[-1]
def authorlabel(r):
 names=r.get('authors_structured')
 if names:
  fam=[x.get('family') or x.get('name') or '' for x in names]
 else:
  fam=[surname(r)] if len(r['authors'])==1 else [x.split()[-1] for x in r['authors']]
 if len(fam)==1:return fam[0]
 if len(fam)==2:return fam[0]+' and '+fam[1]
 return fam[0]+' et al.'
groups={}
for r in merged.values():
 r['author_label']=authorlabel(r);r['citation_year']=str(r['year']) if r['year'] else 'n.d.'
 groups.setdefault((r['author_label'],r['citation_year']),[]).append(r)
for group in groups.values():
 if len(group)>1:
  for i,r in enumerate(sorted(group,key=lambda x:x['title'])):r['citation_year']+=('-' if r['citation_year']=='n.d.' else '')+chr(97+i)
refs=[]
for r in merged.values():
 ident=r['doi'] or r['url'];stem=re.sub('[^a-z0-9]','',surname(r).lower())
 r['key']=stem+str(r['year'] or 'nd')+'_'+hashlib.sha256(ident.encode()).hexdigest()[:6]
 r['citation_label']=r['author_label']+', '+r['citation_year'];r['narrative_citation']=r['author_label']+' ('+r['citation_year']+')'
 if r.get('metadata_title') and r.get('title_token_overlap',0)>=.7:
  r['audited_title']=r['title'];r['title']=r['metadata_title']
 structured=r.get('authors_structured',[])
 formatted=[]
 if structured:
  for au in structured:
   if au.get('family'):
    initials=' '.join(t[0].upper()+'.' for t in re.findall(r'[^\W\d_]+',au.get('given') or '',flags=re.UNICODE))
    formatted.append(au['family']+(', '+initials if initials else ''))
   else:formatted.append(au.get('name') or '')
 else:formatted=r['authors']
 author_text=formatted[0] if len(formatted)==1 else ', '.join(formatted[:-1])+', & '+formatted[-1]
 location=r.get('journal') or r['venue'] or r.get('publisher') or r['source_type']
 if r.get('journal') and r.get('volume'):
  location+=', '+str(r['volume'])+('('+str(r['issue'])+')' if r.get('issue') else '')
  if r.get('pages') or r.get('article_number'):location+=', '+str(r.get('pages') or r['article_number']).replace('-',chr(8211))
 r['citation_text']=author_text+' ('+r['citation_year']+'). '+r['title'].rstrip('.')+'. '+location.rstrip('.')+'. '+('https://doi.org/'+r['doi'] if r['doi'] else r['url'])
 r['checked_date']='2026-09-15';refs.append(r)
refs.sort(key=lambda r:(''.join(c for c in unicodedata.normalize('NFKD',r['author_label'].casefold()) if not unicodedata.combining(c)),r['citation_year'],r['title']))
result={'schema_version':'1.0','scope':'Source-checked references with independent DOI metadata confirmation when available; read-depth is source-specific, not blanket full-text verification.','count':len(refs),'sources':refs,'aliases':{sid:r['key'] for r in refs for sid in r['source_ids']}}
(R/'references_verified.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
with (R/'references_verified.csv').open('w',encoding='utf-8-sig',newline='') as f:
 fields=['key','citation_label','title','authors','year','venue','doi','url','source_type','source_ids','metadata_verification','source_audits','citation_text'];w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
 for r in refs:w.writerow({k:json.dumps(r[k],ensure_ascii=False) if isinstance(r.get(k),(list,dict)) else r.get(k,'') for k in fields})
(R/'references_author_date.md').write_text('# Consolidated source-checked references\n\n'+'\n\n'.join(r['citation_text'] for r in refs),encoding='utf-8')
print('DONE',len(refs),'unique references;',sum(bool(r['doi']) for r in refs),'DOIs;',sum(r['metadata_verification'].get('title_matches_at_least_0_7',False) for r in refs),'DOI/title matches',flush=True)
