from pathlib import Path
import json, re, hashlib
from datetime import datetime, timezone

P=Path(__file__).resolve().parents[1]
# Retained author-year source supplies aliases; the active manuscript is text/manuscript_ieee.md.
SOURCE=P/'text/manuscript_revision_pre_citations.md'
REGISTRY=P/'research/references_verified.json'
KEYMAP=P/'latex/reference_key_map.json'
reg=json.loads(REGISTRY.read_text(encoding='utf-8'))
by={s['key']:s for s in reg['sources']}
old=json.loads(KEYMAP.read_text(encoding='utf-8'))['records']
md=SOURCE.read_text(encoding='utf-8')
body=md.split('## References\n',1)[0]
assert len(old)==45

ABBR={
 'The International Journal of Robotics Research':'Int. J. Robot. Res.',
 'Journal of Field Robotics':'J. Field Robot.',
 'ACM Transactions on Sensor Networks':'ACM Trans. Sensor Netw.',
 'The Journal of Engineering':'J. Eng.',
 'ROBOMECH Journal':'ROBOMECH J.',
 'Applied Sciences':'Appl. Sci.',
 'Atmospheric Measurement Techniques':'Atmos. Meas. Tech.',
 'Journal of Environmental Management':'J. Environ. Manage.',
 'Journal of Intelligent & Robotic Systems':'J. Intell. Robot. Syst.',
 'IEEE Transactions on Robotics':'IEEE Trans. Robot.',
 'Sensors and Actuators B: Chemical':'Sens. Actuators B, Chem.',
 'Machine Learning':'Mach. Learn.',
 'ACM Transactions on Knowledge Discovery from Data':'ACM Trans. Knowl. Discov. Data',
 'International Journal of Adaptive Control and Signal Processing':'Int. J. Adapt. Control Signal Process.',
 'Environmental Science: Atmospheres':'Environ. Sci.: Atmos.',
 'IEEE Robotics & Automation Magazine':'IEEE Robot. Autom. Mag.',
 'IFAC Proceedings Volumes':'IFAC Proc. Volumes',
}
TITLES={
 'alexander1989_c3c6fd':'On the kinematics of wheeled mobile robots',
 'analogdevices2013_f3acfa':'CN0326: Isolated low power pH monitor with temperature compensation',
 'barkjohn2021_7ba5aa':'Development and application of a United States-wide correction for PM2.5 data collected with the PurpleAir sensor',
 'boschsensortec2013_0d84c1':'BMP180 digital pressure sensor data sheet, revision 2.5, BST-BMP180-DS000-09',
 'breiman2001_75dc04':'Random forests',
 'campos2021_973bd6':'ORB-SLAM3: An accurate open-source library for visual, visual–inertial, and multimap SLAM',
 'concas2021_57ba0a':'Low-cost outdoor air quality monitoring and sensor calibration',
 'dfrobotnd_97cee5':'GUVA-S12SD UV detection sensor (TOY0044)',
 'gongora2023_ca6a1d':'Information-driven gas distribution mapping for autonomous mobile robots',
 'hoerl1970_31b919':'Ridge regression: Biased estimation for nonorthogonal problems',
 'iagnemma2004_9f7418':'Traction control of wheeled robotic vehicles in rough terrain with application to planetary rovers',
 'jcgm2008_0d3206':'Evaluation of measurement data—Guide to the expression of uncertainty in measurement',
 'liu2012_0ef0af':'Isolation-based anomaly detection',
 'melo2019_023727':'Development of a robotic airboat for online water quality monitoring in lakes',
 'mohamed2025_7d0710':'Development of a four omni-wheeled mobile robot using telescopic legs',
 'monroy2017_e93884':'GADEN: A 3D gas dispersion simulator for mobile robot olfaction in realistic environments',
 'nist2026_a8b13c':'Performance of emergency response robots',
 'ojeda2023_b7b9b6':'VGR dataset: A CFD-based gas dispersion dataset for mobile robotic olfaction',
 'patel2024_4264a8':'Towards a hygroscopic growth calibration for low-cost PM2.5 sensors',
 'reina2010_3d6119':'An adaptive suspension system for planetary rovers',
 'saputra2021_e81c43':'ResQbot 2.0: An improved design of a mobile rescue robot with an inflatable neck securing device for safe casualty extraction',
 'shan2020_c48065':'LIO-SAM: Tightly-coupled lidar inertial odometry via smoothing and mapping',
 'trevathan2020_3d3a03':'Towards the development of an affordable and practical light attenuation turbidity sensor for remote near real-time aquatic monitoring',
 'usgs2021_e859f3':'Chapter A6.4. Measurement of pH',
 'wang2024_112661':'A compact, low-cost, and low-power turbidity sensor for continuous in situ stormwater monitoring',
 'winsen2021_36e9d6':'Air quality gas sensor (model: MQ135) manual, version 1.6',
 'winsen2021_174511':'Carbon monoxide gas sensor (model: MQ-7B) manual, version 1.6',
 'winsen2021_dd85bc':'Flammable gas sensor (model: MQ-4) manual, version 1.6',
 'microchip_adc_an2537':'AN2537, Section 1.7: Conversion result',
}

