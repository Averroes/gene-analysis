__author__ = 'cwhi19 and mgeb1'
__version__ = '0.2.1'

import sys, ConfigParser, GeneAnalysis, DataRep, os
from PyQt4.Qt import *

settingsLocation = "settings.ini"

class Application(QMainWindow):
    def __init__(self):
        """Set up the GUI elements of the main interface"""
        QMainWindow.__init__(self)
        self.setWindowTitle("Gene Analysis")
        self.mainWidget = QWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.grid = QGridLayout(self.mainWidget)

        self.dataWindowCount = 0 # Allows data windows to be opened, to be able to compare data.
        self.geneSeparationCharacters = [ "\r\n", "\n", "\r", " ", "\t", "," ] # Characters that denote a split between gene names

        menubar = self.menuBar()
        fileMenu = menubar.addMenu("File")
        exitAction = QAction("Open data...", self)
        exitAction.triggered.connect(self.viewDataOpen)
        self.recentDataMenu = QMenu("Recent Data",self)
        fileMenu.addMenu(self.recentDataMenu)
        fileMenu.addAction(exitAction)

        helpMenu = menubar.addMenu("Help")
        helpAction = QAction("Help Documentation",self)
        helpAction.triggered.connect(self.help)
        helpMenu.addAction(helpAction)

        aboutAction = QAction("Program Information", self)
        aboutAction.triggered.connect(self.about)
        helpMenu.addAction(aboutAction)

        #TODO: Create Help Documentation, cascade is created.
        #TODO: Add a Load Setting option?\

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
                vars()[gene].triggered.connect(lambda a, y=location: self.viewData(y))
                self.recentDataMenu.addAction(vars()[gene])

        except ConfigParser.NoSectionError:
            self.recentDataLoc = []
            self.settings.add_section('recentData')
            self.settings.set('recentData','Locations','')
            self.updateSettings()

    def analyse(self):
        """Begin analysis of next gene member of the queue."""
        geneFound = False
        self.outputSet = False
        self.analyseButton.setDisabled(False)
        for gene in self.geneList:
            if not gene.progress and not geneFound:
                geneFound = True
                gene.finished.connect(lambda: self.finishedAnalysis(gene))
                gene.start()

                self.analyseButton.setDisabled(True)

                self.connect(gene, SIGNAL("updateStatuses()"), self.updateStatuses)

    def finishedAnalysis(self, gene):
        """Executes when analysis thread has terminated, takes an AnalyserThread object. Adds the
        generated data to the list of recent data and begins the analysis of the next gene in the queue."""
        if gene.progress == 2:
            self.addRecentLoc(gene.destination)
        self.analyse()

    def addToQueue(self):
        """Adds a new gene member (AnalyserThread object) to the queue based on data in textboxes.
        Also updates the program preferences with new miRNA and TF data locations."""
        self.settings.set('locations', 'miRNA', self.miRNAFileInput.text())
        self.settings.set('locations', 'TF', self.TFFileInput.text())
        self.updateSettings()

        genesToAdd = self.geneNameInput.text()
        
        for splitCharacter in self.geneSeparationCharacters:
            genesToAdd = genesToAdd.replace(splitCharacter, ",")

        genes = genesToAdd.split(',')

        for gene in genes:
            self.geneList += [AnalyserThread(gene, self.miRNAFileInput.text(), self.TFFileInput.text(), str(self.outputFolderInput.text()).replace("[gene]", gene), self)]
            self.queueTabs.insertTab(-1, gene)

        self.geneNameInput.clear()
        self.outputFolderInput.clear()

    def removeGene(self, geneId):
        """Removes the appropriate gene member from the queue. Takes an integer representing the gene's
        position in the queue."""
        if self.geneList[geneId].progress != 1:
            self.queueTabs.removeTab(geneId)
            del self.geneList[geneId]
            self.updateStatuses()

    def moveGene(self, initial, final):
        """Changes the order of a certain gene in the gene queue. Takes two integers representing the gene's
        initial and final positions in the queue."""
        self.geneList.insert(final, self.geneList.pop(initial))

    def updateStatuses(self):
        """Refresh the status messages such that they reflect the status of the currently
        selected gene."""
        self.dataViewButton.hide()
        if len(self.geneList) > 0:
            self.statuses.setText("<br />".join(self.geneList[self.queueTabs.currentIndex()].statuses))
            if self.geneList[self.queueTabs.currentIndex()].progress == 2:
                self.dataViewButton.show()
        else:
            self.statuses.setText("")

    def viewDataButton(self):
        """Opens the data window showing the data generated from the currently selected gene."""
        self.viewData(self.geneList[self.queueTabs.currentIndex()].destination) 

    def viewDataOpen(self):
        """Opens the data window using information from a user-chosen folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select folder")
        if len(folder):
            self.viewData(folder)
            if not folder in self.recentDataLoc:
                self.addRecentLoc(folder)

    def viewData(self, destination):
        """Opens the data window using information from the passed folder."""
        if os.access(destination,os.R_OK):
            varName = 'dataWindow'
            name = varName + str(self.dataWindowCount)
            vars(self)[name] = DataRep.DataRep(destination)
            vars(self)[name].show()
            self.dataWindowCount+=1
        else:
            errorBox = QMessageBox()
            errorBox.setText("File not found")
            errorBox.setInformativeText("The gene data could not be found at " + destination + ".")
            errorBox.setIcon(QMessageBox.Warning)
            errorBox.setStandardButtons(QMessageBox.Ok)
            errorBox.exec_()


    def addRecentLoc(self,folder):
        """Adds the passed folder to the list of recent data (for the menu bar)."""
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

    def updateOutput(self, geneName):
        """Change the output folder textbox value to reflect the value in the gene name textbox. Takes a string containing
        the gene name or list of genes."""
        if not len(self.outputFolderInput.text()):
            self.outputSet = False
        if not self.outputSet:
            multipleGenes = False
            for separationCharacter in self.geneSeparationCharacters:
                if separationCharacter in geneName:
                    multipleGenes = True
            self.outputFolderInput.setText("Output/" + ("[gene]" if multipleGenes else geneName) + "/")

    def chooseFile(self, textbox):
        """Opens a dialog box in which the user can choose a file, the location of which is then added to the textbox
        passed to the function."""
        file = QFileDialog.getOpenFileName(self, "Select file")
        if len(file):
            textbox.setText(file)

    def chooseFolder(self, textbox):
        """Opens a dialog box in which the user can choose a folder, the path to which is then added to the passed
        textbox."""
        folder = QFileDialog.getExistingDirectory(self, "Select folder")
        if len(folder):
            textbox.setText(folder)
            self.outputSet = True

    def updateSettings(self):
        """Updates the settings file with the new settings."""
        with open(settingsLocation, "wb") as settingsFile:
                self.settings.write(settingsFile)

    def keyPressEvent(self, event):
        """Handle the user pressing the enter key -- add a new gene member to the queue."""
        if type(event) == QKeyEvent:
            if event.key() == 16777220:
                self.addToQueue()

    def help(self):
        """Opens the help window."""
        self.helpWindow = HelpDocumentation()
        self.helpWindow.show()

    def about(self):
        """Opens the about window."""
        self.aboutWindow = About()
        self.aboutWindow.show()

class AnalyserThread(QThread):
    def __init__(self, geneName, miRNA, TF, destination, window):
        """Creates the thread object with the properties as passed to the function."""
        QThread.__init__(self)
        
        self.geneName, self.miRNA, self.TF, self.destination, self.window = str(geneName), str(miRNA), str(TF), str(destination), window
        self.statuses = [ "Waiting..." ]
        self.progress = 0

    def feedback(self, string):
        """"Updates the status list for the analysis thread."""
        self.statuses += [ string ]
        self.emit(SIGNAL("updateStatuses()"))

    def confirm(self, title, question):
        """Creates a dialog box from the passed dialog box title and question (strings). Returns a boolean based on
        the user's input."""
        messageBox = QMessageBox()
        messageBox.setText(title)
        messageBox.setInformativeText(question)
        messageBox.setIcon(QMessageBox.Warning)
        messageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        return True if messageBox.exec_() == 16384 else False

    def run(self):
        """Begins the thread and calls the analyser function from GeneAnalyser.py."""
        self.progress = 1

        if GeneAnalysis.Program(self.geneName, self.miRNA, self.TF, self.destination, self):
            self.progress = 2
        else:
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

        Subtitle3 = QLabel('What is the "Enrichment Score"?')
        Subtitle3.setFont(SubHeadingFont)
        grid.addWidget(Subtitle3,5,0)
        #Not sure if the science is correct. :P
        Text3 = QLabel('The Enrichment Score produced is a factor of relevance, being the amount of genes that a miRNA targets with a TF,\n divided by the total amound of genes for that miRNA. This gives an indication of how relevant the two factors are to each other.')
        Text3.setFont(TextFont)
        grid.addWidget(Text3,6,0)

        Exit = QPushButton("Close")
        grid.addWidget(Exit,7,0)
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
        grid.addWidget(QLabel("Working with Doctor Gantier"), 2, 0)
        grid.addWidget(QLabel('Version: '+__version__), 3, 0)


app = QApplication(sys.argv)

window = Application()
window.show()
window.raise_()

app.exec_()