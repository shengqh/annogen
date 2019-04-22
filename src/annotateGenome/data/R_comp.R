#!/usr/bin/env Rscript

#sudo apt-get update && sudo apt-get install pandoc

require(docopt)
'Usage:
R_comp.R [-c <control> --controlName <controlName> -s <sample> --sampleName <sampleName> -r <rmdFile> -d <databaseFolder> -o <output>]

Options:
-h --help     Show this screen.
-c            Control file.
--controlName Control name.
-s            Sample file.
--sampleName  Sample name.
-r            RMD report file
-d            Database folder
-o            Output html file 

]' -> doc

opts <- docopt(doc)

options<-list(control = normalizePath(opts$control),
              controlName = opts$controlName,
              sample = normalizePath(opts$sample),
              sampleName = opts$sampleName,
              rmdFile = normalizePath(opts$rmdFile),
              databaseFolder = normalizePath(opts$databaseFolder),
              outputFile = normalizePath(opts$output))

print(options)

library(rmarkdown)
reportRmd<-opts$rmdFile

output_dir = dirname(opts$output)
output_file = basename(opts$output)

cat("Output report to:", opts$output, "\n")
rmarkdown::render(reportRmd,
                  output_dir = output_dir,
                  output_file = output_file,
                  params = list(data = options))
