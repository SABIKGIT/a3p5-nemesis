from pathlib import Path
import sys,json,csv
from collections import Counter
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'python_packages'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
OUT=ROOT.parent/'figures';OUT.mkdir(exist_ok=True)
S=json.loads((ROOT/'census_summary.json').read_text(encoding='utf-8'))
A=json.loads((ROOT/'bibliography_all.json').read_text(encoding='utf-8'))
C=json.loads((ROOT/'metadata_candidates.json').read_text(encoding='utf-8'))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':11,'axes.labelsize':9,'xtick.labelsize':8,'ytick.labelsize':9,'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white','figure.facecolor':'white'})
NAVY='#17334D';TEAL='#267D88';PALE='#EAF3F4';GRAY='#68747C';LIGHT='#E7EBEE';AMBER='#A5622D'
fig=plt.figure(figsize=(12.2,5.55),layout='constrained')
gs=fig.add_gridspec(1,2,width_ratios=[1,1.12],wspace=.06)
ax=fig.add_subplot(gs[0,0]);ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
ax.set_title('(a)  Metadata retrieval and screening',loc='left',fontweight='bold',color=NAVY,pad=15)
def box(x,y,w,h,label,main=True):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.008,rounding_size=0.012',facecolor=PALE if main else '#FAF7F3',edgecolor=TEAL if main else '#CDBCA9',lw=1.1))
 ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=9.1 if main else 8.1,color=NAVY if main else '#70543A',linespacing=1.45)
def arrow(x1,y1,x2,y2,color=TEAL):ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='-|>',color=color,lw=1.05,mutation_scale=9))
x=.025;w=.53;h=.12;ys=[.83,.655,.48,.305,.13]
labels=['10 thematic queries\n500 records per query','Retrieved occurrences\n'+r'$\bf{n = 5,000}$','Distinct DOI records screened\n'+r'$\bf{n = 4,897}$','Metadata candidates\n'+r'$\bf{n = 1,212}$','Suggested next reads\n'+r'$\bf{n = 150}$']
for y,l in zip(ys,labels):box(x,y,w,h,l)
for y1,y2 in zip(ys[:-1],ys[1:]):arrow(x+w/2,y1,x+w/2,y2+h)
branch=[(.7425,'Repeated DOI\noccurrences removed\n'+r'$\bf{n = 103}$'),(.5675,'Not prioritized by\nmetadata rule\n'+r'$\bf{n = 3,685}$'),(.3925,'Candidates outside\nreading shortlist\n'+r'$\bf{n = 1,062}$')]
# Branches originate at the corresponding downstream screening operation.
for y,lab in branch:
 box(.66,y-.075,.31,.15,lab,False);arrow(.555,y,.65,y,AMBER)
