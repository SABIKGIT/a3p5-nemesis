# Reproducing the study

Run commands from the repository root with Python 3.12. The original environment versions are recorded in [reproducibility_versions.json](../manuscript/reproducibility_versions.json). All pinned packages were checked against their public PyPI release records when this repository was prepared.

## 1. Inspect the archived results without installing packages

```bash
python scripts/verify.py --json verification/local-stdlib-results.json
```

This uses standard-library tests to examine the packaged evidence. It does not run physical hardware or replace the archived scientific calculations with new measurements.

## 2. Prepare the scientific environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Then install the recorded package releases:

```bash
python -m pip install -r requirements.txt
```

## 3. Replay, refit and independently check

```bash
python scripts/verify.py --models
python scripts/verify.py --refit --regenerate-engineering --json verification/local-full-results.json
```

Read the generated report for the exact checks performed. Model replay uses only the saved pipelines supplied with this repository. Refitting repeats the original ordered 21-candidate search and keeps validation-based selection separate from test evaluation. Engineering regeneration is performed in an isolated temporary folder so the publication outputs remain available for comparison.

Saved `.joblib` files are Python serialization artifacts and should be loaded only from a trusted copy of this repository. Exact recorded package versions are required for model replay. Desktop timings depend on hardware and operating system; archived timing measurements are not embedded-controller benchmarks.

## 4. Regenerate figures and source outputs deliberately

These commands replace their generated files within `manuscript/analysis/`; commit or copy any local edits before rerunning them:

```bash
python manuscript/analysis/engineering_analysis.py
python manuscript/analysis/ml_benchmark.py
```

The ML script verifies the input ZIP checksum before reading it. It retains only observations with a valid timestamp, an observed CO target and at least one observed predictor. It fits on 5,140 records, selects on 1,102 validation records and evaluates on 1,102 untouched test records. The `-200` missing-value code is handled explicitly. The validation-selected winner remains Ridge; test ranking never changes that choice.

To repeat the displayed manuscript code independently without replacing benchmark outputs:

```bash
python manuscript/text/code_listing_revision.py
```

## 5. Rebuild the paper

```bash
python manuscript/build_manuscript.py
python manuscript/create_latex.py
```

The Word builder starts from `manuscript/text/manuscript_ieee.md`; the LaTeX builder uses its generated Markdown and figure manifest. The manuscript remains a single-column design study, with a bold title, empty running headers, page-number-only footer and numbered IEEE references. Equations are rendered images in Word and native equations in LaTeX.

For Overleaf, upload the contents of `manuscript/latex/` as one project and select **XeLaTeX**. A local TeX installation can use:

```bash
cd manuscript/latex
latexmk -xelatex A3P5_NEMESIS_Research_Manuscript.tex
```

Check the rendered pages after changing manuscript content or figure dimensions. Rebuilding with different fonts or office software may change Word pagination. The prebuilt Word file is retained for reference; no PDF manuscript is distributed.

## 6. Open or regenerate Blender scenes

The prebuilt files were created in Blender 4.3.2. Open `A3P5_Nemesis_Industrial.blend` or `manuscript/blender/A3P5_Nemesis_Mission_Studies.blend` directly. Textures and reference photographs are packed; distribution paths also point to the included photo files. Geometry is estimated, cable curves are static and the mission scenes are illustrations.

For source regeneration, use an isolated Blender background process. These commands rebuild the repository model outputs:

```bash
blender --background --factory-startup --python nemesis_build.py --python manuscript/blender/create_mission_scenes.py
blender --background manuscript/blender/A3P5_Nemesis_Mission_Studies.blend --python manuscript/blender/render_missions.py
```

An isolated source-build check succeeded in Blender 4.3.2 and packed all four reference photos; see `verification/blender_source_build.json`. The prebuilt models include later manual refinements, so source regeneration is not asserted to be byte-identical to those models.

The two construction scripts must run in the same Blender process so the second script can use the first script's live geometry helpers. The repository's path-normalization check preserves object/mesh geometry and material assignments; it does not establish robot dynamics or wiring functionality.

## 7. Literature and Canva provenance

The literature archive contains 5,000 retrieved metadata occurrences, 4,897 distinct DOI records and 1,212 metadata candidates. This is an exploratory metadata census, not 5,000 full-text reviews. Publisher abstract text and downloaded source-paper PDFs are omitted from this repository. Re-fetching Crossref metadata is required to repeat abstract-based screening; search ranking and metadata can change over time.

The native Canva export and its 14 full-page PNGs are authoritative for the diagrams. Source HTML is an authoring aid. Re-running it does not replace export from Canva or visual review. See the diagram [provenance](../manuscript/diagrams/canva_complete_final_provenance.json) and [print README](../manuscript/diagrams/CANVA_PRINT_README.md).

## 8. Check distribution integrity

```bash
python scripts/manifest.py --check
```

The manifest covers reviewed distribution files, including models and manuscript assets. UTF-8 text hashes normalize CRLF to LF so Git line-ending conversion does not create false failures. The imported-archive hashes in `verification/import_provenance.json` describe the original handoff bytes, before repository portability edits; use `verification/file_manifest.json` for this distribution.

After intentionally editing reviewed source or results, rerun the relevant scientific checks, inspect the changes, then update the distribution record:

```bash
python scripts/manifest.py --write
python scripts/manifest.py --check
```

Do not refresh the manifest simply to hide an unexplained mismatch. Local/CI result reports, caches and regenerated QA are excluded.
