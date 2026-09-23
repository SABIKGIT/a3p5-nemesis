from pathlib import Path
import urllib.request, urllib.parse, urllib.error
import json, datetime, time, hashlib, csv, re, html
from collections import Counter, defaultdict

ROOT=Path(__file__).resolve().parent
RAW=ROOT/'raw_crossref'; RAW.mkdir(exist_ok=True)
QUERIES=[
('Q01','mobile_robot_environment','mobile robot environmental monitoring'),
('Q02','ground_rover_air_quality','unmanned ground vehicle air quality monitoring'),
('Q03','robotic_gas_mapping','robotic gas source localization gas distribution mapping'),
('Q04','low_cost_particle_calibration','low cost particulate matter sensor calibration'),
('Q05','gas_sensor_calibration','metal oxide gas sensor environmental monitoring calibration'),
('Q06','robotic_water_quality','robotic water quality monitoring pH turbidity'),
('Q07','four_wheel_steering','four wheel independent steering mobile robot kinematics'),
('Q08','outdoor_mapping_fusion','outdoor mobile robot environmental mapping sensor fusion'),
('Q09','robotic_sampling','mobile manipulator environmental sampling inspection robot'),
('Q10','environmental_robotics_datasets','robotics environmental monitoring benchmark dataset'),
]
ROWS=500
FILTER='from-pub-date:1990-01-01,until-pub-date:2026-09-15'
HEADERS={'User-Agent':'A3P5-LiteratureMetadataCensus/1.0 (research metadata; no full text)','Accept':'application/json'}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
logs=[]
for qid,topic,query in QUERIES:
    params={'query.bibliographic':query,'rows':ROWS,'offset':0,'sort':'relevance','order':'desc','filter':FILTER}
    url='https://api.crossref.org/v1/works?'+urllib.parse.urlencode(params)
    dest=RAW/f'{qid}_{topic}.json'
    logdest=RAW/f'{qid}_{topic}.request.json'
    if dest.exists() and logdest.exists():
        entry=json.loads(logdest.read_text(encoding='utf-8')); logs.append(entry)
        print(qid,'cached',entry['returned_count'],flush=True);continue
    entry={'query_id':qid,'topic':topic,'query':query,'url':url,'params':params,'started_utc':now(),'attempts':[]}
    for attempt in range(1,5):
        started=time.monotonic()
        try:
            req=urllib.request.Request(url,headers=HEADERS)
            with urllib.request.urlopen(req,timeout=150) as resp:
                raw=resp.read(); status=resp.status; rh=dict(resp.headers.items())
            doc=json.loads(raw)
            assert doc.get('status')=='ok'
            items=doc['message']['items']
            dest.write_bytes(raw)
            entry.update({'finished_utc':now(),'http_status':status,'response_headers':rh,'returned_count':len(items),'api_total_results':doc['message']['total-results'],'sha256':hashlib.sha256(raw).hexdigest(),'byte_count':len(raw),'raw_file':str(dest.relative_to(ROOT))})
            entry['attempts'].append({'attempt':attempt,'seconds':round(time.monotonic()-started,3),'status':status})
            logdest.write_text(json.dumps(entry,indent=2),encoding='utf-8');logs.append(entry)
            print(qid,'downloaded',len(items),'bytes',len(raw),'search_total',entry['api_total_results'],flush=True)
            break
        except Exception as ex:
            entry['attempts'].append({'attempt':attempt,'error':str(ex),'seconds':round(time.monotonic()-started,3)})
            print(qid,'attempt',attempt,'error',str(ex),flush=True)
            if attempt==4:
                logdest.write_text(json.dumps(entry,indent=2),encoding='utf-8');raise
            time.sleep(min(20,attempt*4))
    time.sleep(1)
(ROOT/'query_log.json').write_text(json.dumps(logs,indent=2),encoding='utf-8')
with (ROOT/'query_log.csv').open('w',newline='',encoding='utf-8-sig') as f:
    fields=['query_id','topic','query','started_utc','finished_utc','returned_count','api_total_results','sha256','url','raw_file']
    w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(logs)
print('COMPLETE',sum(x['returned_count'] for x in logs),flush=True)
