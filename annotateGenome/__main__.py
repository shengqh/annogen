import argparse
import sys
import logging
import os
import tabix
import re
import gzip
import numpy as np
import subprocess
import pkg_resources

def initialize_logger(logfile):
  logger = logging.getLogger('genomeAnno')
  logger.setLevel(logging.DEBUG)

  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s - %(message)s')    
 
  # create console handler and set level to info
  handler = logging.StreamHandler()
  handler.setLevel(logging.DEBUG)
  handler.setFormatter(formatter)
  logger.addHandler(handler)
 
  # create error file handler and set level to error
  handler = logging.FileHandler(logfile, "w")
  handler.setLevel(logging.INFO)
  handler.setFormatter(formatter)
  logger.addHandler(handler)
 
  return(logger)

def getDatabase(folder, chrom):
  return folder + "/chr" + chrom + "_all_merged_data12.txt.gz"

def getValidFilename(s):
  s = str(s).strip().replace(' ', '_')
  return re.sub(r'(?u)[^-\w.]', '', s)
  
def runCommand(command, logger):
  logger.info("run : " + command )
  os.system(command)
  
def annotate(args, logger):
  logger.info("start ...")
  logger.info(str(args))
 
  doneFile = args.output + ".done"
  if os.path.isfile(doneFile):
    os.remove(doneFile)

  annoHeader = ""
  dbchr1 = getDatabase(args.database, "1")
  with gzip.open(dbchr1,'rt') as f:
    annoHeader = f.readline().rstrip()
  
  annoParts = annoHeader.split('\t')[3:]
  slimAnnoHeader = "EntryInDB\t" + "\t".join(["\t".join([anno + "_mean", anno + "_sd", anno + "_perc0", anno + "_perc25", anno + "_median", anno + "_perc75", anno + "_perc100"])  for anno in annoParts])
  emptyAnno = "\t" + "\t".join(["\t\t\t\t\t\t" for anno in annoParts])

  inputHeader = ""
  inputHeaderColNumber = 0
  queries = []
  logger.info("reading input file: " + args.input + " ...")
  with open(args.input, "r") as fin:
    inputHeader = fin.readline().rstrip()
    parts = inputHeader.split('\t')
    inputHeaderColNumber = len(parts)
    
    if not args.ignore_exist or not os.path.isfile(args.output):
      if (re.match("^\d+$", parts[1]) is not None) and (re.match("^\d+$", parts[2]) is not None): #no header in bed file
        logger.info("no headerline detected in input file")
        queries.append([parts, inputHeader])
        headers = ["#chr", "start", "end"]
        for idx in range(3, len(parts)):
          headers.append("V" + str(idx))
        inputHeader = "\t".join(headers)

      for line in fin:
        linestr = line.rstrip()
        parts = linestr.split('\t')
        queries.append([parts, linestr])

  if not args.ignore_exist or not os.path.isfile(args.output):
    logger.info("filtering queries ...")
    chroms = set(query[0][0] for query in queries)
    missing_chrs = [chrom for chrom in chroms if not os.path.isfile(getDatabase(args.database, chrom))]
    if len(missing_chrs) > 0:
      logger.warning("missing database file for chromosome:" + ';'.join(missing_chrs))
    missing_chrs = set(missing_chrs)

    queries = [q for q in queries if q[0][0] not in missing_chrs]
    logger.info("processing %d valid queries ..." % len(queries))
  
    lastChrom = ""
    with open(args.output, "w") as fout:
      fout.write(inputHeader + "\t" + slimAnnoHeader + "\n")
      for query in queries:
        parts = query[0]
        linestr = query[1]
        chrom = parts[0]

        if chrom in missing_chrs:
          continue

        if chrom != lastChrom:
          dbChrom = getDatabase(args.database, chrom)
          logger.info("reading database: " + dbChrom + " ...")
          tb = tabix.open(dbChrom)
          lastChrom = chrom
        
        start = int(parts[1])-1
        end = int(parts[2])+1
        tbiter = tb.query(chrom, start, end)
        records = [record for record in tbiter]
        bFound = len(records) > 0

        if not bFound:
          fout.write(linestr + "\t" + emptyAnno + "\n") 
          continue

        if len(records) == 1:
          fout.write(linestr + "\t1")
          for idx in range(3, len(records[0])):
            value = records[0][idx]
            fout.write("\t%s\t\t\t\t%s\t\t" % (value, value))
          fout.write("\n")
          continue

        fout.write(linestr + "\t" + str(len(records)))
        logger.debug(linestr)
        for idx in range(3, len(records[0])):
        #print(str(idx) + ":" + ",".join([record[idx] for record in records]))
          values = [float(record[idx]) for record in records]
          mean = np.mean(values)
          sd = np.std(values)
          perc = np.percentile(values, [0, 25, 50, 75, 100])
          fout.write("\t%f\t%f\t%f\t%f\t%f\t%f\t%f" % (mean, sd, perc[0], perc[1], perc[2], perc[3], perc[4]))
        fout.write("\n")

  if args.track:
    bedClipPath=pkg_resources.resource_filename('annotateGenome', '../bin/bedClip')
    bwPath=pkg_resources.resource_filename('annotateGenome','../bin/bedGraphToBigWig')
    if not os.path.isfile(bedClipPath):
      logger.error("bedClip not exist: " + bedClipPath)
      sys.exit(1)
    else:
      logger.info("Find bedClip at " + bedClipPath)

    for idx, anno in enumerate(annoParts):
      annoIndex = inputHeaderColNumber + 6 + idx * 7
      annoPrefix = args.output + "_" + getValidFilename(anno) + "_median";
      annoFile =  annoPrefix + ".bdg"
      annoSlopFile =  annoFile + ".slop"
      annoClipFile = annoSlopFile + ".clip"
      annoSortFile = annoClipFile + ".sort"
      annoBwFile = annoPrefix + ".bw"
      
      if not args.ignore_exist or not os.path.isfile(annoBwFile):
        runCommand("cut -f1,2,3," + str(annoIndex) + " " + args.output + " > " + annoFile, logger)
        runCommand("bedtools slop -i " + annoFile + " -g " + args.genome + " -b 0 > " + annoSlopFile, logger)
        runCommand(bedClipPath + " " + annoSlopFile + " " + args.genome + " " + annoClipFile, logger)
        runCommand("sort -k1,1 -k2,2n " + annoClipFile + " > " + annoSortFile, logger)
        runCommand(bwPath + " " + annoSortFile + " " + args.genome + " " + annoBwFile, logger)

        if os.path.isfile(annoBwFile):
          os.remove(annoFile)
          os.remove(annoSlopFile)
          os.remove(annoClipFile)
          os.remove(annoSortFile)
    
  with open(args.output + ".done", "w") as fout:
    fout.write("done.")

  logger.info("done.")
        
