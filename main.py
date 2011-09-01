__author__ = 'cwhi19 and mgeb1'

settingsLocation = "settings.ini"

from Tkinter import *
from tkFileDialog import *
import ConfigParser

class Application:

    def __init__(self, root):
        self.font = ("Verdana", 8)
        self.fontBold = ("Verdana", 8, "bold")
        self.state = 0

        # create analyser form

        self.analyserForm = Frame(root)
        self.analyserForm.grid(row=0, column=0, sticky=W)
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

        Button(self.analyserForm, text="Analyse", font=self.fontBold, command=self.analyse).grid(row=4, column=0, columnspan=3, padx=20, pady=20, ipadx=10, ipady=5, sticky=E)

        # create rest of application

        self.status = Label(root, font=self.font)
        self.status.grid(row=1, column=0, sticky=W)

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

    def submit(self, *args):
        if not self.state:
            self.analyse()

    def analyse(self):
        self.settings.set('locations', 'miRNA', self.miRNAFile.get())
        self.settings.set('locations', 'TF', self.TFFile.get())
        self.updateSettings()

        self.setStatus("Analysing...")
        self.analyserForm.grid_remove()

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

def replaceEntryText(widget, text):
    widget.delete(0, END)
    widget.insert(0, text)

root = Tk()
root.title("Gene Analyser")
window = Application(root)
root.mainloop()