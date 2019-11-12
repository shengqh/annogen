# AnnoGen

## Motivation

In spite of six years post its official release, the latest human reference genome GRCh38 is still outweighed by its predecessor in some research settings due to inferiority in annotation richness and convenience. It is imperative to augment quantity and diversity of genome-wide annotation data for the latest reference genome to promote its adoption by ongoing and future impactful studies.

## Results

Here Wwe developed a python toolkit AnnoGen, which firstat the first time, allows the annotation of threewith enormous pragmatic basewise quantities of four pragmatic genomic features for the GRCh38 genome. The three features are, Chemical Bonding including Energy, Entropy, GC content, and Homology Score. The Homology Score is an exceptional feature solved through exhaustive alignment between run-ning DNA windows against the whole genome.that captures the genome wide homology through 100 baseapair ovlapping windows.

## Conclusion

AnnoGen is capabable of annotating the proprietary pragmatic features for variable user-interested genomic regions and option-ally comparing two parallel sets of genomic regions. AnnoGen is characterized with simple utility modes and succinct HTML report of informa-tive statistical tables and plots. 

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

https://cqsweb.app.vumc.org/download1/annotateGenome/examples/

```
wget https://cqsweb.app.vumc.org/download1/annotateGenome/examples/bed.list
wget -B https://cqsweb.app.vumc.org/download1/annotateGenome/examples/ -i bed.list
```

# usage

### Annotate one file (annotation mode)
```
annotateGenome -d folder_with_database -i bed_file -t
```
for example:
```
annotateGenome -d folder_with_database -i H3K27me3.bed -t
```

### Annotate and compare two files (comparison mode)
```
annotateGenome -d folder_with_database -i bed_file -c control_file
```

for example:
```
annotateGenome -d folder_with_database -i H3K27me3.bed -c H3K27ac.bed
```

# running annotateGenome using singularity

We also build docker container for annotateGenome which can be used by singularity.

## running directly

```
singularity exec docker://shengqh/annotate_genome annotateGenome -d folder_with_database -i bed_file -t
```

## convert docker image to singularity image first
```
singularity build annotateGenome.simg docker://shengqh/annotate_genome
singularity exec annotateGenome.simg annotateGenome -d folder_with_database -i bed_file -t
```
