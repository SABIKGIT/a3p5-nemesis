from pathlib import Path
import re,json,shutil,hashlib
from PIL import Image
R=Path(__file__).resolve().parent
OUT=R/'latex';FIG=OUT/'figures';FIG.mkdir(parents=True,exist_ok=True)
SOURCE=R/'final/A3P5_NEMESIS_Research_Manuscript.md'
s=SOURCE.read_text(encoding='utf8')
manifest=json.loads((R/'qa/build_manifest.json').read_text(encoding='utf8'))
refs=json.loads((R/'research/ieee_references.json').read_text(encoding='utf8'))['references']
TITLE=s.splitlines()[0].lstrip('# ')
layout=json.loads((OUT/'layout_config.json').read_text(encoding='utf8'))
counts={'figures':0,'tables':0,'equations':0,'sections':0,'subsections':0,'citation_commands':0}
audit={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'figures':[],'tables':[],'equations':[],'paragraphs':[],'headings':[]}
SPECIAL={'&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}','\\':r'\textbackslash{}','–':'--','—':'---','‐':'-','−':r'\ensuremath{-}','·':r'\ensuremath{\cdot}','°':r'\textdegree{}','×':r'\ensuremath{\times}','≤':r'\ensuremath{\leq}','∈':r'\ensuremath{\in}','±':r'\ensuremath{\pm}','𝒯':r'\ensuremath{\mathcal{T}}'}
GREEK={'ω':'omega','δ':'delta','Ω':'Omega','π':'pi','α':'alpha','μ':'mu','κ':'kappa','τ':'tau','Σ':'Sigma'}
SPECIAL.update({k:chr(92)+'ensuremath{'+chr(92)+v+'}' for k,v in GREEK.items()})
SUP={'⁻':'-','¹':'1','²':'2','³':'3','ᴺ':'N'};SUB={'ᵢ':'i','ₓ':'x','ᵧ':'y','ᵣ':'r','₉':'9','₀':'0'}
mathmap={'xᵢ':'x_i','yᵢ':'y_i','vₓ':'v_x','vᵧ':'v_y','δᵢ':r'\delta_i','Ωᵢ':r'\Omega_i','rᵢ':'r_i','Cᵣᵣ':'C_{rr}','Fᵢ':'F_i','μᵢNᵢ':r'\mu_i N_i','τ':r'\tau','t₉₀':'t_{90}','d₉₀':'d_{90}','Σ_x':r'\Sigma_x'}
for var in ['R_s','R_L','V_c','V_L','R_0','c_raw','d_lag','E_7','u_model','W_req','M_front','y_i','z_i','x_i','c_dry','V_ref']:
 base,sub=var.split('_',1);mathmap[var]=base+'_{'+(r'\mathrm{'+sub+'}' if len(sub)>1 else sub)+'}'
mathmap.update({'v_y':'v_y','m_b':'m_b','m_p':'m_p','p_b':r'\mathbf{p}_b','p_p':r'\mathbf{p}_p','T_j':'T_j'})
math_re=re.compile('|'.join(re.escape(k) for k in sorted(mathmap,key=len,reverse=True)))
forms={'['+str(r['number'])+']':r'\citep{'+r['key']+'}' for r in refs}
form_re=re.compile('|'.join(re.escape(k) for k in sorted(forms,key=len,reverse=True)))

def plain(text):
 text=re.sub(r'\bNemesis\b','NEMESIS',text)
 out=[];i=0
 while i<len(text):
  m=math_re.match(text,i)
  if m:
   out.append(r'\('+mathmap[m.group()]+r'\)');i=m.end();continue
  c=text[i]
  if c in SUP or c in SUB:
   table=SUP if c in SUP else SUB;j=i+1
   while j<len(text) and text[j] in table:j+=1
   out.append(('\\textsuperscript{' if c in SUP else '\\textsubscript{')+''.join(table[x] for x in text[i:j])+'}');i=j;continue
  out.append(SPECIAL.get(c,c));i+=1
 return ''.join(out)
def inline(text,citations=True):
 parts=[];i=0
 token=re.compile(r'https?://[^\s]+|\*\*.*?\*\*|`[^`]+`|\[[^\]]+\]\([^\s]+\)')
 def part(t):
  if not citations:return plain(t)
  out=[];pos=0
  for m in form_re.finditer(t):
   out.append(plain(t[pos:m.start()]));out.append(forms[m.group()]);counts['citation_commands']+=1;pos=m.end()
  out.append(plain(t[pos:]));return ''.join(out)
 for m in token.finditer(text):
  parts.append(part(text[i:m.start()]));t=m.group()
  if t.startswith('http'):
   u=t.rstrip('.,;');tail=t[len(u):];parts.append(r'\url{'+u+'}'+plain(tail))
  elif t.startswith('**'):parts.append(r'\textbf{'+part(t[2:-2])+'}')
  elif t.startswith('`'):parts.append(r'\texttt{'+plain(t[1:-1])+'}')
  else:
   mm=re.match(r'\[([^\]]+)\]\((.*)\)',t);parts.append(r'\href{'+mm[2]+'}{'+part(mm[1])+'}')
  i=m.end()
 parts.append(part(text[i:]));return ''.join(parts)
