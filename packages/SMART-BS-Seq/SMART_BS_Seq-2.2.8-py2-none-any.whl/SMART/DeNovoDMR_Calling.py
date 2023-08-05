#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Time-stamp: <2018-04-20 16:10:00 Hongbo Liu>
'''
Modified on 2018.1.31

@author: Hongbo Liu

'''
import scipy.spatial.distance
import NewEntropy
import NewEntropyNormal
from scipy import stats
import numpy as np
import random
from multiprocessing import Pool
import time
import os
import sys
from collections import defaultdict
import statsmodels.api as sm
from statsmodels.formula.api import ols
import pandas as pd
from math import sqrt
import shutil

def multi_genome_segmentation(args):
        SmallSegmentNumChrome=DeNovoDMR_Calling().GenomeSegmentMeanMethy_MultiProcess_Chrome(*args)
        return SmallSegmentNumChrome

def multi_final_results(args):
        Numdec=DeNovoDMR_Calling().DeNovoFinalResult_MultiProgress_Chrome(*args)
        return Numdec
        

        
class DeNovoDMR_Calling():
    '''
    This module is used merge multiple profiles of the methylation in a chrome into an combined file
    50003153    100
    500170    26
    500190    65
    500191    67
    500198    74
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
    def _chk_asarray(self, a, axis):
        if axis is None:
            a = np.ravel(a)
            outaxis = 0
        else:
            a = np.asarray(a)
            outaxis = axis
        return a, outaxis
    
    def MethySpecificity_Calculator_SMART2(self,PreviousMethydataSet,CurrentMethydataSet,Group_Key,AvailableGroup):
        Groups=Group_Key.keys()
        GroupNum=len(Groups)
        AvailableCommonGroupNum=0 #Number of groups in which at least one sample have methylation value
        PreviousMethydataSet_A=[]
        CurrentMethydataSet_A=[]
        MethySpecificity=-1
        SimilarityEntropyvalue=-1
        EucDistance=-1
        
        Methyentropy=NewEntropy.Entropy()
        
        for eachgroup in Groups:
            Samples_sameGroup=Group_Key[eachgroup]  #The samples in the same group
            for eachvalue_samegroup in Samples_sameGroup:
                if (PreviousMethydataSet[eachvalue_samegroup] != '-' and CurrentMethydataSet[eachvalue_samegroup] != '-'):
                    PreviousMethydataSet_A.append(float(PreviousMethydataSet[eachvalue_samegroup]))
                    CurrentMethydataSet_A.append(float(CurrentMethydataSet[eachvalue_samegroup]))
                    AvailableCommonGroupNum=AvailableCommonGroupNum+1
        if float(AvailableCommonGroupNum)/float(GroupNum) >=AvailableGroup and len(PreviousMethydataSet_A) > 1 and len(CurrentMethydataSet_A) > 1: #Check whether there are enough values for entropy calculate
            EucDistance=scipy.spatial.distance.euclidean(PreviousMethydataSet_A, CurrentMethydataSet_A)/sqrt(AvailableCommonGroupNum)  #calculate the euclidean distance between the methylation leveles of current C and previous C
            EucDistance=("%.3f" % EucDistance)
            DifferMethydataSet=list(map(lambda x: abs(x[0]-x[1]), zip( PreviousMethydataSet_A, CurrentMethydataSet_A)))
            CurrentMethydataSet_A=tuple(CurrentMethydataSet_A)
            MethySpecificity=("%.3f" % (1.0-Methyentropy.EntropyCalculate(CurrentMethydataSet_A)))
            DifferMethydataSet=tuple(DifferMethydataSet)
            SimilarityEntropyvalue=("%.3f" % (1.0-Methyentropy.EntropyCalculate(DifferMethydataSet)))
            
        return MethySpecificity,SimilarityEntropyvalue,EucDistance
    
    
       
    def DataCheck_and_MissReplace(self,MethyData,MissReplace,AvailableGroup,MSthreshold,tmpDMCfolder,DMCmethyfile,p_DMR,statisticout):
        '''
        Split the BS-SEq data into chromes
        Select the CpG sites with methylation values in at least **% samples
        '''
        #RawMethyDataFolderName=MethyDataFolder+'*.wig'
        ChromeArray=[]
        SampleNames=[]
        TotalCpGNum=0
        AvailableCpGNum=0
        DMC_Num=0
        
        if tmpDMCfolder:
            # use a output directory to store Splited Methylation data 
            if not os.path.exists( tmpDMCfolder ):
                try:
                    os.makedirs( tmpDMCfolder )
                except:
                    sys.exit( "Output directory (%s) could not be created. Terminating program." % tmpDMCfolder )
   
        methyfile=open(MethyData,'rb') #open current methylation file
        filecontent=methyfile.readline()
        
        ###First line for sample information
        filecontent=filecontent.strip('\n')
        firstline=filecontent.split('\t')
        SampleNames=firstline[3:]
        SampleNum=len(SampleNames)
        Group_Key = defaultdict(list)
        Column_Key_Group = dict()
        sampleorder=0
        for sample in SampleNames:
            sample_info=sample.split('_')
            if len(sample_info)>=2 and sample_info[-1].isdigit():
                GroupName='_'.join(sample_info[0:-1])
                Group_Key[GroupName].append(sampleorder)
                Column_Key_Group[sampleorder] = GroupName
                sampleorder=sampleorder+1
            else:
                Group_Key[sample].append(sampleorder)
                Column_Key_Group[sampleorder] = sample
                sampleorder=sampleorder+1
        Group_Key_str = str(Group_Key)
        Column_Key_Group_str = str(Column_Key_Group)
        statisticout.write(Group_Key_str)
        statisticout.write(Column_Key_Group_str)
        Groups=Group_Key.keys()
        GroupNum=float(len(Groups))
        ChromeFirstlyOutline=filecontent+"\tMethySpecificity\tSimilarityEntropyvalue\tEucDistance\n"
        #DMCFirstlyOutline=filecontent+"\tMethySpecificity\tSimilarityEntropyvalue\tEucDistance\n"
        DMCmethyfile.write(ChromeFirstlyOutline)
        ###Process methylation data
        filecontent=methyfile.readline()
        CurrentStr='chr'
        ErrorRowNum=0
        FillMissNum=0
        while filecontent:
            TotalCpGNum=TotalCpGNum+1
            filecontent=filecontent.strip('\n')
            currentMeth=filecontent.split('\t')
            ###20170616: add function: Check whether the number of sample name equals the number of sample data
            if len(currentMeth) > len(firstline):
                print "[Warning] Row "+str(TotalCpGNum)+": Number of data columns is more than that of sample names!"
                ErrorRowNum=ErrorRowNum+1
                
            elif len(currentMeth) < len(firstline):
                print "[Warning] Row "+str(TotalCpGNum)+": Number of data columns is less than that of sample names!"
                ErrorRowNum=ErrorRowNum+1
            else:
                chrome=currentMeth[0]
                if chrome != CurrentStr:  #If search the new chrome,
                    ChromeArray.append(chrome)
                    CurrentStr=chrome
                    PreviousMethydataSet=[]
                    #Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
                    #print Starttime+" Start identifying DMC for "+chrome
                    #statisticout.write(Starttime+" Identifying DMC: "+chrome+"\n")
                    chromemethyfile=tmpDMCfolder+chrome+".txt"
                    #print chromemethyfile
                    chromemethyfile=open(chromemethyfile,'wb')
                    chromemethyfile.write(ChromeFirstlyOutline)
                # Data process
                CurrentMethydataSet=currentMeth[3:]
                ## Add missing value using the median value obtained the replicate samples 
                AvailableGroupNum=0 #Number of groups in which at least one sample have methylation value
                for eachgroup in Groups:
                    Samples_sameGroup=Group_Key[eachgroup]  #The samples in the same group
                    GroupSampleNum=float(len(Samples_sameGroup))
                    Valuelist=[]
                    MissValueNum=0
                    for eachvalue_samegroup in Samples_sameGroup:
                        if CurrentMethydataSet[eachvalue_samegroup] != '-':
                        ###20170616: add the data check for DNA methylation values
                            if(float(CurrentMethydataSet[eachvalue_samegroup]) >=0.0 and float(CurrentMethydataSet[eachvalue_samegroup]) <=1.0):
                                Valuelist.append(float(CurrentMethydataSet[eachvalue_samegroup]))
                            else:
                                print "[Warning] Row "+str(TotalCpGNum)+": Data filtering of methylation value that is out of range from 0.0 to 1.0!"
                        else:
                            MissValueNum=MissValueNum+1
                    NoneMissPercentage=float(len(Valuelist))/GroupSampleNum
                    if MissValueNum>0 and NoneMissPercentage >= MissReplace:  #There are enough available values in the samples of the same group
                        MedianValue=self.getMedian(Valuelist)  #Median value
                        MedianValue=("%.3f" % MedianValue)
                        for eachvalue_samegroup in Samples_sameGroup:
                            #print CurrentMethydataSet[eachvalue_samegroup]
                            if CurrentMethydataSet[eachvalue_samegroup] is '-':
                                #print MedianValue
                                CurrentMethydataSet[eachvalue_samegroup] = MedianValue
                                FillMissNum=FillMissNum+1
                    if len(Valuelist) > 0: # 
                        AvailableGroupNum=AvailableGroupNum+1
                        
                ##New methylation data after missing replacement
                MethylationNewList=CurrentMethydataSet
                Methydata=''
                for each in range(SampleNum):
                    MethylationNewList[each]=str(MethylationNewList[each])
                Methydata='\t'.join(MethylationNewList)
                filecontent=currentMeth[0]+"\t"+str(currentMeth[1])+"\t"+str(currentMeth[2])+"\t"+Methydata        
                    
                ## Calculate entropy value for the CpG sites with enough methylation values
                
                if float(AvailableGroupNum)/float(GroupNum) >= AvailableGroup: #Check whether there are enough values for entropy calculate
                    if len(PreviousMethydataSet)==0:
                        PreviousMethydataSet=CurrentMethydataSet
                    ### Entropy and similarity
                    MethySpecificity,SimilarityEntropyvalue,EucDistance = self.MethySpecificity_Calculator_SMART2(PreviousMethydataSet,CurrentMethydataSet,Group_Key,AvailableGroup)
                    
                    ### Determine DMC and output
                    if MethySpecificity >= 0:
                        AvailableCpGNum=AvailableCpGNum+1
                        Outline=filecontent+"\t"+str(MethySpecificity)+"\t"+str(SimilarityEntropyvalue)+"\t"+str(EucDistance)+"\n"
                        chromemethyfile.write(Outline)
                        DMCmethyfile.write(Outline)
                        #DMCOutline=filecontent+"\t"+DMCState+"\t"+str(NAOVA_pvalue)+"\t"+str(MethySpecificity)+"\t"+str(SimilarityEntropyvalue)+"\t"+str(EucDistance)+"\n"
                        #DMCmethyfile.write(DMCOutline)
                        
                PreviousMethydataSet=CurrentMethydataSet        
            filecontent=methyfile.readline()
            
        if (float(ErrorRowNum)/float(TotalCpGNum) > 0.1):
                    sys.exit("[Error:] Program termination due to more than 10% of data rows have errors!")

        #Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        #print Starttime+" Summary of DMC identification: "
        #print "\t\t    Number of total CpG sites: "+str(TotalCpGNum)
        #print "\t\t    Number of CpG sites with methylation in at least "+str(AvailableGroup*100)+"% of groups : "+str(AvailableCpGNum)
        #print "\t\t    Number of identified DMC based threshold "+str(MSthreshold)+": "+str(DMC_Num)
        #statisticout.write(Starttime+" Summary of DMC identification: "+"\n")
        #statisticout.write("\t\t    Number of total CpG sites: "+str(TotalCpGNum)+"\n")
        #statisticout.write("\t\t    Number of CpG sites with methylation in "+str(AvailableGroup*100)+"% of groups : "+str(AvailableCpGNum)+"\n")
        #statisticout.write("\t\t    Number of identified DMC based threshold "+str(MSthreshold)+": "+str(DMC_Num)+"\n")
        return ChromeArray,SampleNames,Group_Key,Column_Key_Group,TotalCpGNum,AvailableCpGNum,DMC_Num,FillMissNum
    
    
    def MissReplace_DMC_callling(self,MethyData,MissReplace,AvailableGroup,MSthreshold,tmpDMCfolder,AvailableCpGmethyfile,DMCmethyfile,p_DMR,statisticout):
        '''
        Split the BS-SEq data into chromes
        Select the CpG sites with methylation values in at least **% samples
        '''
        #RawMethyDataFolderName=MethyDataFolder+'*.wig'
        MissReplace=float(MissReplace)
        ChromeArray=[]
        SampleNames=[]
        TotalCpGNum=0
        AvailableCpGNum=0
        DMC_Num=0
        
        if tmpDMCfolder:
            # use a output directory to store Splited Methylation data 
            if not os.path.exists( tmpDMCfolder ):
                try:
                    os.makedirs( tmpDMCfolder )
                except:
                    sys.exit( "Output directory (%s) could not be created. Terminating program." % tmpDMCfolder )
        
        methyfile=open(MethyData,'rb') #open current methylation file
        filecontent=methyfile.readline()
        
        ###First line for sample information
        filecontent=filecontent.strip('\n')
        firstline=filecontent.split('\t')
        SampleNames=firstline[3:]
        SampleNum=len(SampleNames)
        Group_Key = defaultdict(list)
        Column_Key_Group = dict()
        sampleorder=0
        for sample in SampleNames:
            sample_info=sample.split('_')
            Group_Key[sample_info[0]].append(sampleorder)
            Column_Key_Group[sampleorder] = sample_info[0]
            sampleorder=sampleorder+1
        Group_Key_str = str(Group_Key)
        Column_Key_Group_str = str(Column_Key_Group)
        statisticout.write(Group_Key_str)
        statisticout.write(Column_Key_Group_str)
        Groups=Group_Key.keys()
        GroupNum=float(len(Groups))
        ChromeFirstlyOutline=filecontent+"\tMethySpecificity\tSimilarityEntropyvalue\tEucDistance\n"
        DMCFirstlyOutline=filecontent+"\tDMCState\tNAOVA_pvalue\tMethySpecificity\tSimilarityEntropyvalue\tEucDistance\n"
        DMCmethyfile.write(DMCFirstlyOutline)
        AvailableCpGmethyfile.write(DMCFirstlyOutline)
        ###Process methylation data
        filecontent=methyfile.readline()
        CurrentStr='chr'
        ErrorRowNum=0
        FillMissNum=0
        while filecontent:
            TotalCpGNum=TotalCpGNum+1
            filecontent=filecontent.strip('\n')
            currentMeth=filecontent.split('\t')
            ###20170616: add function: Check whether the number of sample name equals the number of sample data
            if len(currentMeth) > len(firstline):
                print "[Warning] Row "+str(TotalCpGNum)+": Number of data columns is more than that of sample names!"
                ErrorRowNum=ErrorRowNum+1
                
            elif len(currentMeth) < len(firstline):
                print "[Warning] Row "+str(TotalCpGNum)+": Number of data columns is less than that of sample names!"
                ErrorRowNum=ErrorRowNum+1
            else:
                chrome=currentMeth[0]
                if chrome != CurrentStr:  #If search the new chrome,
                    ChromeArray.append(chrome)
                    CurrentStr=chrome
                    PreviousMethydataSet=[]
                    Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
                    print Starttime+" Start identifying DMC for "+chrome
                    #statisticout.write(Starttime+" Identifying DMC: "+chrome+"\n")
                    chromemethyfile=tmpDMCfolder+chrome+".txt"
                    #print chromemethyfile
                    chromemethyfile=open(chromemethyfile,'wb')
                    chromemethyfile.write(ChromeFirstlyOutline)
                # Data process
                CurrentMethydataSet=currentMeth[3:]
                ## Add missing value using the median value obtained the replicate samples 
                AvailableGroupNum=0 #Number of groups in which at least one sample have methylation value
                for eachgroup in Groups:
                    Samples_sameGroup=Group_Key[eachgroup]  #The samples in the same group
                    GroupSampleNum=float(len(Samples_sameGroup))
                    Valuelist=[]
                    MissValueNum=0
                    for eachvalue_samegroup in Samples_sameGroup:
                        if CurrentMethydataSet[eachvalue_samegroup] != '-':
                        ###20170616: add the data check for DNA methylation values
                            if(float(CurrentMethydataSet[eachvalue_samegroup]) >=0.0 and float(CurrentMethydataSet[eachvalue_samegroup]) <=1.0):
                                Valuelist.append(float(CurrentMethydataSet[eachvalue_samegroup]))
                            else:
                                print "[Warning] Row "+str(TotalCpGNum)+": Data filtering of methylation value that is out of range from 0.0 to 1.0!"
                        else:
                            MissValueNum=MissValueNum+1
                    NoneMissPercentage=float(len(Valuelist))/GroupSampleNum
                    if MissValueNum>0 and NoneMissPercentage >= MissReplace:  #There are enough available values in the samples of the same group
                        MedianValue=self.getMedian(Valuelist)  #Median value
                        MedianValue=("%.3f" % MedianValue)                  
                        #print MedianValue
                        for eachvalue_samegroup in Samples_sameGroup:
                            #print CurrentMethydataSet[eachvalue_samegroup]
                            if CurrentMethydataSet[eachvalue_samegroup] is '-':
                                #print MedianValue
                                CurrentMethydataSet[eachvalue_samegroup] = MedianValue
                                FillMissNum=FillMissNum+1
                    if len(Valuelist) > 0: # 
                        AvailableGroupNum=AvailableGroupNum+1
                        
                ##New methylation data after missing replacement
                MethylationNewList=CurrentMethydataSet
                Methydata=''
                for each in range(SampleNum):
                    MethylationNewList[each]=str(MethylationNewList[each])
                Methydata='\t'.join(MethylationNewList)
                filecontent=currentMeth[0]+"\t"+str(currentMeth[1])+"\t"+str(currentMeth[2])+"\t"+Methydata
                
                ## Calculate entropy value for the CpG sites with enough methylation values
                if float(AvailableGroupNum)/float(GroupNum) >= AvailableGroup: #Check whether there are enough values for entropy calculate
                    if len(PreviousMethydataSet)==0:
                        PreviousMethydataSet=CurrentMethydataSet
                    ### Entropy and similarity
                    MethySpecificity,SimilarityEntropyvalue,EucDistance = self.MethySpecificity_Calculator_SMART2(PreviousMethydataSet,CurrentMethydataSet,Group_Key,AvailableGroup)
                    ### ANOVA 
                    Group_Key_Methyl = defaultdict(list)  # Record the methylation values in each group
                    ItemNum=0
                    Group_Key_Methyl_forNAOVA = []
                    #Group_Key_Methyl_new = dict(list)  # Record the methylation values in each group
                    for sampleorder in range(SampleNum):
                        if CurrentMethydataSet[sampleorder] != '-':
                            Group_Key_Methyl[Column_Key_Group[sampleorder]].append(float(CurrentMethydataSet[sampleorder])) # This disc can be used to calculate mean methylation value and compare them across groups
                            Group_Key_Methyl_forNAOVA.append([Column_Key_Group[sampleorder],float(CurrentMethydataSet[sampleorder])])
                            ItemNum=ItemNum+1
                            #Group_Key_Methyl_new[Column_Key_Group[sampleorder]].append(float(eachCpG[sampleorder])) # This disc can be used to calculate mean methylation value and compare them across groups  
                    #Mean methylation
                    Group_Methyl_mean=[]  # Order the same with Groups
                    Group_Methyl_mean_out=[]  # Order the same with Groups
                    for eachgroup in Groups:
                        if Group_Key_Methyl[eachgroup]:
                            Group_Methyl_mean.append(round(np.mean(Group_Key_Methyl[eachgroup]),3))  # for calculation of methylation specificity
                            Group_Methyl_mean_out.append(round(np.mean(Group_Key_Methyl[eachgroup]),3))  # for output of methylation specificity
                        else:
                            Group_Methyl_mean_out.append('-')
                      
                    #one-way ANOVA tests
                    if ItemNum==len(Groups): #To avoid the error introduced by only one value in a group
                        Group_Key_Methyl_forNAOVA.extend(Group_Key_Methyl_forNAOVA)
                    
                    Group_Key_Methyl_Frame =pd.DataFrame(Group_Key_Methyl_forNAOVA,columns=['Group', 'Methyl'])
                    #print Group_Key_Methyl_Frame
                    if np.std(Group_Key_Methyl_Frame['Methyl']) == 0:
                        NAOVA_pvalue=1.0
                    else:
                        mod = ols('Methyl ~ Group',data=Group_Key_Methyl_Frame).fit()
                        #print mod
                        try:
                            aov_table = sm.stats.anova_lm(mod, typ=2)
                            NAOVA_pvalue = aov_table['PR(>F)']['Group']
                            NAOVA_pvalue= "%.2e" % NAOVA_pvalue
                        except:
                            NAOVA_pvalue=1.0
                    
                    ### Determin DMC and output
                    if MethySpecificity >= 0:
                        AvailableCpGNum=AvailableCpGNum+1
                        if float(MethySpecificity) >= MSthreshold and float(NAOVA_pvalue) < p_DMR:
                            DMCState='DMC'
                            DMC_Num=DMC_Num+1
                            Outline=filecontent+"\t"+str(MethySpecificity)+"\t"+str(SimilarityEntropyvalue)+"\t"+str(EucDistance)+"\n"
                            DMCOutline=filecontent+"\t"+DMCState+"\t"+str(NAOVA_pvalue)+"\t"+str(MethySpecificity)+"\t"+str(SimilarityEntropyvalue)+"\t"+str(EucDistance)+"\n"
                            chromemethyfile.write(Outline)                        
                            DMCmethyfile.write(DMCOutline)
                            AvailableCpGmethyfile.write(DMCOutline)
                        else:
                            DMCState='NonDMC'
                            Outline=filecontent+"\t"+str(MethySpecificity)+"\t"+str(SimilarityEntropyvalue)+"\t"+str(EucDistance)+"\n"
                            DMCOutline=filecontent+"\t"+DMCState+"\t"+str(NAOVA_pvalue)+"\t"+str(MethySpecificity)+"\t"+str(SimilarityEntropyvalue)+"\t"+str(EucDistance)+"\n"
                            chromemethyfile.write(Outline)
                            AvailableCpGmethyfile.write(DMCOutline)
                        
                PreviousMethydataSet=CurrentMethydataSet        
            filecontent=methyfile.readline()

        if (float(ErrorRowNum)/float(TotalCpGNum) > 0.1):
                    sys.exit("[Error:] Program termination due to more than 10% of data rows have errors!")
        
        return ChromeArray,SampleNames,Group_Key,Column_Key_Group,TotalCpGNum,AvailableCpGNum,DMC_Num,FillMissNum
    
    def getMedian(self,dataSet):
        newData=[];
        for i in range(len(dataSet)):    
            newData.append(dataSet[i]);
        newData.sort()  #Sort
        if(len(dataSet)%2!=0):
            return newData[len(dataSet)/2];    #for odd number of samples 
        else:
            return (newData[len(dataSet)/2]+newData[len(dataSet)/2-1])/2.0;  #for even number of samples
          

    def GenomeSegmentMeanMethy_MultiProcess_Chrome(self,RegionChrome,SampleNames,Group_Key,Column_Key_Group,tmpDMCfolder,tmpFolder,MSthreshold,EDthreshold,SMthreshold,CDthreshold,p_DMR):
        '''
        For each ChromeArrayome, segment it based the methylation entropy, differentroy and EuclideanDistance
        '''
        Extremep_DMR=p_DMR/0.00000000000000000001
        ExtrmeMSthreshold=MSthreshold/3
        SampleNum=len(SampleNames)
        Groups=Group_Key.keys()
        GroupNum=float(len(Groups))
        GenomeSegmentOutFolder=tmpFolder+"GenomeSegment/"
        GenomeSegmentMethyOutFolder=tmpFolder+"GenomeSegmentMethy/"
        Methyentropy=NewEntropy.Entropy()
        
        if GenomeSegmentOutFolder:
            # use a output directory to store merged Methylation data 
            if not os.path.exists( GenomeSegmentOutFolder ):
                try:
                    os.makedirs( GenomeSegmentOutFolder )
                except:
                    sys.exit( "Output directory (%s) could not be created. Terminating program." % GenomeSegmentOutFolder )
        if GenomeSegmentMethyOutFolder:
            # use a output directory to store merged Methylation data 
            if not os.path.exists( GenomeSegmentMethyOutFolder ):
                try:
                    os.makedirs( GenomeSegmentMethyOutFolder )
                except:
                    sys.exit( "Output directory (%s) could not be created. Terminating program." % GenomeSegmentMethyOutFolder )
        SmallSegNum=0
        SmallDMRNum=0

        EntropyDEEDFile =open(tmpDMCfolder+RegionChrome+".txt", 'r')  #Open the corresbondign methylation file
        #SegmentOUT=open(GenomeSegmentOutFolder+RegionChrome+".txt", 'w')  #Open the file for the segment
        SegmentMethyOUT=open(GenomeSegmentMethyOutFolder+RegionChrome+".txt", 'w')  #Open the file for segment and methylation
        #Parameter initialization
        SegmentCpGlist=[]
        SegmentMethyMatrix=[]
        
        #Perform segmentation
        CurrentCline=EntropyDEEDFile.readline()     #Read the first line (Colomn Name) of the methylation file
        PreviousState=''
        PreviousLocation=0
        CurrentCline=EntropyDEEDFile.readline()     #Read the first data line
        while CurrentCline:
            CurrentCline=CurrentCline.strip('\n')      #
            MethyEntropyInfor=CurrentCline.split()
            CurrentLocation=int(MethyEntropyInfor[1])              
            Entropy=float(MethyEntropyInfor[-3])
            SimilarityEntropy=float(MethyEntropyInfor[-2])
            EuclidDistance=float(MethyEntropyInfor[-1])
            #Determine the cell-specificity of current CpG
        #                 print CurrentLocation
        #                 print Entropy
        #                 print SimilarityEntropy
        #                 print EuclidDistance
            if Entropy>=MSthreshold:
                CurrentState='DMC'
            else:
                CurrentState='NonDMC'
        #                 print CurrentState   
            #Merge the neighboring CpG with the same cell-specificity
        #                if CurrentState==PreviousState and (SimilarityEntropy<0.6 and EuclidDistance<0.2) and (CurrentLocation-PreviousLocation)<=500:  #If the states are the same and the methylation are similar, merge them
            if (CurrentState==PreviousState and SimilarityEntropy <= SMthreshold and EuclidDistance <= EDthreshold) and (CurrentLocation-PreviousLocation)<=CDthreshold:  #If the states are the same and the methylation are similar, merge them
                SegmentMethyMatrix.append(MethyEntropyInfor[3:-3])
                #MethySumList=[x+y for x, y in zip(MethySumList, MethyList)]  #Sum the methylaion in each cell type
                SegmentCpGlist.append(MethyEntropyInfor[1])  #Record current CpG and merge it
                #print SegmentCpGlist
            else:     #If the merger condition is not filled, output current segment, and initialize the new segment
                #output current segment
                SegmentCpGNum=len(SegmentCpGlist)
                #print SegmentCpGlist
                if len(SegmentCpGlist)>0:
                    # Output a segment with its mean methylation in each group, methylation specificity and p value
                    Group_Key_Methyl = defaultdict(list)  # Record the methylation values in each group
                    ItemNum=0
                    Group_Key_Methyl_forNAOVA = []
                    #Group_Key_Methyl_new = dict(list)  # Record the methylation values in each group
                    for eachCpG in SegmentMethyMatrix:
                        for sampleorder in range(SampleNum):
                            if eachCpG[sampleorder] != '-':
                                Group_Key_Methyl[Column_Key_Group[sampleorder]].append(float(eachCpG[sampleorder])) # This disc can be used to calculate mean methylation value and compare them across groups
                                Group_Key_Methyl_forNAOVA.append([Column_Key_Group[sampleorder],float(eachCpG[sampleorder])])
                                ItemNum=ItemNum+1
                                #Group_Key_Methyl_new[Column_Key_Group[sampleorder]].append(float(eachCpG[sampleorder])) # This disc can be used to calculate mean methylation value and compare them across groups  
                    #Mean methylation
                    Group_Methyl_mean=[]  # Order the same with Groups
                    Group_Methyl_mean_out=[]  # Order the same with Groups
                    for eachgroup in Groups:
                        if Group_Key_Methyl[eachgroup]:
                            Group_Methyl_mean.append(round(np.mean(Group_Key_Methyl[eachgroup]),3))  # for calculation of methylation specificity
                            Group_Methyl_mean_out.append(round(np.mean(Group_Key_Methyl[eachgroup]),3))  # for output of methylation specificity
                        else:
                            Group_Methyl_mean_out.append('-')
                    #Methylation specificity                    
                    MethySumListforEntropy=tuple(Group_Methyl_mean)
                    #print MethySumListforEntropy
                    MethySpecificity=round(1.0-Methyentropy.EntropyCalculate(MethySumListforEntropy),3)       #Calculate the new MethySpecificity for mean methylation     
                    #one-way ANOVA tests
                    if ItemNum==len(Groups): #To avoid the error introduced by only one value in a group
                        Group_Key_Methyl_forNAOVA.extend(Group_Key_Methyl_forNAOVA)
        
                    Group_Key_Methyl_Frame =pd.DataFrame(Group_Key_Methyl_forNAOVA,columns=['Group', 'Methyl'])
                    #print Group_Key_Methyl_Frame
                    if np.std(Group_Key_Methyl_Frame['Methyl']) == 0:
                        NAOVA_pvalue=1.0
                    else:
                        mod = ols('Methyl ~ Group',data=Group_Key_Methyl_Frame).fit()
                        #print mod
                        try:
                            aov_table = sm.stats.anova_lm(mod, typ=2)
                            NAOVA_pvalue = aov_table['PR(>F)']['Group']
                            NAOVA_pvalue= "%.2e" % NAOVA_pvalue
                        except:
        #                                 print Group_Methyl_mean
        #                                 print MethySumListforEntropy
        #                                 print Group_Key_Methyl_Frame
        #                                 print aov_table
                            NAOVA_pvalue=1.0
                        
                    #print NAOVA_pvalue
                    
                    if ((float(MethySpecificity) >= MSthreshold and float(NAOVA_pvalue) < p_DMR) or (float(MethySpecificity) >= ExtrmeMSthreshold and float(NAOVA_pvalue) < Extremep_DMR)):
                        SegmentState='DMR'
                        SmallDMRNum=SmallDMRNum+1
                    else:
                        SegmentState='NonDMR'
                        
                    #Output
                    SegmentInfor=RegionChrome+":"+SegmentCpGlist[0]+"-"+str(int(SegmentCpGlist[-1])+2)+"\t"+SegmentState+"\t"+str(SegmentCpGNum)
                    SmallSegNum=SmallSegNum+1
                    #print >> SegmentOUT, SegmentInfor
                    print >> SegmentMethyOUT, SegmentInfor, Group_Methyl_mean_out
        #                         print SegmentInfor
        #                         print MethySpecificity 
        #                         print NAOVA_pvalue
                    
#                     Methydata=''
#                     for GroupOrder in range(len(Group_Methyl_mean_out)):
#                         Group_Methyl_mean_out[GroupOrder]=str(Group_Methyl_mean_out[GroupOrder])
#                     Methydata=','.join(Group_Methyl_mean_out)
#                     
#                     SegmentBedOutFile.write(RegionChrome+"\t"+SegmentCpGlist[0]+"\t"+str(int(SegmentCpGlist[-1])+2)+"\t"+str(SegmentCpGNum)+"\t"+SegmentState+"\t"+str(MethySpecificity)+"\t"+str(NAOVA_pvalue)+"\t"+Methydata+"\n")
                #initialize the new segment
                SegmentCpGlist=[]
                SegmentMethyMatrix=[]
                SegmentMethyMatrix.append(MethyEntropyInfor[3:-3])
                SegmentCpGlist.append(MethyEntropyInfor[1])  #Record current CpG and merge it                                                                                                     
            PreviousState=CurrentState
            PreviousLocation=CurrentLocation
            CurrentCline=EntropyDEEDFile.readline()
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Finish segmentation for "+RegionChrome  #Report the region are segmented
        #statisticout.write(Starttime+" Finish segmentation for "+RegionChrome+"\n")    
        return SmallSegNum
            
    
    def GenomeSegmentMeanMethy_MultiProcess(self,ChromeArray,SampleNames,Group_Key,Column_Key_Group,tmpDMCfolder,tmpFolder,MSthreshold,EDthreshold,SMthreshold,CDthreshold,p_DMR):
        '''
        For each ChromeArrayome, segment it based the methylation entropy, differentroy and EuclideanDistance
        '''
        GenomeSegmentOutFolder=tmpFolder+"GenomeSegment/"
        GenomeSegmentMethyOutFolder=tmpFolder+"GenomeSegmentMethy/"

        if GenomeSegmentOutFolder:
            # use a output directory to store merged Methylation data 
            if not os.path.exists( GenomeSegmentOutFolder ):
                try:
                    os.makedirs( GenomeSegmentOutFolder )
                except:
                    sys.exit( "Output directory (%s) could not be created. Terminating program." % GenomeSegmentOutFolder )
        if GenomeSegmentMethyOutFolder:
            # use a output directory to store merged Methylation data 
            if not os.path.exists( GenomeSegmentMethyOutFolder ):
                try:
                    os.makedirs( GenomeSegmentMethyOutFolder )
                except:
                    sys.exit( "Output directory (%s) could not be created. Terminating program." % GenomeSegmentMethyOutFolder )
                    
        pool = Pool(len(ChromeArray))
        tasks=[]
        for RegionChrome in ChromeArray:
            tasks.append((RegionChrome,SampleNames,Group_Key,Column_Key_Group,tmpDMCfolder,tmpFolder,MSthreshold,EDthreshold,SMthreshold,CDthreshold,p_DMR))

        SmallSegmentNumChrome=pool.map(multi_genome_segmentation,tasks)
        pool.close()
        SmallSegmentNum=0
        for each in SmallSegmentNumChrome:
            SmallSegmentNum=SmallSegmentNum+each
        return SmallSegmentNum
            
    
    def MethySpecificity_Calculator_Merge(self,PreviousMethydataSet,CurrentMethydataSet,Groups,AvailableGroup):
        '''
        Constructor
        Caculate the SimilarityEntropy and Euclidean Distance between neighbring CpG
        '''
        GroupNum=len(Groups)
        AvailableCommonGroupNum=0 #Number of groups in which at least one sample have methylation value
        PreviousMethydataSet_A=[]
        CurrentMethydataSet_A=[]
        SimilarityEntropyvalue=-1
        EucDistance=-1
        Methyentropy=NewEntropy.Entropy()

        for GroupOrder in range(GroupNum):
            if (PreviousMethydataSet[GroupOrder] != "'-'" and CurrentMethydataSet[GroupOrder] != "'-'"):
                PreviousMethydataSet_A.append(float(PreviousMethydataSet[GroupOrder]))
                CurrentMethydataSet_A.append(float(CurrentMethydataSet[GroupOrder]))
                AvailableCommonGroupNum=AvailableCommonGroupNum+1
        if (float(AvailableCommonGroupNum)/GroupNum) >= AvailableGroup: #Check whether there are enough values for entropy calculate
            EucDistance=scipy.spatial.distance.euclidean( PreviousMethydataSet_A, CurrentMethydataSet_A)/sqrt(AvailableCommonGroupNum)  #calculate the euclidean distance between the methylation leveles of current C and previous C
            DifferMethydataSet=list(map(lambda x: abs(x[0]-x[1]), zip( PreviousMethydataSet_A, CurrentMethydataSet_A)))
            DifferMethydataSet=tuple(DifferMethydataSet)
            SimilarityEntropyvalue=1.0-Methyentropy.EntropyCalculate(DifferMethydataSet)
            
#             CurrentMethydataSet_A=tuple(CurrentMethydataSet_A)
#             CurrentSpecificity=1.0-Methyentropy.EntropyCalculate(CurrentMethydataSet_A)
#             PreviousMethydataSet_A=tuple(PreviousMethydataSet_A)
#             PreviousSpecificity=1.0-Methyentropy.EntropyCalculate(PreviousMethydataSet_A)
                       
        return SimilarityEntropyvalue,round(EucDistance,3)

                
    def SegmentMerge(self,ChromeArray,SampleNames,Groups,tmpFolder,AvailableGroup,MSthreshold,EDthreshold,SMthreshold,CDthreshold,statisticout):
        '''
        For each ChromeArrayome, Merge the segments based on the methylation entropy, differentroy and EuclideanDistance
        '''
        MergedGenomeSegmentOutFolder=tmpFolder+"MergedGenomeSegment/"
        if MergedGenomeSegmentOutFolder:
            # use a output directory to store merged Methylation data 
            if not os.path.exists( MergedGenomeSegmentOutFolder ):
                try:
                    os.makedirs( MergedGenomeSegmentOutFolder )
                except:
                    sys.exit( "Output directory (%s) could not be created. Terminating program." % MergedGenomeSegmentOutFolder )
        for RegionChrome in ChromeArray:
            
            #statisticout.write(Starttime+" Merging Segments for "+RegionChrome+"\n")
            file=open(tmpFolder+"GenomeSegmentMethy/"+RegionChrome+".txt", 'r')  #Open the file for segment and methylation
            MergedSegmentOUT =open(MergedGenomeSegmentOutFolder+RegionChrome+".txt", 'w')  #Open the file for the segment
            list0=[]
            length=len(list0)
            n=0
            while n<=(7-length):
                line=file.readline()
                if line:
                    line=line.strip('\n')
                    line0=line.split('\t')
                    a1=line0[0].split(':')
                    a2=a1[-1].split('-')
                    a1=a1+a2 
                    del a1[1]
                    line1=line0[-1].split(' [')
                    a=line1[-1].strip(']')
                    a=a.split(', ')
                    a1.append(line0[1])
                    a1.append(line1[0])
                    a1=a1+a
                    list0.append(a1)
                    n=n+1
                else:
                    break
            line=file.readline()
            j=1
            CpGNum=0
            #print list0
            while j<=(len(list0)-1):
                PreviousMethydataSet=list0[0][5:len(list0[0])]
                MethydataSet=list0[j][5:len(list0[0])]
                PreviousState=list0[0][3]
                CurrentState=list0[j][3]
#                 print "***************"
#                 print list0[0]
#                 print list0[j]
                ## Count the CpG Number between two segment
                IntraCpGNum=0
                for IntraSegNum in range(1,j):
                    IntraCpGNum=IntraCpGNum+int(list0[IntraSegNum][4])

                SimilarityEntropyvalue,EucDistance = self.MethySpecificity_Calculator_Merge(PreviousMethydataSet,MethydataSet,Groups,AvailableGroup)
                
#                 print PreviousMethydataSet
#                 print MethydataSet
#                 print str(math.fabs(PreviousSpecificity-CurrentSpecificity))+":"+CurrentState+PreviousState+":"+str(SimilarityEntropyvalue)+":"+str(EucDistance)+":"+str((int(list0[j][1])-int(list0[0][2])))+":"+str(IntraCpGNum)
                
                if CurrentState==PreviousState and SimilarityEntropyvalue<= SMthreshold and EucDistance<= EDthreshold and (int(list0[j][1])-int(list0[0][2]))<= CDthreshold and IntraCpGNum<=5:     
                    #avEntropyvalue=(float(list0[0][3])*float(list0[0][4])+float(list0[j][3])*float(list0[j][4]))/(float(list0[0][4])+float(list0[j][4]))
                    #avEntropyvalue=round(avEntropyvalue,3)
                    #avEntropyvalue=round(CurrentSpecificity,3)
                    count=int(list0[0][4])+int(list0[j][4])
                    a1=[list0[0][0],list0[0][1],list0[j][2],CurrentState,count]
                    b1=list0[0][5:len(list0[0])]
                    b2=list0[j][5:len(list0[0])]
                    for q in range(len(b1)):
                        if b1[q]!= "'-'" and b2[q]!= "'-'":
                            b1[q]=(float(b1[q])*float(list0[0][4])+float(b2[q])*float(list0[j][4]))/(float(list0[0][4])+float(list0[j][4]))
                            b1[q]=round(b1[q],3)
                        elif b1[q]!= "'-'":
                            b1[q]=round(float(b1[q]),3)
                        elif b2[q]!= "'-'":
                            b1[q]=round(float(b2[q]),3)
                        else:
                            b1[q]="'-'"
                    newlist=a1+b1
                    list0[j]=newlist
                    list0=list0[j:len(list0)]
                    length=len(list0)
                    n=0
                    while n<=(7-length) and line:
                        line=line.strip('\n')
                        line0=line.split('\t')
                        a1=line0[0].split(':')
                        a2=a1[-1].split('-')
                        a1=a1+a2 
                        del a1[1]
                        line1=line0[-1].split(' [')
                        a=line1[-1].strip(']')
                        a=a.split(', ')
                        a1.append(line0[1])
                        a1.append(line1[0])
                        a1=a1+a
                        list0.append(a1)
                        n=n+1
                        line=file.readline()
                    j=1
                elif j==(len(list0)-1):
                    MethyList=[str(x) for x in list0[0][5:len(list0[0])]]
                    Methydata='\t'.join(MethyList)
                    Segmentname=list0[0][0]+":"+list0[0][1]+"-"+list0[0][2]
                    MeanSpecificity=list0[0][3]
                    CpGNum=str(list0[0][4])
                    MergedSegmentOUT.write(Segmentname+"\t"+MeanSpecificity+"\t"+CpGNum+"\t"+Methydata+"\n")
                    list0=list0[1:len(list0)]
                    n=0
                    while n<=(7-len(list0))and line:
                        line=line.strip('\n')
                        line0=line.split('\t')
                        a1=line0[0].split(':')
                        a2=a1[-1].split('-')
                        a1=a1+a2 
                        del a1[1]
                        line1=line0[-1].split(' [')
                        a=line1[-1].strip(']')
                        a=a.split(', ')
                        a1.append(line0[1])
                        a1.append(line1[0])
                        a1=a1+a
                        list0.append(a1)
                        n=n+1
                        line=file.readline()
                    j=1
                else:
                    j=j+1
            if len(list0)==1:
                MethyList=[str(x) for x in list0[0][5:len(list0[0])]]
                Methydata='\t'.join(MethyList)
                Segmentname=list0[0][0]+":"+list0[0][1]+"-"+list0[0][2]
                MeanSpecificity=list0[0][3]
                CpGNum=str(list0[0][4])
                MergedSegmentOUT.write(Segmentname+"\t"+MeanSpecificity+"\t"+CpGNum+"\t"+Methydata+"\n")
            Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
            print Starttime+" Finish merging segments for "+RegionChrome  #Report the region are segmented


    def FoldertxttoBed9withMethyandSpecificity(self, tmpDMCfolder, InputFolder,BedOutFile,MergedSegmentOutFile,DMR_methyl_OutFile,DMR_Specificity_OutFile,SegmentCellTypeMethymarkPvalue,ChromeArray,SampleNames,Groups,Column_Key_Group,MSthreshold,SCthreshold,SLthreshold,p_DMR,p_MethylMark,statisticout):
        '''
        
        '''
        Extremep_DMR=p_DMR/0.00000000000000000001
        ExtrmeMSthreshold=MSthreshold/3
        MethyTB=NewEntropyNormal.Entropy()
        Methyentropy=NewEntropy.Entropy()
        Numdec={'MergedSegment':0, 'DMR':0, 'NonDMR':0, 'UniHypo':0, 'UnipLow':0,'UnipHigh':0,'UniHyper':0, 'MethyMark':0, 'HypoMark':0, 'HyperMark':0}
        SampleNum=len(SampleNames)
        CellTypeHypoNum={}
        CellTypeHyperNum={}
        for CellTypeName in Groups:
            CellTypeHypoNum[CellTypeName]=0
            CellTypeHyperNum[CellTypeName]=0
        
        for chrome in ChromeArray:
            
            #statisticout.write(Starttime+" Generating Results for "+chrome+"\n")
            
            EntropyDEEDFile =open(tmpDMCfolder+chrome+".txt", 'r')  #Open the corresbondign methylation file
            CurrentCline=EntropyDEEDFile.readline()     #Read the first line (Colomn Name) of the methylation file
            CurrentCline=EntropyDEEDFile.readline()     # First data line

            InputFilename=InputFolder+chrome+".txt"
            InputFile=open(InputFilename,'r')
            RegionFileLine=InputFile.readline()
            while RegionFileLine:
                #chrM:33-14946 0.0 684 [0.009, 0.006, 0.009, 0.011,
                
                RegionFileLine=RegionFileLine.strip('\n')
                RegionFileLine=RegionFileLine.replace(":",'\t')
                RegionFileLine=RegionFileLine.replace('-','\t')
                RegionFileLine=RegionFileLine.replace(']','')
                RegionFileLine=RegionFileLine.replace("\'",'')
                RegionFileLine=RegionFileLine.replace('[','')
                RegionFileLine=RegionFileLine.replace(', ','\t')
                #print RegionFileLine
                CurrentRegionrawinfor=RegionFileLine.split('\t')
                RegionChrome=CurrentRegionrawinfor[0]
                RegionStart=int(CurrentRegionrawinfor[1])
                RegionEnd=int(CurrentRegionrawinfor[2])+2
                # Obtain the methylation level in a merged region in each group
                SegmentMethyMatrix=[]
                RegionCNum=0
                while CurrentCline:
                    #CurrentCline=CurrentCline.strip('\n')      #
                    MethyEntropyInfor=CurrentCline.split()
                    CurrentLocation=int(MethyEntropyInfor[1])+1
                    if (CurrentLocation >= RegionStart) and (CurrentLocation <= RegionEnd):  # Obtain the methylation level in a merged region in each group
                        SegmentMethyMatrix.append(MethyEntropyInfor[3:-3])
                        RegionCNum=RegionCNum+1
                        CurrentCline=EntropyDEEDFile.readline()
                    elif CurrentLocation < RegionStart:
                        CurrentCline=EntropyDEEDFile.readline()
                    else:
                        break
                
                # Output a segment with its mean methylation in each group, methylation specificity and p value
                Group_Key_Methyl = defaultdict(list)  # Record the methylation values in each group
                Group_Key_Methyl_forNAOVA = []
                #Group_Key_Methyl_new = dict(list)  # Record the methylation values in each group
                for eachCpG in SegmentMethyMatrix:
                    for sampleorder in range(SampleNum):
                        if eachCpG[sampleorder] != '-':
                            Group_Key_Methyl[Column_Key_Group[sampleorder]].append(float(eachCpG[sampleorder])) # This disc can be used to calculate mean methylation value and compare them across groups
                            Group_Key_Methyl_forNAOVA.append([Column_Key_Group[sampleorder],float(eachCpG[sampleorder])])
                            #Group_Key_Methyl_new[Column_Key_Group[sampleorder]].append(float(eachCpG[sampleorder])) # This disc can be used to calculate mean methylation value and compare them across groups  
                #Mean methylation
                MethylationRawList=[]  # Order the same with Groups
                Group_Methyl_mean_out=[]  # Order the same with Groups
                for eachgroup in Groups:
                    if Group_Key_Methyl[eachgroup]:
                        MethylationRawList.append(round(np.mean(Group_Key_Methyl[eachgroup]),3))  # for calculation of methylation specificity
                        Group_Methyl_mean_out.append(round(np.mean(Group_Key_Methyl[eachgroup]),3))  # for output of methylation specificity
                    else:
                        Group_Methyl_mean_out.append('-')
                #Methylation specificity
   
                if len(MethylationRawList) > 0: # Avoid the errors induced by the short segment
    
                    MethySumListforEntropy=tuple(MethylationRawList)
                    MethySpecificity=round(1.0-Methyentropy.EntropyCalculate(MethySumListforEntropy),3)       #Calculate the new MethySpecificity for mean methylation     
                    #one-way ANOVA tests
                    Group_Key_Methyl_Frame =pd.DataFrame(Group_Key_Methyl_forNAOVA,columns=['Group', 'Methyl'])
                    #print Group_Key_Methyl_Frame
                    if np.std(Group_Key_Methyl_Frame['Methyl']) == 0:
                        NAOVA_pvalue=1.0
                    else:
                        mod = ols('Methyl ~ Group',data=Group_Key_Methyl_Frame).fit()
                        #print mod
                        try:
                            aov_table = sm.stats.anova_lm(mod, typ=2)
                            NAOVA_pvalue = aov_table['PR(>F)']['Group']
                            NAOVA_pvalue= "%.2e" % NAOVA_pvalue
                        except:
                            NAOVA_pvalue=1.0
                    
                    
                    
                    ## Normal_TB           
                    MethyList=[]
                    for CelltNum in range(0,len(MethylationRawList)):
                        MethylationRawList[CelltNum]=float(MethylationRawList[CelltNum])
                        MethyList.append(MethylationRawList[CelltNum])
                    MethydataSet=tuple(MethyList)              
                    Normal_TB_Entropy=MethyTB.EntropyCalculate(MethydataSet)
                    MethySpecificity=round(1.0-Normal_TB_Entropy[-1],3)       #Caculate the new MethySpecificity for mean methylation      
                    Tukey_biweight= float(Normal_TB_Entropy[-2])
                    RegionStrand='+'
                    MeanMethy=round(sum(MethylationRawList)/len(MethylationRawList),3)
                    if ((float(MethySpecificity) >= MSthreshold and float(NAOVA_pvalue) < p_DMR) or (float(MethySpecificity) >= ExtrmeMSthreshold and float(NAOVA_pvalue) < Extremep_DMR)):
                        RegionColor='0,0,255'
                        SpecificityState='DMR'
                        MethyState='DMR'
                        Numdec['DMR']=Numdec['DMR']+1
                    else:
                        SpecificityState='NonDMR'
                        Numdec['NonDMR']=Numdec['NonDMR']+1
                        if MeanMethy<=0.25:
                            RegionColor='0,255,0'
                            MethyState='UniHypo'
                            Numdec['UniHypo']=Numdec['UniHypo']+1
                        elif MeanMethy>0.25 and MeanMethy<=0.6:
                            RegionColor='34,139,34'
                            MethyState='UnipLow'
                            Numdec['UnipLow']=Numdec['UnipLow']+1
                        elif MeanMethy>0.6 and MeanMethy<=0.8:
                            RegionColor='255,165,0'
                            MethyState='UnipHigh'
                            Numdec['UnipHigh']=Numdec['UnipHigh']+1
                        else:
                            RegionColor='255,0,0'
                            MethyState='UniHyper'
                            Numdec['UniHyper']=Numdec['UniHyper']+1
                    SegmentLength=int(RegionEnd)-int(RegionStart)+1
                    ###Calculate the CellTypeSpecificityPvalue
                    Normalbase=Normal_TB_Entropy[0:-2]
                    NormalList=[]
                    for CelltNum in range(0,len(MethylationRawList)):
                        if Normalbase[CelltNum]>=0.5:
                            RandomLevel=random.randint(0,5)
                            if (RandomLevel==0):
                                NormalList.append(MethylationRawList[CelltNum])
                            elif(RandomLevel==1):
                                NormalList.append(MethylationRawList[CelltNum]+0.001)
                            elif(RandomLevel==2):
                                NormalList.append(MethylationRawList[CelltNum]-0.005)
                            elif(RandomLevel==3):
                                NormalList.append(MethylationRawList[CelltNum]-0.001)
                            elif(RandomLevel==4):
                                NormalList.append(MethylationRawList[CelltNum]+0.005)
                            else:
                                NormalList.append(MethylationRawList[CelltNum]-0.001)
                    #print NormalList
                    CellTypeSpecificityPvalueList=[]                    
                    for CelltNum in range(0,len(MethylationRawList)):
                        CellTypeName=Groups[CelltNum]
                        Methylation=MethylationRawList[CelltNum]
                        if Normalbase[CelltNum]>=0.5:
                            CellTypeSpecificityPvalueList.append('1')
                        else:
                            a=NormalList
                            axis=0
                            a, axis = DeNovoDMR_Calling()._chk_asarray(a, axis)
                            n=a.shape[axis]
                            v = np.var(a, axis, ddof=1)
                            denom = np.sqrt(v / float(n))
                            if denom==0:
                                pvalue=1
                            else:
                                one_sample_Ttest=stats.ttest_1samp(NormalList,float(Methylation))
                                pvalue=one_sample_Ttest[1]                                
                            if (pvalue==0):
                                pvalue=1.0e-100
                            if ((Tukey_biweight-Methylation)>=0.3):
                                CellTypeSpecificityPvalueList.append('-'+"{:.2e}".format(pvalue))
                                Pvalueformated="{:.2e}".format(pvalue)
                                MethyMarkType="HypoMark"
                            elif ((Methylation-Tukey_biweight)>=0.3):
                                CellTypeSpecificityPvalueList.append("{:.2e}".format(pvalue))
                                Pvalueformated="{:.2e}".format(pvalue)
                                MethyMarkType="HyperMark"
                            #Only output the segment with more than 5 CpGs and 20bp
                            if (float(MethySpecificity) >= MSthreshold and float(NAOVA_pvalue) < p_DMR and int(RegionCNum)>=SCthreshold and int(SegmentLength)>=SLthreshold and pvalue < p_MethylMark and abs(Methylation-Tukey_biweight)>=0.3):
                            #if (float(MethySpecificity)>=0.5 and int(RegionCNum)>=10 and int(SegmentLength)>=20):
                                SegmentCellTypeMethymarkPvalue.write(RegionChrome+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+SpecificityState+"\t"+CellTypeName+"\t"+MethyMarkType+"\t"+Pvalueformated+"\n")
                                Numdec['MethyMark']=Numdec['MethyMark']+1
                                if MethyMarkType=="HypoMark":
                                    Numdec['HypoMark']=Numdec['HypoMark']+1
                                    CellTypeHypoNum[CellTypeName]=CellTypeHypoNum[CellTypeName]+1
                                elif MethyMarkType=="HyperMark":
                                    Numdec['HyperMark']=Numdec['HyperMark']+1
                                    CellTypeHyperNum[CellTypeName]=CellTypeHyperNum[CellTypeName]+1                         
                    ##############OUTPUT
                    Methydata=''
                    for GroupOrder in range(len(MethylationRawList)):
                        MethylationRawList[GroupOrder]=str(MethylationRawList[GroupOrder])
                    Methydata=','.join(MethylationRawList)
                    
                    if (int(RegionCNum) >= SCthreshold and int(SegmentLength) >= SLthreshold):   #Only output the segment with more than 5 CpGs and 20bp
                        Numdec['MergedSegment']=Numdec['MergedSegment']+1
                        RegionName=MethyState+':S='+str(round(MethySpecificity,1))+',M='+str(round(MeanMethy,1))+',L='+str(SegmentLength)
                        ##########Output the segments with core infor
                        BedOutFile.write(RegionChrome+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+RegionName+"\t"+str(int(MeanMethy*1000))+"\t"+RegionStrand+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+RegionColor+"\n")
                        MergedSegmentOutFile.write(RegionChrome+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+SpecificityState+"\t"+MethyState+"\t"+str(MethySpecificity)+"\t"+str(NAOVA_pvalue)+"\t"+str(MeanMethy)+"\t"+"\t"+str(RegionCNum)+"\t"+str(SegmentLength)+"\n")
                        ##########Output the segments with core infor and methylation data
                        DMR_methyl_OutFile.write(RegionChrome+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+SpecificityState+"\t"+MethyState+"\t"+str(MethySpecificity)+"\t"+str(NAOVA_pvalue)+"\t"+str(MeanMethy)+"\t"+"\t"+str(RegionCNum)+"\t"+str(SegmentLength)+"\t"+Methydata+"\n")
                        ##########Output the segments with core infor and cell-type-specificity
                        if (float(MethySpecificity)>=MSthreshold and float(NAOVA_pvalue) < p_DMR):
                            CellTypeSpecificityPvalue=','.join(CellTypeSpecificityPvalueList)
                            DMR_Specificity_OutFile.write(RegionChrome+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+SpecificityState+"\t"+MethyState+"\t"+str(MethySpecificity)+"\t"+str(NAOVA_pvalue)+"\t"+str(MeanMethy)+"\t"+str(RegionCNum)+"\t"+str(SegmentLength)+"\t"+CellTypeSpecificityPvalue+"\n")
                
                RegionFileLine=InputFile.readline()
            Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
            print Starttime+" Finish DMR identification for "+chrome
        #print Numdec
        return Numdec,CellTypeHypoNum,CellTypeHyperNum


    def DeNovoFinalResult_MultiProgress_Chrome(self,chrome,tmpFolder,SampleNames,Groups,Column_Key_Group,MSthreshold,SCthreshold,SLthreshold,p_DMR,p_MethylMark,Case_control_matrix,p_DMR_CaseControl,AbsMeanMethDiffer):
        '''
        
        '''
#         Extremep_DMR=p_DMR*0.00000000000000000001
#         ExtrmeMSthreshold=MSthreshold/3
        MethyTB=NewEntropyNormal.Entropy()
        Methyentropy=NewEntropy.Entropy()
        Numdec={'MergedSegment':0, 'DMR':0, 'NonDMR':0, 'UniHypo':0, 'UnipLow':0,'UnipHigh':0,'UniHyper':0, 'MethyMark':0, 'HypoMark':0, 'HyperMark':0}
        SampleNum=len(SampleNames)
        CellTypeHypoNum={}
        CellTypeHyperNum={}
        for CellTypeName in Groups:
            CellTypeHypoNum[CellTypeName]=0
            CellTypeHyperNum[CellTypeName]=0

        tmpDMCfolder=tmpFolder+'DifferMethlCpG/'
        InputFolder=tmpFolder+"MergedGenomeSegment/"
        tmpFinalResultsFolder=tmpFolder+"TmpFinalResults/"
        BedOutFile=open(tmpFinalResultsFolder+"2_MergedSegment_"+chrome+".bed",'wb') #Build  a bed file
        MergedSegmentOutFile=open(tmpFinalResultsFolder+"3_MergedSegment_Methylation_"+chrome+".txt",'wb') #Build a bed file    
        DMR_methyl_OutFile=open(tmpFinalResultsFolder+"4_MergedSegment_Group_Methyl_"+chrome+".txt",'wb') #Build  a bed file 
        DMR_Specificity_OutFile=open(tmpFinalResultsFolder+"5_DMR_Group_Specificity_"+chrome+".txt",'wb') #Build a bed file    
        SegmentCellTypeMethymarkPvalue=open(tmpFinalResultsFolder+"6_DMR_Methylmark_"+chrome+".txt",'wb') #Build a bed file  
        Case_control_results=open(tmpFinalResultsFolder+"7_DMR_Case_control_"+chrome+".txt",'wb') #Build a bed file     
        
        ## Obtain case-control pair
        Case_control_matrix_file=open(Case_control_matrix,'r') #Read Case control matrix for comparison
        Case_control_line = Case_control_matrix_file.readline()
        Case_control_Num = 0
        Case_list = []
        Cont_list = []
        while Case_control_line:
            Case_control_Num = Case_control_Num + 1
            Case_control_line=Case_control_line.strip('\n')
            Case_control_infor=Case_control_line.split('\t')
            Case_list.append(Case_control_infor[0])
            Cont_list.append(Case_control_infor[1])
            Case_control_line = Case_control_matrix_file.readline()
        Case_control_matrix_file.close()
        
        ## Read data
        EntropyDEEDFile =open(tmpDMCfolder+chrome+".txt", 'r')  #Open the corresbondign methylation file
        CurrentCline=EntropyDEEDFile.readline()     #Read the first line (Colomn Name) of the methylation file
        CurrentCline=EntropyDEEDFile.readline()     # First data line
        
        InputFilename=InputFolder+chrome+".txt"
        InputFile=open(InputFilename,'r')
        RegionFileLine=InputFile.readline()
        while RegionFileLine:
        #chrM:33-14946 0.0 684 [0.009, 0.006, 0.009, 0.011,
            
            RegionFileLine=RegionFileLine.strip('\n')
            RegionFileLine=RegionFileLine.replace(":",'\t')
            RegionFileLine=RegionFileLine.replace('-','\t')
            RegionFileLine=RegionFileLine.replace(']','')
            RegionFileLine=RegionFileLine.replace("\'",'')
            RegionFileLine=RegionFileLine.replace('[','')
            RegionFileLine=RegionFileLine.replace(', ','\t')
            #print RegionFileLine
            CurrentRegionrawinfor=RegionFileLine.split('\t')
            RegionChrome=CurrentRegionrawinfor[0]
            RegionStart=int(CurrentRegionrawinfor[1])
            RegionEnd=int(CurrentRegionrawinfor[2])+2
            SegmentLength=int(RegionEnd)-int(RegionStart)+1
            # Obtain the methylation level in a merged region in each group
            SegmentMethyMatrix=[]
            RegionCNum=0
            while CurrentCline:
                #CurrentCline=CurrentCline.strip('\n')      #
                MethyEntropyInfor=CurrentCline.split()
                CurrentLocation=int(MethyEntropyInfor[1])+1
                if (CurrentLocation >= RegionStart) and (CurrentLocation <= RegionEnd):  # Obtain the methylation level in a merged region in each group
                    SegmentMethyMatrix.append(MethyEntropyInfor[3:-3])
                    RegionCNum=RegionCNum+1
                    CurrentCline=EntropyDEEDFile.readline()
                elif CurrentLocation < RegionStart:
                    CurrentCline=EntropyDEEDFile.readline()
                else:
                    break
            
            # Output a segment with its mean methylation in each group, methylation specificity and p value
            Group_Key_Methyl = defaultdict(list)  # Record the methylation values in each group
            Sample_Key_Methyl = defaultdict(list)  # Record the methylation values in each sample
            Group_Key_Methyl_forNAOVA = []
            Sample_MethylationList=[] # Order the same with Samples
            #Group_Key_Methyl_new = dict(list)  # Record the methylation values in each group
            for eachCpG in SegmentMethyMatrix:
                for sampleorder in range(SampleNum):
                    if eachCpG[sampleorder] != '-':
                        Sample_Key_Methyl[sampleorder].append(float(eachCpG[sampleorder])) 
                        Group_Key_Methyl[Column_Key_Group[sampleorder]].append(float(eachCpG[sampleorder])) # This disc can be used to calculate mean methylation value and compare them across groups
                        Group_Key_Methyl_forNAOVA.append([Column_Key_Group[sampleorder],float(eachCpG[sampleorder])])
                        #Group_Key_Methyl_new[Column_Key_Group[sampleorder]].append(float(eachCpG[sampleorder])) # This disc can be used to calculate mean methylation value and compare them across groups  
            #print Group_Key_Methyl
            #{'HEK293T': [0.22, 0.19, 0.16, 0.24, 0.19, 0.14, 0.05, 0.0, 0.0, 0.09, 0.16, 0.26], 'HCC1187C': [0.15, 0.26, 0.17, 0.24, 0.08, 0.03, 0.16, 0.19]}
            
            #Sample mean methylation
            for sampleorder in range(SampleNum):
                if Sample_Key_Methyl[sampleorder]: ## If there are methylation values, calculate the mean methyaltion level for the segment in the sample
                    Sample_MethylationList.append(str(round(np.mean(Sample_Key_Methyl[sampleorder]),3)))  # mean methylation value
                else:
                    Sample_MethylationList.append('-')  # No value, use '-'
            Sample_Mean_Methydata=','.join(Sample_MethylationList)
                
            #Mean methylation
            MethylationRawList=[]  # Order the same with Groups
            MethylationRawList_out=[]  # Order the same with Groups
            Group_Methyl_mean_out=[]  # Order the same with Groups
            for eachgroup in Groups:
                if Group_Key_Methyl[eachgroup]:
                    MethylationRawList.append(round(np.mean(Group_Key_Methyl[eachgroup]),3))  # for calculation of methylation specificity
                    MethylationRawList_out.append(round(np.mean(Group_Key_Methyl[eachgroup]),3))  # for calculation of methylation specificity
                    Group_Methyl_mean_out.append(round(np.mean(Group_Key_Methyl[eachgroup]),3))  # for output of methylation specificity
                else:
                    Group_Methyl_mean_out.append('-')
                    MethylationRawList_out.append('-')   
            
            #Methylation specificity
            if len(MethylationRawList) > 0 and int(RegionCNum)>=SCthreshold and int(SegmentLength)>=SLthreshold: # Avoid the errors induced by the short segment and only output the segment with more than 5 CpGs and 20bp
                Numdec['MergedSegment']=Numdec['MergedSegment']+1
                MethySumListforEntropy=tuple(MethylationRawList)
                MethySpecificity=round(1.0-Methyentropy.EntropyCalculate(MethySumListforEntropy),3)       #Calculate the new MethySpecificity for mean methylation     
                #one-way ANOVA tests
                Group_Key_Methyl_Frame =pd.DataFrame(Group_Key_Methyl_forNAOVA,columns=['Group', 'Methyl'])
                #print Group_Key_Methyl_Frame
                if np.std(Group_Key_Methyl_Frame['Methyl']) == 0:
                    NAOVA_pvalue=1.0
                else:
                    mod = ols('Methyl ~ Group',data=Group_Key_Methyl_Frame).fit()
                    #print mod
                    try:
                        aov_table = sm.stats.anova_lm(mod, typ=2)
                        NAOVA_pvalue = aov_table['PR(>F)']['Group']
                        NAOVA_pvalue= "%.2e" % NAOVA_pvalue
                    except:
                        NAOVA_pvalue=1.0
                
                #Case_control_analysis
                for Case_control in range(0,Case_control_Num):
                    CaseGroup=Case_list[Case_control]
                    ContGroup=Cont_list[Case_control]                    
                    CaseGroup_CpGmethyl=Group_Key_Methyl[CaseGroup]
                    ContGroup_CpGmethyl=Group_Key_Methyl[ContGroup]
                    if len(CaseGroup_CpGmethyl) > 1 and len(ContGroup_CpGmethyl) > 1:
                        #print CaseGroup_CpGmethyl,ContGroup_CpGmethyl
                        TwoSampleTtest = stats.ttest_ind(CaseGroup_CpGmethyl, ContGroup_CpGmethyl, equal_var=False)
                        TwoSampleTtest_pvalue = "%.2e" % TwoSampleTtest[1]
                        CaseGroup_CpGmethyl_mean = round(np.mean(CaseGroup_CpGmethyl),3)
                        ContGroup_CpGmethyl_mean = round(np.mean(ContGroup_CpGmethyl),3)
                        MeanMethDiffer = CaseGroup_CpGmethyl_mean - ContGroup_CpGmethyl_mean
                        # DMR
                        if (abs(MeanMethDiffer) > AbsMeanMethDiffer) and ( float(TwoSampleTtest_pvalue) < p_DMR_CaseControl):
                            if MeanMethDiffer > 0:
                                Case_Status = "Hyper"
                            else:
                                Case_Status = "Hypo"
                            Case_control_results.write(RegionChrome+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+str(RegionCNum)+"\t"+str(SegmentLength)+"\t"+CaseGroup+"\t"+ContGroup+"\t"+Case_Status+"\t"+str(CaseGroup_CpGmethyl_mean)+"\t"+str(ContGroup_CpGmethyl_mean)+"\t"+str(MeanMethDiffer)+"\t"+TwoSampleTtest_pvalue+"\n")                        
                
                ## Normal_TB           
                MethyList=[]
                for CelltNum in range(0,len(MethylationRawList)):
                    MethylationRawList[CelltNum]=float(MethylationRawList[CelltNum])
                    MethyList.append(MethylationRawList[CelltNum])
                MethydataSet=tuple(MethyList)              
                Normal_TB_Entropy=MethyTB.EntropyCalculate(MethydataSet)
                MethySpecificity=round(1.0-Normal_TB_Entropy[-1],3)       #Calculate the new MethySpecificity for mean methylation      
                Tukey_biweight= float(Normal_TB_Entropy[-2])
                RegionStrand='+'
                MeanMethy=round(sum(MethylationRawList)/len(MethylationRawList),3)
#                 if (((float(MethySpecificity) >= MSthreshold) and (float(NAOVA_pvalue) < p_DMR)) or ((float(MethySpecificity) >= ExtrmeMSthreshold) and (float(NAOVA_pvalue) < Extremep_DMR))):
                if (float(MethySpecificity)>=MSthreshold and float(NAOVA_pvalue) < p_DMR):    
#                     print MethySpecificity,NAOVA_pvalue,p_DMR,MethySpecificity,ExtrmeMSthreshold,Extremep_DMR
                    RegionColor='0,0,255'
                    SpecificityState='DMR'
                    MethyState='DMR'
                    Numdec['DMR']=Numdec['DMR']+1
                else:
                    SpecificityState='NonDMR'
                    Numdec['NonDMR']=Numdec['NonDMR']+1
                    if MeanMethy<=0.25:
                        RegionColor='0,255,0'
                        MethyState='UniHypo'
                        Numdec['UniHypo']=Numdec['UniHypo']+1
                    elif MeanMethy>0.25 and MeanMethy<=0.6:
                        RegionColor='34,139,34'
                        MethyState='UnipLow'
                        Numdec['UnipLow']=Numdec['UnipLow']+1
                    elif MeanMethy>0.6 and MeanMethy<=0.8:
                        RegionColor='255,165,0'
                        MethyState='UnipHigh'
                        Numdec['UnipHigh']=Numdec['UnipHigh']+1
                    else:
                        RegionColor='255,0,0'
                        MethyState='UniHyper'
                        Numdec['UniHyper']=Numdec['UniHyper']+1
                
                ###Calculate the CellTypeSpecificityPvalue
                Normalbase=Normal_TB_Entropy[0:-2]
                NormalList=[]
                for CelltNum in range(0,len(MethylationRawList)):
                    if Normalbase[CelltNum]>=0.5:
                        RandomLevel=random.randint(0,5)
                        if (RandomLevel==0):
                            NormalList.append(MethylationRawList[CelltNum])
                        elif(RandomLevel==1):
                            NormalList.append(MethylationRawList[CelltNum]+0.001)
                        elif(RandomLevel==2):
                            NormalList.append(MethylationRawList[CelltNum]-0.005)
                        elif(RandomLevel==3):
                            NormalList.append(MethylationRawList[CelltNum]-0.001)
                        elif(RandomLevel==4):
                            NormalList.append(MethylationRawList[CelltNum]+0.005)
                        else:
                            NormalList.append(MethylationRawList[CelltNum]-0.001)
                #print NormalList
                CellTypeSpecificityPvalueList=[]                    
                for CelltNum in range(0,len(MethylationRawList)):
                    CellTypeName=Groups[CelltNum]
                    Methylation=MethylationRawList[CelltNum]
                    if Normalbase[CelltNum]>=0.5:
                        CellTypeSpecificityPvalueList.append('1')
                    else:
                        a=NormalList
                        axis=0
                        a, axis = DeNovoDMR_Calling()._chk_asarray(a, axis)
                        n=a.shape[axis]
                        v = np.var(a, axis, ddof=1)
                        denom = np.sqrt(v / float(n))
                        if denom==0:
                            pvalue=1
                        else:
                            one_sample_Ttest=stats.ttest_1samp(NormalList,float(Methylation))
                            pvalue=one_sample_Ttest[1]
                        if (pvalue==0):
                            pvalue=1.0e-100
                        if ((Tukey_biweight-Methylation)>=0.3):
                            CellTypeSpecificityPvalueList.append('-'+"{:.2e}".format(pvalue))
                            Pvalueformated="{:.2e}".format(pvalue)
                            MethyMarkType="HypoMark"
                        elif ((Methylation-Tukey_biweight)>=0.3):
                            CellTypeSpecificityPvalueList.append("{:.2e}".format(pvalue))
                            Pvalueformated="{:.2e}".format(pvalue)
                            MethyMarkType="HyperMark"
                        
                        if (float(MethySpecificity) >= MSthreshold and float(NAOVA_pvalue) < p_DMR and pvalue < p_MethylMark and abs(Methylation-Tukey_biweight)>=0.3):
                        #if (float(MethySpecificity)>=0.5 and int(RegionCNum)>=10 and int(SegmentLength)>=20):
                            SegmentCellTypeMethymarkPvalue.write(RegionChrome+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+SpecificityState+"\t"+CellTypeName+"\t"+MethyMarkType+"\t"+Pvalueformated+"\n")
                            Numdec['MethyMark']=Numdec['MethyMark']+1
                            if MethyMarkType=="HypoMark":
                                Numdec['HypoMark']=Numdec['HypoMark']+1
                                CellTypeHypoNum[CellTypeName]=CellTypeHypoNum[CellTypeName]+1
                            elif MethyMarkType=="HyperMark":
                                Numdec['HyperMark']=Numdec['HyperMark']+1
                                CellTypeHyperNum[CellTypeName]=CellTypeHyperNum[CellTypeName]+1                         
                ##############OUTPUT
                Methydata=''
                for GroupOrder in range(len(MethylationRawList_out)):
                    MethylationRawList_out[GroupOrder]=str(MethylationRawList_out[GroupOrder])
                Methydata=','.join(MethylationRawList_out)
                
                RegionName=MethyState+':S='+str(round(MethySpecificity,1))+',M='+str(round(MeanMethy,1))+',L='+str(SegmentLength)
                ##########Output the segments with core infor
                BedOutFile.write(RegionChrome+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+RegionName+"\t"+str(int(MeanMethy*1000))+"\t"+RegionStrand+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+RegionColor+"\n")
                ##########Output the segments with core infor and methylation data
                MergedSegmentOutFile.write(RegionChrome+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+SpecificityState+"\t"+MethyState+"\t"+str(MethySpecificity)+"\t"+str(NAOVA_pvalue)+"\t"+str(MeanMethy)+"\t"+str(RegionCNum)+"\t"+str(SegmentLength)+"\t"+Methydata+"\t"+Sample_Mean_Methydata+"\n")
                ##########Output the DMRs with core infor and methylation data
                #DMR_methyl_OutFile.write(RegionChrome+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+SpecificityState+"\t"+MethyState+"\t"+str(MethySpecificity)+"\t"+str(NAOVA_pvalue)+"\t"+str(MeanMethy)+"\t"+str(RegionCNum)+"\t"+str(SegmentLength)+"\t"+Methydata+"\n")
                ##########Output the segments with core infor and cell-type-specificity
                if (float(MethySpecificity)>=MSthreshold and float(NAOVA_pvalue) < p_DMR):
                    DMR_methyl_OutFile.write(RegionChrome+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+SpecificityState+"\t"+MethyState+"\t"+str(MethySpecificity)+"\t"+str(NAOVA_pvalue)+"\t"+str(MeanMethy)+"\t"+str(RegionCNum)+"\t"+str(SegmentLength)+"\t"+Methydata+"\t"+Sample_Mean_Methydata+"\n")
                    CellTypeSpecificityPvalue=','.join(CellTypeSpecificityPvalueList)
                    DMR_Specificity_OutFile.write(RegionChrome+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+SpecificityState+"\t"+MethyState+"\t"+str(MethySpecificity)+"\t"+str(NAOVA_pvalue)+"\t"+str(MeanMethy)+"\t"+str(RegionCNum)+"\t"+str(SegmentLength)+"\t"+Methydata+"\t"+CellTypeSpecificityPvalue+"\n")
        
            RegionFileLine=InputFile.readline()
        
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Finish DMR identification for "+chrome
        #print Numdec
        return Numdec

    def DeNovoFinalResult_MultiProgress(self,tmpFolder,BedOutFile,MergedSegmentOutFile,DMR_methyl_OutFile,DMR_Specificity_OutFile,SegmentCellTypeMethymarkPvalue,ChromeArray,SampleNames,Groups,Column_Key_Group,MSthreshold,SCthreshold,SLthreshold,p_DMR,p_MethylMark,statisticout,Case_control_matrix,Case_control_results,p_DMR_CaseControl,AbsMeanMethDiffer):
        '''
        
        '''
#         Extremep_DMR=p_DMR/0.00000000000000000001
#         ExtrmeMSthreshold=MSthreshold/3
#         MethyTB=NewEntropyNormal.Entropy()
#         Methyentropy=NewEntropy.Entropy()
        Total_Numdec={'MergedSegment':0, 'DMR':0, 'NonDMR':0, 'UniHypo':0, 'UnipLow':0,'UnipHigh':0,'UniHyper':0, 'MethyMark':0, 'HypoMark':0, 'HyperMark':0}
        Numdec_Keys=Total_Numdec.keys()

        tmpFinalResultsFolder=tmpFolder+"TmpFinalResults/"
        CellTypeHypoNum={}
        CellTypeHyperNum={}
        for CellTypeName in Groups:
            CellTypeHypoNum[CellTypeName]=0
            CellTypeHyperNum[CellTypeName]=0
            
        ## Obtain case-control pair    
        Case_Control_Hypo_Num={}
        Case_Control_Hyper_Num={}        
        Case_control_matrix_file=open(Case_control_matrix,'r') #Read Case control matrix for comparison
        Case_control_line = Case_control_matrix_file.readline()
        while Case_control_line:
            Case_control_line=Case_control_line.strip('\n')
            Case_control_infor=Case_control_line.split('\t')
            Case_Control_Hypo_Num[Case_control_infor[0]+"_"+Case_control_infor[1]]=0
            Case_Control_Hyper_Num[Case_control_infor[0]+"_"+Case_control_infor[1]]=0
            Case_control_line = Case_control_matrix_file.readline()
        Case_control_matrix_file.close()
        
        pool = Pool(len(ChromeArray))
        tasks=[]
        for chrome in ChromeArray:
            tasks.append((chrome,tmpFolder,SampleNames,Groups,Column_Key_Group,MSthreshold,SCthreshold,SLthreshold,p_DMR,p_MethylMark,Case_control_matrix,p_DMR_CaseControl,AbsMeanMethDiffer))
            
        Chrome_Numdec=pool.map(multi_final_results,tasks)
        pool.close()
        
        #Combine all chrome results
        for chrome in ChromeArray:
            BedOutFile_chrome=open(tmpFinalResultsFolder+"2_MergedSegment_"+chrome+".bed",'r') #Build  a bed file
            MergedSegmentOutFile_chrome=open(tmpFinalResultsFolder+"3_MergedSegment_Methylation_"+chrome+".txt",'r') #Build a bed file    
            DMR_methyl_OutFile_chrome=open(tmpFinalResultsFolder+"4_MergedSegment_Group_Methyl_"+chrome+".txt",'r') #Build  a bed file 
            DMR_Specificity_OutFile_chrome=open(tmpFinalResultsFolder+"5_DMR_Group_Specificity_"+chrome+".txt",'r') #Build a bed file    
            SegmentCellTypeMethymarkPvalue_chrome=open(tmpFinalResultsFolder+"6_DMR_Methylmark_"+chrome+".txt",'r') #Build a bed file  
            Case_control_results_chrome=open(tmpFinalResultsFolder+"7_DMR_Case_control_"+chrome+".txt",'r') #Build a bed file  
            
            CurrentCline=BedOutFile_chrome.readline()
            while CurrentCline:
                BedOutFile.write(CurrentCline)
                CurrentCline=BedOutFile_chrome.readline()
            
            CurrentCline=MergedSegmentOutFile_chrome.readline()
            while CurrentCline:
                MergedSegmentOutFile.write(CurrentCline)
                CurrentCline=MergedSegmentOutFile_chrome.readline()
                
            CurrentCline=DMR_methyl_OutFile_chrome.readline()
            while CurrentCline:
                DMR_methyl_OutFile.write(CurrentCline)
                CurrentCline=DMR_methyl_OutFile_chrome.readline()
            
            CurrentCline=Case_control_results_chrome.readline()
            while CurrentCline:
                Case_control_results.write(CurrentCline)
                CurrentCline=CurrentCline.strip('\n')
                Markinfor=CurrentCline.split('\t')
                if Markinfor[7]=="Hypo":
                    Case_Control_Hypo_Num[Markinfor[5]+"_"+Markinfor[6]]=Case_Control_Hypo_Num[Markinfor[5]+"_"+Markinfor[6]]+1
                elif Markinfor[7]=="Hyper":
                    Case_Control_Hyper_Num[Markinfor[5]+"_"+Markinfor[6]]=Case_Control_Hyper_Num[Markinfor[5]+"_"+Markinfor[6]]+1  
                CurrentCline=Case_control_results_chrome.readline()
            
            CurrentCline=DMR_Specificity_OutFile_chrome.readline()
            while CurrentCline:
                DMR_Specificity_OutFile.write(CurrentCline)   
                CurrentCline=DMR_Specificity_OutFile_chrome.readline()
            
            CurrentCline=SegmentCellTypeMethymarkPvalue_chrome.readline()
            while CurrentCline:
                SegmentCellTypeMethymarkPvalue.write(CurrentCline)
                CurrentCline=CurrentCline.strip('\n')
                Markinfor=CurrentCline.split('\t')
                if Markinfor[5]=="HypoMark":
                    CellTypeHypoNum[Markinfor[4]]=CellTypeHypoNum[Markinfor[4]]+1
                elif Markinfor[5]=="HyperMark":
                    CellTypeHyperNum[Markinfor[4]]=CellTypeHyperNum[Markinfor[4]]+1
                CurrentCline=SegmentCellTypeMethymarkPvalue_chrome.readline()
        
        for eachChrome in Chrome_Numdec:
            for eachKey in Numdec_Keys:
                Total_Numdec[eachKey]=Total_Numdec[eachKey]+eachChrome[eachKey]
        
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Finish DMR identification for all chromesomes"
        return Total_Numdec,CellTypeHypoNum,CellTypeHyperNum,Case_Control_Hyper_Num,Case_Control_Hypo_Num


    def DM_ROI(self, tmpDMCfolder,GenomeRegions,GenomeRegionFolder,BedOutFile,MergedSegmentOutFile,DMR_methyl_OutFile,DMR_Specificity_OutFile,SegmentCellTypeMethymarkPvalue,ChromeArray,SampleNames,Groups,Column_Key_Group,MSthreshold,SCthreshold,SLthreshold,p_DMR,p_MethylMark,statisticout,Case_control_matrix,Case_control_results,p_DMR_CaseControl,AbsMeanMethDiffer):
        '''
        
        '''
        ### Split genome region file into chromes
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Start to check genome region file ..."
        statisticout.write(Starttime+" Start to check genome region file...\n")
        #RawMethyDataFolderName=MethyDataFolder+'*.wig'
        GenomeRegionsInput=open(GenomeRegions,'rb') #open the genome region file 
        TotalRegionNum=0
        CurrentStr='chr'
        ROI_ChromeArray=[]
        if GenomeRegionFolder:
            # use a output directory to store Splited Methylation data 
            if not os.path.exists( GenomeRegionFolder ):
                try:
                    os.makedirs( GenomeRegionFolder )
                except:
                    sys.exit( "Output directory (%s) could not be created. Terminating program." % GenomeRegionFolder )
        filecontent=GenomeRegionsInput.readline()
        while filecontent:
            TotalRegionNum=TotalRegionNum+1
            filecontent=filecontent.strip('\n')
            currentRegion=filecontent.split('\t')
            chrome=currentRegion[0]
            if chrome != CurrentStr:  #If search a new chrome,
                ROI_ChromeArray.append(chrome)
                CurrentStr=chrome
                Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
                print Starttime+" Start checking regions in: "+chrome
                statisticout.write(Starttime+" Start checking regions in: "+chrome+"\n")
                chromeregionfile=GenomeRegionFolder+chrome+".txt"
                #print chromemethyfile
                chromeregionfile_out=open(chromeregionfile,'wb')
            # Data output
            chromeregionfile_out.write(filecontent+"\n")
            # Next
            filecontent=GenomeRegionsInput.readline()
        chromeregionfile_out.close()
        GenomeRegionsInput.close()
        
        ##Obtain common chromesomes between methylation file and ROI file
        commonChrome=[]
        for eachROIchrome in ROI_ChromeArray:
            for eachCpGchrome in ChromeArray:
                if eachROIchrome==eachCpGchrome:
                    commonChrome.append(eachROIchrome)
        
        ### Start to process methylation data
        if len(commonChrome)==0:
            print ""
            sys.exit( "[Error:] ROI file (%s) have no regions corresponding CpG sites in the methylation data. Terminating program." % GenomeRegions )
            
        else:    
            Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
            print Starttime+" Start to identify DM ROIs ..."
            statisticout.write(Starttime+" Start to identify DM ROIs...\n")
            MethyTB=NewEntropyNormal.Entropy()
            Methyentropy=NewEntropy.Entropy()
            Numdec={'AvilableGenomeRegion':0, 'DMR':0, 'NonDMR':0, 'UniHypo':0, 'UnipLow':0,'UnipHigh':0,'UniHyper':0, 'MethyMark':0, 'HypoMark':0, 'HyperMark':0}
            SampleNum=len(SampleNames)
            CellTypeHypoNum={}
            CellTypeHyperNum={}
            for CellTypeName in Groups:
                CellTypeHypoNum[CellTypeName]=0
                CellTypeHyperNum[CellTypeName]=0     
        
            ## Obtain case-control pair
            Case_control_matrix_file=open(Case_control_matrix,'r') #Read Case control matrix for comparison
            Case_control_line = Case_control_matrix_file.readline()
            Case_control_Num = 0
            Case_list = []
            Cont_list = []
            Case_Control_Hypo_Num={}
            Case_Control_Hyper_Num={}
            while Case_control_line:
                Case_control_Num = Case_control_Num + 1
                Case_control_line=Case_control_line.strip('\n')
                Case_control_infor=Case_control_line.split('\t')
                Case_list.append(Case_control_infor[0])
                Cont_list.append(Case_control_infor[1])
                Case_Control_Hypo_Num[Case_control_infor[0]+"_"+Case_control_infor[1]]=0
                Case_Control_Hyper_Num[Case_control_infor[0]+"_"+Case_control_infor[1]]=0
                Case_control_line = Case_control_matrix_file.readline()
            Case_control_matrix_file.close()

            
            for chrome in commonChrome:              
                # Open the region file in chrome
                chromeregionfile_input=open(GenomeRegionFolder+chrome+".txt",'r')
                
                
#                 Case_control_results=open(tmpFinalResultsFolder+"7_DMR_Case_control_"+chrome+".txt",'wb') #Build a bed file
                
                #Open the correspond methylation file
                EntropyDEEDFile =open(tmpDMCfolder+chrome+".txt", 'r')  
                CurrentCline=EntropyDEEDFile.readline()     #Read the first line (Colomn Name) of the methylation file
                CurrentCline=EntropyDEEDFile.readline()     # First data line
    
                RegionFileLine=chromeregionfile_input.readline()
                while RegionFileLine:
                    #chr1    100000    100300
                    filecontent=RegionFileLine.strip('\n')
                    CurrentRegionrawinfor=filecontent.split('\t')
                    if (len(CurrentRegionrawinfor)>=3):
                        RegionChrome=CurrentRegionrawinfor[0]
                        RegionStart=int(CurrentRegionrawinfor[1])
                        RegionEnd=int(CurrentRegionrawinfor[2])
                        # Obtain the methylation level in a merged region in each group
                        SegmentMethyMatrix=[]
                        RegionCNum=0
                        while CurrentCline:
                            #CurrentCline=CurrentCline.strip('\n')      #
                            MethyEntropyInfor=CurrentCline.split()
                            CurrentLocation=int(MethyEntropyInfor[1])+1
                            if (CurrentLocation >= RegionStart) and (CurrentLocation <= RegionEnd):  # Obtain the methylation level in a merged region in each group
                                SegmentMethyMatrix.append(MethyEntropyInfor[3:-3])
                                RegionCNum=RegionCNum+1
                                CurrentCline=EntropyDEEDFile.readline()
                            elif CurrentLocation < RegionStart:
                                CurrentCline=EntropyDEEDFile.readline()
                            else:
                                break
                        
                        # Output a segment with its mean methylation in each group, methylation specificity and p value
                        Group_Key_Methyl = defaultdict(list)  # Record the methylation values in each group
                        Sample_Key_Methyl = defaultdict(list)  # Record the methylation values in each sample
                        Group_Key_Methyl_forNAOVA = []
                        Sample_MethylationList=[] # Order the same with Samples
                        #Group_Key_Methyl_new = dict(list)  # Record the methylation values in each group
                        for eachCpG in SegmentMethyMatrix:
                            for sampleorder in range(SampleNum):
                                if eachCpG[sampleorder] != '-':
                                    Sample_Key_Methyl[sampleorder].append(float(eachCpG[sampleorder])) 
                                    Group_Key_Methyl[Column_Key_Group[sampleorder]].append(float(eachCpG[sampleorder])) # This disc can be used to calculate mean methylation value and compare them across groups
                                    Group_Key_Methyl_forNAOVA.append([Column_Key_Group[sampleorder],float(eachCpG[sampleorder])])
                                    #Group_Key_Methyl_new[Column_Key_Group[sampleorder]].append(float(eachCpG[sampleorder])) # This disc can be used to calculate mean methylation value and compare them across groups  
                        #Sample mean methylation
                        for sampleorder in range(SampleNum):
                            if Sample_Key_Methyl[sampleorder]: ## If there are methylation values, calculate the mean methyaltion level for the segment in the sample
                                Sample_MethylationList.append(str(round(np.mean(Sample_Key_Methyl[sampleorder]),3)))  # mean methylation value
                            else:
                                Sample_MethylationList.append('-')  # No value, use '-'
                        Sample_Mean_Methydata=','.join(Sample_MethylationList)
                        
                        #Mean methylation
                        MethylationRawList=[]  # Order the same with Groups
                        MethylationRawList_out=[]  # Order the same with Groups
                        Group_Methyl_mean_out=[]  # Order the same with Groups
                        for eachgroup in Groups:
                            if Group_Key_Methyl[eachgroup]:
                                MethylationRawList.append(round(np.mean(Group_Key_Methyl[eachgroup]),3))  # for calculation of methylation specificity
                                MethylationRawList_out.append(round(np.mean(Group_Key_Methyl[eachgroup]),3))  # for calculation of methylation specificity
                                Group_Methyl_mean_out.append(round(np.mean(Group_Key_Methyl[eachgroup]),3))  # for output of methylation specificity
                            else:
                                Group_Methyl_mean_out.append('-')
                                MethylationRawList_out.append('-')
                                
                        #Methylation specificity
                        if len(MethylationRawList) > 0: # Avoid the errors induced by the short segment
                            Numdec['AvilableGenomeRegion']=Numdec['AvilableGenomeRegion']+1
                            MethySumListforEntropy=tuple(MethylationRawList)
                            MethySpecificity=round(1.0-Methyentropy.EntropyCalculate(MethySumListforEntropy),3)       #Calculate the new MethySpecificity for mean methylation     
                            #one-way ANOVA tests
                            Group_Key_Methyl_Frame =pd.DataFrame(Group_Key_Methyl_forNAOVA,columns=['Group', 'Methyl'])
                            #print Group_Key_Methyl_Frame
                            if np.std(Group_Key_Methyl_Frame['Methyl']) == 0:
                                NAOVA_pvalue=1.0
                            else:
                                mod = ols('Methyl ~ Group',data=Group_Key_Methyl_Frame).fit()
                                #print mod
                                try:
                                    aov_table = sm.stats.anova_lm(mod, typ=2)
                                    NAOVA_pvalue = aov_table['PR(>F)']['Group']
                                    NAOVA_pvalue= "%.2e" % NAOVA_pvalue
                                except:
                                    NAOVA_pvalue=1.0
                            
                            #Case_control_analysis
                            for Case_control in range(0,Case_control_Num):
                                CaseGroup=Case_list[Case_control]
                                ContGroup=Cont_list[Case_control]                    
                                CaseGroup_CpGmethyl=Group_Key_Methyl[CaseGroup]
                                ContGroup_CpGmethyl=Group_Key_Methyl[ContGroup]
                                if len(CaseGroup_CpGmethyl) > 1 and len(ContGroup_CpGmethyl) > 1:
                                    #print CaseGroup_CpGmethyl,ContGroup_CpGmethyl
                                    TwoSampleTtest = stats.ttest_ind(CaseGroup_CpGmethyl, ContGroup_CpGmethyl, equal_var=False)
                                    TwoSampleTtest_pvalue = "%.2e" % TwoSampleTtest[1]
                                    CaseGroup_CpGmethyl_mean = round(np.mean(CaseGroup_CpGmethyl),3)
                                    ContGroup_CpGmethyl_mean = round(np.mean(ContGroup_CpGmethyl),3)
                                    MeanMethDiffer = CaseGroup_CpGmethyl_mean - ContGroup_CpGmethyl_mean
                                    # DMR
                                    if (abs(MeanMethDiffer) > AbsMeanMethDiffer) and ( float(TwoSampleTtest_pvalue) < p_DMR_CaseControl):
                                        if MeanMethDiffer > 0:
                                            Case_Status = "Hyper"
                                            Case_Control_Hyper_Num[CaseGroup+"_"+ContGroup]=Case_Control_Hyper_Num[CaseGroup+"_"+ContGroup]+1
                                        else:
                                            Case_Status = "Hypo"
                                            Case_Control_Hypo_Num[CaseGroup+"_"+ContGroup]=Case_Control_Hypo_Num[CaseGroup+"_"+ContGroup]+1
                                        Case_control_results.write(RegionChrome+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+str(RegionCNum)+"\t"+str(RegionEnd-RegionStart+1)+"\t"+CaseGroup+"\t"+ContGroup+"\t"+Case_Status+"\t"+str(CaseGroup_CpGmethyl_mean)+"\t"+str(ContGroup_CpGmethyl_mean)+"\t"+str(MeanMethDiffer)+"\t"+TwoSampleTtest_pvalue+"\n")                                                    
                            
                            ## Normal_TB           
                            MethyList=[]
                            for CelltNum in range(0,len(MethylationRawList)):
                                MethylationRawList[CelltNum]=float(MethylationRawList[CelltNum])
                                MethyList.append(MethylationRawList[CelltNum])
                            MethydataSet=tuple(MethyList)              
                            Normal_TB_Entropy=MethyTB.EntropyCalculate(MethydataSet)
                            MethySpecificity=round(1.0-Normal_TB_Entropy[-1],3)       #Calculate the new MethySpecificity for mean methylation      
                            Tukey_biweight= float(Normal_TB_Entropy[-2])
                            RegionStrand='+'
                            MeanMethy=round(sum(MethylationRawList)/len(MethylationRawList),3)
                            if (float(MethySpecificity) >= MSthreshold and float(NAOVA_pvalue) < p_DMR):
                                RegionColor='0,0,255'
                                SpecificityState='DMR'
                                MethyState='DMR'
                                Numdec['DMR']=Numdec['DMR']+1
                            else:
                                SpecificityState='NonDMR'
                                Numdec['NonDMR']=Numdec['NonDMR']+1
                                if MeanMethy<=0.25:
                                    RegionColor='0,255,0'
                                    MethyState='UniHypo'
                                    Numdec['UniHypo']=Numdec['UniHypo']+1
                                elif MeanMethy>0.25 and MeanMethy<=0.6:
                                    RegionColor='34,139,34'
                                    MethyState='UnipLow'
                                    Numdec['UnipLow']=Numdec['UnipLow']+1
                                elif MeanMethy>0.6 and MeanMethy<=0.8:
                                    RegionColor='255,165,0'
                                    MethyState='UnipHigh'
                                    Numdec['UnipHigh']=Numdec['UnipHigh']+1
                                else:
                                    RegionColor='255,0,0'
                                    MethyState='UniHyper'
                                    Numdec['UniHyper']=Numdec['UniHyper']+1
                            SegmentLength=int(RegionEnd)-int(RegionStart)+1
                            ###Calculate the CellTypeSpecificityPvalue
                            Normalbase=Normal_TB_Entropy[0:-2]
                            NormalList=[]
                            for CelltNum in range(0,len(MethylationRawList)):
                                if Normalbase[CelltNum]>=0.5:
                                    RandomLevel=random.randint(0,5)
                                    if (RandomLevel==0):
                                        NormalList.append(MethylationRawList[CelltNum])
                                    elif(RandomLevel==1):
                                        NormalList.append(MethylationRawList[CelltNum]+0.001)
                                    elif(RandomLevel==2):
                                        NormalList.append(MethylationRawList[CelltNum]-0.005)
                                    elif(RandomLevel==3):
                                        NormalList.append(MethylationRawList[CelltNum]-0.001)
                                    elif(RandomLevel==4):
                                        NormalList.append(MethylationRawList[CelltNum]+0.005)
                                    else:
                                        NormalList.append(MethylationRawList[CelltNum]-0.001)
                            #print NormalList
                            CellTypeSpecificityPvalueList=[]                    
                            for CelltNum in range(0,len(MethylationRawList)):
                                CellTypeName=Groups[CelltNum]
                                Methylation=MethylationRawList[CelltNum]
                                if Normalbase[CelltNum]>=0.5:
                                    CellTypeSpecificityPvalueList.append('1')
                                else:
                                    a=NormalList
                                    axis=0
                                    a, axis = DeNovoDMR_Calling()._chk_asarray(a, axis)
                                    n=a.shape[axis]
                                    v = np.var(a, axis, ddof=1)
                                    denom = np.sqrt(v / float(n))
                                    if denom==0:
                                        pvalue=1
                                    else:
                                        one_sample_Ttest=stats.ttest_1samp(NormalList,float(Methylation))
                                        pvalue=one_sample_Ttest[1]
                                    if (pvalue==0):
                                        pvalue=1.0e-100
                                    if ((Tukey_biweight-Methylation)>=0.3):
                                        CellTypeSpecificityPvalueList.append('-'+"{:.2e}".format(pvalue))
                                        Pvalueformated="{:.2e}".format(pvalue)
                                        MethyMarkType="HypoMark"
                                    elif ((Methylation-Tukey_biweight)>=0.3):
                                        CellTypeSpecificityPvalueList.append("{:.2e}".format(pvalue))
                                        Pvalueformated="{:.2e}".format(pvalue)
                                        MethyMarkType="HyperMark"
                                    #Only output the segment with more than 5 CpGs and 20bp
                                    if (float(MethySpecificity) >= MSthreshold and float(NAOVA_pvalue) < p_DMR and pvalue < p_MethylMark and abs(Methylation-Tukey_biweight)>=0.3):
                                    #if (float(MethySpecificity)>=0.5 and int(RegionCNum)>=10 and int(SegmentLength)>=20):
                                        SegmentCellTypeMethymarkPvalue.write(RegionChrome+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+SpecificityState+"\t"+CellTypeName+"\t"+MethyMarkType+"\t"+Pvalueformated+"\n")
                                        Numdec['MethyMark']=Numdec['MethyMark']+1
                                        if MethyMarkType=="HypoMark":
                                            Numdec['HypoMark']=Numdec['HypoMark']+1
                                            CellTypeHypoNum[CellTypeName]=CellTypeHypoNum[CellTypeName]+1
                                        elif MethyMarkType=="HyperMark":
                                            Numdec['HyperMark']=Numdec['HyperMark']+1
                                            CellTypeHyperNum[CellTypeName]=CellTypeHyperNum[CellTypeName]+1                         
                            ##############OUTPUT
                            Methydata=''
                            for GroupOrder in range(len(MethylationRawList_out)):
                                MethylationRawList_out[GroupOrder]=str(MethylationRawList_out[GroupOrder])
                            Methydata=','.join(MethylationRawList_out)
                            
                            RegionName=MethyState+':S='+str(round(MethySpecificity,1))+',M='+str(round(MeanMethy,1))+',L='+str(SegmentLength)
                            ##########Output the segments with core infor
                            BedOutFile.write(RegionChrome+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+RegionName+"\t"+str(int(MeanMethy*1000))+"\t"+RegionStrand+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+RegionColor+"\n")
                            ##########Output the segments with core infor and methylation data
                            MergedSegmentOutFile.write(RegionChrome+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+SpecificityState+"\t"+MethyState+"\t"+str(MethySpecificity)+"\t"+str(NAOVA_pvalue)+"\t"+str(MeanMethy)+"\t"+str(RegionCNum)+"\t"+str(SegmentLength)+"\t"+Methydata+"\t"+Sample_Mean_Methydata+"\n")
                            ##########Output the DMRs with core infor and methylation data
                            #DMR_methyl_OutFile.write(RegionChrome+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+SpecificityState+"\t"+MethyState+"\t"+str(MethySpecificity)+"\t"+str(NAOVA_pvalue)+"\t"+str(MeanMethy)+"\t"+str(RegionCNum)+"\t"+str(SegmentLength)+"\t"+Methydata+"\n")
                            ##########Output the segments with core infor and cell-type-specificity
                            if (float(MethySpecificity)>=MSthreshold and float(NAOVA_pvalue) < p_DMR):
                                DMR_methyl_OutFile.write(RegionChrome+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+SpecificityState+"\t"+MethyState+"\t"+str(MethySpecificity)+"\t"+str(NAOVA_pvalue)+"\t"+str(MeanMethy)+"\t"+str(RegionCNum)+"\t"+str(SegmentLength)+"\t"+Methydata+"\t"+Sample_Mean_Methydata+"\n")
                                CellTypeSpecificityPvalue=','.join(CellTypeSpecificityPvalueList)
                                DMR_Specificity_OutFile.write(RegionChrome+"\t"+str(RegionStart)+"\t"+str(RegionEnd)+"\t"+SpecificityState+"\t"+MethyState+"\t"+str(MethySpecificity)+"\t"+str(NAOVA_pvalue)+"\t"+str(MeanMethy)+"\t"+str(RegionCNum)+"\t"+str(SegmentLength)+"\t"+Methydata+"\t"+CellTypeSpecificityPvalue+"\n")
                    RegionFileLine=chromeregionfile_input.readline()
                Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
                print Starttime+" Finish identifying DM ROI for: "+chrome
        #print Numdec
        return TotalRegionNum,Numdec,CellTypeHypoNum,CellTypeHyperNum,Case_Control_Hyper_Num,Case_Control_Hypo_Num
           

    def median(self,sequence):
            if len(sequence) < 1:
                return None
            else:
                sequence.sort()
                return sequence[len(sequence) // 2]
    
    
    def runDeNovo(self,UserArgslist,MethyData,ProjectName,MissReplace,AvailableGroup,MSthreshold,EDthreshold,SMthreshold,CDthreshold,SCthreshold,SLthreshold,p_DMR,p_MethylMark,OutFolder,Case_control_matrix,p_DMR_CaseControl,AbsMeanMethDiffer):

        MissReplace = float(MissReplace)
        AvailableGroup = float(AvailableGroup)
        MSthreshold = float(MSthreshold)
        EDthreshold = float(EDthreshold)
        SMthreshold = float(SMthreshold)
        CDthreshold = int(CDthreshold)
        SCthreshold = int(SCthreshold)
        SLthreshold = int(SLthreshold)
        p_DMR = float(p_DMR)
        p_MethylMark = float(p_MethylMark)
        p_DMR_CaseControl = float(p_DMR_CaseControl)
        AbsMeanMethDiffer = float(AbsMeanMethDiffer)

        MethyDataFolderName=MethyData
        
        Searchregion=DeNovoDMR_Calling()
        
        FinalResultFolder=OutFolder+'DeNovoDMR/'
        tmpDMCfolder=FinalResultFolder+'tmp/DifferMethlCpG/'
        tmpFolder=FinalResultFolder+'tmp/'
        tmpFinalResultsFolder=tmpFolder+"TmpFinalResults/"
        RecordFile=FinalResultFolder+"Summary.txt"
    
        Searchregion=DeNovoDMR_Calling()
        
        if FinalResultFolder:
            # use a output directory to store merged Methylation data 
            if os.path.exists( FinalResultFolder ):
                shutil.rmtree(FinalResultFolder)
            try:
                os.makedirs( FinalResultFolder )
            except:
                sys.exit( "Output directory (%s) could not be created. Terminating program." % FinalResultFolder )
            try:
                os.makedirs( tmpFolder )
            except:
                sys.exit( "Output directory (%s) could not be created. Terminating program." % tmpFolder )
            try:
                os.makedirs( tmpFinalResultsFolder )
            except:
                sys.exit( "Output directory (%s) could not be created. Terminating program." % tmpFinalResultsFolder )
        
        statisticout=open(RecordFile,'w')
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print "\n"
        print Starttime+" ***************Project "+ProjectName+" parameters**************"
        print UserArgslist        
        statisticout.write(Starttime+" ***************Project "+ProjectName+" parameters**************\n"+UserArgslist+"\n\n")
        
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print "\n"
        print Starttime+" *****************Project "+ProjectName+" Start*****************"
        statisticout.write(Starttime+" *****************Project "+ProjectName+" Start*****************\n")
        
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Start to check methylation data and fill missing value..."
        statisticout.write(Starttime+" Start to check data and fill missing value...\n")
        
        DMCmethyfile=open(FinalResultFolder+"1_AvailableCpGs.txt",'wb') #Built a txt file 
        ChromeArray,SampleNames,Group_Key,Column_Key_Group,TotalCpGNum,AvailableCpGNum,DMC_Num,FillMissNum = Searchregion.DataCheck_and_MissReplace(MethyDataFolderName,MissReplace,AvailableGroup,MSthreshold,tmpDMCfolder,DMCmethyfile,p_DMR,statisticout)
        Groups=Group_Key.keys()
        #Genome segmentation based on methylation similarity between neighboring C...
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Start genome segmentation ..."
        statisticout.write(Starttime+" Start genome segmentation ...\n")
        #SegmentBedOutFile=open(FinalResultFolder+"2_SmallSegment.bed",'wb') #Built a bed file  
        #SmallSegNum,Groups=Searchregion.GenomeSegmentMeanMethy(ChromeArray,SampleNames,Group_Key,Column_Key_Group,tmpDMCfolder,tmpFolder,SegmentBedOutFile,MSthreshold,EDthreshold,SMthreshold,CDthreshold,p_DMR,statisticout)
        SmallSegNum=Searchregion.GenomeSegmentMeanMethy_MultiProcess(ChromeArray,SampleNames,Group_Key,Column_Key_Group,tmpDMCfolder,tmpFolder,MSthreshold,EDthreshold,SMthreshold,CDthreshold,p_DMR)
     
        #SegmentBedOutFile.close()
        
        #Merging Segmentation
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Start to merge small segments..."
        statisticout.write(Starttime+" Start to merge small segments...\n")
        Searchregion.SegmentMerge(ChromeArray,SampleNames,Groups,tmpFolder,AvailableGroup,MSthreshold,EDthreshold,SMthreshold,CDthreshold,statisticout)
        
        #Generate the final result
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Start to identify DMRs..."
        statisticout.write(Starttime+" Start to to identify DMRs...\n")
        InputFolder=tmpFolder+"MergedGenomeSegment/"
        
        BedOutFile=open(FinalResultFolder+"2_MergedSegment.bed",'wb') #Build  a bed file
        BedOutFile.write("#Merged segments information for visualization in Genome browser.\ntrack name=\"MergedMethySegment\" description=\"Merged Methylation Segment by SMART2\" visibility=2 itemRgb=\"On\"\n")
        #BedOutFile.write("track name=\"MergedMethySegment\" description=\"Merged Methylation Segment of Human Cells/Tissues (0.4&0.2&500)\" visibility=2 itemRgb=\"On\"\n")
        ######Bed9 for Visualization in Hub of UCSC genome browser
        MergedSegmentOutFile=open(FinalResultFolder+"3_MergedSegment_Methylation.txt",'wb') #Build a bed file    
        MergedSegmentOutFile.write("#Merged segments and its methylation in each sample or group. NAOVA_pvalue represents the significance of methylation difference among multiple groups.\nChrome\tStart\tEnd\tDMR_State\tMethyl_State\tMethyl_Specificity\tNAOVA_pvalue\tMean_Methyl\tCpG_Num\tLength\tGroup_Methyl:"+','.join(Groups)+"\tSample_Methyl:"+','.join(SampleNames)+"\n")
        ######SegmentwithMethylation data
        DMR_methyl_OutFile=open(FinalResultFolder+"4_DMR_Methylation.txt",'wb') #Build a bed file 
        DMR_methyl_OutFile.write("#DMR and its methylation in each sample or group. NAOVA_pvalue represents the significance of methylation difference among multiple groups.\nChrome\tStart\tEnd\tDMR_State\tMethyl_State\tMethyl_Specificity\tNAOVA_pvalue\tMean_Methyl\tCpG_Num\tLength\tGroup_Methyl:"+','.join(Groups)+"\tSample_Methyl:"+','.join(SampleNames)+"\n")
        ######Cell-type-specificity
        DMR_Specificity_OutFile=open(FinalResultFolder+"5_DMR_Group_Specificity.txt",'wb') #Build a bed file    
        DMR_Specificity_OutFile.write("#Group specificity of each DMR. p value is the one sample t test and represents the significance of difference between specific group methylation level and the baseline methylation levels.\nChrome\tStart\tEnd\tDMR_State\tMethyl_State\tMethyl_Specificity\tNAOVA_pvalue\tMean_Methyl\tCpG_Num\tLength\tGroup_Methyl:"+','.join(Groups)+"\tGroup_Ttest_Pvalue:"+','.join(Groups)+"\n")
        ######Cell-type-specificity2
        SegmentCellTypeMethymarkPvalue=open(FinalResultFolder+"6_DMR_Methylmark.txt",'wb') #Build a bed file  
        SegmentCellTypeMethymarkPvalue.write("##Methylation marks of each group. p value is the one sample t test and represents the significance of difference between specific group methylation level and the baseline methylation levels.\nChrome\tStart\tEnd\tDMR_State\tGroup\tMethylMark_Type\tMethylMark_pValue\n")    
        ######Case_control_results
        if Case_control_matrix == '':
            Case_control_matrix = tmpFinalResultsFolder+"Case_control_matrix.txt"
            Case_control_matrix_input=open(Case_control_matrix,'wb') #Input randomly selected two groups
            Case_control_matrix_input.write(Groups[0]+"\t"+Groups[1]+"\n")
            Case_control_matrix_input.close()
        Case_control_results=open(FinalResultFolder+"7_DMR_Case_control.txt",'wb') #Build a bed file  
        Case_control_results.write("##DMRs for each pairwise comparison between case group and control group. p value is the two sample t test and represents the significance of methylation difference between case group and control group.\nRegionChrome\tRegionStart\tRegionEnd\tRegionCpGNum\tSegmentLength\tCase_Group\tControl_Group\tCase_Status\tCaseGroup_CpGmethyl_mean\tContGroup_CpGmethyl_mean\tMeanMethDiffer\tTwoSampleTtest_pvalue\n")
        
        Numdec,CellTypeHypoNum,CellTypeHyperNum,Case_Control_Hyper_Num,Case_Control_Hypo_Num=Searchregion.DeNovoFinalResult_MultiProgress(tmpFolder,BedOutFile,MergedSegmentOutFile,DMR_methyl_OutFile,DMR_Specificity_OutFile,SegmentCellTypeMethymarkPvalue,ChromeArray,SampleNames,Groups,Column_Key_Group,MSthreshold,SCthreshold,SLthreshold,p_DMR,p_MethylMark,statisticout,Case_control_matrix,Case_control_results,p_DMR_CaseControl,AbsMeanMethDiffer)
        #Numdec,CellTypeHypoNum,CellTypeHyperNum=Searchregion.FoldertxttoBed9withMethyandSpecificity(tmpFinalResultsFolder,tmpDMCfolder,InputFolder,BedOutFile,MergedSegmentOutFile,DMR_methyl_OutFile,DMR_Specificity_OutFile,SegmentCellTypeMethymarkPvalue,ChromeArray,SampleNames,Groups,Column_Key_Group,MSthreshold,SCthreshold,SLthreshold,p_DMR,p_MethylMark,statisticout)
        
        #print Numdec
        shutil.rmtree(tmpFolder) #Delete tmp files
        
        BedOutFile.close()
        MergedSegmentOutFile.close()
        DMR_methyl_OutFile.close()
        DMR_Specificity_OutFile.close()
        SegmentCellTypeMethymarkPvalue.close()
        
        Endtime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print "\n"
        print Endtime+" ********************Project Summary******************"
        print Endtime+" Chromesomes   : "+','.join(ChromeArray)
        print Endtime+" Sample Number : "+str(len(SampleNames))
        print Endtime+" Sample Names  : "+','.join(SampleNames)
        print Endtime+" Group Number  : "+str(len(Groups)) 
        print Endtime+" Group Names   : "+','.join(Groups)
        print Endtime+" Number of total CpG sites in all chromesomes       :"+str(TotalCpGNum)
        print Endtime+" Number of CpG sites with methylation in all groups :"+str(AvailableCpGNum)
        print Endtime+" Number of missing values that have been filled     :"+str(FillMissNum)
        print Endtime+" Small  Segment Number                              :"+str(SmallSegNum)
        print Endtime+" Merged Segment Number                              :"+str(Numdec['MergedSegment'])
        print Endtime+" DMR Number                                         :"+str(Numdec['DMR'])
        print Endtime+" NonDMR Number                                      :"+str(Numdec['NonDMR'])
        print Endtime+" NonDMR-UniHypo Segment Number                      :"+str(Numdec['UniHypo'])
        print Endtime+" NonDMR-UnipLow Segment Number                      :"+str(Numdec['UnipLow'])
        print Endtime+" NonDMR-UnipHigh Segment Number                     :"+str(Numdec['UnipHigh'])
        print Endtime+" NonDMR-UniHyper Segment Number                     :"+str(Numdec['UniHyper'])
        print Endtime+" MethyMark Segment Number                           :"+str(Numdec['MethyMark'])
        print Endtime+" MethyMark-HypoMark Segment Number                  :"+str(Numdec['HypoMark'])
        print Endtime+" MethyMark-HyperMark Segment Number                 :"+str(Numdec['HyperMark'])
        
        statisticout.write("\n")
        statisticout.write(Endtime+" ********************Project Summary******************\n")
        statisticout.write(Endtime+" Chromesomes  : "+','.join(ChromeArray)+"\n")
        statisticout.write(Endtime+" SampleNumber : "+str(len(SampleNames))+"\n")
        statisticout.write(Endtime+" SampleNames  : "+','.join(SampleNames)+"\n")
        statisticout.write(Endtime+" Group Number : "+str(len(Groups)) +"\n")
        statisticout.write(Endtime+" Group Names  : "+','.join(Groups)+"\n")
        statisticout.write(Endtime+" Number of total CpG sites in all chromesomes      :"+str(TotalCpGNum)+"\n")
        statisticout.write(Endtime+" Number of CpG sites with methylation in all groups:"+str(AvailableCpGNum)+"\n")
        statisticout.write(Endtime+" Number of missing values that have been filled    :"+str(FillMissNum)+"\n")
        statisticout.write(Endtime+" Small Segment Number                              :"+str(SmallSegNum)+"\n")
        statisticout.write(Endtime+" Merged Segment Number                             :"+str(Numdec['MergedSegment'])+"\n")
        statisticout.write(Endtime+" DMR Number                                        :"+str(Numdec['DMR'])+"\n")
        statisticout.write(Endtime+" NonDMR Number                                     :"+str(Numdec['NonDMR'])+"\n")
        statisticout.write(Endtime+" NonDMR-UniHypo Segment Number                     :"+str(Numdec['UniHypo'])+"\n")
        statisticout.write(Endtime+" NonDMR-UnipLow Segment Number                     :"+str(Numdec['UnipLow'])+"\n")
        statisticout.write(Endtime+" NonDMR-UnipHigh Segment Number                    :"+str(Numdec['UnipHigh'])+"\n")
        statisticout.write(Endtime+" NonDMR-UniHyper Segment Number                    :"+str(Numdec['UniHyper'])+"\n")
        statisticout.write(Endtime+" MethyMark Segment Number                          :"+str(Numdec['MethyMark'])+"\n")
        statisticout.write(Endtime+" MethyMark-HypoMark Segment Number                 :"+str(Numdec['HypoMark'])+"\n")
        statisticout.write(Endtime+" MethyMark-HyperMark Segment Number                :"+str(Numdec['HyperMark'])+"\n")
        for i in CellTypeHypoNum: 
            print Endtime+" "+i+" HypoMark  Number: "+str(CellTypeHypoNum[i])
            statisticout.write(Endtime+" "+i+" HypoMark  Number: "+str(CellTypeHypoNum[i])+"\n")
            print Endtime+" "+i+" HyperMark Number: "+str(CellTypeHyperNum[i])
            statisticout.write(Endtime+" "+i+" HyperMark Number: "+str(CellTypeHyperNum[i])+"\n")
        
        for i in Case_Control_Hyper_Num: 
            print Endtime+" "+i+" Case Hypo DMR Number: "+str(Case_Control_Hypo_Num[i])
            statisticout.write(Endtime+" "+i+"Case Hypo DMR Number: "+str(Case_Control_Hypo_Num[i])+"\n")
            print Endtime+" "+i+" Case Hyper DMR Number: "+str(Case_Control_Hyper_Num[i])
            statisticout.write(Endtime+" "+i+"Case Hyper DMR Number: "+str(Case_Control_Hyper_Num[i])+"\n")
        
        Endtime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Endtime+" *********************Summary End*********************"
        statisticout.write(Endtime+" *********************Summary End*********************\n")
        print "\n"
        print Endtime+" Detailed results in "+OutFolder
        print Endtime+" For any questions, visit http://fame.edbc.org/smart/ or contact Hongbo Liu (hongbo919@gmail.com)"
        print "\n"
        print Endtime+" ***************Project "+ProjectName+" Finished!***************"
        statisticout.write("\n")
        statisticout.write(Endtime+" The final Results can be found in "+OutFolder+"\n")
        statisticout.write(Endtime+" For any questions, visit http://fame.edbc.org/smart/ or contact Hongbo Liu (hongbo919@gmail.com)\n")
        statisticout.write("\n")
        statisticout.write(Endtime+" ***************Project "+ProjectName+" Finished!***************\n")
        statisticout.close()


    def runDMROI(self,UserArgslist,MethyData,ProjectName,MissReplace,AvailableGroup,GenomeRegions,MSthreshold,EDthreshold,SMthreshold,CDthreshold,SCthreshold,SLthreshold,p_DMR,p_MethylMark,OutFolder,Case_control_matrix,p_DMR_CaseControl,AbsMeanMethDiffer):

        MissReplace = float(MissReplace)
        AvailableGroup = float(AvailableGroup)
        MSthreshold = float(MSthreshold)
        EDthreshold = float(EDthreshold)
        SMthreshold = float(SMthreshold)
        CDthreshold = int(CDthreshold)
        SCthreshold = int(SCthreshold)
        SLthreshold = int(SLthreshold)
        p_DMR = float(p_DMR)
        p_MethylMark = float(p_MethylMark)
        p_DMR_CaseControl = float(p_DMR_CaseControl)
        AbsMeanMethDiffer = float(AbsMeanMethDiffer)

        MethyDataFolderName=MethyData
        
        Searchregion=DeNovoDMR_Calling()
                
        FinalResultFolder=OutFolder+'DMROI/'
        tmpDMCfolder=FinalResultFolder+'tmp/DifferMethlCpG/'
        tmpFolder=FinalResultFolder+'tmp/'
        RecordFile=FinalResultFolder+"Summary.txt"
        GenomeRegionFolder=tmpFolder+"GenomeRegions/"
        
        if FinalResultFolder:
            # use a output directory to store merged Methylation data 
            if os.path.exists( FinalResultFolder ):
                shutil.rmtree(FinalResultFolder)
            try:
                os.makedirs( FinalResultFolder )
            except:
                sys.exit( "Output directory (%s) could not be created. Terminating program." % FinalResultFolder )
            try:
                os.makedirs( tmpFolder )
            except:
                sys.exit( "Output directory (%s) could not be created. Terminating program." % tmpFolder )
        
        statisticout=open(RecordFile,'w')
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print "\n"
        print Starttime+" ***************Project "+ProjectName+" parameters**************"
        print UserArgslist        
        statisticout.write(Starttime+" ***************Project "+ProjectName+" parameters**************\n"+UserArgslist+"\n\n")
        
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print "\n"
        print Starttime+" *****************Project "+ProjectName+" Start*****************"
        statisticout.write(Starttime+" *****************Project "+ProjectName+" Start*****************\n")
        
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Start to check methylation data and fill missing value..."
        statisticout.write(Starttime+" Start to check data and fill missing value...\n")
        
        DMCmethyfile=open(FinalResultFolder+"1_AvailableCpGs.txt",'wb') #Built a txt file 
        ChromeArray,SampleNames,Group_Key,Column_Key_Group,TotalCpGNum,AvailableCpGNum,DMC_Num,FillMissNum = Searchregion.DataCheck_and_MissReplace(MethyDataFolderName,MissReplace,AvailableGroup,MSthreshold,tmpDMCfolder,DMCmethyfile,p_DMR,statisticout)
        Groups=Group_Key.keys()
        ###### Bed file
        BedOutFile=open(FinalResultFolder+"2_ROI.bed",'wb') #Build  a bed file
        BedOutFile.write("#ROI information for visualization in Genome browser.\ntrack name=\"MergedMethySegment\" description=\"Merged Methylation Segment by SMART2\" visibility=2 itemRgb=\"On\"\n")
        #BedOutFile.write("track name=\"MergedMethySegment\" description=\"Merged Methylation Segment of Human Cells/Tissues (0.4&0.2&500)\" visibility=2 itemRgb=\"On\"\n")
        ######Bed9 for Visualization in Hub of UCSC genome browser
        MergedSegmentOutFile=open(FinalResultFolder+"3_ROI_Methylation.txt",'wb') #Build a bed file    
        MergedSegmentOutFile.write("#ROI and its methylation in each sample or group. NAOVA_pvalue represents the significance of methylation difference among multiple groups.\nChrome\tStart\tEnd\tDMR_State\tMethyl_State\tMethyl_Specificity\tNAOVA_pvalue\tMean_Methyl\tCpG_Num\tLength\tGroup_Methyl:"+','.join(Groups)+"\tSample_Methyl:"+','.join(SampleNames)+"\n")
        ######SegmentwithMethylation data
        DMR_methyl_OutFile=open(FinalResultFolder+"4_DMROI_Methylation.txt",'wb') #Build a bed file 
        DMR_methyl_OutFile.write("#DMROI and its methylation in each sample or group. NAOVA_pvalue represents the significance of methylation difference among multiple groups.\nChrome\tStart\tEnd\tDMR_State\tMethyl_State\tMethyl_Specificity\tNAOVA_pvalue\tMean_Methyl\tCpG_Num\tLength\tGroup_Methyl:"+','.join(Groups)+"\tSample_Methyl:"+','.join(SampleNames)+"\n")
        ######Cell-type-specificity
        DMR_Specificity_OutFile=open(FinalResultFolder+"5_DMROI_Group_Specificity.txt",'wb') #Build a bed file    
        DMR_Specificity_OutFile.write("#Group specificity of each DMROI. p value is the one sample t test and represents the significance of difference between specific group methylation level and the baseline methylation levels.\nChrome\tStart\tEnd\tDMR_State\tMethyl_State\tMethyl_Specificity\tNAOVA_pvalue\tMean_Methyl\tCpG_Num\tLength\tGroup_Methyl:"+','.join(Groups)+"\tGroup_Ttest_Pvalue:"+','.join(Groups)+"\n")
        ######Cell-type-specificity2
        SegmentCellTypeMethymarkPvalue=open(FinalResultFolder+"6_DMROI_Methylmark.txt",'wb') #Build a bed file  
        SegmentCellTypeMethymarkPvalue.write("##Methylation marks of each group. p value is the one sample t test and represents the significance of difference between specific group methylation level and the baseline methylation levels.\nChrome\tStart\tEnd\tDMR_State\tGroup\tMethylMark_Type\tMethylMark_pValue\n")    
        ######Case_control_results
        if Case_control_matrix == '':
            Case_control_matrix = tmpFolder+"Case_control_matrix.txt"
            Case_control_matrix_input=open(Case_control_matrix,'wb') #Input randomly selected two groups
            Case_control_matrix_input.write(Groups[0]+"\t"+Groups[1]+"\n")
            Case_control_matrix_input.close()
        Case_control_results=open(FinalResultFolder+"7_DMROI_Case_control.txt",'wb') #Build a bed file  
        Case_control_results.write("##DMROIs for each pairwise comparison between case group and control group. p value is the two sample t test and represents the significance of methylation difference between case group and control group.\nRegionChrome\tRegionStart\tRegionEnd\tRegionCpGNum\tRegionLength\tCase_Group\tControl_Group\tCase_Status\tCaseGroup_CpGmethyl_mean\tContGroup_CpGmethyl_mean\tMeanMethDiffer\tTwoSampleTtest_pvalue\n")
       
        TotalRegionNum,Numdec,CellTypeHypoNum,CellTypeHyperNum,Case_Control_Hyper_Num,Case_Control_Hypo_Num = Searchregion.DM_ROI(tmpDMCfolder,GenomeRegions,GenomeRegionFolder,BedOutFile,MergedSegmentOutFile,DMR_methyl_OutFile,DMR_Specificity_OutFile,SegmentCellTypeMethymarkPvalue,ChromeArray,SampleNames,Groups,Column_Key_Group,MSthreshold,SCthreshold,SLthreshold,p_DMR,p_MethylMark,statisticout,Case_control_matrix,Case_control_results,p_DMR_CaseControl,AbsMeanMethDiffer)       
        #print Numdec
        shutil.rmtree(tmpFolder) #Delete tmp files
        
        BedOutFile.close()
        MergedSegmentOutFile.close()
        DMR_methyl_OutFile.close()
        DMR_Specificity_OutFile.close()
        SegmentCellTypeMethymarkPvalue.close()
        
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Finish DMROI identification on chromosomes." 
        statisticout.write(Starttime+" Finish DMROI identification on all chromosomes.\n")
        
        Endtime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print "\n"
        print Endtime+" ********************Project Summary******************"
        print Endtime+" Chromesomes   : "+','.join(ChromeArray)
        print Endtime+" Sample Number : "+str(len(SampleNames))
        print Endtime+" Sample Names  : "+','.join(SampleNames)
        print Endtime+" Group Number  : "+str(len(Groups)) 
        print Endtime+" Group Names   : "+','.join(Groups)
        print Endtime+" Number of total CpG sites in all chromesomes            :"+str(TotalCpGNum)
        print Endtime+" Number of CpG sites with methylation in all groups      :"+str(AvailableCpGNum)
        print Endtime+" Number of missing values that have been filled          :"+str(FillMissNum)
        print Endtime+" Number of total genome regions of interest (ROIs)       :"+str(TotalRegionNum)
        print Endtime+" Number of ROIs with methylation in all groups           :"+str(Numdec['AvilableGenomeRegion'])
        print Endtime+" DMROI Number                                              :"+str(Numdec['DMR'])
        print Endtime+" NonDMROI Number                                           :"+str(Numdec['NonDMR'])
        print Endtime+" NonDMROI-UniHypo Segment Number                           :"+str(Numdec['UniHypo'])
        print Endtime+" NonDMROI-UnipLow Segment Number                           :"+str(Numdec['UnipLow'])
        print Endtime+" NonDMROI-UnipHigh Segment Number                          :"+str(Numdec['UnipHigh'])
        print Endtime+" NonDMROI-UniHyper Segment Number                          :"+str(Numdec['UniHyper'])
        print Endtime+" MethyMark Segment Number                                :"+str(Numdec['MethyMark'])
        print Endtime+" MethyMark-HypoMark Segment Number                       :"+str(Numdec['HypoMark'])
        print Endtime+" MethyMark-HyperMark Segment Number                      :"+str(Numdec['HyperMark'])
       
        statisticout.write("\n")
        statisticout.write(Endtime+" ********************Project Summary******************\n")
        statisticout.write(Endtime+" Chromesomes  : "+','.join(ChromeArray)+"\n")
        statisticout.write(Endtime+" SampleNumber : "+str(len(SampleNames))+"\n")
        statisticout.write(Endtime+" SampleNames  : "+','.join(SampleNames)+"\n")
        statisticout.write(Endtime+" Group Number : "+str(len(Groups)) +"\n")
        statisticout.write(Endtime+" Group Names  : "+','.join(Groups)+"\n")
        statisticout.write(Endtime+" Number of total CpG sites in all chromesomes            :"+str(TotalCpGNum)+"\n")
        statisticout.write(Endtime+" Number of CpG sites with methylation in all groups      :"+str(AvailableCpGNum)+"\n")
        statisticout.write(Endtime+" Number of missing values that have been filled          :"+str(FillMissNum)+"\n")
        statisticout.write(Endtime+" Number of total genome regions of interest (ROIs)       :"+str(TotalRegionNum)+"\n")
        statisticout.write(Endtime+" Number of ROIs with methylation in all groups           :"+str(Numdec['AvilableGenomeRegion'])+"\n")
        statisticout.write(Endtime+" DMROI Number                                              :"+str(Numdec['DMR'])+"\n")
        statisticout.write(Endtime+" NonDMROI Number                                           :"+str(Numdec['NonDMR'])+"\n")
        statisticout.write(Endtime+" NonDMROI-UniHypo Segment Number                           :"+str(Numdec['UniHypo'])+"\n")
        statisticout.write(Endtime+" NonDMROI-UnipLow Segment Number                           :"+str(Numdec['UnipLow'])+"\n")
        statisticout.write(Endtime+" NonDMROI-UnipHigh Segment Number                          :"+str(Numdec['UnipHigh'])+"\n")
        statisticout.write(Endtime+" NonDMROI-UniHyper Segment Number                          :"+str(Numdec['UniHyper'])+"\n")
        statisticout.write(Endtime+" MethyMark Segment Number                                :"+str(Numdec['MethyMark'])+"\n")
        statisticout.write(Endtime+" MethyMark-HypoMark Segment Number                       :"+str(Numdec['HypoMark'])+"\n")
        statisticout.write(Endtime+" MethyMark-HyperMark Segment Number                      :"+str(Numdec['HyperMark'])+"\n")
        for i in CellTypeHypoNum: 
            print Endtime+" "+i+" HypoMark  Number: "+str(CellTypeHypoNum[i])
            statisticout.write(Endtime+" "+i+" HypoMark  Number: "+str(CellTypeHypoNum[i])+"\n")
            print Endtime+" "+i+" HyperMark Number: "+str(CellTypeHyperNum[i])
            statisticout.write(Endtime+" "+i+" HyperMark Number: "+str(CellTypeHyperNum[i])+"\n")
        
        for i in Case_Control_Hyper_Num: 
            print Endtime+" "+i+" Case Hypo DMR Number: "+str(Case_Control_Hypo_Num[i])
            statisticout.write(Endtime+" "+i+"Case Hypo DMROI Number: "+str(Case_Control_Hypo_Num[i])+"\n")
            print Endtime+" "+i+" Case Hyper DMR Number: "+str(Case_Control_Hyper_Num[i])
            statisticout.write(Endtime+" "+i+"Case Hyper DMROI Number: "+str(Case_Control_Hyper_Num[i])+"\n")
        
        Endtime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Endtime+" *********************Summary End*********************"
        statisticout.write(Endtime+" *********************Summary End*********************\n")
        print "\n"
        print Endtime+" Detailed results in "+OutFolder
        print Endtime+" For any questions, visit http://fame.edbc.org/smart/ or contact Hongbo Liu (hongbo919@gmail.com)"
        print "\n"
        print Endtime+" ***************Project "+ProjectName+" Finished!***************"
        statisticout.write("\n")
        statisticout.write(Endtime+" The final Results can be found in "+OutFolder+"\n")
        statisticout.write(Endtime+" For any questions, visit http://fame.edbc.org/smart/ or contact Hongbo Liu (hongbo919@gmail.com)\n")
        statisticout.write("\n")
        statisticout.write(Endtime+" ***************Project "+ProjectName+" Finished!***************\n")
        statisticout.close()




    def runDMC(self,UserArgslist,MethyData,ProjectName,MissReplace,AvailableGroup,MSthreshold,EDthreshold,SMthreshold,CDthreshold,SCthreshold,SLthreshold,p_DMR,p_MethylMark,OutFolder):

        MissReplace = float(MissReplace)
        AvailableGroup = float(AvailableGroup)
        MSthreshold = float(MSthreshold)
        EDthreshold = float(EDthreshold)
        SMthreshold = float(SMthreshold)
        CDthreshold = int(CDthreshold)
        SCthreshold = int(SCthreshold)
        SLthreshold = int(SLthreshold)
        p_DMR = float(p_DMR)
        p_MethylMark = float(p_MethylMark)

        MethyDataFolderName=MethyData
        
        Searchregion=DeNovoDMR_Calling()
        
        FinalResultFolder=OutFolder+'DifferMethlCpG/'
        tmpDMCfolder=FinalResultFolder+'tmp/DifferMethlCpG/'
        tmpFolder=FinalResultFolder+'tmp/'
        RecordFile=FinalResultFolder+"Summary.txt"
        
        if FinalResultFolder:
            # use a output directory to store merged Methylation data 
            if os.path.exists( FinalResultFolder ):
                shutil.rmtree(FinalResultFolder)
            try:
                os.makedirs( FinalResultFolder )
            except:
                sys.exit( "Output directory (%s) could not be created. Terminating program." % FinalResultFolder )
            try:
                os.makedirs( tmpFolder )
            except:
                sys.exit( "Output directory (%s) could not be created. Terminating program." % tmpFolder )
        
        statisticout=open(RecordFile,'w')
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print "\n"
        print Starttime+" ***************Project "+ProjectName+" parameters**************"
        print UserArgslist        
        statisticout.write(Starttime+" ***************Project "+ProjectName+" parameters**************\n"+UserArgslist+"\n\n")
        
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print "\n"
        print Starttime+" *****************Project "+ProjectName+" Start*****************"
        statisticout.write(Starttime+" *****************Project "+ProjectName+" Start*****************\n")
        
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" It should be noted that DMC identification is time-consuming for whole-genome methylation data. DeNovoDMR function is recommended for whole-genome methylation data. \n"
        print Starttime+" Start to identify Differentially methylated CpG sites (DMC)..."
        statisticout.write(Starttime+" Start to identify Differentially methylated CpG sites (DMC)...\n")
        
        AvailableCpGmethyfile=open(FinalResultFolder+"1_AvailableCpGs.txt",'wb') #Built a txt file 
        DMCmethyfile=open(FinalResultFolder+"2_DifferMethlCpGs.txt",'wb') #Built a txt file
        ChromeArray,SampleNames,Group_Key,Column_Key_Group,TotalCpGNum,AvailableCpGNum,DMC_Num,FillMissNum = Searchregion.MissReplace_DMC_callling(MethyDataFolderName,MissReplace,AvailableGroup,MSthreshold,tmpDMCfolder,AvailableCpGmethyfile,DMCmethyfile,p_DMR,statisticout)
        DMCmethyfile.close()
        AvailableCpGmethyfile.close()
        shutil.rmtree(tmpFolder) #Delete tmp files
        
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Finish DMC identification on all chromosomes..."
        statisticout.write(Starttime+" Finish DMC identification on all chromosomes...\n")
        
        Endtime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print "\n"
        print Endtime+" ********************Project Summary******************"
        print Endtime+" Chromesomes   : "+','.join(ChromeArray)
        print Endtime+" Sample Number : "+str(len(SampleNames))
        print Endtime+" Sample Names  : "+','.join(SampleNames)
        print Endtime+" Group Number  : "+str(len(Group_Key)) 
        print Endtime+" Group Names   : "+','.join(Group_Key)
        print Endtime+" Number of total CpG sites in all chromesomes       :"+str(TotalCpGNum)
        print Endtime+" Number of CpG sites with methylation in all groups :"+str(AvailableCpGNum)
        print Endtime+" Number of missing values that have been filled     :"+str(FillMissNum)
        print Endtime+" Number of identified DMC                           :"+str(DMC_Num)
        
        statisticout.write("\n")
        statisticout.write(Endtime+" ********************Project Summary******************\n")
        statisticout.write(Endtime+" Chromesomes   : "+','.join(ChromeArray)+"\n")
        statisticout.write(Endtime+" SampleNumber  : "+str(len(SampleNames))+"\n")
        statisticout.write(Endtime+" SampleNames   : "+','.join(SampleNames)+"\n")
        statisticout.write(Endtime+" Group Number  : "+str(len(Group_Key)) +"\n")
        statisticout.write(Endtime+" Group Names   : "+','.join(Group_Key)+"\n")
        statisticout.write(Endtime+" Number of total CpG sites in all chromesomes      :"+str(TotalCpGNum)+"\n")
        statisticout.write(Endtime+" Number of CpG sites with methylation in all groups:"+str(AvailableCpGNum)+"\n")
        statisticout.write(Endtime+" Number of missing values that have been filled    :"+str(FillMissNum)+"\n")
        statisticout.write(Endtime+" Number of identified DMC                          :"+str(DMC_Num)+"\n")
        
        Endtime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Endtime+" *********************Summary End*********************"
        statisticout.write(Endtime+" *********************Summary End*********************\n")
        print "\n"
        print Endtime+" Detailed results in "+OutFolder
        print Endtime+" For any questions, visit http://fame.edbc.org/smart/ or contact Hongbo Liu (hongbo919@gmail.com)"
        print "\n"
        print Endtime+" ***************Project "+ProjectName+" Finished!***************"
        statisticout.write("\n")
        statisticout.write(Endtime+" The final Results can be found in "+OutFolder+"\n")
        statisticout.write(Endtime+" For any questions, visit http://fame.edbc.org/smart/ or contact Hongbo Liu (hongbo919@gmail.com)\n")
        statisticout.write("\n")
        statisticout.write(Endtime+" ***************Project "+ProjectName+" Finished!***************\n")
        statisticout.close()




if __name__ == '__main__':
    MissReplace = 0.5
    AvailableGroup = 0.5
    MSthreshold = 0.5
    EDthreshold = 0.2
    SMthreshold = 1.0
    CDthreshold = 500
    SCthreshold = 1
    SLthreshold = 1
    p_DMR = 0.001
    p_MethylMark = 0.00000001
    p_DMR_CaseControl = 0.05
    AbsMeanMethDiffer = 0.3
    GenomeRegions=''
    ProjectName='SMART'
    UserArgslist=""
    
    MethyDataFolderName='/Users/hongbo.liu/Documents/HongboData/Projects/00SMART2/TestData2/MethylMatrix_Test.txt'
    Case_control_matrix="/Users/hongbo.liu/Documents/HongboData/Projects/00SMART2/TestData2/Case_control_matrix.txt"
    
    #MethyDataFolderName='/Users/hongbo.liu/Desktop/file_forSMART.txt'
    #MethyDataFolderName='/Users/hongbo.liu/Documents/HongboData/Projects/00SMART2/Testdata/TurSeqEPIC_CpGMethyl_Matrix_Test_chr2.bed'
    #Case_control_matrix="/Users/hongbo.liu/Documents/HongboData/Projects/00SMART2/Testdata/Case_control_matrix.txt"
    
    #MethyDataFolderName='/Users/hongbo.liu/Documents/HongboData/Projects/00SMART2/Testdata/TurSeqEPIC_CpGMethyl_Matrix_Test.bed'
    #MethyDataFolderName='/Users/hongbo.liu/Documents/HongboData/Projects/00SMART2/Testdata/TurSeqEPIC_CpGMethyl_Matrix.bed'
    #MethyDataFolderName='/Users/hongbo.liu/Documents/HongboData/Projects/00SMART2/Testdata/Chr1_45735342_45857045_Test_segment.bed'
#     GenomeRegions='/Users/hongbo.liu/Desktop/chrY_CGI.bed'
    GenomeRegions='/Users/hongbo.liu/Documents/HongboData/Projects/00SMART2/Testdata/CpGisland_hg19_20161023.bed'
#     MethyDataFolderName='/Users/hongbo.liu/Desktop/MethylMatrix_Combined_POETIC_33Samples_CpG_chrY.bed'
    OutFolder="/Users/hongbo.liu/Documents/HongboData/Projects/00SMART2/TestData2/TestResults/"
    
    Function=DeNovoDMR_Calling()
    MethyData=MethyDataFolderName
    Function.runDeNovo(UserArgslist,MethyData,ProjectName,MissReplace,AvailableGroup,MSthreshold,EDthreshold,SMthreshold,CDthreshold,SCthreshold,SLthreshold,p_DMR,p_MethylMark,OutFolder,Case_control_matrix,p_DMR_CaseControl,AbsMeanMethDiffer)
#     Function.runDMC(UserArgslist,MethyData,ProjectName,MissReplace,AvailableGroup,MSthreshold,EDthreshold,SMthreshold,CDthreshold,SCthreshold,SLthreshold,p_DMR,p_MethylMark,OutFolder)
    #Function.runDMROI(UserArgslist,MethyData,ProjectName,MissReplace,AvailableGroup,GenomeRegions,MSthreshold,EDthreshold,SMthreshold,CDthreshold,SCthreshold,SLthreshold,p_DMR,p_MethylMark,OutFolder,Case_control_matrix,p_DMR_CaseControl,AbsMeanMethDiffer)
    

    
    
    
