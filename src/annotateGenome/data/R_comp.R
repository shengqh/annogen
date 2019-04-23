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

options<-list(control = normalizePath(opts$control),
              controlName = opts$controlName,
              sample = normalizePath(opts$sample),
              sampleName = opts$sampleName,
              rmdFile = rmdFile,
              databaseFolder = normalizePath(opts$databaseFolder),
              outputFile = normalizePath(opts$output))

print(options)

library(rmarkdown)
reportRmd<-options$rmdFile

output_dir = dirname(options$output)
output_file = basename(options$output)

cat("Output report to:", options$output, "\n")
rmarkdown::render(reportRmd,
                  output_dir = output_dir,
                  output_file = output_file,
                  params = list(data = options))
