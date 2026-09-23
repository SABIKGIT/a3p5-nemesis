from pathlib import Path
import json,re,collections
R=Path(__file__).resolve().parent
j=json.loads((R/'references_verified.json').read_text(encoding='utf-8'));bykey={r['key']:r for r in j['sources']};aliases=j['aliases'];src=(R/'related_work_source.md.in').read_text(encoding='utf-8-sig')
pat=r'\{\{(narr|cite):([^}]+)\}\}'
used=collections.Counter()
def render(m):
 typ,ids=m.groups();rr=[bykey[aliases[s.strip()]] for s in ids.split(';')]
 for r in rr:used[r['key']]+=1
 if typ=='narr':assert len(rr)==1;return rr[0]['narrative_citation']
 return '('+'; '.join(r['citation_label'] for r in rr)+')'
out=re.sub(pat,render,src)
assert '{{' not in out
wc=lambda s:len(re.findall(r"\b[\w]+(?:[’'-][\w]+)*\b",s))
words=wc(out);assert 1500<=words<=2000,words
ledger=collections.Counter()
for p in src.split('\n\n'):
 ids={q.strip() for m in re.finditer(pat,p) for q in m.group(2).split(';')};para=re.sub(pat,render,p);count=wc(para)
 for key in {aliases[q] for q in ids}:ledger[key]+=count
assert max(ledger.values())<=200,ledger
(R/'related-work-draft.md').write_text(out,encoding='utf-8')
ca={'body_word_count_including_headings_and_citations':words,'cited_unique_sources':len(ledger),'unresolved_citation_placeholders':0,'attribution_method':'Conservative: each entire cited paragraph, including Nemesis-specific interpretation, is counted against every distinct source cited in that paragraph. Bibliographic citation text is included.','maximum_conservative_words_per_source':max(ledger.values()),'source_limit':200,'cited_sources':[{'key':k,'citation':bykey[k]['citation_label'],'conservative_paragraph_word_count':v} for k,v in sorted(ledger.items())]}
(R/'related_work_citation_audit.json').write_text(json.dumps(ca,ensure_ascii=False,indent=2),encoding='utf-8')
refs=j['sources'];ds=[r['doi'] for r in refs if r['doi']];assert len(ds)==len(set(ds));assert len(refs)==len(bykey);assert all(r['title'] and r['authors'] and r['url'] and r['citation_text'] for r in refs)
assert all(r['metadata_verification']['title_matches_at_least_0_7'] for r in refs if r['doi'])
assert all(k in bykey for k in aliases.values())
v={'unique_references':len(refs),'unique_doi_references':len(ds),'independently_confirmed_doi_title_pairs':sum(r['metadata_verification'].get('title_matches_at_least_0_7',False) for r in refs),'no_doi_primary_source_audits':len(refs)-len(ds),'source_aliases':len(aliases),'duplicate_dois':0,'unresolved_aliases':0,'missing_authors_or_title_or_url':0,'corrected_mismatches':[{'source_ids':r['source_ids'],'title':r['title'],'doi':r['doi'],'corrections':[a['audit_correction'] for a in r['source_audits'] if a.get('audit_correction')]} for r in refs if any(a.get('audit_correction') for a in r['source_audits'])],'date_conventions':[{'source_ids':r['source_ids'],'notes':r.get('metadata_discrepancies')} for r in refs if r.get('metadata_discrepancies')],'scope':'Metadata confirmation does not imply that every source was read in full. Each source retains its specific read depth, supported claims and limitations.'}
(R/'references_validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'registry':v,'draft':{k:v for k,v in ca.items() if k!='cited_sources'}},ensure_ascii=False,indent=2))
for sid in ['T01','M03','M12','SEN01','SEN02','SEN03','R09','ADD01','ADD02','ADD03','ADD04']:
 print(sid,bykey[aliases[sid]]['citation_text'])
