from config import *

for exp in [2,3,4]:
    for conf in ['Low_and_High','High']:
        df = pd.read_csv(f'stats/Exp_{exp}_{conf}_MLM_stats.csv'
             ).rename(columns={'Unnamed: 0':'Effect','Pr(>|z|)':'p-val'})[['Effect','Estimate','z value','p-val']].loc[([5,7,6]),]
        df['sig'] = df['p-val'].apply(p_convert)
        pg.print_table(df,floatfmt=".2e",tablefmt="github")

    print('press enter to go to next experiment')
    input()

