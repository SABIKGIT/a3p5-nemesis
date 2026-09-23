# A3P5 NEMESIS — LaTeX source

The main document is `A3P5_NEMESIS_Research_Manuscript.tex`. It contains editable manuscript text, 18 native LaTeX equations, 6 tables, 45 figures and the verified machine-learning evaluation listing. Its 45 IEEE-style numbered references are ordered by first citation and embedded using `natbib` and `thebibliography`; no BibTeX or Biber step is needed.

## Overleaf

1. ZIP the contents of this `manuscript/latex/` folder (including `figures/`), then choose **New Project → Upload Project** in Overleaf and upload that ZIP. Do not upload the entire GitHub repository as the Overleaf project.
2. Set `A3P5_NEMESIS_Research_Manuscript.tex` as the main document.
3. Select **XeLaTeX** as the compiler and recompile. Do not use pdfLaTeX.

## Local compilation

With a current TeX installation, run from this folder:

```sh
latexmk -xelatex A3P5_NEMESIS_Research_Manuscript.tex
```

Alternatively, run XeLaTeX twice to resolve citations and cross-references:

```sh
xelatex A3P5_NEMESIS_Research_Manuscript.tex
xelatex A3P5_NEMESIS_Research_Manuscript.tex
```

The included `.latexmkrc` selects XeLaTeX and disables bibliography-tool processing.

## Files and layout

Keep UTF-8 encoding and preserve the `figures/` folder beside the main document. Its 32 assets comprise 31 raster images and one native 14-page Canva PDF; individual PDF pages supply the 14 Canva figures. Keep their filenames unchanged. This PDF is a vector figure asset, not a compiled copy of the manuscript; the deliverable manuscript formats are Word and editable LaTeX source.

`\FloatBarrier` commands keep figures within their assigned sections and subsections. Running headers are empty; footers contain only page numbers. Pagination can differ from the accompanying Word document. Recompile and visually check figures, captions, equations and page breaks after editing. Compiler binaries are not included.

The displayed Python evaluation core is embedded in the main source. The full executable companion and archived data are in this repository under `manuscript/analysis/` and `manuscript/research/`.
