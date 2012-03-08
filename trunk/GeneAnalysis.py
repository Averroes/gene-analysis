from DatabaseImport import *
import os
__author__ = 'cwhi19 and mgeb1'
def writeData(geneX,intersections,enrichments,destination):#,threshold,topMirnas):
    """After sorting the data, writes from the Program into text and csv files. Note:TopMirna functionality removed."""
    folderList = destination.split('/')
    runningDirectory = ''
    for folder in folderList:
        runningDirectory += folder + '/'
        if not os.access(runningDirectory,os.R_OK):
            os.mkdir(runningDirectory)
    txt = open(destination+'/'+str(geneX)+' - Results.txt','w') #All files named with Gene Name, and
    txt.write('MiRNA\tTF\tEnrichment Score\tNumber of Genes\tGenes') #Titles for each column.
    csv = open(destination+'/'+str(geneX)+' - Spreadsheet.csv','w')
    csv.write('MiRNA,TF,Enrichment Score,Number of Genes')
#    txt2 = open(destination+'/'+str(geneX)+' - Top'+str(threshold)+'Mirna\'s.txt','w')
#    txt2.write('MiRNA\tFrequency')
    orderedCombinations=sorted(intersections,key=lambda x:len(intersections[x]),reverse=True)
    for combination in orderedCombinations:
        txt.write('\n'+combination[0]+'\t'+combination[1]+'\t'+str(enrichments[combination])+'\t'+str(len(intersections[combination]))+'\t'+str(intersections[combination]))
        csv.write('\n'+combination[0]+','+combination[1]+','+str(enrichments[combination])+','+str(len(intersections[combination])))
#    for Mirna in topMirnas:
#        txt2.write('\n'+str(Mirna)+'\t'+str(topMirnas[Mirna]))
    txt.close(),csv.close()#,txt2.close()
    return

def removeDir(dir):
    """Function for removing files in a directory and their sub files."""
    for directory,dirs,files in os.walk(dir,False):
        for file in files:
            os.remove(file)
        os.remove(directory)
        if dir == directory:
            break

