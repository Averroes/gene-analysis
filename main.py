__author__ = 'cwhi19 and mgeb1'

settingsLocation = "settings.ini"

from Tkinter import *
from tkFileDialog import *
from tkMessageBox import askyesno
import ConfigParser, GeneAnalysis, threading

class Application:

    def __init__(self, root):
        self.font = ("Verdana", 8)
        self.fontBold = ("Verdana", 8, "bold")
        self.geneQueue = []
        self.currentGene = -1

        # create analyser form

        self.analyserForm = Frame(root)
        self.analyserForm.grid(row=0, column=0, sticky=W)

        self.informationWindow = Frame(root, height=100)
        self.informationWindow.grid(row=2, column=0, sticky=W)
        Frame(self.informationWindow, height=180).grid(row=0, column=0)
        self.information = Frame(self.informationWindow)
        self.information.grid(row=0, column=1)

        self.geneListContainer = Frame(root, height=250)
        self.geneListContainer.grid(row=1, column=0, sticky=W)
        Button(self.geneListContainer, text="Analyse", padx=5, command=self.analyse).grid(row=0, column=0)
        self.geneList = Frame(self.geneListContainer)
        self.geneList.grid(row=1, column=0, sticky=W)

        root.bind("<Return>", self.submit)

        self.geneNameVar = StringVar()
        self.geneNameVar.trace(mode="w", callback=self.updateOutput)
        Label(self.analyserForm, text="Gene Name:", font=self.font).grid(row=0, column=0, sticky=W)
        self.geneName = Entry(self.analyserForm, textvariable=self.geneNameVar)
        self.geneName.grid(row=0, column=1, columnspan=2, sticky=W)
        self.geneName.focus_set()

        Label(self.analyserForm, text="Simplified miRNA File:", font=self.font).grid(row=1, column=0, sticky=W)
        self.miRNAFile = Entry(self.analyserForm)
        self.miRNAFile.grid(row=1, column=1, sticky=W)
        Button(self.analyserForm, text="Browse", command=self.choosemiRNA, takefocus=FALSE).grid(row=1, column=2, sticky=W)

        Label(self.analyserForm, text="Simplified TF File:", font=self.font).grid(row=2, column=0, sticky=W)
        self.TFFile = Entry(self.analyserForm)
        self.TFFile.grid(row=2, column=1, sticky=W)
        Button(self.analyserForm, text="Browse", command=self.chooseTF, takefocus=FALSE).grid(row=2, column=2, sticky=W)

        Label(self.analyserForm, text="Output directory:", font=self.font).grid(row=3, column=0, sticky=W)
        self.outputFolder = Entry(self.analyserForm)
        self.outputFolder.grid(row=3, column=1, sticky=W)
        Button(self.analyserForm, text="Browse", command=self.chooseOutput, takefocus=FALSE).grid(row=3, column=2, sticky=W)

        Button(self.analyserForm, text="Add to queue", font=self.fontBold, command=self.addToQueue).grid(row=4, column=0, columnspan=3, padx=20, pady=20, ipadx=10, ipady=5, sticky=E)

        # create rest of application

        self.status = Label(root, font=self.font)
        self.status.grid(row=3, column=0, sticky=W)

        # retrieve settings

        self.settings = ConfigParser.RawConfigParser()
        try:
            self.settings.read(settingsLocation)
            replaceEntryText(self.miRNAFile, self.settings.get('locations', 'miRNA'))
            replaceEntryText(self.TFFile, self.settings.get('locations', 'TF'))
            self.setStatus("Application started.")
        except ConfigParser.NoSectionError:
            replaceEntryText(self.miRNAFile, "Resources/miRNA.txt")
            replaceEntryText(self.TFFile, "Resources/TF.txt")
            self.setStatus("Settings file could not be found. Reverting file locations to defaults.")

            self.settings.add_section('locations')
            self.settings.set('locations', 'miRNA', 'Resources/miRNA.txt')
            self.settings.set('locations', 'TF', 'Resources/TF.txt')

            self.updateSettings()

    def analyse(self):
        geneToBeAnalysed = -1
        i = 0
        for gene in self.geneQueue:
            if geneToBeAnalysed == -1 and gene.progress != 2:
                geneToBeAnalysed = i
            i += 1

        if geneToBeAnalysed == -1:
            self.setStatus("No genes have been queued for analysis.")
        else:
            self.geneQueue[geneToBeAnalysed].runAnalysis()

    def refreshGeneList(self):
        self.geneList.destroy()
        self.geneList = Frame(self.geneListContainer)
        self.geneList.grid(row=0, column=1, sticky=W)

        i = 0
        statusColours = [ "blue", "#DD0", "green" ]
        for gene in self.geneQueue:
            tab = Button(self.geneList, text=gene.geneName, anchor=W, fg=statusColours[gene.progress], font=(self.fontBold if i == self.currentGene else self.font), command=lambda index=i: self.selectGene(index))
            tab.grid(row=0, column=i+1, sticky=W)
            i += 1

    def selectGene(self, index):
        self.currentGene = index
        self.refreshGeneList()
        self.refreshStatuses()

    def refreshStatuses(self):
        self.information.destroy()
        self.information = Frame(self.informationWindow)
        self.information.grid(row=0, column=1, sticky=N)

        i = 0
        for message in self.geneQueue[self.currentGene].statuses:
            Label(self.information, text=message).grid(row=i, column=0, sticky=W)
            i += 1


    def submit(self, *args):
        self.addToQueue()

    def addToQueue(self):
        self.settings.set('locations', 'miRNA', self.miRNAFile.get())
        self.settings.set('locations', 'TF', self.TFFile.get())
        self.updateSettings()

        self.geneQueue += [GeneMember(self.geneName.get(), self.miRNAFile.get(), self.TFFile.get(), self.outputFolder.get(), self)]
        replaceEntryText(self.geneName, "")
        replaceEntryText(self.outputFolder, "")

        if self.currentGene == -1:
            self.selectGene(0)

        self.refreshGeneList()

    def setStatus(self, string):
        self.status["text"] = string

    def updateSettings(self):
        with open(settingsLocation, "wb") as settingsFile:
                self.settings.write(settingsFile)

    def choosemiRNA(self):
        replaceEntryText(self.miRNAFile, askopenfilename())

    def chooseTF(self):
        replaceEntryText(self.TFFile, askopenfilename())

    def chooseOutput(self):
        replaceEntryText(self.outputFolder, askdirectory())

    def updateOutput(self, *args):
        replaceEntryText(self.outputFolder, "Output/" + self.geneName.get() + "/")

