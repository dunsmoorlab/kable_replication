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

    #score each trial based on either high or low confidence
    df['Low_and_High'] = df.buttonPressedCertainty.apply(lambda x: 1 if x in [1,2] else 0)
    df['High'] = df.buttonPressedCertainty.apply(lambda x: 1 if x in [1] else 0)
    
    df.to_csv(f'{experiment}_data.csv') #save data out here after minimal processing

    avg = df.groupby(['phase','condition','subject'])[['Low_and_High','High']].mean() 
    hr = avg.loc[([1,2,3]),].reset_index().set_index(['subject','condition','phase']).sort_index() #hit rate is rate of "old" responses for old items
    fa = avg.loc[(4),].reset_index().set_index(['subject','condition']).sort_index() #false alarm rate is rate of "old" responses for new items

    cr = (hr - fa).reset_index().set_index(['condition','subject']).sort_index() #corrected recognition is hit rate - false alarm rate

    '''normality check for both'''
    normality = pg.normality(cr).loc[['Low_and_High','High']].reset_index().rename(columns={'index':'confidence'})
    pg.print_table(normality,floatfmt=".2e",tablefmt="github")
    normality.to_csv(f'stats/{experiment}_normality_check.csv')

    fig, ax = plt.subplots(1,2,sharey=True,figsize=(10,5))
    for c, conf in enumerate(['Low_and_High','High']):
        '''plot the data'''
        conf_str = conf.replace('_',' ')
        sns.barplot(data=cr.reset_index(),x='phase',y=conf,hue='condition',palette=cpal,ax=ax[c],saturation=1)
        sns.stripplot(data=cr.reset_index(),x='phase',y=conf,hue='condition',dodge=True,color='black',ax=ax[c],alpha=.25)

        '''label axes and add titles'''
        ax[c].legend(handles=legend_elements,loc='upper right',bbox_to_anchor=(1,1),frameon=False)
        ax[c].set_xticklabels(['Pre','Conditioning','Post'])
        ax[c].set_ylabel('Corrected recognition') if c == 0 else ax[c].set_ylabel('')
        ax[c].set_title(f'{conf_str} confidence')

        '''run the anova stats, print the table, and save the results'''
        anova = pg.rm_anova(data=cr.reset_index(),dv=conf,within=['phase','condition'],subject='subject')[['Source','ddof1','ddof2','F','p-unc','np2']]
        print(f'{conf_str} confidence corrected recognition repeated measures ANOVA')
        anova['sig'] = anova['p-unc'].apply(p_convert)
        pg.print_table(anova,floatfmt=".2e",tablefmt="github")
        anova.to_csv(f'stats/{experiment}_{conf}_confidence_anova_stats.csv',index=False)

        '''run the t-tests, print the table, and save the results'''
        tstats = cr.groupby('phase').apply(lambda x: pg.ttest(x.loc[('CS+'),conf], x.loc[('CS-'),conf],paired=True))
        tstats['sig'] = tstats['p-val'].apply(p_convert)
        print(f'{conf_str} confidence corrected recognition CS+ vs. CS- ttests')
        tstats = tstats[['T','dof','tail','p-val','cohen-d','BF10','sig']]
        tstats['BF10'] = tstats['BF10'].astype(float) * 2 #need to multiple the BF10 by 2 to match the one-sided values used in the paper
        pg.print_table(tstats.reset_index().drop(columns='level_1'),floatfmt='.2e',tablefmt='github')
        tstats.to_csv(f'stats/{experiment}_{conf}_confidence_ttest_stats.csv',index=True)

        '''these lines add the significance markers to the plot'''
        upper = [line.get_ydata().max() for line in ax[c].lines]
        ylim = ax[c].get_ylim()
        for p, phase in enumerate([1,2,3]):
            star = tstats.loc[phase,'sig'].values[0]
            if len(star) > 0: paired_barplot_annotate_brackets(star,p,(upper[p+0],upper[p+3]),ylim,barh=.025,ax=ax[c])

        '''since high confidence CR is non-normally distributed, we also look at wilcoxon signed-rank test'''
        if conf == 'High':
            wstats = cr.groupby('phase').apply(lambda x: pg.wilcoxon(x.loc[('CS+'),conf], x.loc[('CS-'),conf]))
            wstats['sig'] = wstats['p-val'].apply(p_convert)
            wstats = wstats.reset_index().rename(columns={'level_1':'test'})[['phase','test','p-val','CLES','sig']]
            pg.print_table(wstats,floatfmt='.2e',tablefmt='github')

    plt.suptitle(f'Experiment {experiment.split("_")[-1]}')
    plt.tight_layout()
    plt.savefig(f'figures/{experiment}_results.png')
    
    print('press a key to continue to outlier detection')
    input()
    
    '''next we look at boxplot of the CS+ vs. CS- difference in each phase to identify outliers'''
    diff = cr.reset_index().set_index(['condition','phase','subject']).sort_index() #corrected recognition is hit rate - false alarm rate
    diff = diff.loc['CS+'] - diff.loc['CS-']

    cr = cr.reset_index().set_index(['phase','condition','subject']).sort_index()
    fig, ax = plt.subplots(1,2,sharey=True,figsize=(10,5))
    for c, conf in enumerate(['Low_and_High','High']):
        conf_str = conf.replace('_',' ')
        sns.boxplot(data=diff.reset_index(),x='phase',y=conf,color='grey',ax=ax[c],saturation=1)
        # sns.stripplot(data=cr.reset_index(),x='phase',y=conf,hue='condition',dodge=True,color='black',ax=ax[c],alpha=.25)
        ax[c].set_xticklabels(['Pre','Conditioning','Post'])
        ax[c].set_ylabel('Corrected recognition\nCS+ - CS-') if c == 0 else ax[c].set_ylabel('')
        ax[c].set_title(f'{conf_str} confidence')

        '''get the subject number and phase of each outlier'''
        outliers = {phase:identify_outliers(diff.loc[phase,conf]) for phase in [1,2,3]}
        tstats = {}
        for phase in [1,2,3]:
            if len(outliers[phase]) > 0:
                tstats[phase] = pg.ttest(cr.drop(outliers[phase],level='subject').loc[(phase,'CS+'),conf], cr.drop(outliers[phase],level='subject').loc[(phase,'CS-'),conf], paired=True)
            else:
                tstats[phase] = pg.ttest(cr.loc[(phase,'CS+'),conf], cr.loc[(phase,'CS-'),conf], paired=True)
            tstats[phase]['phase'] = phase
        tstats = pd.concat(tstats.values()).reset_index()[['phase','T','dof','tail','p-val','cohen-d','BF10']]
        tstats['sig'] = tstats['p-val'].apply(p_convert)
        tstats['BF10'] = tstats['BF10'].astype(float) * 2 # paper uses 1-sided BF10 values
        print(f'{conf_str} confidence corrected recognition CS+ vs. CS- ttests without outliers')
        pg.print_table(tstats,floatfmt='.2e',tablefmt='github')
        tstats.to_csv(f'stats/{experiment}_{conf}_confidence_no_outliers_ttest_stats.csv',index=True)

    plt.suptitle(f'Experiment {experiment.split("_")[-1]}')
    plt.tight_layout()
    plt.savefig(f'figures/{experiment}_diff_boxplot.png')



    print('press a key to continue to the next experiment')
    input()