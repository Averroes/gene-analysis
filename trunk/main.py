__author__ = 'cwhi19 and mgeb1'
__version__ = '0.0.1'

import sys, ConfigParser, GeneAnalysis, DataRep, os
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
        exitAction = QAction("Open data...", self) #Simplified from "previously generate", just for elagency. Should be self explainatory enough.
        exitAction.triggered.connect(self.viewDataOpen)
        self.recentDataMenu = QMenu("Recent Data",self)
        fileMenu.addMenu(self.recentDataMenu)
        fileMenu.addAction(exitAction)

        helpMenu = menubar.addMenu("Help")
        helpAction = QAction("Help Documentation",self)
        helpAction.triggered.connect(self.help)
        helpMenu.addAction(helpAction)

        aboutAction = QAction("About", self)
        aboutAction.triggered.connect(self.about)
        helpMenu.addAction(aboutAction)

        #TODO: Create Help Documentation, cascade is created.
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
        self.connect(self.dataViewButton, SIGNAL('clicked()'), self.viewDataButton)
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

        try:
            self.recentDataLoc = self.settings.get('recentData','Locations').split(',')
            for location in self.recentDataLoc:
                if not os.access(location,os.R_OK):
                    self.recentDataLoc.remove(location)

            for location in self.recentDataLoc:
                location += '/' if location[-1] != '/' else ''
                gene = location.split('/')[-2]
                vars()[gene] = QAction(str(gene),self)
                vars()[gene].triggered.connect(lambda a:self.viewData(location))
                self.recentDataMenu.addAction(vars()[gene])

        except ConfigParser.NoSectionError:
            self.recentDataLoc = []
            self.settings.add_section('recentData')
            self.settings.set('recentData','Locations','')
            self.updateSettings()

    def analyse(self):
        geneFound = False
        self.outputSet = False
        self.analyseButton.setDisabled(False)
        for gene in self.geneList:
            if not gene.progress and not geneFound:
                geneFound = True
                gene.finished.connect(self.analyse)
                gene.start()

                self.analyseButton.setDisabled(True)

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

    def viewDataButton(self):
        self.viewData(self.geneList[self.queueTabs.currentIndex()].destination) 

    def viewDataOpen(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder")
        if len(folder):
            self.viewData(folder)
            if not folder in self.recentDataLoc:
                self.addRecentLoc(folder)

    def viewData(self, destination):
        if os.access(destination,os.R_OK):
            self.dataWindow = DataRep.DataRep(destination)
            self.dataWindow.show()
        else:
            #TODO: Do we want some sort of "Error" window here? This is for when someone's changed a pre-existing directory location whilein program...
            return False

    def addRecentLoc(self,folder):
        folder += '/' if folder[-1] != '/' else ''
        gene = folder.split('/')[-2]
        while len(self.recentDataLoc) > 10:
            self.recentDataLoc.pop(0)
        if len(self.recentDataLoc) > 9 and not folder in self.recentDataLoc:
            self.recentDataLoc.pop(0)
        if not folder in self.recentDataLoc:
            self.recentDataLoc += [folder]
        string = ''
        for location in self.recentDataLoc:
            string += ',' if string != '' else ''
            string += location
        self.settings.set('recentData','Locations',string)
        self.updateSettings()

        vars()[gene] = QAction(str(gene),self)
        vars()[gene].triggered.connect(lambda a:self.viewData(folder))
        self.recentDataMenu.addAction(vars()[gene])

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
    def help(self):
        self.helpWindow = HelpDocumentation()
        self.helpWindow.show()

    def about(self):
        self.aboutWindow = About()
        self.aboutWindow.show()

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

        if GeneAnalysis.Program(self.geneName, self.miRNA, self.TF, self.destination, self):
            self.progress = -1


class HelpDocumentation(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        grid = QGridLayout(self)
        self.setWindowTitle("Help")
        QWidget.setMinimumSize(self,600,400)

        TitleFont = QFont("Times",20)
        SubHeadingFont = QFont('Times',14)
        TextFont = QFont('Times',10)

        Title = QLabel('Gene Analysis Documentation:')
        Title.setFont(TitleFont)
        grid.addWidget(Title,0,0)

        Subtitle1 = QLabel('Purpose:')
        Subtitle1.setFont(SubHeadingFont)
        grid.addWidget(Subtitle1,1,0)
        #This text1 isjust an example, and is not by any means what I intend to put in.
        Text1 = QLabel('The purpose of this program is to provide data that represents the most common TF sites and mirna binding sites to the user.\n Based on these, users may be able to determine other genes with simmilar functions.')
        Text1.setFont(TextFont)
        grid.addWidget(Text1,2,0)

        Subtitle2 = QLabel('Setting Up:')
        Subtitle2.setFont(SubHeadingFont)
        grid.addWidget(Subtitle2,3,0)
        #This text2 is also just an example.
        Text2 = QLabel('In this application, the files "Mirna.txt" and "TF.txt" will automatically be looked for from the location of the Main.exe file.\n If you don\'t have these files under "Resources/..." then you will have to select the locations using the file option.\n Once you have selected these options, you can select a gene to process, such as TNFAIP3, IRAK1, RNF11 or PTEN.\nThe program will then create a set of files with data under the location of the executible, unless a destination is specified otherwise.')
        Text2.setFont(TextFont)
        grid.addWidget(Text2,4,0)


        Exit = QPushButton("Close")
        grid.addWidget(Exit,5,0)
        self.connect(Exit,SIGNAL('clicked()'),self.Cancel)

    def Cancel(self):
        self.close()

class About(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        grid = QGridLayout(self)
        self.setWindowTitle("About")

        programTitle = QLabel("Gene Analyser")
        programTitle.setFont(QFont("Arial", 12))
        grid.addWidget(programTitle, 0, 0)
        grid.addWidget(QLabel("Matt Gebert and Chris Whittle"), 1, 0)
        grid.addWidget(QLabel("working with Doctor Gantier"), 2, 0)
        grid.addWidget(QLabel(__version__), 3, 0)


app = QApplication(sys.argv)

window = Application()
window.show()

app.exec_()