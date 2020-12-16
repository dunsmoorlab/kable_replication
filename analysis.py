from config import *

for exp in [2,3,4]:
    experiment = f'Exp_{exp}'

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

    #score each trial based on either high or low confidence
    df['Low_hit'] = df.buttonPressedCertainty.apply(lambda x: 1 if x in [1,2] else 0)
    df['High_hit'] = df.buttonPressedCertainty.apply(lambda x: 1 if x == 1 else 0)

    avg = df.groupby(['phase','condition','subject'])[['Low_hit','High_hit']].mean()
    hr = avg.loc[([1,2,3]),].reset_index().set_index(['subject','condition','phase']).sort_index() #hit rate is rate of "old" responses for old items
    fa = avg.loc[(4),].reset_index().set_index(['subject','condition']).sort_index() #false alarm rate is rate of "old" responses for new items

    cr = (hr - fa).reset_index().set_index(['condition','subject']).sort_index() #corrected recognition is hit rate - false alarm rate

    #for the legend
    legend_elements = [Patch(facecolor=cpal[0],edgecolor=None,label='CS+'),
                       Patch(facecolor=cpal[1],edgecolor=None,label='CS-')]

    fig, ax = plt.subplots(1,2,sharey=True,figsize=(10,5))
    for c, conf in enumerate(['Low_hit','High_hit']):
        conf_str = conf.split("_")[0]
        sns.barplot(data=cr.reset_index(),x='phase',y=conf,hue='condition',palette=cpal,ax=ax[c],saturation=1)
        sns.stripplot(data=cr.reset_index(),x='phase',y=conf,hue='condition',dodge=True,color='black',ax=ax[c],alpha=.25)

        ax[c].legend(handles=legend_elements,loc='upper right',bbox_to_anchor=(1,1),frameon=False)
        ax[c].set_xticklabels(['Pre','Conditioning','Post'])
        ax[c].set_ylabel('Corrected recognition') if c == 0 else ax[c].set_ylabel('')
        ax[c].set_title(f'{conf_str} confidence')

        anova = pg.rm_anova(data=cr.reset_index(),dv=conf,within=['phase','condition'],subject='subject')[['Source','ddof1','ddof2','F','p-unc','np2']]
        print(f'{conf_str} confidence corrected recognition repeated measures ANOVA')
        print(anova)
        anova.to_csv(f'stats/{experiment}_{conf_str}_confidence_anova_stats.csv',index=False)

        stats = cr.groupby('phase').apply(lambda x: pg.ttest(x.loc[('CS+'),conf], x.loc[('CS-'),conf],paired=True))
        stats['sig'] = stats['p-val'].apply(p_convert)
        print(f'{conf_str} confidence corrected recognition CS+ vs. CS- ttests')
        stats = stats[['T','dof','tail','p-val','cohen-d','BF10','sig']]
        print(stats)
        stats.to_csv(f'stats/{experiment}_{conf_str}_confidence_ttest_stats.csv',index=True)

        upper = [line.get_ydata().max() for line in ax[c].lines]
        ylim = ax[c].get_ylim()

        for p, phase in enumerate([1,2,3]):
            star = stats.loc[phase,'sig'].values[0]
            if len(star) > 0: paired_barplot_annotate_brackets(star,p,(upper[p+0],upper[p+3]),ylim,barh=.025,ax=ax[c])

    plt.suptitle(f'Experiment {experiment.split("_")[-1]}')
    plt.tight_layout()
    plt.savefig(f'figures/{experiment}_results.png')
