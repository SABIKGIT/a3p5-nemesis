from pathlib import Path
import json,csv,re,html,hashlib,datetime
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parent

def clean(s):
    text=str(s)
    for _ in range(3):text=html.unescape(text)
    return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',text)).strip()
def has(p,s):return bool(re.search(p,s,re.I))
P={
'robot':r'\brobot\w*\b|\brover\b|unmanned ground|\bugv\b|mobile manipulat',
'env':r'environmental monitor|environment monitor|air quality|water quality|gas (?:sens|source|distribution|mapping)|chemical sens|pollut|particulate|olfact|odor source|odour source|methane|turbid',
'air':r'air quality|air pollut|particulate matter|\bpm\s*2[.]?5\b|plantower|pms[ -]?7003|pms[ -]?5003',
'gas':r'gas sens|metal[ -]oxide|\bmox\b|electronic nose|\be-nose\b|olfact|gas distribution|gas source|odor source|odour source',
'water':r'water quality|water monitor|water sampl|turbidity|(?:water|aquatic).{0,30}\bpH\b',
'calib':r'calibrat|cross[ -]sensitiv|sensor drift|field evaluat|laboratory evaluat|sensor evaluat|sensor performance|sensor accuracy|humidity compensat',
'sensor':r'sensor|sensing|measurement|monitoring',
'steer':r'four[ -]wheel|4[ -]?wheel|4wis|independent.{0,20}steer|all[ -]wheel steer',
'nav':r'\bslam\b|locali[sz]ation|navigation|sensor fusion|simultaneous locali|odometry|mapping|path planning',
'outdoor':r'outdoor|unmanned ground|\bugv\b|\brover\b|field robot',
'sampling':r'(?:water|soil|environmental|chemical|sample) sampl|sample collection|sampling robot|robotic sampl|environmental inspection',
'embedded':r'arduino|esp32|internet of things|\biot\b|wireless sensor network|low[ -]cost',
'review':r'\breview\b|\bsurvey\b|state[ -]of[ -]the[ -]art|critical analysis',
'dataset':r'\bdataset\b|\bdata set\b|\bbenchmark\w*\b|\bdata repository\b',
}
TOPICS=['robotic_environmental_monitoring','gas_olfaction_mapping','particulate_air_quality','gas_sensor_calibration','water_quality_monitoring','four_wheel_steering','outdoor_navigation_fusion','robotic_sampling','embedded_environmental_sensing']

def classify(title,abstract):
    combo=title+' '+abstract
    b={k:has(p,combo) for k,p in P.items()}
    t={k:has(p,title) for k,p in P.items()}
    tags=[]
    if b['robot'] and b['env']:tags.append(TOPICS[0])
    if b['gas'] and (b['robot'] or has(r'gas distribution|gas source|odor source|odour source',combo)):tags.append(TOPICS[1])
    if b['air'] and b['sensor']:tags.append(TOPICS[2])
    if b['gas'] and b['calib'] and b['sensor']:tags.append(TOPICS[3])
    if b['water'] and (b['sensor'] or b['robot']):tags.append(TOPICS[4])
    if b['steer'] and (b['robot'] or has(r'steer|kinematic',combo)):tags.append(TOPICS[5])
    if b['robot'] and b['nav'] and b['outdoor']:tags.append(TOPICS[6])
    if b['robot'] and b['sampling']:tags.append(TOPICS[7])
    if b['embedded'] and b['env'] and b['sensor']:tags.append(TOPICS[8])
    # Compact deterministic heuristic; points measure metadata match, not study quality.
    score=sum((3 if t[k] else 1) for k in P if b[k] and k not in ['review','dataset'])
    score+=min(len(tags),3)*2
    score+=2*int(t['robot'] and t['env'])+2*int(t['calib'] and (t['air'] or t['gas']))
    score+=2*int(t['robot'] and (t['steer'] or t['sampling']))
    title_noise=has(r'\bsurgical\b|\bsurgery\b|\bmicrorobot\w*\b|\bnanorobot\w*\b|\bchemotherapy\b|\bretract\w*\b|^correction|^erratum|^corrigendum|^front matter|^back matter|^copyright|^dedication|^contents|^index$|^acknowledg|^nomenclature|^preface|^list of (?:figures|tables)',title)
    candidate=bool(tags) and score>=10 and not title_noise
    primary=next((x for x in [TOPICS[1],TOPICS[5],TOPICS[7],TOPICS[4],TOPICS[2],TOPICS[3],TOPICS[6],TOPICS[0],TOPICS[8]] if x in tags),'other')
    return {'topics':tags,'primary_topic':primary,'relevance_score':score,'is_review_title':t['review'],'is_dataset_title':t['dataset'],'has_abstract':bool(abstract),'screening_decision':'metadata_candidate' if candidate else 'not_prioritized_by_metadata_rule','screening_reason':';'.join(tags) if candidate else ('out_of_scope_or_notice_or_administrative_title' if title_noise else 'no_qualifying_topic_conjunction_or_score_below_10'),'matched_title_categories':[k for k,v in t.items() if v]}

