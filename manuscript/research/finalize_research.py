from pathlib import Path
import json,csv,re,hashlib,datetime
from collections import Counter
R=Path(__file__).resolve().parent
j=lambda n:json.loads((R/n).read_text(encoding='utf-8'))
s=j('census_summary.json');a=j('bibliography_all.json');c=j('metadata_candidates.json');z=j('shortlist.json');q=j('query_log.json');context=j('context_sources.json')
assert len(a)==s['unique_records_after_doi_deduplication'] and len(c)==s['metadata_candidates'] and len(z)==s['heuristic_shortlist']
assert sum(x['returned_count'] for x in q)==5000
assert len({x['doi'] for x in a})==len(a)
assert all(x['screening_decision']=='metadata_candidate' for x in z)
assert all(x['type']!='peer-review' for x in z)
assert len({re.sub(r'\W+','',x['title'].lower()) for x in z})==150
for cohort,count in [('all_unique',len(a)),('metadata_candidates',len(c)),('shortlist',len(z))]:
    for prefix in ['year_counts','topic_counts','year_topic_counts']:
        rows=list(csv.DictReader((R/f'{prefix}_{cohort}.csv').open(encoding='utf-8-sig')))
        assert sum(int(x['count']) for x in rows)==count,(prefix,cohort)
for r in q:
    assert hashlib.sha256((R/r['raw_file']).read_bytes()).hexdigest()==r['sha256']
bydoi={r['doi']:r for r in a}
for x in context:
    found=bydoi.get(x['doi'].lower())
    x['in_ten_query_census']=bool(found)
    x['relationship_to_census']='also retrieved in the ten-query census' if found else 'supplemental contextual source, outside census counts'
    if found:x['census_screening_decision']=found['screening_decision'];x['census_score']=found['relevance_score']
(R/'context_sources.json').write_text(json.dumps(context,ensure_ascii=False,indent=2),encoding='utf-8')
with (R/'context_sources.csv').open('w',newline='',encoding='utf-8-sig') as f:
    fields=list(dict.fromkeys(k for r in context for k in r));w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(context)
def esc(t):
    return str(t).replace('\\','\\textbackslash{}').replace('&',r'\&').replace('%',r'\%').replace('_',r'\_').replace('#',r'\#').replace('{','').replace('}','')
bib=[]
for i,r in enumerate(z,1):
    typ={'journal-article':'article','proceedings-article':'inproceedings','book-chapter':'incollection','book':'book','report':'techreport'}.get(r['type'],'misc')
    entries={'title':r['title'],'author':r['authors'].replace('; ',' and '),'year':r['year'],'doi':r['doi'],'url':r['doi_url']}
    entries['journal' if typ=='article' else 'booktitle']=r['venue']
    for k in ['volume','issue','pages']:
        if r[k]:entries['number' if k=='issue' else k]=r[k]
    bib.append('@'+typ+'{A3P5Meta'+str(i).zfill(3)+',\n'+',\n'.join('  '+k+' = {'+esc(v)+'}' for k,v in entries.items() if v)+'\n}')
(R/'shortlist.bib').write_text('% Automatically formatted from Crossref metadata; verify records against full text before publication.\n\n'+'\n\n'.join(bib),encoding='utf-8')
text=f'''# Achieved literature-metadata census

Completed on 15 September 2026. The final screening rules are version 1.2.

| Stage | Count |
|---|---:|
| Search queries | 10 |
| Raw retrieved record occurrences | 5,000 |
| Duplicate DOI occurrences removed | 103 |
| Distinct DOI records screened | 4,897 |
| Records with available abstracts | 1,291 |
| Records without abstracts | 3,606 |
| Metadata candidates | {len(c):,} |
| Records not prioritized by the metadata rule | {len(a)-len(c):,} |
| Suggested next reads | 150 |
| Suggested reads with abstracts | {sum(r['has_abstract'] for r in z)} |
| Full texts read as part of the census | 0 |

All ten raw response hashes and all nine plot-table totals were verified. The shortlist contains no Crossref peer-review reports and no exact normalized-title duplicates. The complete corpus retains separate DOI records even when their titles match; `exact_title_duplicates.csv` makes these visible.

## Wording suitable for a manuscript methods section

On 15 September 2026, ten thematic queries to the public Crossref REST API retrieved 5,000 relevance-ranked metadata records, capped at 500 records per query and filtered to publication dates from 1 January 1990 to 15 September 2026. Case-insensitive DOI deduplication yielded 4,897 distinct records. A reproducible keyword-and-topic-conjunction rule screened titles and 1,291 available abstracts, identifying {len(c):,} metadata candidates. A topic-balanced ranking produced a 150-record reading shortlist. This exploratory metadata census was not a systematic review or full-text evidence synthesis. Raw responses, request logs, DOI provenance, screening code, and analysis tables were archived.

## How to use the results

Use `shortlist.csv` for the next-reading queue, `context_sources.md` for 11 source-checked starting points, and `bibliography_all.csv` to audit every decision. Two contextual leads also appear in the ten-query corpus; the other nine supplement it and are not included in its counts. Source checking was limited to the scope recorded for each lead.

Use the year and topic CSV files only to describe this retrieved sample. Query ranking, record caps, English terms, uneven DOI coverage, missing abstracts, and an incomplete 2026 publication year prevent interpretation as field-wide publication trends or evidence of novelty. A metadata relevance score is not a study-quality score.

No rover experiments or benchmark experiments were run. Literature and external datasets cannot establish the performance of the modeled rover.
'''
(R/'RESULTS.md').write_text(text,encoding='utf-8')
readme=(R/'README.md').read_text(encoding='utf-8-sig')
readme=readme.replace('Visible retraction', 'Visible retraction')
readme=readme.replace('are not prioritized. The full regular expressions','are not prioritized. Crossref peer-review reports and administrative container record types are also not prioritized. The full regular expressions')
readme=readme.replace('until 150 are selected. Review/dataset','until 150 are selected, while suppressing exact normalized-title duplicates in the shortlist. Review/dataset')
readme=readme.replace('- `census_summary.json`: exact final counts and abstract coverage.','- `census_summary.json` and `RESULTS.md`: exact final counts, abstract coverage, and a concise methods paragraph.\n- `shortlist.bib`: metadata-derived BibTeX for the 150 suggested reads; verify before publication.\n- `exact_title_duplicates.csv`: matching normalized titles registered under different DOIs.')
(R/'README.md').write_text(readme,encoding='utf-8')
validation={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'raw_response_hashes_verified':10,'plot_tables_total_checked':9,'all_unique_dois':len(a),'candidate_count':len(c),'shortlist_count':len(z),'shortlist_peer_review_reports':0,'shortlist_exact_normalized_title_duplicates':0,'source_checked_leads':len(context),'source_checked_leads_in_census':sum(x['in_ten_query_census'] for x in context),'raw_download_bytes':sum(x['byte_count'] for x in q),'retrieval_started_utc':min(x['started_utc'] for x in q),'retrieval_finished_utc':max(x['finished_utc'] for x in q)}
(R/'validation.json').write_text(json.dumps(validation,indent=2),encoding='utf-8')
print(json.dumps(validation,indent=2))
print('Candidate primary topics',dict(Counter(x['primary_topic'] for x in c)))
