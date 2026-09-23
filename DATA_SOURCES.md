# Data sources and provenance

## UCI Air Quality

**Citation:** S. Vito, *Air Quality*, UCI Machine Learning Repository, 2008, DOI [10.24432/C59K5F](https://doi.org/10.24432/C59K5F). Official source: [UCI dataset page](https://archive.ics.uci.edu/dataset/360/air%2Bquality), checked 21 September 2026. Associated study: De Vito et al., 2008, DOI [10.1016/j.snb.2007.09.060](https://doi.org/10.1016/j.snb.2007.09.060).

The provider's current License section displays [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The same page retains older wording: “This dataset can be used exclusively for research purposes. Commercial purposes are fully excluded.” Both notices are recorded here; this repository does not resolve that source inconsistency or grant additional dataset rights. The archive is retained for this research study's offline reproduction.

- File: `manuscript/research/air_quality.zip`
- Archive SHA-256: `d4a64013fb385288a8a48d9d193ca7079b2e1bbddf6f8d458feb8c08ab2b8a2a`
- CSV SHA-256: `13277ae5d8581e80b7be09d47c7d3d06fe9b8e957078f2cf6e859f955e62f996`
- Archive members: `AirQualityUCI.csv`, `AirQualityUCI.xlsx`; no separate license/README file is present.
- Cleaning and split record: [data_audit.json](manuscript/analysis/ml_outputs/data_audit.json).

The file contains 9,357 valid timestamps and 7,344 eligible observations under the study rule. These are file-derived counts, not a substitution for the provider's descriptive metadata. Dates are dataset-local naive timestamps; no timezone was inferred. Predictor and target units are defined in the manuscript and benchmark source.

## Engineering scenario data

[analysis_results.json](manuscript/analysis/analysis_results.json) records geometry estimates, assumed inputs and conventions. The nine engineering CSV tables and eight graph pairs are derived from those inputs. They are not hardware measurements. [engineering-calculations.md](docs/engineering-calculations.md) explains the equations, units and interpretation.

## Photographs, models and mission arrangements

Four distinct prototype photographs supplied by the authors are retained in `manuscript/research/prototype_photos/`. Geometry is estimated from them. The two `.blend` files contain packed copies of these references and local/procedural materials. Source-model distribution paths were normalized while object and mesh geometry hashes were verified unchanged. See [blender_distribution.json](verification/blender_distribution.json).

## Diagrams and reused figures

The 14 Canva figures retain their native export, embedded titles/arrow legends, source specifications and hashes. External journal figures remain separately attributed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). They are not rover measurements.

## Literature metadata

Ten archived Crossref queries retrieved 5,000 occurrences and 4,897 distinct DOI records. Logs, metadata, screening rules and source hashes are retained. Abstract text and raw response bodies containing it are excluded; the `has_abstract` flag is retained. See [literature results](manuscript/research/RESULTS.md) and [Crossref metadata guidance](https://www.crossref.org/documentation/retrieve-metadata/). Re-fetching metadata is needed to repeat abstract-based screening, and changed search results cannot be treated as the original snapshot.