def yr(x):
    for key in ['published','published-print','published-online','issued']:
        try:return x[key]['date-parts'][0][0]
        except (KeyError,IndexError,TypeError):pass
    return None

def authors(x):
    return '; '.join(' '.join(filter(None,[a.get('given'),a.get('family')])) or a.get('name','') for a in x.get('author',[]))

records={};occurrences=[];raw_count=0;verified_files=[]
for lp in sorted((ROOT/'raw_crossref').glob('Q*.request.json')):
    log=json.loads(lp.read_text(encoding='utf-8'));qid=log['query_id']
    p=ROOT/log['raw_file'];raw=p.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==log['sha256'],str(p)
    doc=json.loads(raw);verified_files.append(str(p.relative_to(ROOT)))
    for rank,x in enumerate(doc['message']['items'],1):
        raw_count+=1;doi=x.get('DOI','').lower().strip();title=clean(' '.join(x.get('title',[])));abstract=clean(x.get('abstract',''))
        key=doi or 'title:'+re.sub(r'\W+','',title.lower())+':'+str(yr(x))
        provenance={'query_id':qid,'query_rank':rank,'api_score':x.get('score'),'raw_file':str(p.relative_to(ROOT)),'raw_item_index':rank-1}
        occurrences.append({'record_key':key,**provenance})
        if key in records:
            records[key]['provenance'].append(provenance)
            if not records[key]['abstract'] and abstract:records[key]['abstract']=abstract
            continue
        records[key]={'record_key':key,'doi':doi,'doi_url':'https://doi.org/'+doi if doi else x.get('URL',''),'title':title,'authors':authors(x),'year':yr(x),'venue':clean(' '.join(x.get('container-title',[]))),'publisher':x.get('publisher',''),'type':x.get('type',''),'abstract':abstract,'crossref_cited_by':x.get('is-referenced-by-count',0),'volume':x.get('volume',''),'issue':x.get('issue',''),'pages':x.get('page',''),'article_number':x.get('article-number',''),'provenance':[provenance]}
assert len(verified_files)==10, 'Wait until all ten query responses are available'
allrec=list(records.values())
for r in allrec:
    r.update(classify(r['title'],r['abstract']))
    if r['type'] in ['peer-review','component','journal','book-series','report-series','journal-issue']:
        r['screening_decision']='not_prioritized_by_metadata_rule'
        r['screening_reason']='administrative_or_peer_review_record_type'

def title_key(r):return re.sub(r'\W+','',r['title'].lower())
title_groups=defaultdict(list)
for r in allrec:title_groups[title_key(r)].append(r['doi'])
for r in allrec:r['exact_normalized_title_doi_count']=len(title_groups[title_key(r)])
# Citation count breaks otherwise equal matches; it is not an evidence-quality assessment.
ranker=lambda r:(-r['relevance_score'],-int(r['is_review_title']),-int(r['is_dataset_title']),-r['crossref_cited_by'],-(r['year'] or 0),r['doi'],r['title'])
allrec.sort(key=ranker);candidates=[r for r in allrec if r['screening_decision']=='metadata_candidate']
selected={};selected_titles=set()
# Ensure methodological support categories are represented; suppress exact title duplicates.
for topic in TOPICS:
    topic_added=0
    for r in [r for r in candidates if r['primary_topic']==topic]:
        if title_key(r) in selected_titles:continue
        selected[r['record_key']]=r;selected_titles.add(title_key(r));topic_added+=1
        if topic_added>=12:break
