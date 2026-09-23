## Distribution note
This archive omits publisher abstract text and original response bodies. Only sanitized bibliographic copies, original SHA-256 hashes and query-request logs are distributed. The exact original responses remain in the local workspace; rerun retrieval before the raw-response screening steps below.

# Research metadata census: A3P5 environmental rover

## Scope

This is a reproducible exploratory search and automated metadata screen, not a systematic review, PRISMA review, meta-analysis, or claim that thousands of full texts were read. The eventual exact achieved counts are in `census_summary.json`; do not infer those counts from the API's much larger `total-results` values.

Ten relevance-ranked Crossref bibliographic queries each request their first 500 records, with publication dates from 1990-01-01 through 2026-09-15 inclusive. The queries cover robotic environmental monitoring, ground-rover air sensing, robotic gas mapping, particulate sensor calibration, metal-oxide sensor calibration, robotic water monitoring, four-wheel steering, outdoor sensor fusion, robotic sampling, and environmental-robotics datasets. The full query strings, HTTP URLs, timestamps, response headers, response counts, and retry history are retained in the request logs.

## Reproducibility

1. Run `retrieve_crossref.py` to retrieve metadata. Existing successful responses are reused.
2. Run `screen_metadata.py` after all ten searches finish. It verifies each raw response against its SHA-256 hash, deduplicates DOI strings case-insensitively, normalizes titles and abstracts, and applies the documented rules.
3. Run `finalize_research.py` to validate table totals, finalize the source membership, and export the reading bibliography.
4. Preserve `raw_crossref/`, the scripts, `query_log.*`, and `record_provenance.csv` alongside the bibliography.

The raw JSON response bytes are preserved without editing. A repeated live search may return different ranking, deposit updates, or counts. The archived responses support exact re-analysis of this run.

## Screening rule

Title matches receive three points per keyword category; matches only in an available abstract receive one. Qualifying topic conjunctions add up to six points. A robotics-plus-environment title, or a calibration-plus-air/gas title, receives two additional points. An explicit robotics-plus-steering or robotics-plus-sampling title also receives two points so concise mechanical titles are not penalized for containing fewer general keyword categories. Records require at least one qualifying topic conjunction and a score of at least ten to enter the metadata-candidate set. Surgical/miniature-robot topics, visible retraction and correction notices, and common administrative titles are not prioritized. Crossref peer-review reports and administrative container record types are also not prioritized. The full regular expressions and conjunctions are in `screen_metadata.py`.

This score measures textual relevance, not scientific quality, reproducibility, novelty, or experimental credibility. The shortlist includes the leading 12 candidates per primary topic where available, followed by the highest-ranked remaining candidates until 150 are selected, while suppressing exact normalized-title duplicates in the shortlist. Review/dataset title flags, Crossref citation counts, year, DOI, and title provide deterministic tie-breaks. The shortlist still requires full-text assessment before evidence is used in a manuscript.

## Outputs

- `bibliography_all.csv/json`: every distinct retrieved record and its screen result.
- `metadata_candidates.csv/json`: records passing the stated metadata rule.
- `shortlist.csv/json`: 150 suggested next reads, subject to available candidates.
- `record_provenance.csv`: query, original rank, and raw item index for every occurrence.
- `year_counts_*.csv`, `topic_counts_*.csv`, `year_topic_counts_*.csv`: plot-ready tables for all distinct records, candidates, and the shortlist. Primary-topic counts are mutually exclusive; topic tags in the bibliography can overlap.
- `census_summary.json` and `RESULTS.md`: exact final counts, abstract coverage, and a concise methods paragraph.
- `shortlist.bib`: metadata-derived BibTeX for the 150 suggested reads; verify before publication.
- `exact_title_duplicates.csv`: matching normalized titles registered under different DOIs.
- `context_sources.json` and `context_sources.md`: a separate, small, source-checked starting bibliography. These sources are not automatically added to the ten-query census count.

## Interpretation limits

Crossref is a DOI metadata index rather than a complete scientific corpus. Bibliographic relevance search is not an exact Boolean search; container titles and other fields can return irrelevant records. The first-500 cutoff creates ranking bias, and repeated queries overlap. Different DOI versions of the same study are not collapsed into one study. Many records lack abstracts, and English keyword rules can miss other languages or synonyms. Publication dates and citation counts reflect deposited metadata and may be imperfect. Automated notice filtering is not a complete retraction check.

Charts must be labeled as distributions of this retrieved metadata sample or its screened candidates. They do not establish field-wide publication trends, technology prevalence, evidence strength, or the rover's novelty. No rover experiments, sensor calibration measurements, navigation benchmarks, or environmental performance results are produced by this literature search.

## API source checks

Crossref documents public access without registration: https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/
Crossref documents query controls and response caching: https://www.crossref.org/documentation/retrieve-metadata/rest-api/tips-for-using-the-crossref-rest-api/
OpenAlex announced API-key requirements for 2026, so this run uses the public Crossref service and does not request an account or key: https://groups.google.com/g/openalex-users/c/rI1GIAySpVQ