class Analyser():
    def __init__(self):
        self.stackData = {} #Ongoing data that is congregated though generations.
        self.lastDestination = '' #Used to save the stack data to a localised location (where data generations are)
        self.stackNames = [] #To add the names of Target Gene's when saving stackData
        self.lastMergeFile = '' #A loci for when "finished" a break loop, to open the saved data.

    def saveStackData(self):
        """Saves the StackData, which is a congregation of a set of analysed genes' TopMirna lists"""
        folderList = self.lastDestination.split('/')
        runningDirectory = ''
        for folder in folderList[0:-1]: #Sets the directory one level up from where the normal generation data was last saved.
            runningDirectory += folder + '/'
            if not os.access(runningDirectory,os.R_OK):
                os.mkdir(runningDirectory)
        validName = False
        name = 0
        while not validName:
            if not os.access(runningDirectory + '/MergedTopMirnaData' + str(name) + '.txt',os.R_OK):
                file = open(runningDirectory + '/MergedTopMirnaData' + str(name) + '.txt','w')
                title = 'Data of Genes:\t'
                for gene in self.stackNames:
                    title+= ' '+str(gene)
                file.write(title)
                file.write('\nMiRNA\tFrequency')
                for Mirna in sorted(self.stackData.keys(),key=lambda x:self.stackData[x],reverse=True):
                    file.write('\n'+str(Mirna)+'\t'+str(self.stackData[Mirna]))
                self.lastMergeFile = str(runningDirectory) + '/MergedTopMirnaData' + str(name) + '.txt'
                validName=True
            else:
                name += 1
        self.stackData = {}
        self.stackNames = []

    def importData(self,mirnaLoc,tfLoc):
        self.mirnaLoc = mirnaLoc
        self.tfLoc = tfLoc
        self.mirnaDic = getMiRNA(mirnaLoc)
        self.tfDic = getTF(tfLoc)

    def Program(self,geneX,destinationFolder,window):#,threshold,stackable=False):
        """This Function runs all the other base functions for sorting
         and dealing with the Database Data to return results to the user."""

        #Needs to check if selected/current directory already exist. Ie - Override?
        geneX = geneX.lower()
        if geneX == 'break':
            self.saveStackData()
            self.stackData = {}
            self.stackNames = []
            return

        destinationFolder = destinationFolder.replace('\\','/')

        if destinationFolder == '':
            window.feedback("No output directory specified.")
            return

        elif destinationFolder[-1] == '/':
            #Removes extra forward slash if exists
            destinationFolder = destinationFolder[0:len(destinationFolder)-1]
        if os.access(destinationFolder+'/',os.F_OK) and len(geneX):
            if not window.confirm('Override?',"Files for the directory...\n\n" + destinationFolder+'/'+"\n\n...already exists.\nDo you want to override these files?"):
                window.feedback('Directory will not be Overridden.')
                return False

        self.lastDestination = destinationFolder

        Mirnas = []
        for Mirna in self.mirnaDic:
            if geneX in self.mirnaDic[Mirna]:
                Mirnas.append(Mirna)

        window.feedback('Finding MiRNA\'s and their targeted genes, associated with ' + str(geneX) + '.')
        if Mirnas == False:
            window.feedback("MiRNA file not found. Program Terminated.")
            return False
        elif not len(Mirnas):
            window.feedback('MirnaError: There are no Mirna\'s found for ' + str(geneX) + ', Program Terminated.') #If there are no results, no point in proceeding.
            return False
        else:
            #To provide feedback to the user - Incorperated with Interface
            window.feedback("There are "+str(len(Mirnas))+' miRNA\'s targeting '+str(geneX))

        window.feedback('Finding TF\'s and their targeted genes, associated with ' + str(geneX) + '.')
        
        Tfs = []
        for Tf in self.tfDic:
            if geneX in self.tfDic[Tf]:
                Tfs.append(Tf)
        
        if Tfs == False:
            window.feedback("TF file not found. Program Terminated.")
            return False
        elif not len(Tfs):
            window.feedback('TfError: There are no TF\'s found for ' + str(geneX) + ', Program Terminated.')
            return False
        else:
            #To provide feedback to the user - Now Incorperated with UserInterface
            window.feedback("There are "+str(len(Tfs))+' TF\'s targeting '+str(geneX)+'.')

        window.feedback('Creating Intersections between Mirna\'s and Tf\'s and Generating Enrichment Scores for all intersections.')
        intersections = {} #Dictionary for all combinations of TF and miRNA. Key = (Mirna,TF) and Value = [Genes...]
        enrichments = {} #Dictionary for all combinations and their "Enrichment" score.
        for mirna in Mirnas:
            mirnaSet = set(self.mirnaDic[mirna])
            for tf in Tfs:
                combinationName = (mirna,tf)
                #Generates intersection keys
                tfSet = set(self.tfDic[tf])
                intersection = sorted(list(mirnaSet.intersection(tfSet)))
                if not intersection:
                    window.feedback('Not Intersections' + str(intersection) + ', Program Terminated.')
                    return False
                intersections.update({combinationName:intersection}) #Creates form Key = (Mirna,TF) and Value = [Gene,Gene2,....]
                #Generates enrichment score
                enrichment = float(len(intersections[combinationName]))/float(len(set(self.mirnaDic[combinationName[0]])))*100
                enrichments.update({combinationName:enrichment}) #Creates form Key = (Mirna,TF) and Value = Enrichment Integer

        #Writes the data to files.
        window.feedback('Writing Data To Files.')
        writeData(geneX,intersections,enrichments,destinationFolder)#,threshold,topXpercent,)

        window.feedback('Operations Completed Successfully.\nData saved to: '+str(destinationFolder))
        return True #If true, Main.py creates a "View Data" button for the user to access.