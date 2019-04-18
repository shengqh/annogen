#!/usr/bin/env Rscript

#cmpr2in.R
### Assuming interval-level annotation files (*1.genome_anno.tsv & *2.genome_anno.tsv) are ready as result of parental PY script.
### stem1,stem2 = TWO STRINGS AS STEM NAMES FOR THE USER INPUT FILE 1 & 2
### call( ["Rscript","cmpr2in.R",stem1,stem2] )

mnFeatures<-c(-132.13,-798.53,2.63,3.62,4.18,46.17,1.81,-135.18,-803.57,2.61,3.62,4.19,48.77,1.21,-131.33,-797.97,2.64,3.63,4.18,45.29,3.44)
sdFeatures<-c(14.31,19.11,0.21,0.20,0.18,13.21,30.86,14.70,20.63,0.16,0.17,0.14,13.35,11.15,13.79,19.52,0.22,0.22,0.20,12.52,57.16)
mnFeatures <- matrix(mnFeatures,nc=3,dimnames=list(c('delta_G37','delta_H','Entropy2','Entropy3','Entropy4','gc','HS'),c('introns','exons','intergene')))
sdFeatures <- matrix(sdFeatures,nc=3,dimnames=dimnames(mnFeatures))
#cmpr2in(): Summarize users' interval-level features in graphics and statistically compare the various features between two inputs.
### INPUT stem1 & stem2: stems of annotated file names (most likely the ultimate input file names to the software).
### regionLoc: directory where bed files for three types of genomic regions are stored.
### INPUT mn & sd: mean & sd statistics of 4*3 background distributions (feature4 by region3)
### NOTE currently I adopt the mean feature score (instead of median, 25%, etc.)
cmpr2in <- function(file1, fileName1, file2, fileName2, outputPrefix, regionLoc='./',mn=mnFeatures,sd=sdFeatures) {
  files<-c(file1, file2)
  names<-c(fileName1, fileName2)
  ####################### Read in python-annotated files & derive GC% ###################
  intv.ls2 <- lapply(files),
  function(x) {
    anno <- read.delim(x,check.names=F,as.is=T)
    gc_mean <- anno[,'G%_mean']+anno[,'C%_mean']
    anno <- data.frame(anno,gc_mean=gc_mean)
    anno
  }
)
intv1 <- intv.ls2[[1]]
intv2 <- intv.ls2[[2]]
################## Discern genomic regions of input intervals #################
library(GenomicRanges)
gr2 <- lapply(intv.ls2,deriveGRfrItv); names(gr2) <- names
regions <- c('introns','exons','intergene')
rFiles <- paste(regionLoc,paste0('HG38.',regions,'.bed'),sep='/')
GR3 <- lapply(rFiles,deriveGRfrBed); names(GR3) <- regions
regionSum <- matrix(0,nr=2,nc=length(regions),dimnames=list(names,regions )  )
for (input in names) {
  gr <- gr2[[input]]
  for (region in regions) {
    GR <- GR3[[region]]
    ovlappedItvs <- subsetByOverlaps(gr,GR)
    regionSum[input,region] <- 100*round(length(ovlappedItvs)/length(gr),3)	
  }
}
regionSum <- cbind(regionSum,totalNum=c(nrow(intv1),nrow(intv2)))
colnames(regionSum)[1:length(regions)] <- paste0(colnames(regionSum)[1:length(regions)],'(%)')
################## End discerning #############################################
subNames <- list(
  energy=c('delta_G37','delta_H'),
  entropy=c(paste0('Entropy',2:4)),
  gc=c('gc'),
  map=c('HS')
)
feature4 <- names(subNames)
subN <- sapply(subNames,length); names(subN) <- feature4
######################### Plot foreground/background distributions #####################
subfs.all <- unlist(subNames)
cmprTbl <- matrix(NA,nr=length(subfs.all),nc=14,
                  dimnames=list(subfs.all,c(paste0('Med',1:2),
                                            paste(rep(c('W','W+','W-'),each=2),rep(c('','p'),3),sep='.' ), 
                                            paste(rep(c('D','D+','D-'),each=2),rep(c('','p'),3),sep='.' )
                  )
                  )
)
colnames(cmprTbl) <- gsub('\\.$','',colnames(cmprTbl),perl=T)
for (feature in feature4) {
  vars <- subNames[[feature]]#paste0('Entropy',c(2,3,4))
  col.ls2 <- lapply(intv.ls2,function(x,cols) x[,cols,drop=F], paste(vars,'mean',sep='_') )
  pdf(paste0(feature,'.pdf'))
  plot_a_feature(col.ls2,names,vars,mn,sd)
  dev.off()
  # Statistical comparison of basewise scores through Wilcoxon & KS test
  for (subf in subNames[[feature]]) {
    subf.ls2 <- lapply(col.ls2,function(x,subf) x[,paste0(subf,'_mean')],subf)
    cmprTbl[subf,] <- itvCmpr_a_subf(subf.ls2)
  }		
}
write.table(regionSum,paste0(outputPrefix, '_regionSum.tsv'),col.names=NA,quote=F,sep='\t')
write.table(cmprTbl,paste0(outputPrefix,'_cmpr.tsv'),col.names=NA,quote=F,sep='\t')
cmprTbl
}
deriveGRfrItv <- function(itvMore) {
  require(GenomicRanges)
  itv <- itvMore[,1:3]
  colnames(itv) <- c('chr','start','end')
  gr <- makeGRangesFromDataFrame(itv)
  gr
}
deriveGRfrBed <- function(bedFile) {
  require(GenomicRanges)
  bed <- read.delim(bedFile,head=F)
  colnames(bed) <- c('chr','start','end')
  gr <- makeGRangesFromDataFrame(bed)
  gr
}
#itvCmpr_a_subf(): for a list of two series of subfeature values, return 6*2 statistics values plus two median values.
itvCmpr_a_subf <- function(ls2) {
  dat1 <- ls2[[1]]
  dat2 <- ls2[[2]]
  D.res <- ks.test(dat1,dat2)
  Dp.res <- ks.test(dat1,dat2,alternative='greater') # plus
  Dm.res <- ks.test(dat1,dat2,alternative='less')
  W.res <- wilcox.test(dat1,dat2)
  Wp.res <- wilcox.test(dat1,dat2,alternative='greater')
  Wm.res <- wilcox.test(dat1,dat2,alternative='less')
  stats <- c(W.res$statistic,W.res$p.value,Wp.res$statistic,Wp.res$p.value,Wm.res$statistic,Wm.res$p.value,
             D.res$statistic,D.res$p.value,Dp.res$statistic,Dp.res$p.value,Dm.res$statistic,Dm.res$p.value)
  stats <- c(median(dat1),median(dat2),stats)
  stats
}
plot_a_feature <- function(ls2,stemName2,subNames,mn=mnFeatures,sd=sdFeatures) { #col.ls2,c(stem1,stem2),c('Entropy2','Entropy3','Entropy4')
  library(ggplot2)
  library(gridExtra)
  nSub <- ncol(ls2[[1]])
  pS <- vector('list',nSub)
  mnSubfs <- mn[subNames,,drop=F]
  sdSubfs <- sd[subNames,,drop=F]
  for (i in 1:nSub) {
    ############ Prepare xs & ys for background distributions #########
    if (subNames[1]!='HS') {
      cols <- c('gray50','black','gray80') #introns,exons,intergene
      names(cols) <- colnames(mn)
      mnSubf <- mnSubfs[i,,drop=F]
      sdSubf <- sdSubfs[i,,drop=F]
      datNorm <- vector('list',ncol(mn)); names(datNorm)=colnames(mn)
      for (region in colnames(mn)) {
        mn.r <- mnSubf[1,region]
        sd.r <- sdSubf[1,region]
        xs <- seq(from=mn.r-3*sd.r,to=mn.r+3*sd.r,length.out=1000)
        ys <- dnorm(xs,mean=mn.r,sd=sd.r)
        datNorm[[region]] <- data.frame(x=xs,y=ys)
        #p0 <- ggplot(datNorm,aes(x,y))+geom_line(color=cols[region])      
      }
      #pS[[i]] <- pS[[i]]+p0
    }
    ################## End preparation #################
    subi.ls2 <- lapply(ls2,function(x) x[,i])
    in1 <- data.frame(score=subi.ls2[[1]],Input=stemName2[1])
    in2 <- data.frame(score=subi.ls2[[2]],Input=stemName2[2])
    dataFeature <- rbind(in1,in2)
    #p <- ggplot(data,aes(score,fill=Input)) + geom_histogram( aes(y = ..density.. ),alpha=1,position='dodge' ) # aes(y = ..density.. )
    #p <- p + labs(x=subNames[i])
    #if (i!=nSub) {
    #	P <- p+theme(legend.position='none')
    #} else {
    #  P <- p+theme(legend.position='top')
    #}
    if (subNames[1]!='HS') {
      if (i!=nSub) {
        pS[[i]] <- qplot(geom='blank')+geom_histogram(data=dataFeature,aes(x=score,y=..density..,fill=Input),alpha=1,position='dodge' )+geom_line(data=datNorm[['introns']],aes(x,y),color=cols['introns']) + geom_line(data=datNorm[['exons']],aes(x,y),color=cols['exons']) + geom_line(data=datNorm[['intergene']],aes(x,y),color=cols['intergene'])+labs(x=subNames[i],y='density') +theme(legend.position='none') #aes(y = ..density.. )
      } else {
        pS[[i]] <- qplot(geom='blank')+ geom_histogram(data=dataFeature,aes(x=score,y=..density..,fill=Input),alpha=1,position='dodge' ) +geom_line(data=datNorm[['introns']],aes(x,y),color=cols['introns']) + geom_line(data=datNorm[['exons']],aes(x,y),color=cols['exons']) + geom_line(data=datNorm[['intergene']],aes(x,y),color=cols['intergene']) +labs(x=subNames[i],y='density') +theme(legend.position='top')
      }
    } else {
      #if (i!=nSub) {
      #  pS[[i]] <- qplot(geom='blank') +  geom_histogram(data=dataFeature,aes(x=score,y=..density..,fill=Input),alpha=1,position='dodge' ) + labs(x=subNames[i]) +theme(legend.position='none') #aes(y = ..density.. )
      #} else {
      pS[[i]] <- qplot(geom='blank') + geom_histogram(data=dataFeature,aes(x=score,y=..density..,fill=Input),alpha=1,position='dodge' ) + labs(x=subNames[i],y='density') +theme(legend.position='top')
      
    }
  }
  do.call('grid.arrange',c(pS,nrow=1))
}

require(docopt)
'Usage:
cmpr2in.R [-c <control> --controlName <controlName> -s <sample> --sampleName <sampleName> -o <outputPrefix>]

Options:
-h --help     Show this screen.
-c            Control file.
--controlName Control name.
-s            Sample file.
--sampleName  Sample name.
-o            Output file prefix

]' -> doc

opts <- docopt(doc)
print(opts)
cmpred <- cmpr2in(opts$c, opts$controlName, opts$s, opts$sampleName, opts$o)