canva_pdf=R/'diagrams/canva_complete_native/A3P5_Canva_Final_Figures_Print.pdf'
shutil.copy2(canva_pdf,FIG/'canva_figures.pdf')
preamble=r"""% !TeX program = xelatex
% Complete editable source of the final A3P5 NEMESIS manuscript.
% Compile with XeLaTeX twice, latexmk -xelatex, or Tectonic.
\documentclass[11pt,a4paper]{article}
\usepackage[textwidth=6.8in,top=0.65in,bottom=0.65in,headheight=13pt,headsep=12pt]{geometry}
\usepackage{fontspec}
\setmainfont{texgyretermes-regular.otf}[BoldFont=texgyretermes-bold.otf,ItalicFont=texgyretermes-italic.otf,BoldItalicFont=texgyretermes-bolditalic.otf]
\setsansfont{texgyreheros-regular.otf}[BoldFont=texgyreheros-bold.otf]
\setmonofont{lmmono10-regular.otf}[Scale=MatchLowercase]
\usepackage{amsmath,amssymb,unicode-math}
\setmathfont{texgyretermes-math.otf}
\usepackage{graphicx,xcolor,booktabs,array,longtable,listings}
\usepackage{caption,placeins,needspace,titlesec,fancyhdr,enumitem,float}
\usepackage[numbers,square]{natbib}
\usepackage{xurl}
\usepackage[hidelinks,unicode]{hyperref}
\urlstyle{same}
\hypersetup{pdftitle={TITLE_PLACEHOLDER},pdfauthor={Shafi Bin Sultan; Sabik Bin Sultan; Safwan Sadad}}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt plus 1pt minus 1pt}
\setlength{\emergencystretch}{2em}
\raggedbottom
\widowpenalty=1000
\clubpenalty=1000
\setlength{\textfloatsep}{10pt plus 2pt minus 2pt}
\setlength{\intextsep}{8pt plus 2pt minus 2pt}
\setcounter{topnumber}{4}
\setcounter{bottomnumber}{4}
\setcounter{totalnumber}{6}
\renewcommand{\topfraction}{0.95}
\renewcommand{\bottomfraction}{0.9}
\renewcommand{\textfraction}{0.04}
\renewcommand{\floatpagefraction}{0.8}
\makeatletter
\setlength{\@fptop}{0pt}
\setlength{\@fpsep}{6pt}
\setlength{\@fpbot}{0pt plus 1fil}
\makeatother
\captionsetup{font=small,labelfont=normalfont,labelsep=period,skip=5pt,justification=justified,singlelinecheck=false}
\captionsetup[table]{position=top}
\captionsetup[lstlisting]{justification=raggedright}
\titleformat{\section}{\normalfont\fontsize{13}{15}\selectfont}{\thesection}{0.6em}{}
\titleformat{\subsection}{\normalfont\fontsize{12}{14}\selectfont}{\thesubsection}{0.6em}{}
\titlespacing*{\section}{0pt}{10pt plus 2pt minus 2pt}{5pt}
\titlespacing*{\subsection}{0pt}{8pt plus 2pt minus 2pt}{4pt}
\pagestyle{fancy}
\fancyhf{}
\fancyfoot[C]{\small\thepage}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\setlength{\bibsep}{1.5pt plus 0.5pt}
\renewcommand{\bibfont}{\fontsize{9}{10.7}\selectfont}
\setlist[itemize]{leftmargin=1.5em,itemsep=2pt,topsep=3pt}
\setlength{\LTpre}{6pt}
\setlength{\LTpost}{6pt}
\begin{document}
\thispagestyle{fancy}
\begin{center}
{\fontsize{18.5}{22}\selectfont\bfseries TITLE_PLACEHOLDER\par}
\vspace{7pt}
{\normalsize\bfseries Shafi Bin Sultan\textsuperscript{1}\quad Sabik Bin Sultan\textsuperscript{2}\quad Safwan Sadad\textsuperscript{3}\par}
\vspace{4pt}
{\small\textsuperscript{1}St. Joseph Higher Secondary School\par
\textsuperscript{2}BAF Shaheen College Kurmitola\par
\textsuperscript{3}Greenland Residential School\par}
\vspace{3pt}
{\footnotesize\textsuperscript{1}\href{mailto:shafibinsultan0207@gmail.com}{shafibinsultan0207@gmail.com}\quad
\textsuperscript{2}\href{mailto:sabikbinsultan@gmail.com}{sabikbinsultan@gmail.com}\quad
\textsuperscript{3}\href{mailto:Avoidsafwan@gmail.com}{Avoidsafwan@gmail.com}\par}
\end{center}
"""
preamble=preamble.replace('TITLE_PLACEHOLDER',plain(TITLE))
preamble=preamble.replace(r'\begin{document}',r'\lstset{language=Python,basicstyle=\ttfamily\fontsize{8.5}{10.5}\selectfont,breaklines=true,columns=fullflexible,keepspaces=true,showstringspaces=false,keywordstyle={},commentstyle={},stringstyle={},captionpos=t,aboveskip=6pt,belowskip=7pt}'+'\n'+r'\begin{document}')
body=[];current='';first=True;numref=0
parse_s=re.sub(r'(?m)^(!EQ\[.*\])$',r'\n\1\n',s)
blocks=re.split(r'\n\s*\n',parse_s)
# LaTeX-specific balance, entirely within subsection 4.1: show its small geometry
# table before the tall prototype montage. Every source block is retained once.
photo=next(i for i,b in enumerate(blocks) if b.startswith('!FIG[figures/prototype_views.png'))
table=next(i for i,b in enumerate(blocks) if b.startswith('!TABLE[Geometric quantity|'))
if photo<table:
 block_to_move=blocks.pop(table);blocks.insert(photo,block_to_move)
