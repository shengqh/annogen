# AnnoGen

## Motivation

Genome annotation is an important step for all in-depth bioinformatics analysis. It is imperative to augment quantity and diversity of genome-wide annotation data for the latest reference genome to promote its adoption by ongoing and future impactful studies.

## Results

We developed a python toolkit AnnoGen, which at the first time, allows the annotation of three pragmatic genomic features for the GRCh38 genome in enormous base-wise quantities. The three features are chemical binding Energy, sequence information Entropy, and Homology Score. The Homology Score is an exceptional feature that captures the genome-wide homology through single-base-offset tiling windows of 100 continual nucleotide bases.

## Conclusion

AnnoGen is capable of annotating the proprietary pragmatic features for variable user-interested genomic regions and optionally comparing two parallel sets of genomic regions. AnnoGen is characterized with simple utility modes and succinct HTML report of informative statistical tables and plots. 

# installation

Install python main package:

```
pip install git+git://github.com/shengqh/annogen.git
```

Install packages in R before you perform in comparison mode:

```
install.packages(c("optparse", "rmarkdown", "knitr", "pscl", "gridExtra"))

if (!requireNamespace("BiocManager", quietly = TRUE))
    install.packages("BiocManager")

BiocManager::install("GenomicRanges")
```

For old R version, you may have to try:

```
source("https://bioconductor.org/biocLite.R")
BiocInstaller::biocLite("GenomicRanges")
```

# required database (hg38)

Download **ALL** database files to same folder from:

https://cqsweb.app.vumc.org/download1/annotateGenome/hg38/

The database files include gzipped genome annotation for each chromosome (.gz), corresponding index file (.gz.tbi), range file (.bed) and chromosome length file (sizes.genome.txt).

```
wget https://cqsweb.app.vumc.org/download1/annotateGenome/hg38/file.list
wget -B https://cqsweb.app.vumc.org/download1/annotateGenome/hg38/ -i file.list
```

# example target files

You may download example target region files from:

https://cqsweb.app.vumc.org/download1/annotateGenome/

```
wget https://cqsweb.app.vumc.org/download1/annotateGenome/bed.list
wget -B https://cqsweb.app.vumc.org/download1/annotateGenome/ -i bed.list
```

# usage

### Annotate one file (annotation mode)

```
annogen -d folder_with_database -i bed_file -t
```
for example:
```
annogen -d folder_with_database -i H3K27me3.bed -t
```

### Annotate and compare two files (comparison mode)

```
annogen -d folder_with_database -i bed_file -c control_file
```

for example:
```
annogen -d folder_with_database -i H3K27me3.bed -c H3K27ac.bed
```

After comparison, annogen will generate html report about the features in two conditions. For example, [H3K27me3_VS_H3K27ac report](https://htmlpreview.github.io/?https://github.com/shengqh/annogen/blob/master/result/H3K27me3_VS_H3K27ac.html) includes two parts: 1) Catalogue of input intervals by genomic region type; and 2) Statistical comparison of genomic features. Energy, entropy, GC content and homology score figures are displayed side by side for comparison.

# running annogen using singularity

We also build docker container for annogen which can be used by singularity.

## running directly

```
singularity exec -e docker://shengqh/annogen annogen -d folder_with_database -i bed_file -t
```

## convert docker image to singularity image first

```
singularity build annogen.simg docker://shengqh/annogen
singularity exec -e annogen.simg annogen -d folder_with_database -i bed_file -t
```