def tex(s):
    table={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}','–':'--','—':'---','‐':'-','−':'-'}
    return ''.join(table.get(c,c) for c in str(s))

def initials(given):
    # Recognize contiguous initials (J.C.) as well as full and hyphenated names.
    words=re.findall(r'[^\W\d_]+(?:-[^\W\d_]+)*', given, flags=re.UNICODE)
    return ' '.join('-'.join(part[0]+'.' for part in w.split('-')) for w in words)

def author_text(s):
    names=[]
    for a in s.get('authors_structured') or []:
        if a.get('family'): names.append((initials(a.get('given',''))+' '+a['family']).strip())
        elif a.get('name'): names.append(a['name'])
    if not names: names=s['authors']
    if len(names)>6:return names[0]+' et al.'
    if len(names)==1:return names[0]
    if len(names)==2:return ' and '.join(names)
    return ', '.join(names[:-1])+', and '+names[-1]

def style(s):
    k=s['key']; a=author_text(s); title=TITLES.get(k,s['title']); venue=s.get('journal') or ''; year=s.get('year'); doi=s.get('doi') or ''; url=s.get('url') or ''
    parts=[]; italics=[]; notes=[]
    if k=='rasmussen2006_5c445c':
        parts=[a, title, s['publisher'], str(year)]; italics=[title]; typ='book'
    elif k=='jcgm2008_0d3206':
        parts=[a, title, 'JCGM 100:2008', str(year)]; italics=[title]; typ='technical_guide'
    elif k=='usgs2021_e859f3':
        parts=[a, '“'+title+'”', 'Techniques and Methods', str(year)]; italics=['Techniques and Methods']; typ='technical_guide'
    elif k=='vito2008_026a72':
        parts=[a, '“'+title+'”', 'UCI Machine Learning Repository', str(year), '[Data set]']; typ='dataset'
    elif k in ('papadopoulos1996_3a8aa9','shan2020_c48065'):
        conf='Proc. IEEE Int. Conf. Robot. Autom. (ICRA)' if k.startswith('papadopoulos') else 'Proc. IEEE/RSJ Int. Conf. Intell. Robots Syst. (IROS)'
        parts=[a,'“'+title+'”','in '+conf,str(year)]; italics=[conf]; typ='conference_paper'
        if s.get('volume'):parts.append('vol. '+s['volume'])
        if s.get('pages'):parts.append('pp. '+s['pages'].replace('-','–'))
    elif venue:
        ab=ABBR.get(venue,venue); parts=[a,'“'+title+'”',ab]; italics=[ab]; typ='journal_article'
        if s.get('volume'):parts.append('vol. '+s['volume'])
        if s.get('issue'):parts.append('no. '+s['issue'].replace('-','–'))
        art=s.get('article_number')
        if not art and s.get('publisher')=='MDPI AG' and str(s.get('pages') or '').isdigit():
            art=s['pages']; notes.append('The registry page field is the MDPI article identifier and is formatted as Art. no.')
        if s.get('pages') and not art:parts.append('pp. '+s['pages'].replace('-','–'))
        parts.append(str(year))
        if art:parts.append('Art. no. '+str(art))
    else:
        parts=[a,'“'+title+'”']; typ='online_manual_or_webpage'
        if year:parts.append(str(year))
        access=datetime.strptime(s['checked_date'],'%Y-%m-%d').strftime('%b. %d, %Y').replace(' 0',' ')
        plain=(', '.join(parts)+'. Accessed: '+access+'. [Online]. Available: '+url).replace('”,', ',”').replace('”.', '.”')
        latex=tex(plain[:-len(url)])+r'\url{'+url+'}'
        return plain,latex,typ,notes
    if doi:parts.append('doi: '+doi)
    plain=(', '.join(parts)+'.').replace('”,', ',”').replace('”.', '.”')
    latex=tex(plain)
    for phrase in sorted(italics,key=len,reverse=True):latex=latex.replace(tex(phrase),r'\textit{'+tex(phrase)+'}',1)
    if ' et al.' in latex:latex=latex.replace(' et al.',r' \textit{et al.}',1)
    if doi:latex=latex.replace(tex(doi),r'\href{https://doi.org/'+doi+r'}{\nolinkurl{'+doi+'}}')
    return plain,latex,typ,notes

