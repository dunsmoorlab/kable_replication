require(lme4)
require(lmerTest)
require(emmeans)
require(dplyr)
afex::set_sum_contrasts()

setwd('/Users/ach3377/Documents/kable_replication')
df <- read.csv('Exp_2_data.csv')

#im not sure the following is necessary as just including factor(phase) uses 4 as the reference, which is what we want
df$phase <- as.factor(df$phase)
df$phase <- relevel(df$phase, ref = "4")

df <- df %>% 
    mutate(condition = recode(condition, 
                    "CS-" = 0, 
                    "CS+" = 1))

mod <- glmer(Low_and_High ~ condition*factor(phase)+(1|subject), family="binomial", data=df)
summary(mod)

emmeans(mod,pairwise ~ condition,adjust="None")