ax.text(.025,.035,'Titles and available abstracts screened.\nNo full-text eligibility assessment in this census.',color=GRAY,fontsize=8.5,va='bottom')
bx=fig.add_subplot(gs[0,1]);bx.set_title('(b)  Primary topics of metadata candidates',loc='left',fontweight='bold',color=NAVY,pad=15)
labels={'particulate_air_quality':'Particulate matter / air quality','water_quality_monitoring':'Water-quality monitoring','gas_olfaction_mapping':'Gas / olfaction mapping','four_wheel_steering':'Four-wheel steering','outdoor_navigation_fusion':'Outdoor navigation / sensor fusion','robotic_environmental_monitoring':'Robotic environmental monitoring','embedded_environmental_sensing':'Embedded environmental sensing','gas_sensor_calibration':'Gas-sensor calibration','robotic_sampling':'Robotic sampling'}
cnt=Counter(r['primary_topic'] for r in C);items=sorted(cnt.items(),key=lambda kv:-kv[1]);y=np.arange(len(items))
bx.barh(y,[v for k,v in items],color=TEAL,height=.6)
bx.set_yticks(y,[labels[k] for k,v in items]);bx.invert_yaxis();bx.set_xlabel('Distinct DOI records');bx.set_xlim(0,440)
bx.set_xticks([0,100,200,300,400]);bx.grid(axis='x',alpha=.25,lw=.6);bx.set_axisbelow(True);bx.spines['left'].set_visible(False);bx.tick_params(axis='y',length=0)
for i,(k,v) in enumerate(items):bx.text(v+7,i,f'{v:,}',va='center',fontsize=9,color=NAVY)
bx.text(.99,.015,'Mutually exclusive primary topics; total n = 1,212.',transform=bx.transAxes,ha='right',va='bottom',fontsize=8,color=GRAY)
for ext in ['png','svg','pdf']:fig.savefig(OUT/f'Fig_L1_metadata_census.{ext}',dpi=360,bbox_inches='tight')
plt.close(fig)
# Supplemental year/abstract coverage plot; this is a ranked sample, not a field-wide time trend.
years=list(range(1990,2027));total=Counter(r['year'] for r in A);ab=Counter(r['year'] for r in A if r['has_abstract']);without=[total[y]-ab[y] for y in years]
fig,axs=plt.subplots(1,2,figsize=(12.2,4.25),layout='constrained',gridspec_kw={'width_ratios':[1.35,1]})
a,b=axs
x=np.array(years)
a.bar(x,without,color=LIGHT,width=.8,label='No abstract in metadata',edgecolor='white',linewidth=.3)
a.bar(x,[ab[y] for y in years],bottom=without,color=TEAL,width=.8,label='Abstract available',edgecolor='white',linewidth=.3)
a.set_title('(a)  Retrieved records by publication year',loc='left',fontweight='bold',color=NAVY)
a.set_xlabel('Publication year');a.set_ylabel('Distinct DOI records');a.set_xticks(range(1990,2027,4));a.set_xlim(1989.3,2026.8);a.grid(axis='y',alpha=.25,lw=.6);a.set_axisbelow(True);a.legend(frameon=False,fontsize=8,loc='upper left')
coverage=[100*ab[y]/total[y] if total[y] else np.nan for y in years]
b.plot(years,coverage,color=TEAL,lw=1.7,marker='o',ms=3.5)
b.axhline(100*S['records_with_abstract']/len(A),ls='--',lw=1,color=AMBER,label=f"Overall: {100*S['records_with_abstract']/len(A):.1f}%")
b.set_title('(b)  Abstract availability within each year',loc='left',fontweight='bold',color=NAVY)
b.set_ylabel('Records with abstracts (%)');b.set_xlabel('Publication year');b.set_xticks(range(1990,2027,6));b.set_xlim(1989.3,2026.8);b.set_ylim(0,100);b.grid(axis='y',alpha=.25,lw=.6);b.legend(frameon=False,fontsize=8)
fig.supxlabel('Crossref relevance-ranked sample; 2026 includes records through 15 September. Counts do not measure field-wide publication activity.',fontsize=8,color=GRAY)
for ext in ['png','svg','pdf']:fig.savefig(OUT/f'Fig_L2_metadata_abstract_coverage.{ext}',dpi=360,bbox_inches='tight')
plt.close(fig)
with (ROOT/'abstract_coverage_by_year.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['year','unique_records','with_abstract','without_abstract','abstract_coverage_percent']);w.writeheader();w.writerows([{'year':y,'unique_records':total[y],'with_abstract':ab[y],'without_abstract':total[y]-ab[y],'abstract_coverage_percent':100*ab[y]/total[y] if total[y] else ''} for y in years])
captions={'Fig_L1_metadata_census':'Exploratory literature-metadata census. (a) Ten relevance-ranked Crossref queries returned 5,000 occurrences; DOI deduplication retained 4,897 records. The documented title/available-abstract rule identified 1,212 metadata candidates and a 150-record reading shortlist. (b) Each candidate is assigned one primary topic; counts therefore sum to 1,212. The census is not a full-text systematic review, and its query caps and ranking limit interpretation to the retrieved sample.','Fig_L2_metadata_abstract_coverage':'Metadata availability in the retrieved Crossref sample. (a) Publication-year counts partitioned by abstract availability. (b) Within-year abstract coverage, with overall coverage of 26.4% marked. Publication date filtering ends on 15 September 2026. Unequal coverage, ranked retrieval, and the incomplete 2026 year preclude field-wide growth or prevalence claims.'}
(ROOT/'literature_figure_captions.json').write_text(json.dumps(captions,indent=2),encoding='utf-8')
print('Saved two publication figures as PNG, SVG and PDF, plus exact plot data and captions.')
