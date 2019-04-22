#sudo apt-get update && sudo apt-get install pandoc
#Run this code with:
#Rscript  --vanilla --slave cmpr2in.R H3K9me3.bed H3K27ac.bed


#setwd("/home/yaguo/genome_annotation/R_compare")
library(rmarkdown)
args <- commandArgs(T)
#print(args)
#args=c("H3K9me3.bed","H3K27ac.bed")
render("R_comp_hui.Rmd")
