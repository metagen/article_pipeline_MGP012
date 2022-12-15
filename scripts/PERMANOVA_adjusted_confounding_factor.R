#!/usr/bin/env Rscript
# ライブラリのインストール
# install.packages("vegan")
library("vegan")

# def main():
setwd("/Users/nsmt/Desktop/metagen_docker/DockerGalaxy/data_root/Statistics/MGP012/220807_ReAnalysis")
df_co <- read.csv("./data_input/co.tsv", sep="\t", header=T, row.names=1)
df_wu <- read.csv("./data_input/wu.tsv", sep="\t", header=T, row.names=1)
df_me <- read.csv("./data_input/me.tsv", sep="\t", header=T, row.names=1)

df_co_t = as.data.frame(t(df_co))
df_me_t = t(df_me)
df_me_t = as.data.frame(df_me_t)

# 交絡因子はSex & Age
wu_out = adonis2(df_wu ~ timepoint*group+subject_id+sex+age, data=df_me_t)
co_out = adonis2(df_co_t ~ timepoint*group+subject_id+sex+age, data=df_me_t)

write.csv(as.data.frame(wu_out), "data_output/pcoa/wu.permanova.csv", quote=F)
write.csv(as.data.frame(co_out), "data_output/pcoa/co.permanova.csv", quote=F)
