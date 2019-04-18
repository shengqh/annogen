import argparse
import sys
import logging
import os
import tabix
import re
import gzip
import numpy as np
import subprocess

def initialize_logger(logfile, args):
  logger = logging.getLogger('genomeAnno')
  loglevel = logging.DEBUG if args.debug else logging.INFO
  logger.setLevel(loglevel)

  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s - %(message)s')    
 
  # create console handler and set level to info
  handler = logging.StreamHandler()
  handler.setLevel(loglevel)
  handler.setFormatter(formatter)
  logger.addHandler(handler)
 
  # create error file handler and set level to error
  handler = logging.FileHandler(logfile, "w")
  handler.setLevel(loglevel)
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
  
def getIntegralAverage(values):
  vlen = len(values)
  if vlen == 1:
    return values[0]
  result = 0.0
  for idx in range(0, vlen-2):
    result = result + (values[idx] + values[idx+1])
  result = result / 2
  if vlen > 2:
    result = result / (vlen - 1)
  return result 
  
def doAnnotate(annoParts, slimAnnoHeader, emptyAnno, input, output, args, logger):
  inputHeader = ""
  inputHeaderColNumber = 0
  queries = []
  logger.info("reading input file: " + input + " ...")
  with open(input, "r") as fin:
    inputHeader = fin.readline().rstrip()
    parts = inputHeader.split('\t')
    inputHeaderColNumber = len(parts)
    
    if not args.ignore_exist or not os.path.isfile(output):
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

  if not args.ignore_exist or not os.path.isfile(output):
    logger.info("filtering queries ...")
    chroms = set(query[0][0] for query in queries)
    missing_chrs = [chrom for chrom in chroms if not os.path.isfile(getDatabase(args.database, chrom))]
    if len(missing_chrs) > 0:
      logger.warning("missing database file for chromosome:" + ';'.join(missing_chrs))
    missing_chrs = set(missing_chrs)

    queries = [q for q in queries if q[0][0] not in missing_chrs]

    logger.info("sorting queries ...")
    queries = sorted(queries, key = lambda x: (x[0][0], int(x[0][1]), int(x[0][2])))
  
    logger.info("processing %d valid queries ..." % len(queries))
    lastChrom = ""
    with open(output, "w") as fout:
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
          values = [float(record[idx]) for record in records]
          mean = np.mean(values)
          sd = np.std(values)
          perc = np.percentile(values, [0, 25, 50, 75, 100])
          ia = getIntegralAverage(values)
          fout.write("\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f" % (mean, sd, perc[0], perc[1], perc[2], perc[3], perc[4], ia))
        fout.write("\n")

  if args.track:
    #make sure there is no overlap in file
    noOverlapFile = output + ".nooverlap"
    with open(output, "r") as fin:
      with open(noOverlapFile, "w") as fout:
        fout.write(fin.readline())
        lastParts = ['0', 0, 0, '']
        for line in fin:
          parts = line.split('\t')
          istart = int(parts[1])
          iend = int(parts[2])

          if parts[0] == lastParts[0]:
            if istart == lastParts[1]:
              logger.info("Removed due to overlap: %s:%d-%d with %s:%d-%d" % (lastParts[0], lastParts[1], lastParts[2], parts[0], istart, iend))
              lastParts = [parts[0], istart, iend, line]
              continue

            if istart <= lastParts[2]:
              logger.info("Removed due to overlap: %s:%d-%d with %s:%d-%d" % (parts[0], istart, iend, lastParts[0], lastParts[1], lastParts[2]))
              continue

          if lastParts[3] != '':
            fout.write(lastParts[3])
          lastParts = [parts[0], istart, iend, line]

        if lastParts[3] != '':
          fout.write(lastParts[3])

    #realpath = os.path.dirname(os.path.realpath(__file__))
    #bwPath = realpath + "/../bin/bedGraphToBigWig"
    bwPath = "bedGraphToBigWig"
    bwCreated = True
    for idx, anno in enumerate(annoParts):
      annoIndex = inputHeaderColNumber + 6 + idx * 8
      annoPrefix = output + "_" + getValidFilename(anno) + "_median";
      annoFile =  annoPrefix + ".bdg"
      annoBwFile = annoPrefix + ".bw"
      
      if not args.ignore_exist or not os.path.isfile(annoBwFile):
        runCommand("cut -f1,2,3," + str(annoIndex) + " \"" + noOverlapFile + "\" > \"" + annoFile + "\"", logger)
        runCommand(bwPath + " \"" + annoFile + "\" \"" + args.genome + "\" \"" + annoBwFile + "\"", logger)

        if os.path.isfile(annoBwFile):
          os.remove(annoFile)
          
      bwCreated = bwCreated and os.path.isfile(annoBwFile)
    
    if bwCreated:
      os.remove(noOverlapFile)
    
  with open(output + ".done", "w") as fout:
    fout.write("done.")

  logger.info("analyze " + input + " done.")

