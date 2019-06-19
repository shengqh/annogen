FROM shengqh/bioinfo:r_python2

RUN pip install git+git://github.com/shengqh/annotateGenome.git

RUN annotateGenome -h
