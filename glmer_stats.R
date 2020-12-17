require(lme4)
require(lmerTest)
require(dplyr)

setwd('/Users/ach3377/Documents/kable_replication')
df <- read.csv('Exp_4_data.csv')

df <- df %>% 
    mutate(condition = recode(condition, 
                    "CS-" = "0", 
                    "CS+" = "1"),
            phase = recode(phase,
                     "1" = "one",
                     "2" = "two",
                     "3" = "three",
                     "4" = "four"))

low_and_high <- glmer(Low_and_High ~ condition*phase + (1|subject) + (1|filename), family="binomial", data=df)
low_and_high.summ <- summary(low_and_high)
write.csv(low_and_high.summ$coefficients,'stats/Exp_4_Low_and_High_MLM_stats.csv')

high <- glmer(High ~ condition*phase + (1|subject) + (1|filename), family="binomial", data=df)
high.summary <- summary(high)
write.csv(high.summary$coefficients,'stats/Exp_4_High_MLM_stats.csv')
