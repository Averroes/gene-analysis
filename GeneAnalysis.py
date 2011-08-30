from DatabaseImport import *

__author__ = 'cwhi19 and mgeb1'

def Program(geneX):
    """This Function runs all the other base functions for sorting
     and dealing with the Database Data to return results to the user."""

    Mirnas,mirnaDic = getMiRNA(geneX)
    if not len(Mirnas):
        return False #If there are no results, no point in proceeding.
    else:
        #To provide feedback to the user - Needs to be incorporated with GUI
        print "There are",str(len(Mirnas)),'miRNA\'s targeting', str(geneX)


    Tfs,tfDic = getTf(geneX)
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