def annotate(args, logger):
  logger.info("start ...")
  logger.info(str(args))
 
  doneFile = args.output + ".done"
  if os.path.isfile(doneFile):
    os.remove(doneFile)

  dbchr1 = getDatabase(args.database, "1")
  with gzip.open(dbchr1,'rt') as f:
    annoHeader = f.readline().rstrip()
  
  annoParts = annoHeader.split('\t')[3:]
  slimAnnoHeader = "EntryInDB\t" + "\t".join(["\t".join([anno + "_mean", anno + "_sd", anno + "_perc0", anno + "_perc25", anno + "_median", anno + "_perc75", anno + "_perc100", anno + "_integralAverage"])  for anno in annoParts])
  emptyAnno = "\t" + "\t".join(["\t\t\t\t\t\t\t" for anno in annoParts])

  doAnnotate(annoParts, slimAnnoHeader, emptyAnno, args.input, args.output, args, logger)
  
  if(args.controlInput is not None) and (args.controlOutput is not None) and (args.comparisonOutput is not None):
    doAnnotate(annoParts, slimAnnoHeader, emptyAnno, args.controlInput, args.controlOutput, args, logger)
    rPath = "cmpr2in.R"
    controlName = os.path.splitext(os.path.basename(args.controlInput))[0]
    sampleName = os.path.splitext(os.path.basename(args.input))[0]
    runCommand(rPath + " -c \"" + args.controlOutput + "\" --controlName " + controlName + " -s \"" + args.output + "\" --sampleName " + sampleName + " -o " + args.comparisonOutputPrefix, logger)
        
def main():
  parser = argparse.ArgumentParser(description="Annoate genome info.",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  
  DEBUG = False
  NOT_DEBUG = not DEBUG
  
  parser.add_argument('-d', '--database', action='store', nargs='?', help='Input database folder', required=NOT_DEBUG)
  parser.add_argument('-i', '--input', action='store', nargs='?', help="Input locus file (chr, start, end, splited by tab)", required=NOT_DEBUG)
  parser.add_argument('--inputName', action='store', nargs='?', help="Input name")
  parser.add_argument('-o', '--output', action='store', nargs='?', help="Output annotated file")
  parser.add_argument('-t', '--track', action='store_true', help="Generate IGV track files", default=False)
  parser.add_argument('-g', '--genome', action='store', nargs='?', help="Genome size file for building IGV track")
  parser.add_argument('--controlInput', action='store', nargs='?', help="Control input locus file (chr, start, end, splited by tab)")
  parser.add_argument('--controlName', action='store', nargs='?', help="Control name")
  parser.add_argument('--controlOutput', action='store', nargs='?', help="Control output annotated file")
  parser.add_argument('--comparisonOutputPrefix', action='store', nargs='?', help="Comparison output prefix of control and input")
  parser.add_argument('--ignore_exist', action='store_true', help="Ignore the result which is exist", default=False)
  parser.add_argument('--debug', action='store_true', help="Output debug information", default=False)
  
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
    args.debug=True

  if args.output is None:
    args.output = args.input + ".genome_anno.tsv"

  if args.inputName is None:
    args.inputName = os.path.splitext(os.path.basename(args.input))[0]

  if args.controlInput is not None:
    if args.controlOutput is None:
      args.controlOutput = args.controlInput + ".genome_anno.tsv"
      
    if args.controlName is None:
      args.controlName = os.path.splitext(os.path.basename(args.controlInput))[0]
      
    if args.comparisonOutputPrefix is None:
      args.comparisonOutputPrefix = args.inputName + "_vs_" + args.controlName

  if args.track:
    if args.genome is None:
      print "error: argument -g/--genome is required to generate IGV track files"
      parser.print_help()
      sys.exit(1)
  
  logger = initialize_logger(args.output + ".log", args)
  annotate(args, logger)
  
if __name__ == "__main__":
    main()
