# annotateGenome

This package is used to annotate bed file with pre-calculated genome information.

# installation

```
pip install git+git://github.com/shengqh/annotateGenome.git
```

# required database (hg38)

Download all database files to same folder from:

https://cqsweb.app.vumc.org/download1/annotateGenome/hg38/

The database files include gzipped genome annotation for each chromosome (.gz), corresponding index file (.gz.tbi), range file (.bed) and chromosome length file (sizes.genome.txt).

# example target files

You may download example target region files from:

https://cqsweb.app.vumc.org/download1/annotateGenome/examples/

# usage

### Annotate one file
```
annotateGenome -d folder_with_database -i bed_file -t
```
for example:
```
annotateGenome -d folder_with_database -i H3K27me3.bed -t
```

### Annotate and compare two files
```
annotateGenome -d folder_with_database -i bed_file -c control_file
```

for example:
```
annotateGenome -d folder_with_database -i H3K27me3.bed -c H3K27ac.bed
```
