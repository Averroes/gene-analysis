from DatabaseImport import *
import os

__author__ = 'cwhi19 and mgeb1'

def writeData(geneX,intersections,enrichments,topMirnas):
    """After sorting the data, writes from the Program into text and csv files."""
    if os.access(os.getcwd()+'\\'+str(geneX)+'\\',os.F_OK) and len(geneX):
        removeDir(os.getcwd()+'\\'+str(geneX)+'\\')
    txt = open(os.getcwd()+'\\'+str(geneX)+' - Results.txt')
    txt.write('MiRNA:\tTF:\tEnrichment Score:\tLenOfGenes:\tGenes:') #Labels for each column.
    csv = open(os.getcwd()+'\\'+str(geneX)+' - Spreadsheet.csv')
    csv.write('MiRNA:\tTF:\tEnrichment Score:\tLenOfGenes:')
    txt2 = open(os.getcwd()+'\\'+str(geneX)+' - TopMirna\'s')
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
    """Aim of this program is to return a frequency list for the top 25% of MiRNA's in each tf set of combinations."""
    scores = {}
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

def Program(geneX):
    """This Function runs all the other base functions for sorting
     and dealing with the Database Data to return results to the user."""

    #Needs to check
    if os.access(os.getcwd()+'\\'+str(geneX)+'\\',os.F_OK) and len(geneX):
        print "Files for This directory already exists."
        print "Do you want to override these files?" #Needs to have input to the GUI!
        answer = input('>')
        if not answer == 'True': #Needs to become less specific answer...
            return False

    Mirnas,mirnaDic = getMiRNA(geneX)
    if not len(Mirnas):
        return False #If there are no results, no point in proceeding.
    else:
        #To provide feedback to the user - Needs to be incorporated with GUI
        print "There are",str(len(Mirnas)),'miRNA\'s targeting', str(geneX)


    Tfs,tfDic = getTF(geneX)
    if not len(Tfs):
        return False
    else:
        #To provide feedback to the user - Needs to be incorporated with GUI
        print "There are",str(len(Tfs)),'TF\'s targeting', str(geneX)

    intersections = {} #Dictionary for all combinations of TF and miRNA. Key = (Mirna,TF) and Combinations = [...]
    for mirna in Mirnas:
        for tf in Tfs:
            combinationName = (mirna,tf)
            intersection = list(set(mirnaDic[mirna]).intersection(set(tfDic[tf]))).sort()
            intersections.update({combinationName:intersection})

    enrichments = {} #Dictionary for all combinations and their "Enrichment" score.
    for combination in intersections.keys():
        enrichment = float(len(intersections[combination]))/float(len(mirnaDic[combination[0]]))
        enrichments.update({combination:enrichment})

    top25percent = getTop25()

    writeData(geneX,intersections,enrichments,top25percent)

