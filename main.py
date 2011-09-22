__author__ = 'cwhi19 and mgeb1'

import sys, ConfigParser, GeneAnalysis, DataRep
from PyQt4.Qt import *

settingsLocation = "settings.ini"

class Application(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Gene Analysis")
        self.mainWidget = QWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.grid = QGridLayout(self.mainWidget)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu("File")
        exitAction = QAction("Open previously generated data...", self)
        exitAction.triggered.connect(self.viewDataOpen)
        fileMenu.addAction(exitAction)

        #TODO: Add a menu to the Window, to be able to open up previous data (Should save locations/previous files, in Settings.ini File)
        #TODO: Help Cascade for Documentation
        #TODO: Add a Load Setting option?
        

        self.geneList = []

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
        self.outputSet = False

        self.queueButton = QPushButton("Add to queue")
        self.queueButton.setAutoDefault(True)
        self.grid.addWidget(self.queueButton, 4, 0, 1, 3)

        self.analyseButton = QPushButton("Begin Analysis")
        self.grid.addWidget(self.analyseButton, 5, 0, 1, 3)

        self.queueTabs = QTabBar()
        self.queueTabs.setTabsClosable(True)
        self.queueTabs.setMovable(True)
        self.grid.addWidget(self.queueTabs, 6, 0, 1, 3)

        self.statuses = QLabel("")
        self.grid.addWidget(self.statuses, 7, 0, 1, 3)
        self.statuses.setAlignment(Qt.AlignTop)

        self.statuses = QLabel("")
        self.grid.addWidget(self.statuses, 7, 0, 1, 3)
        self.statuses.setAlignment(Qt.AlignTop)

        self.dataViewButton = QPushButton("View results")
        self.grid.addWidget(self.dataViewButton, 8, 0, 1, 3)
        self.dataViewButton.hide()

        self.connect(self.geneNameInput, SIGNAL('textChanged(QString)'), (lambda x: self.updateOutput(x)))
        self.connect(self.miRNABrowse, SIGNAL('clicked()'), lambda: self.chooseFile(self.miRNAFileInput))
        self.connect(self.TFBrowse, SIGNAL('clicked()'), lambda: self.chooseFile(self.TFFileInput))
        self.connect(self.outputBrowse, SIGNAL('clicked()'), lambda: self.chooseFolder(self.outputFolderInput))
        self.connect(self.queueButton, SIGNAL('clicked()'), self.addToQueue)
        self.connect(self.analyseButton, SIGNAL('clicked()'), self.analyse)
        self.connect(self.dataViewButton, SIGNAL('clicked()'), lambda: self.viewData(self.outputFolderInput.text()))
        self.connect(self.queueTabs, SIGNAL('currentChanged(int)'), self.updateStatuses)
        self.connect(self.queueTabs, SIGNAL('tabCloseRequested(int)'), lambda x: self.removeGene(x))
        self.connect(self.queueTabs, SIGNAL('tabMoved(int,int)'), lambda x, y: self.moveGene(x, y))

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
        geneFound = False
        self.outputSet = False
        for gene in self.geneList:
            if not gene.progress and not geneFound:
                geneFound = True
                gene.finished.connect(self.analyse)
                gene.start()

                self.connect(gene, SIGNAL("updateStatuses()"), self.updateStatuses)

    def addToQueue(self):
        self.settings.set('locations', 'miRNA', self.miRNAFileInput.text())
        self.settings.set('locations', 'TF', self.TFFileInput.text())
        self.updateSettings()

        self.geneList += [AnalyserThread(self.geneNameInput.text(), self.miRNAFileInput.text(), self.TFFileInput.text(), self.outputFolderInput.text(), self)]
        self.queueTabs.insertTab(-1, self.geneNameInput.text())

        self.geneNameInput.clear()
        self.outputFolderInput.clear()

    def removeGene(self, geneId):
        if self.geneList[geneId].progress != 1:
            self.queueTabs.removeTab(geneId)
            del self.geneList[geneId]
            self.updateStatuses()

    def moveGene(self, initial, final):
        self.geneList.insert(final, self.geneList.pop(initial))

    def updateStatuses(self):
        self.dataViewButton.hide()
        if len(self.geneList) > 0:
            self.statuses.setText("<br />".join(self.geneList[self.queueTabs.currentIndex()].statuses))
            if self.geneList[self.queueTabs.currentIndex()].progress == 2:
                self.dataViewButton.show()
        else:
            self.statuses.setText("")

    def viewDataOpen(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder")
        if len(folder):
            self.viewData(folder)

    def viewData(self, destination):
        self.dataWindow = DataRep.DataRep(destination)
        self.dataWindow.show()

    def updateOutput(self, x):
        if not len(self.outputFolderInput.text()):
            self.outputSet = False
        if not self.outputSet:
            self.outputFolderInput.setText("Output/" + x + "/")

    def chooseFile(self, textbox):
        file = QFileDialog.getOpenFileName(self, "Select file")
        if len(file):
            textbox.setText(file)

    def chooseFolder(self, textbox):
        folder = QFileDialog.getExistingDirectory(self, "Select folder")
        if len(folder):
            textbox.setText(folder)
            self.outputSet = True

    def updateSettings(self):
        with open(settingsLocation, "wb") as settingsFile:
                self.settings.write(settingsFile)

    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
            if event.key() == 16777220:
                self.addToQueue()

class AnalyserThread(QThread):
    def __init__(self, geneName, miRNA, TF, destination, window):
        QThread.__init__(self)
        
        self.geneName, self.miRNA, self.TF, self.destination, self.window = str(geneName), str(miRNA), str(TF), str(destination), window
        self.statuses = [ "Waiting..." ]
        self.progress = 0

    def feedback(self, string):
        self.statuses += [ string ]
        self.emit(SIGNAL("updateStatuses()"))

    def confirm(self, title, question):
        messageBox = QMessageBox()
        messageBox.setText(title)
        messageBox.setInformativeText(question)
        messageBox.setIcon(QMessageBox.Warning)
        messageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        return True if messageBox.exec_() == 16384 else False

    def run(self):
        self.progress = 1

        GeneAnalysis.Program(self.geneName, self.miRNA, self.TF, self.destination, self)

        self.progress = 2
        

app = QApplication(sys.argv)

window = Application()
window.show()

app.exec_()