def main():
  parser = argparse.ArgumentParser(description="Annoate genome info.",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  
  DEBUG = False
  NOT_DEBUG = not DEBUG
  
  parser.add_argument('-d', '--database', action='store', nargs='?', help='Input database folder', required=NOT_DEBUG)
  parser.add_argument('-i', '--input', action='store', nargs='?', help="Input locus file (chr, start, end, splited by tab)", required=NOT_DEBUG)
  parser.add_argument('-o', '--output', action='store', nargs='?', help="Output annotated file")
  parser.add_argument('-t', '--track', action='store_true', help="Generate IGV track files", default=False)
  parser.add_argument('-g', '--genome', action='store', nargs='?', help="Genome size file for building IGV track")
  parser.add_argument('--ignore_exist', action='store_true', help="Ignore the result which is exist", default=False)
  
  if not DEBUG and len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

  args = parser.parse_args()
  
  if DEBUG:
    args.database="/scratch/cqs/shengq2/guoyan/20190131_genome_annotation/"
    args.input="/scratch/cqs/shengq2/guoyan/20190131_genome_annotation/input.txt"
    args.output="/scratch/cqs/shengq2/guoyan/20190131_genome_annotation/input.anno.txt"
    args.track=True
    args.genome="/home/shengq2/program/projects/guoyan/20190204_genome_annotation/hg38.sizes.genome"

  if args.output is None:
    args.output = args.input + ".genome_anno.tsv"

  if args.track:
    if args.genome is None:
      print "error: argument -g/--genome is required to generate IGV track files"
      sys.exit(1)
  
  logger = initialize_logger(args.output + ".log")
  annotate(args, logger)
  
if __name__ == "__main__":
    main()