import os
import pandas as pd
import pingouin as pg
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import Patch
'''settings'''
sns.set_context('notebook',font_scale=1.4)
sns.set_style('ticks', {'axes.spines.right':False, 'axes.spines.top':False})
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = 'Arial'
rcParams['savefig.dpi'] = 300
cpal = ['darkorange','grey']

'''experiment 2 (1B)'''
experiment = 'Exp_1B'

dfs = {}
for file in os.listdir(experiment):
    if 'phase_4' in file and '.csv' in file:
        sub = int(file.split('_phase')[0].split('vp_')[1])
        csp = 'animal' if 'animals' in file else 'tool'
        dfs[sub] = pd.read_csv(f'{experiment}/{file}')
        dfs[sub]['subject'] = sub
        dfs[sub]['condition'] = dfs[sub]['object'].apply(lambda x: 'CS+' if x == csp else 'CS-')
df = pd.concat(dfs.values())
df.to_csv(f'{experiment}_data.csv')

df['low_hit'] = df.buttonPressedCertainty.apply(lambda x: 1 if x in [1,2] else 0)
df['high_hit'] = df.buttonPressedCertainty.apply(lambda x: 1 if x == 1 else 0)

avg = df.groupby(['phase','condition','subject'])[['low_hit','high_hit']].mean()
hr = avg.loc[([1,2,3]),].reset_index().set_index(['subject','condition','phase']).sort_index()
fa = avg.loc[(4),].reset_index().set_index(['subject','condition']).sort_index()

cr = (hr - fa).reset_index().set_index(['phase','condition','subject']).sort_index()

fig, ax = plt.subplots(1,2,sharey=True)
for c, conf in enumerate(['low_hit','high_hit']):
    sns.barplot(data=cr.reset_index(),x='phase',y=conf,hue='condition',palette=cpal,ax=ax[c])
    sns.stripplot(data=cr.reset_index(),x='phase',y=conf,hue='condition',dodge=True,color='black',ax=ax[c],alpha=.25)
    legend_elements = [Patch(facecolor=cpal[0],edgecolor=None,label='CS+'),
                       Patch(facecolor=cpal[1],edgecolor=None,label='CS-')]
    ax[c].legend(handles=legend_elements,loc='upper right',bbox_to_anchor=(1,1),frameon=False)
    ax[c].set_xticklabels(['Pre','Conditioning','Post'])
    ax[c].set_ylabel('Corrected recognition')
    ax[c].set_title(f'{conf.split("_")[0]} confidence')

    print(pg.ttest(cr.loc[(1,'CS+'),conf], cr.loc[(1,'CS-'),conf],paired=True))
    print(pg.wilcoxon(cr.loc[(1,'CS+'),conf], cr.loc[(1,'CS-'),conf]))