for r in candidates:
    if len(selected)>=150:break
    if title_key(r) in selected_titles:continue
    selected[r['record_key']]=r;selected_titles.add(title_key(r))
shortlist=sorted(selected.values(),key=ranker)
for rank,r in enumerate(shortlist,1):r['shortlist_rank']=rank;r['selection_status']='heuristic_shortlist_requires_full_text_assessment'

FIELDS=['shortlist_rank','doi','doi_url','title','authors','year','venue','type','publisher','volume','issue','pages','article_number','crossref_cited_by','relevance_score','primary_topic','topics','is_review_title','is_dataset_title','has_abstract','screening_decision','screening_reason','matched_title_categories','exact_normalized_title_doi_count','provenance','abstract']
def writecsv(name,rows,fields=FIELDS):
    with (ROOT/name).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
        for r in rows:w.writerow({k:json.dumps(r[k],ensure_ascii=False) if isinstance(r.get(k),(dict,list)) else r.get(k,'') for k in fields})
for name,rows in [('bibliography_all',allrec),('metadata_candidates',candidates),('shortlist',shortlist)]:
    (ROOT/f'{name}.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8');writecsv(f'{name}.csv',rows)
writecsv('record_provenance.csv',occurrences,['record_key','query_id','query_rank','api_score','raw_file','raw_item_index'])
summary={'retrieval_method':'Crossref public REST API, relevance-ranked top 500 per each of ten bibliographic queries','date_filter':'1990-01-01 through 2026-09-15 inclusive','query_count':len(verified_files),'raw_record_occurrences':raw_count,'unique_records_after_doi_deduplication':len(allrec),'duplicate_occurrences_removed':raw_count-len(allrec),'records_without_doi':sum(not r['doi'] for r in allrec),'records_with_abstract':sum(r['has_abstract'] for r in allrec),'records_without_abstract':sum(not r['has_abstract'] for r in allrec),'metadata_candidates':len(candidates),'not_prioritized':len(allrec)-len(candidates),'heuristic_shortlist':len(shortlist),'shortlist_with_abstract':sum(r['has_abstract'] for r in shortlist),'verified_sha256_raw_files':len(verified_files),'screened_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'full_texts_reviewed_in_census':0,'review_type':'reproducible exploratory metadata census; not a systematic review or PRISMA study selection','scoring_version':'1.2, fully specified in screen_metadata.py','candidate_peer_review_reports':sum(r['type']=='peer-review' for r in candidates),'shortlist_exact_normalized_title_duplicates':len(shortlist)-len({title_key(r) for r in shortlist})}
(ROOT/'census_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
for group,rows in [('all_unique',allrec),('metadata_candidates',candidates),('shortlist',shortlist)]:
    cnt=Counter(r['year'] for r in rows)
    writecsv(f'year_counts_{group}.csv',[{'year':y,'count':n,'cohort':group} for y,n in sorted(cnt.items(),key=lambda x:x[0] or 0)],['year','count','cohort'])
    cnt=Counter(r['primary_topic'] for r in rows)
    writecsv(f'topic_counts_{group}.csv',[{'topic':t,'count':cnt[t],'cohort':group} for t in TOPICS+['other']],['topic','count','cohort'])
    cnt=Counter((r['year'],r['primary_topic']) for r in rows)
    writecsv(f'year_topic_counts_{group}.csv',[{'year':y,'topic':t,'count':n,'cohort':group} for (y,t),n in sorted(cnt.items(),key=lambda x:(x[0][0] or 0,x[0][1]))],['year','topic','count','cohort'])
writecsv('exact_title_duplicates.csv',[{'normalized_title':k,'doi_count':len(v),'dois':v} for k,v in title_groups.items() if len(v)>1],['normalized_title','doi_count','dois'])
print(json.dumps(summary,indent=2))
print('\nTOP SHORTLIST RECORDS')
for r in shortlist[:25]:print(r['relevance_score'],r['year'],r['doi'],r['title'])