# Keep the external evaluation comparator inside 10.3, before its metric discussion.
metric_heading=next(i for i,b in enumerate(blocks) if b.startswith('### 10.3.'))
comparator=next(i for i,b in enumerate(blocks) if b.startswith('!FIG[research/licensed_figures/barkjohn2021_fig4.png'))
blocks.insert(metric_heading+1,blocks.pop(comparator))
for block in blocks:
 block=block.strip()
 if not block:continue
 if block=='## References':break
 if block.startswith('# '):continue
 if block.startswith('#'):
  m=re.match(r'(#+)\s+(.*)',block);level=len(m[1]);h=m[2];number=re.match(r'^(\d+(?:\.\d+)*)\.?\s+(.*)',h)
  body.append(r'\FloatBarrier')
  if number:
   current=number[1];cmd='section' if level==2 else 'subsection';counts[cmd+'s']+=1
   if current=='10.3':body.append(r'\Needspace{9\baselineskip}')
   body.append('\\'+cmd+'{'+inline(number[2],False)+'}'+r'\label{sec:'+current+'}')
  else:body.append(r'\section*{'+inline(h,False)+'}');current=h
  audit['headings'].append({'heading':h,'section':current});continue
 if block.startswith('!FIG['):
  path,caption,maxh=block[5:-1].split('|',2);counts['figures']+=1;n=counts['figures'];src=(R/path).resolve();native=manifest['figures'][n-1]
  assert Path(native['path']).resolve()==src
  cm=re.search(r'canva_(\d+)_print\.png$',path)
  if cm:
   asset='figures/canva_figures.pdf';options=f'page={int(cm[1])},'
  else:
   name=f'figure_{n:02d}'+src.suffix.lower();shutil.copy2(src,FIG/name);asset='figures/'+name;options=''
  height=layout.get('height_overrides',{}).get(str(n),native['height_in'])
  width=layout.get('width_overrides',{}).get(str(n),native['width_in'])
  options+=f'width={width:.3f}in,height={height:.3f}in,keepaspectratio'
  placement=layout.get('placements',{}).get(str(n),'!htbp')
  body.extend([r'\begin{figure}['+placement+']',r'\centering',r'\includegraphics['+options+']{'+asset+'}',r'\caption{'+inline(caption)+'}',r'\label{fig:'+str(n)+'}',r'\end{figure}'])
  audit['figures'].append({'number':n,'source':path,'asset':asset,'canva_page':int(cm[1]) if cm else None,'section':current,'width_in':width,'height_in':height});continue
 if block.startswith('!CODE['):
  path,caption=block[6:-1].split('|',1)
  body.extend([r'\par\noindent\begin{minipage}{\linewidth}',r'\begin{lstlisting}[caption={'+inline(caption,False)+r'},label={lst:evaluation}]',(R/path).read_text(encoding='utf8').rstrip(),r'\end{lstlisting}',r'\end{minipage}\par'])
  continue
 if block.startswith('!EQ['):
  eq=block[4:-1];counts['equations']+=1;n=counts['equations'];texeq=eq
  if n in [6,8,18]:texeq=r'\begin{gathered}'+'\n'+eq.replace(r',\qquad',r', \\')+'\n'+r'\end{gathered}'
  if n==17:
   texeq=r'\begin{aligned}(\widehat{\beta}_0,\widehat{\boldsymbol{\beta}})=\arg\min_{\beta_0,\boldsymbol{\beta}}\Bigl[&\sum_{i\in\mathcal{T}}(y_i-\beta_0-\mathbf{z}_i^{\mathsf{T}}\boldsymbol{\beta})^2\\&+\alpha\lVert\boldsymbol{\beta}\rVert_2^2\Bigr].\end{aligned}'
  texeq=texeq.replace(r'\boldsymbol',r'\symbfit')
  body.extend([r'\begin{equation}',r'\label{eq:'+str(n)+'}',texeq,r'\end{equation}'])
  audit['equations'].append({'number':n,'source_latex':eq,'render_latex':texeq,'section':current});continue
 if block.startswith('!TABLE['):
  rows=[row.split('|') for row in block[7:-1].split(';')];nc=len(rows[0]);assert all(len(x)==nc for x in rows)
  counts['tables']+=1;n=counts['tables'];caption=manifest['tables'][n-1]['caption'];weights={3:[.25,.29,.46],4:[.17,.27,.20,.36],5:[.27,.20,.18,.18,.17]}[nc]
  spec=''.join(r'>{\raggedright\arraybackslash}p{\dimexpr '+str(w)+r'\linewidth-2\tabcolsep\relax}' for w in weights)
  head=' & '.join(r'\textbf{'+inline(c)+'}' for c in rows[0])+r' \\'
  body.extend([r'\FloatBarrier',r'\begingroup',r'\fontsize{9.5}{11.2}\selectfont',r'\renewcommand{\arraystretch}{1.16}',r'\setlength{\tabcolsep}{5pt}',r'\begin{longtable}{'+spec+'}',r'\caption{'+inline(caption)+'.'+r'}\label{tab:'+str(n)+r'}\\',r'\toprule',head,r'\midrule',r'\endfirsthead',r'\multicolumn{'+str(nc)+r'}{l}{\small Table \thetable\ continued}\\',r'\toprule',head,r'\midrule',r'\endhead',r'\midrule',r'\multicolumn{'+str(nc)+r'}{r}{\footnotesize Continued on the next page}\\',r'\endfoot',r'\bottomrule',r'\endlastfoot'])
  body.extend(' & '.join(inline(c) for c in row)+r' \\' for row in rows[1:]);body.extend([r'\end{longtable}',r'\endgroup'])
  audit['tables'].append({'number':n,'rows':len(rows)-1,'columns':nc,'section':current,'caption':caption});continue
 if block.startswith('- '):
  body.append(r'\begin{itemize}')
  body.extend(r'\item '+inline(t[2:]) for t in block.splitlines() if t.startswith('- '));body.append(r'\end{itemize}');continue
 if block.startswith('For n held-out observations'):
  body.append(r'\Needspace{12\baselineskip}')
 if block.endswith('Ridge solves'):
  body.append(r'\Needspace{9\baselineskip}')
 body.append(inline(' '.join(block.splitlines())))
 audit['paragraphs'].append({'section':current,'source':block})
bibliography=(OUT/'references_ieee.tex').read_text(encoding='utf8')
body.extend([r'\FloatBarrier',bibliography,r'\end{document}'])
tex=preamble+'\n\n'.join(body)+'\n'
for env in ['equation','longtable','figure','itemize']:
 pattern=re.escape('\\begin{'+env+'}')+r'.*?'+re.escape('\\end{'+env+'}')
 tex=re.sub(pattern,lambda m:re.sub(r'\n[ \t]*\n','\n',m.group()),tex,flags=re.S)
assert counts['figures']==45 and counts['tables']==6 and counts['equations']==18
assert '!FIG[' not in tex and '!EQ[' not in tex and '!TABLE[' not in tex
(OUT/'A3P5_NEMESIS_Research_Manuscript.tex').write_text(tex,encoding='utf8')
audit['counts']=counts;audit['bibliography_entries']=len(refs);audit['main_tex_sha256']=hashlib.sha256(tex.encode()).hexdigest()
(OUT/'conversion_manifest.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'counts':counts,'bibliography_entries':len(refs),'assets':len(list(FIG.iterdir())),'tex_bytes':len(tex.encode())},indent=2))
