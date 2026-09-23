# Portable XeLaTeX build; references are embedded in the main source.
$pdf_mode = 5;
$xelatex = 'xelatex -no-pdf -interaction=nonstopmode -halt-on-error -file-line-error %O %S';
$bibtex_use = 0;
$max_repeat = 5;
@default_files = ('A3P5_NEMESIS_Research_Manuscript.tex');
