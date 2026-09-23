# IEEE citation audit

## Outcome

- 45 selected sources, all mapped unambiguously and numbered by first appearance.
- 79 source mentions: 68 in prose and 11 in figure captions; no cited source appears first in a table.
- 74 atomic replacement regions; 96 accepted author/year alias forms.
- No unmatched author/year parenthetical citations, duplicate DOIs, or DOI/URL mentions that precede the assigned first citation.
- 45 manual numeric bibliography items; 37 DOI-bearing sources and 8 online manuals/pages.

## Integration

`ieee_references.json` exposes `references` in numerical order. Each record includes `number`, stable `key`, `plain_text`, `latex_text`, citation aliases, original verified metadata and source locations. Plain text omits the leading number. Use `references_ieee.tex` directly with numeric natbib; no BibTeX/Biber step is needed.

Replace complete parenthetical groups atomically: `(Winsen, 2021a; Winsen, 2021c)` becomes `[11], [12]`. Narrative authors may remain: `Francis et al. (2022)` becomes `Francis et al. [1]`. Offsets refer to the original normalized author/year input, not the subsequently revised document. Use `by_citation_form` after prose edits. Recheck first-use order after moving citation-bearing content.

## Verified style

The current official [IEEE Reference Guide](https://journals.ieeeauthorcenter.ieee.org/wp-content/uploads/sites/7/IEEE_Reference_Guide.pdf), checked 16 September 2026, requests individual bracketed numbers instead of compressed citation ranges, one source per reference number, initials before surnames, and all authors up to six (first author plus *et al.* for more than six). The supplied bibliography follows those rules. The exact journal submission instructions remain authoritative if a target journal specifies a variation.

## Preserved distinctions and metadata limits

- Dataset author **S. Vito** ([29]) is distinct from **S. De Vito et al.** ([30]), the associated journal article.
- Winsen MQ135 ([11]), MQ4 ([12]) and MQ-7B ([13]) remain separate. The existing MQ-7B-versus-prototype-MQ7 qualification is unchanged.
- Undated Microchip ([40]) and DFRobot ([42]) pages have access dates, not invented publication dates.
- JCGM and USGS long-name aliases resolve to [43] and [23].
- Existing verified publication years are preserved, including RTAB-Map 2019, Burghi et al. 2024, and the Rasmussen/Williams book 2006.
- DOI links or the exact verified online URL are retained. Unknown publication months, conference locations and publisher cities have been omitted rather than inferred.
- Registry MDPI single-number page fields are correctly presented as article identifiers. IEEE-style sentence capitalization changes neither titles' wording nor source identity.

No source-identification exception requires an author decision.
