#!/usr/bin/env Rscript

library("optparse")
parser <- OptionParser()
parser <- add_option(parser, c("-c", "--control"), action="store", help="Control file")
parser <- add_option(parser, c("--controlName"), action="store", help="Control name")
parser <- add_option(parser, c("-s", "--sample"), action="store", help="Sample file")
parser <- add_option(parser, c("--sampleName"), action="store", help="Sample name")
parser <- add_option(parser, c("-d", "--databaseFolder"), action="store", help="Database folder")
parser <- add_option(parser, c("-o", "--output"), action="store", help="Output html file")
opts<-parse_args(parser, commandArgs(trailing=TRUE))

check_file<-function(fileName){
  if (!file.exists(fileName)){
    stop(paste0("File not exists : ", fileName))
  }
}

check_file(opts$control)
check_file(opts$sample)
check_file(opts$databaseFolder)

args<-commandArgs(trailing=FALSE)
scriptFile=args[grepl("--file=", args)]
scriptFile<-gsub("--file=","",scriptFile)
scriptFile<-normalizePath(scriptFile)
rmdFile<-gsub(".R$", ".Rmd", scriptFile)

outputFile<-normalizePath(opts$output, mustWork = FALSE)
output_dir = dirname(outputFile)

outputFileRmd<-gsub(".[^.]*$", ".Rmd", outputFile)

cat("Copy rmd file to ", outputFileRmd, "\n")

file.copy(rmdFile, outputFileRmd, overwrite=T )

options<-list(control = normalizePath(opts$control),
              controlName = opts$controlName,
              sample = normalizePath(opts$sample),
              sampleName = opts$sampleName,
              databaseFolder = normalizePath(opts$databaseFolder))

optionDf<-data.frame("Key"=c("control", "controlName", "sample", "sampleName", "databaseFolder"),
                     "Value"=c(normalizePath(opts$control),opts$controlName, normalizePath(opts$sample), opts$sampleName, normalizePath(opts$databaseFolder)))

optionFile<-paste0(output_dir, "/fileList1.txt")

cat("Write options to ", optionFile, "\n")

write.table(optionDf, file=optionFile, sep="\t", row.names=F)

library(rmarkdown)

cat("Output report to:", outputFile, "\n")
rmarkdown::render(outputFileRmd, output_dir = output_dir)

