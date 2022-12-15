#!/bin/bash
set -eu

# environment
dd="data_input"
di="data_inter"
st2="scripts"

# python, scipy, statsmodels, sklearn, seaborn
mkdir -p data_output
bash scripts/export_env.sh

# raw
me_base="me.tsv"
ge_base="ge.tsv"
ra_base="ra.tsv"
co_base="co.tsv"
nm_base="nm.tsv"
wu_base="wu.tsv"
uu_base="uu.tsv"

me="$dd/$me_base"
ge="$dd/$ge_base"
ra="$dd/$ra_base"
co="$dd/$co_base"
nm="$dd/$nm_base"
wu="$dd/$wu_base"
uu="$dd/$uu_base"

# inter
ra25="$dd/ra.25.tsv"
ge0001="$dd/genus.0.001.tsv"

ad_diff="$dd/ad.diff.tsv"
me_diff="$dd/me.diff.tsv"
ge0001_diff="$dd/ge.0.001.diff.tsv"
ra25_diff="$dd/ra.25.diff.tsv"
nm_diff="$dd/nm.diff.tsv"

# config_color
colors=("C_0w:#6ca39a" "C_4w:#2e7c70" "T_0w:#c25d67" "T_4w:#a91826")
cref="data_config/cref.tsv"
cref_gt="data_config/cref_gt.tsv" # group_timepoint
cref_ge="/data_root/RefFiles/colorcodes/metagen_color_list_genus.tsv"
cref_co="/data_root/RefFiles/colorcodes/metagen_color_list_compound.tsv"

# echo "## Step0: 前処理"
python $st2/preprocess_filtering.py $ge -m mean -c 0.001 -o $ge0001
python $st2/preprocess_filtering.py $ra -m freq -c 0.25 -o $ra25
python $st2/calc_samesubject_diff.py $ge0001 $me -mk timepoint -mv1 "0w" -mv2 "4w" -o1 $ge0001_diff -o2 $me_diff
python $st2/calc_samesubject_diff.py $ra25 $me -mk timepoint -mv1 "0w" -mv2 "4w" -o1 $ra25_diff -o2 $me_diff
python $st2/calc_samesubject_diff.py $nm $me -mk timepoint -mv1 "0w" -mv2 "4w" -o1 $nm_diff -o2 $me_diff

# レスポンダーとタイムポイント内の検定用
for i in $ge $co $ge0001 $ra25 $nm; do
for g in "C" "T"; do
python $st2/preprocess_extract.py $i $me -mk group -mv $g -o1 $i.$g.tsv -o2 $me.$g.tsv
done
done

# echo "## Step1_2: PCoA"
do="data_output/pcoa"; mkdir -p $do
python $st2/calc_distance_matrix.py $co -o $co.bc.tsv -m braycurtis
python $st2/draw_mds.py $uu $me -o "$do/$uu_base.mds.del_label.pdf" -ot "$do/$uu_base.mds.del_label.tsv" -mk group_timepoint -c $cref_gt --del_label --hidden_legend
python $st2/draw_mds.py $wu $me -o "$do/$wu_base.mds.del_label.pdf" -ot "$do/$wu_base.mds.del_label.tsv" -mk group_timepoint -c $cref_gt --del_label --hidden_legend
python $st2/draw_mds.py $co.bc.tsv $me -o "$do/co.bc.mds.pdf"       -ot "$do/co.bc.mds.del_label.tsv" -mk group_timepoint -c $cref_gt --del_label --hidden_legend

do="data_output/dist_boxplot"; mkdir -p $do
python $st2/calc_samesubject_diff_distance_matrix.py $uu $me -ot $do/uu.dist.tsv -op $do/uu.dist.box.pdf -mk1 "timepoint" -mv1 "0w" "4w" -mk2 "group" -mv2 "C" "T" -c "#2e7c70" "#a91826"
python $st2/calc_samesubject_diff_distance_matrix.py $wu $me -ot $do/wu.dist.tsv -op $do/wu.dist.box.pdf -mk1 "timepoint" -mv1 "0w" "4w" -mk2 "group" -mv2 "C" "T" -c "#2e7c70" "#a91826"
python $st2/calc_samesubject_diff_distance_matrix.py $co.bc.tsv $me -ot $do/co.bc.dist.tsv -op $do/co.bc.dist.box.pdf -mk1 "timepoint" -mv1 "0w" "4w" -mk2 "group" -mv2 "C" "T" -c "#2e7c70" "#a91826"

do="data_output/htest"; mkdir -p $do
for i in $ge0001_diff $ra25_diff $nm_diff; do
  path_base=$(basename $i)
  python $st2/calc_htest_2group.py $i $me_diff -mk group -mv1 "C" -mv2 "T" -o $do/$path_base.htest.C.T.tsv
done

# tp間検定
do="data_output/htest_tp"
mkdir -p $do
for i in $ge0001 $ra25 $nm; do
  for g in "C" "T"; do
    path_base=$(basename $i)
    python $st2/calc_htest_2group.py $i.$g.tsv $me.$g.tsv -mk timepoint -mv1 "0w" -mv2 "4w" -o $do/$path_base.htest.0w.4w.$g.tsv --paired
  done
done

# echo "## Step6: レスポンダー"
do="data_output/responder"
mkdir -p $do
dk="IgA"
for g in "C" "T"; do
  python $st2/calc_responder_analysis_parallel.py $ge0001.$g.tsv $ra25.$g.tsv $nm.$g.tsv $me.$g.tsv \
  -o "$do/table.responder.$g.1.$dk" -dk "$dk" -mk timepoint -mv "0w" "4w" -p 1
done

# after revise
do="data_output/volcano"
mkdir -p $do
for i in $ge0001_diff $ra25_diff; do
  path_base=$(basename $i)
  python $st2/draw_volcanoplot.py $i $me_diff -mk group -mv1 "C" -mv2 "T" \
  -o $do/$path_base.volcano.C.T.pdf \
  -o2 $do/$path_base.volcano.C.T.annot.pdf \
  -ot $do/$path_base.volcano.C.T.tsv
done

for i in $ge0001 $ra25; do
  for g in "C" "T"; do
    path_base=$(basename $i)
    python $st2/draw_volcanoplot.py $i.$g.tsv $me.$g.tsv -mk timepoint -mv1 "0w" -mv2 "4w" --paired --adjust_text \
    -o  $do/$path_base.volcano.0w.4w.$g.pdf \
    -o2 $do/$path_base.volcano.0w.4w.$g.annot.pdf \
    -ot $do/$path_base.volcano.0w.4w.$g.tsv 
  done
done

# Rscripts
Rscript $st2/calc_effsize.R
Rscript $st2/ANOVA_TypeIII_Paired2.R
Rscript $st2/PERMANOVA_adjusted_confounding_factor.R
