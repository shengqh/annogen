FROM shengqh/bioinfo:r3.6.0_python3.7.3

RUN pip install git+git://github.com/shengqh/annotateGenome.git

RUN annotateGenome -h