records=[]
for r in old:
    s=by[r['key']]; forms=list(dict.fromkeys(r.get('citation_forms') or [r['citation_label'],r['narrative_citation']]))
    matches={}
    for f in forms:
        for m in re.finditer(r'(?<!\w)'+re.escape(f),body):
            line=body.count('\n',0,m.start())+1; line_text=body.splitlines()[line-1]
            matches[(m.start(),m.end())]={'start':m.start(),'end':m.end(),'line':line,'text':m.group(),'kind':'figure_caption' if line_text.startswith('!FIG[') else 'table' if line_text.startswith('!TABLE[') else 'prose','context':body[max(0,m.start()-65):min(len(body),m.end()+65)]}
    assert matches, r['key']
    occurrences=sorted(matches.values(),key=lambda m:m['start'])
    plain,latex,typ,notes=style(s)
    records.append({'key':s['key'],'author_label':r['author_label'],'year':r['year'],'citation_label':r['citation_label'],'narrative_citation':r['narrative_citation'],'citation_forms':forms,'source_aliases':r.get('registry_source_ids',[]),'plain_text':plain,'latex_text':latex,'source_type':typ,'doi':s.get('doi') or '','url':s.get('url') or '','first_appearance':occurrences[0],'occurrences':occurrences,'occurrence_count':len(occurrences),'formatting_notes':notes,'verified_metadata':{k:s.get(k) for k in ['title','authors','authors_structured','year','journal','volume','issue','pages','article_number','publisher','checked_date']},'prior_author_year_reference':r['citation_text']})
records.sort(key=lambda r:r['first_appearance']['start'])
for n,r in enumerate(records,1):r['number']=n; r['ieee_plain_text']=r['plain_text']; r['ieee_tex_text']=r['latex_text']

# Full parenthetical groups are replaced atomically; narrative references retain their author text.
form_map={f:r for r in records for f in r['citation_forms']}
replacements=[]
for m in re.finditer(r'\(([^()]+)\)',body):
    tokens=[s.strip() for s in m.group(1).split(';')]
    if tokens and all(t in form_map and ', ' in t for t in tokens):
        rs=[form_map[t] for t in tokens]
        replacements.append({'start':m.start(),'end':m.end(),'old':m.group(),'new':', '.join('['+str(r['number'])+']' for r in rs),'keys':[r['key'] for r in rs],'kind':'parenthetical_group'})
