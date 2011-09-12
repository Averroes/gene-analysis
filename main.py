__author__ = 'cwhi19 and mgeb1'

import sys, ConfigParser, GeneAnalysis
from PyQt4.Qt import *

settingsLocation = "settings.ini"

class Application(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Gene Analysis")
        self.grid = QGridLayout(self)

        self.geneList = {}

        self.grid.addWidget(QLabel("Gene Name:"), 0, 0)
        self.geneNameInput = QLineEdit()
        self.grid.addWidget(self.geneNameInput, 0, 1, 1, 2)

        self.grid.addWidget(QLabel("Simplified miRNA File:"), 1, 0)
        self.miRNAFileInput = QLineEdit()
        self.grid.addWidget(self.miRNAFileInput, 1, 1)
        self.miRNABrowse = QPushButton("Browse")
        self.grid.addWidget(self.miRNABrowse, 1, 2)

        self.grid.addWidget(QLabel("Simplified TF File:"), 2, 0)
        self.TFFileInput = QLineEdit()
        self.grid.addWidget(self.TFFileInput, 2, 1)
        self.TFBrowse = QPushButton("Browse")
        self.grid.addWidget(self.TFBrowse, 2, 2)

        self.grid.addWidget(QLabel("Output Directory:"), 3, 0)
        self.outputFolderInput = QLineEdit()
        self.grid.addWidget(self.outputFolderInput, 3, 1)
        self.outputBrowse = QPushButton("Browse")
        self.grid.addWidget(self.outputBrowse, 3, 2)

        self.queueButton = QPushButton("Add to queue")
        self.queueButton.setAutoDefault(True)
        self.grid.addWidget(self.queueButton, 4, 0, 1, 3)

        self.analyseButton = QPushButton("Begin Analysis")
        self.grid.addWidget(self.analyseButton, 5, 0, 1, 3)

        self.queueTabs = QTabBar()
        self.queueTabs.setTabsClosable(True)
        self.geneNumber = 0
        self.grid.addWidget(self.queueTabs, 6, 0, 1, 3)

        self.statuses = QLabel("")
        self.grid.addWidget(self.statuses, 7, 0, 1, 3)
        self.statuses.setAlignment(Qt.AlignTop)

        self.connect(self.geneNameInput, SIGNAL('textChanged(QString)'), (lambda x: self.updateOutput(x)))
        self.connect(self.miRNABrowse, SIGNAL('clicked()'), lambda: self.chooseFile(self.miRNAFileInput))
        self.connect(self.TFBrowse, SIGNAL('clicked()'), lambda: self.chooseFile(self.TFFileInput))
        self.connect(self.outputBrowse, SIGNAL('clicked()'), lambda: self.chooseFolder(self.outputFolderInput))
        self.connect(self.queueButton, SIGNAL('clicked()'), self.addToQueue)
        self.connect(self.analyseButton, SIGNAL('clicked()'), self.analyse)
        self.connect(self.queueTabs, SIGNAL('currentChanged(int)'), self.updateStatuses)

        self.settings = ConfigParser.RawConfigParser()
        try:
            self.settings.read(settingsLocation)
            self.miRNAFileInput.setText(self.settings.get('locations', 'miRNA'))
            self.TFFileInput.setText(self.settings.get('locations', 'TF'))
        except ConfigParser.NoSectionError:
            self.miRNAFileInput.setText("Resources/miRNA.txt")
            self.TFFileInput.setText("Resources/TF.txt")

            self.settings.add_section('locations')
            self.settings.set('locations', 'miRNA', 'Resources/miRNA.txt')
            self.settings.set('locations', 'TF', 'Resources/TF.txt')

            self.updateSettings()

    def analyse(self):
        #TODO: add checking for whether there are items in a queue (that have not been analysed)
        #TODO: make thread an attribute of the window, as opposed to the GeneMember
        #TODO: add statuses to tabs (ie. loading icon for "in progress", bold for finished)
        #TODO: add button to analyse results
        #TODO: add ability to delete tabs
        index = -1
        for geneNumber in self.geneList:
            if not self.geneList[geneNumber].progress and index == -1:
                index = geneNumber

        self.geneList[index].thread = AnalyserThread(self.geneList[index])
        self.geneList[index].thread.finished.connect(self.analyse)
        self.geneList[index].thread.start()

        self.connect(self.geneList[index].thread, SIGNAL("updateStatuses()"), self.updateStatuses)

    def addToQueue(self):
        self.settings.set('locations', 'miRNA', self.miRNAFileInput.text())
        self.settings.set('locations', 'TF', self.TFFileInput.text())
        self.updateSettings()

        self.geneList[self.geneNumber] = GeneMember(self.geneNameInput.text(), self.miRNAFileInput.text(), self.TFFileInput.text(), self.outputFolderInput.text(), self)
        self.queueTabs.insertTab(self.geneNumber, self.geneNameInput.text())
        self.geneNumber += 1

        self.geneNameInput.clear()
        self.outputFolderInput.clear()

    def updateStatuses(self):
        self.statuses.setText("<br />".join(self.geneList[self.queueTabs.currentIndex()].statuses))

    def updateOutput(self, x):
        self.outputFolderInput.setText("Output/" + x + "/")

    def chooseFile(self, textbox):
        file = QFileDialog.getOpenFileName(self, "Select file")
        if len(file):
            textbox.setText(file)

    def chooseFolder(self, textbox):
        folder = QFileDialog.getExistingDirectory(self, "Select folder")
        if len(folder):
            textbox.setText(folder)

    def updateSettings(self):
        with open(settingsLocation, "wb") as settingsFile:
                self.settings.write(settingsFile)

    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
            if event.key() == 16777220:
                self.addToQueue()

class AnalyserThread(QThread):
    #TODO: merge AnalyserThread and GeneMember
    def __init__(self, gene):
        QThread.__init__(self)
        self.gene = gene

    def run(self):
        self.gene.progress = 1

        GeneAnalysis.Program(self.gene.geneName, self.gene.miRNA, self.gene.TF, self.gene.destination, self.gene)

        self.gene.progress = 2

class GeneMember:
    def __init__(self, geneName, miRNA, TF, destination, window):
        self.geneName, self.miRNA, self.TF, self.destination, self.window = str(geneName), str(miRNA), str(TF), str(destination), window
        self.statuses = [ "Waiting..." ]
        self.progress = 0

    def feedback(self, string):
        self.statuses += [ string ]
        self.thread.emit(SIGNAL("updateStatuses()"))

    def confirm(self, title, question):
        messageBox = QMessageBox()
        messageBox.setText(title)
        messageBox.setInformativeText(question)
        messageBox.setIcon(QMessageBox.Warning)
        messageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        return True if messageBox.exec_() == 16384 else False
        

app = QApplication(sys.argv)

window = Application()
window.show()

app.exec_()