class GeneMember:
    def __init__(self, geneName, miRNA, TF, destination, window):
        self.geneName, self.miRNA, self.TF, self.destination = geneName, miRNA, TF, destination
        self.statuses = [ "Waiting..." ]
        self.progress = 0
        self.window = window

    def feedback(self, string):
        self.statuses += [string]
        self.window.refreshStatuses()

    def confirm(self, title, question):
        return askyesno(title=title, message=question)

    def runAnalysis(self):
        thread = AnalyserThread(self.geneName, self.miRNA, self.TF, self.destination, self)
        thread.start()

class AnalyserThread(threading.Thread):
    def __init__(self, geneName, miRNA, TF, destination, memberClass):
        threading.Thread.__init__(self)
        self.geneName, self.miRNA, self.TF, self.destination, self.memberClass = geneName, miRNA, TF, destination, memberClass

    def run(self):
        self.memberClass.progress = 1
        self.memberClass.window.refreshGeneList()

        GeneAnalysis.Program(self.geneName, self.miRNA, self.TF, self.destination, self.memberClass)

        self.memberClass.progress = 2

def replaceEntryText(widget, text):
    widget.delete(0, END)
    widget.insert(0, text)

root = Tk()
root.title("Gene Analyser")
window = Application(root)
root.mainloop()