for r in records:
    for oc in r['occurrences']:
        if any(x['start']<=oc['start'] and oc['end']<=x['end'] for x in replacements):continue
        assert oc['text'].endswith(')'),oc
        name=oc['text'][:oc['text'].rfind(' (')]
        replacements.append({'start':oc['start'],'end':oc['end'],'old':oc['text'],'new':name+' ['+str(r['number'])+']','keys':[r['key']],'kind':'narrative'})
replacements.sort(key=lambda x:x['start'])
assert all(a['end']<=b['start'] for a,b in zip(replacements,replacements[1:]))
converted=body
for x in reversed(replacements):converted=converted[:x['start']]+x['new']+converted[x['end']:]
unmapped_year_parens=[{'text':m.group(),'line':converted.count('\n',0,m.start())+1} for m in re.finditer(r'\([^()]*\b(?:19|20)\d{2}[a-z]?[^()]*\)',converted)]
assert not unmapped_year_parens,unmapped_year_parens
assert sum(len(x['keys']) for x in replacements)==sum(r['occurrence_count'] for r in records)
assert len({r['key'] for r in records})==45
assert len({r['doi'].lower() for r in records if r['doi']})==sum(bool(r['doi']) for r in records)

result={'schema_version':'1.0','style':'IEEE numeric; ordered by first citation in body, including tables and figure captions','count':len(records),'created_utc':datetime.now(timezone.utc).isoformat(),'input_manuscript':str(SOURCE.relative_to(P)).replace('\\','/'),'input_manuscript_sha256':hashlib.sha256(md.encode()).hexdigest(),'source_registry':'research/references_verified.json','official_style_source':'https://journals.ieeeauthorcenter.ieee.org/wp-content/uploads/sites/7/IEEE_Reference_Guide.pdf','guide_checked_date':'2026-09-16','style_decisions':['One reference per number; first appearance determines number.','Current IEEE guide requests individual bracketed numbers, not compressed ranges.','Bibliography lists all authors up to six; more than six becomes first author et al.','Article titles are sentence case; established acronyms and proper names retain capitalization.','No unverified publication months or publisher locations are added.','DOI links are retained for scholarly records; online manuals retain verified URL and original verification date.'],'references':records,'by_key':{r['key']:r['number'] for r in records},'by_citation_form':{f:{'key':r['key'],'number':r['number']} for r in records for f in r['citation_forms']},'replacements':replacements,'audit':{'selected_sources':45,'matched_sources':len(records),'citation_occurrences':sum(r['occurrence_count'] for r in records),'replacement_regions':len(replacements),'unmapped_author_year_parentheses':unmapped_year_parens,'duplicate_dois':0,'ambiguous_sources':[]},'integration_guidance':['Use references[] in numeric order; plain_text has no leading bracketed number.','Replace complete author-year parenthetical groups with numeric groups; do not leave outer parentheses.','Narrative authors remain, but their parenthetical years become bracketed citation numbers.','Use \\usepackage[numbers]{natbib}; do not enable sort&compress. Manual bibitems have no optional author-year labels.','The replacements[] offsets apply only to the recorded input SHA-256; by_citation_form permits robust replacement after prose edits.','Re-scan first-use order after any citation-bearing paragraphs, tables, or figures move.']}
(P/'research/ieee_references.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
lines=['% IEEE numeric bibliography, first-citation order. Requires hyperref (or url) and UTF-8 XeLaTeX.','% Source: research/ieee_references.json; no BibTeX/Biber step.','\\begin{thebibliography}{99}']
for r in records:lines+=['',r'\bibitem{'+r['key']+'}',r['latex_text']]
lines+=['',r'\end{thebibliography}','']
(P/'latex/references_ieee.tex').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps(result['audit'],ensure_ascii=False))
for r in records:print(f"[{r['number']}] {r['plain_text']}")
