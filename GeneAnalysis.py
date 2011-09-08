from DatabaseImport import *
import os

__author__ = 'cwhi19 and mgeb1'

def writeData(geneX,intersections,enrichments,topMirnas,destination):
    """After sorting the data, writes from the Program into text and csv files."""
    if os.access(destination+'\\'+str(geneX)+'\\',os.F_OK) and len(geneX):
        removeDir(destination+'\\'+str(geneX)+'\\')
    txt = open(destination+'\\'+str(geneX)+' - Results.txt')
    txt.write('MiRNA:\tTF:\tEnrichment Score:\tLenOfGenes:\tGenes:') #Labels for each column.
    csv = open(destination+'\\'+str(geneX)+' - Spreadsheet.csv')
    csv.write('MiRNA:\tTF:\tEnrichment Score:\tLenOfGenes:')
    txt2 = open(destination+'\\'+str(geneX)+' - TopMirna\'s')
    txt2.write('MiRNA:\tFrequency:')
    orderedCombinations=sorted(intersections,key=lambda x:x[1],reverse=True)
    for combination in orderedCombinations:
        txt.write('\n'+combination[0]+'\t'+combination[1]+'\t'+str(enrichments[combination])+'\t'+str(len(intersections[combination]))+'\t'+str(intersections[combination]))
        csv.write('\n'+combination[0]+','+combination[1]+','+str(enrichments[combination])+','+str(len(intersections[combination])))
    for Mirna in topMirnas:
        txt2.write('\n'+str(Mirna)+'\t'+str(topMirnas[Mirna]))
    txt.close(),csv.close(),txt2.close()
    return

def removeDir(dir):
    """Function for removing files in a directory and their sub files."""
    for directory,dirs,files in os.walk(dir,False):
        for file in files:
            os.remove(file)
        os.remove(directory)

def getTop25(tfs,miRNAs,enrichments, percentile = 25):
    """This program returns a frequency dictionary for the top 25% of MiRNA's in each tf set of combinations.
    Should return the most common and most important MiRNA's specific to gene X. Data is used for Word Cloud"""
    enrichSort = sorted(enrichments,key= lambda x:enrichments[x],reverse=True)
    percentile = percentile*len(miRNAs)/100
    topmiRNAs = {}
    for TF in tfs:
        x = 0
        for element in enrichSort:
            if element[1] == TF:
                if topmiRNAs.has_key(element[0]):
                    topmiRNAs[element[0]] += 1
                else:
                    topmiRNAs[element[0]] = 1
                x += 1
            if not x <= percentile:
                break

    return topmiRNAs

def Program(geneX,mirnaLoc,tfLoc,destinationFolder,window):
    """This Function runs all the other base functions for sorting
     and dealing with the Database Data to return results to the user."""

    #Needs to check if selected/current directory already exist. Ie - Override?
    if destinationFolder[-1] == '/':
        #Removes extra forward slash if it exists.
        destinationFolder = destinationFolder[0:len(destinationFolder)-1]
    if os.access(destinationFolder+'\\'+str(geneX)+'\\',os.F_OK) and len(geneX):
        if not window.confirm('Override?',"Files for This directory already exists.\nDo you want to override these files?"):
            window.feedback('Directory will not be Overridden.')
            return False

    window.feedback('Finding MiRNA\'s and their targeted genes, associated with ' + str(geneX) + '.')
    Mirnas,mirnaDic = getMiRNA(geneX,mirnaLoc)
    if not len(Mirnas):
        return MirnaError('MirnaError: There are no Mirna\'s found for ' + str(geneX)) #If there are no results, no point in proceeding.
    else:
        #To provide feedback to the user - Incorperated with Interface
        window.feedback("There are "+str(len(Mirnas))+' miRNA\'s targeting '+str(geneX))

    window.feedback('Finding TF\'s and their targeted genes, associated with ' + str(geneX) + '.')
    Tfs,tfDic = getTF(geneX,tfLoc)
    if not len(Tfs):
        return TfError('TfError: There are no TF\'s found for ' + str(geneX))
    else:
        #To provide feedback to the user - Now Incorperated with UserInterface
        window.feedback("There are "+str(len(Tfs))+' TF\'s targeting '+str(geneX))

    window.feedback('Creating Interections between Mirna\'s and Tf\'s.')
    intersections = {} #Dictionary for all combinations of TF and miRNA. Key = (Mirna,TF) and Value = [Genes...]
    for mirna in Mirnas:
        for tf in Tfs:
            combinationName = (mirna,tf)
            intersection = list(set(mirnaDic[mirna]).intersection(set(tfDic[tf]))).sort()
            intersections.update({combinationName:intersection})

    window.feedback('Generating Enrichment Scores for all intersections.')
    enrichments = {} #Dictionary for all combinations and their "Enrichment" score.
    for combination in intersections.keys():
        enrichment = float(len(intersections[combination]))/float(len(mirnaDic[combination[0]]))
        enrichments.update({combination:enrichment}) #Creates form Key = (Mirna,TF) and Value = Enrichment Integer

    #Obtains the top 25% of each TF's mirna's based on enrichment score, returning them as a frequency dictionary.
    window.feedback('Obtaining frequency list of most common MiRNA\'s for '+str(geneX))
    top25percent = getTop25(Tfs,Mirnas,enrichments)

    #Writes the data to files.
    window.feedback()
    writeData(geneX,intersections,enrichments,top25percent,destinationFolder)
    return True

class TfError(Exception):
    """Used to return Errors when no TF's are found for GeneX."""
    def __init__(self,value):
        self.value=value
    def __str__(self):
        return repr(self.value)

class MirnaError(Exception):
    """Used to return Errors when no Mirna's are found for GeneX."""
    def __init__(self,value):
        self.value=value
    def __str__(self):
        return repr(self.value)