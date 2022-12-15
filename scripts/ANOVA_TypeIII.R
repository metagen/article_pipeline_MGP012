#!/usr/bin/env Rscript

# preprocess
# need for car install
#! brew install cmake
# 前準備
# Do you want to install from sources the packages which need compilation? (Yes/no/cancel) => No にしたら行けた
# install.packages("car")

# initializePtr() でエラー: 
# 関数 'Rcpp_precious_remove' はパッケージ 'Rcpp' では提供されていません 
# => Reinstall Rcpp
# install.packages('Rcpp')

library(car)
library(lme4)
library(Rcpp)

### ファイル読み込み
setwd("/Users/nsmt/Desktop/metagen_docker/DockerGalaxy/data_root/Statistics/MGP012/220807_ReAnalysis")
df_me <- read.csv("./data_input/me.all_tp.tsv", sep="\t", header=T, row.names=1)
df_nm <- read.csv("./data_input/nm.all_tp.tsv", sep="\t", header=T, row.names=1)

df_me <- as.data.frame(t(df_me))
df_nm <- as.data.frame(t(df_nm))
IgA <- as.double(df_nm$IgA)
IgA_rank <- rank(as.double(df_nm$IgA))
group <- as.factor(df_me$group)
timepoint <- as.factor(df_me$timepoint)
subject_id <- as.factor(df_me$subject_id)
df_concat = data.frame(IgA, IgA_rank, group, timepoint, subject_id)

# result_lm_rawIgA = lm(
#   IgA ~ group*timepoint,
#   df_concat,
#   contrasts=list(group="contr.sum", timepoint="contr.sum")
# )
# result_anova_raw = Anova(result_lm_rawIgA, type="III")
# result_anova_raw

# result_lm_rankIgA = lm(
#   IgA_rank ~ group*timepoint,
#   df_concat,
#   contrasts=list(group="contr.sum", timepoint="contr.sum")
# )
# result_anova_rank = Anova(result_lm_rankIgA, type="III")
# result_anova_rank

result_lm2_rankIgA = lmer(
  IgA_rank ~ group*timepoint+(1|subject_id),
  df_concat,
  contrasts=list(group="contr.sum", timepoint="contr.sum", subject_id="contr.sum")
)
result_anova_rank = Anova(result_lm2_rankIgA, type="III")
write.csv(result_anova_rank, "result_anova_typeIII_rankIgA.tsv", sep="\t", quote=F)
