# annotateGenome

This package is used to annotate bed file with pre-calculated genome information.

# installation

```
pip install git+git://github.com/shengqh/annotateGenome.git
```

# usage

```
annotateGenome -d folder_with_database -i bed_file -t -g hg38.sizes.genome
```

# required hg38.sizes.genome

The file contains chromosome and length seperated by tab.

```
1       248956422
10      133797422
11      135086622
12      133275309
13      114364328
14      107043718
15      101991189
16      90338345
17      83257441
18      80373285
19      58617616
2       242193529
20      64444167
21      46709983
22      50818468
3       198295559
4       190214555
5       181538259
6       170805979
7       159345973
8       145138636
9       138394717
MT      16569
X       156040895
Y       57227415
```
