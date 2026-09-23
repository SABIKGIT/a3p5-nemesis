# Achieved literature-metadata census

Completed on 15 September 2026. The final screening rules are version 1.2.

| Stage | Count |
|---|---:|
| Search queries | 10 |
| Raw retrieved record occurrences | 5,000 |
| Duplicate DOI occurrences removed | 103 |
| Distinct DOI records screened | 4,897 |
| Records with available abstracts | 1,291 |
| Records without abstracts | 3,606 |
| Metadata candidates | 1,212 |
| Records not prioritized by the metadata rule | 3,685 |
| Suggested next reads | 150 |
| Suggested reads with abstracts | 71 |
| Full texts read as part of the census | 0 |

All ten raw response hashes and all nine plot-table totals were verified. The shortlist contains no Crossref peer-review reports and no exact normalized-title duplicates. The complete corpus retains separate DOI records even when their titles match; `exact_title_duplicates.csv` makes these visible.

## Wording suitable for a manuscript methods section

On 15 September 2026, ten thematic queries to the public Crossref REST API retrieved 5,000 relevance-ranked metadata records, capped at 500 records per query and filtered to publication dates from 1 January 1990 to 15 September 2026. Case-insensitive DOI deduplication yielded 4,897 distinct records. A reproducible keyword-and-topic-conjunction rule screened titles and 1,291 available abstracts, identifying 1,212 metadata candidates. A topic-balanced ranking produced a 150-record reading shortlist. This exploratory metadata census was not a systematic review or full-text evidence synthesis. Raw responses, request logs, DOI provenance, screening code, and analysis tables were archived.

## How to use the results

Use `shortlist.csv` for the next-reading queue, `context_sources.md` for 11 source-checked starting points, and `bibliography_all.csv` to audit every decision. Two contextual leads also appear in the ten-query corpus; the other nine supplement it and are not included in its counts. Source checking was limited to the scope recorded for each lead.

Use the year and topic CSV files only to describe this retrieved sample. Query ranking, record caps, English terms, uneven DOI coverage, missing abstracts, and an incomplete 2026 publication year prevent interpretation as field-wide publication trends or evidence of novelty. A metadata relevance score is not a study-quality score.

No rover experiments or benchmark experiments were run as part of this literature-metadata census. The separate external-data calibration experiment is documented under ../analysis/ml_outputs/. Literature and external datasets cannot establish the performance of the modeled rover.
