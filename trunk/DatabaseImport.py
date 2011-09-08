import os,re

__author__ = 'cwhi19 and mgeb1'

def getMiRNA(geneX):
    """This function opens the simplified miRNA database,
    used for returning a dictionary of MiRNA and the genes they affect,
    as well as the MiRNAs that target the subject gene."""

    miRNA_Database = open(os.getcwd() + '\\Resources\\miRNA.txt','r')
    miRNAs = [] #List for MiRNAs targeting gene X
    mirnaDic = {} #Dictionary for all MiRNA and their targeted Genes.
    for line in miRNA_Database:
        line = line.split('\t') #The document is in the form "Mirna [\t] Gene"
        if len(line) > 1:
            mirna  = line[0] #The MiRNA.
            gene = line[1] #The target gene.
            if gene == str(geneX):
                miRNAs.append([mirna])
            mirnaDic.update({mirna:mirnaDic[mirna]+[gene]}) if mirna in mirnaDic else mirnaDic.update({mirna:[gene]}) #Keeps duplicates in list, adds to previous lists.
    return miRNAs,mirnaDic

def getTF(geneX):
    """"This function opens the simplified TF database,
    used for returning a dictionary of TFs and their targeted genes,
    as well as the TFs that target the subject gene."""

    TF_Database = open(os.getcwd() + '\\Resources\\TF.txt','r')
    tfs = [] #List for TFs targeting gene X
    tfDic = {} #Dictionary for all MiRNA and their targeted Genes.
    for line in TF_Database:
        line = line.split('\t') #Doc in same form as miRNA_Database.
        if len(line)>1:
            TF = line[0]
            gene = line[1]
            if gene == geneX:
                tfs.append(TF)
            tfDic.update({TF:tfDic[TF] + [gene]}) if TF in tfDic else tfDic.update({TF:[gene]})

    return tfs,tfDic

def convertMirnaData():
    """Code to convert the 'mouse_predictions_S_C_aug2010.txt'
    TF Database to a simpler file."""

    mirnaDatabase = open(os.getcwd()+'\\mouse_predictions_S_C_aug2010.txt','r')
    MiGeneList = open(os.getcwd() + '\\Resources\\migenelist.txt','w')
    for line in mirnaDatabase:
        data = re.search('(.*?)[ \t]+(.*?)[ \t]+(.*?)[ \t]+(.*?)[ \t](.*)',line,re.IGNORECASE)
        if type(data.group(2)).__name__ != 'None' and type(data.group(4)).__name__ != 'None':
            MiGeneList.write(data.group(2).lower() + '\t' + data.group(4).lower() +'\n')
    MiGeneList.close()
    return

def convertTfData():
    """"Code to convert the 'MRNV101203.txt' miRNA
    Database to a simpler file."""

    tfDatabase = open(os.getcwd()+'\\MRNV101203.txt','r') #Data File.
    TfGeneList = open(os.getcwd()+'\\Resources\\tfgenelist.txt','w') #Simple File.
    for line in tfDatabase:
        data = re.search('(.*?)[ \t]+(.*?)[ \t]+(.*)[ \t]+(.*)[\n]+',line,re.IGNORECASE)
        if str(data.group(4)) == 'TF->Gene':
            TfGeneList.write(data.group(1).lower() + '\t' + data.group(2).lower() +'\n')
    TfGeneList.close()
    return