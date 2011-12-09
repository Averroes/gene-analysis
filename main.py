__author__ = 'cwhi19 and mgeb1'
__version__ = '0.3.0'

import sys, ConfigParser, GeneAnalysis, DataRep, os
from PyQt4.Qt import *

settingsLocation = "settings.ini"

class Application(QMainWindow):
    def __init__(self):
        """Set up the GUI elements of the main interface"""

        # Initialise application window and layout
        QMainWindow.__init__(self)
        self.setWindowTitle("Gene Analysis")
        self.mainWidget = QWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.grid = QGridLayout(self.mainWidget)

        self.dataWindowCount = 0 # Allows data windows to be opened, to be able to compare data.
        self.geneSeparationCharacters = [ "\r\n", "\n", "\r", " ", "\t", "," ] # Characters that denote a split between gene names
        self.dataImported = False
        self.analyser = GeneAnalysis.Analyser()

        menubar = self.menuBar() # Initialise program menu bar
        fileMenu = menubar.addMenu("File") # Create file menu
        openAction = QAction("Open data...", self) # Menu option for choosing data from a given path
        openAction.triggered.connect(self.viewDataOpen)
        self.recentDataMenu = QMenu("Recent Data",self) # Menu option for viewing data that has been recently opened/generated
        fileMenu.addMenu(self.recentDataMenu)
        fileMenu.addAction(openAction)

        helpMenu = menubar.addMenu("Help") # Create help menu
        helpAction = QAction("Help Documentation",self) # Menu option for viewing documentation window
        helpAction.triggered.connect(self.help)
        helpMenu.addAction(helpAction)

        aboutAction = QAction("Program Information", self) # Menu option for viewing basic program information
        aboutAction.triggered.connect(self.about)
        helpMenu.addAction(aboutAction)

        self.geneList = [] # Create empty gene queue

        self.grid.addWidget(QLabel("Simplified miRNA File:"), 0, 0) # Row for miRNA textbox and file browser
        self.miRNAFileInput = QLineEdit()
        self.grid.addWidget(self.miRNAFileInput, 0, 1)
        self.miRNABrowse = QPushButton("Browse")
        self.grid.addWidget(self.miRNABrowse, 0, 2)

        self.grid.addWidget(QLabel("Simplified TF File:"), 1, 0) # Row for TF textbox and file browser
        self.TFFileInput = QLineEdit()
        self.grid.addWidget(self.TFFileInput, 1, 1)
        self.TFBrowse = QPushButton("Browse")
        self.grid.addWidget(self.TFBrowse, 1, 2)

        self.databaseProgress = QProgressBar()
        self.databaseProgress.setRange(0, 0)
        self.databaseProgress.setTextVisible(False)
        self.grid.addWidget(self.databaseProgress, 2, 0, 1, 3)
        self.databaseImportButton = QPushButton("Import Databases")
        self.grid.addWidget(self.databaseImportButton, 2, 0, 1, 3)
        self.databaseProgress.hide()

        self.grid.addWidget(QLabel("Gene Name:"), 3, 0) # Row for gene input
        self.geneNameInput = QLineEdit()
        self.grid.addWidget(self.geneNameInput, 3, 1, 1, 2)

        self.grid.addWidget(QLabel("Output Directory:"), 4, 0) # Row for destination location of data
        self.outputFolderInput = QLineEdit()
        self.grid.addWidget(self.outputFolderInput, 4, 1)
        self.outputBrowse = QPushButton("Browse")
        self.grid.addWidget(self.outputBrowse, 4, 2)
        self.outputSet = False

        self.queueButton = QPushButton("Add to queue") # Button to add gene information to queue
        self.queueButton.setAutoDefault(True)
        self.grid.addWidget(self.queueButton, 5, 0, 1, 3)

        self.analyseButton = QPushButton("Begin Analysis") # Button to begin analysis of genes in queue
        self.grid.addWidget(self.analyseButton, 6, 0, 1, 3)
        self.analyseButton.setDisabled(True)

        self.queueTabs = QTabBar() # Tabbed interface showing gene queue
        self.queueTabs.setTabsClosable(True)
        self.queueTabs.setMovable(True)
        self.grid.addWidget(self.queueTabs, 7, 0, 1, 3)

        self.statuses = QLabel("") # Empty status label, is later updated with information relating to gene
        self.grid.addWidget(self.statuses, 8, 0, 1, 3)
        self.statuses.setAlignment(Qt.AlignTop)

        self.dataViewButton = QPushButton("View results") # Add button for viewing generated results, only visible if analysis succeeded
        self.grid.addWidget(self.dataViewButton, 9, 0, 1, 3)
        self.dataViewButton.hide()

        # Connect events (eg. button pushes) to appropriate events
        self.connect(self.geneNameInput, SIGNAL('textChanged(QString)'), (lambda x: self.updateOutput(x)))
        self.connect(self.miRNABrowse, SIGNAL('clicked()'), lambda: self.chooseFile(self.miRNAFileInput))
        self.connect(self.TFBrowse, SIGNAL('clicked()'), lambda: self.chooseFile(self.TFFileInput))
        self.connect(self.databaseImportButton, SIGNAL('clicked()'), self.importData)
        self.connect(self.outputBrowse, SIGNAL('clicked()'), lambda: self.chooseFolder(self.outputFolderInput))
        self.connect(self.queueButton, SIGNAL('clicked()'), self.addToQueue)
        self.connect(self.analyseButton, SIGNAL('clicked()'), self.analyse)
        self.connect(self.dataViewButton, SIGNAL('clicked()'), self.viewDataButton)
        self.connect(self.queueTabs, SIGNAL('currentChanged(int)'), self.updateStatuses)
        self.connect(self.queueTabs, SIGNAL('tabCloseRequested(int)'), lambda x: self.removeGene(x))
        self.connect(self.queueTabs, SIGNAL('tabMoved(int,int)'), lambda x, y: self.moveGene(x, y))

        # Handle settings.ini
        self.settings = ConfigParser.RawConfigParser() # Initialise settings object for program duration
        try: # Set TF and miRNA location textboxes to values found in settings.ini
            self.settings.read(settingsLocation)
            self.miRNAFileInput.setText(self.settings.get('locations', 'miRNA'))
            self.TFFileInput.setText(self.settings.get('locations', 'TF'))
        except ConfigParser.NoSectionError: # If settings.ini not in correct format (ie. headers not found), set values to defaults
            self.miRNAFileInput.setText("Resources/miRNA.txt")
            self.TFFileInput.setText("Resources/TF.txt")

            self.settings.add_section('locations')
            self.settings.set('locations', 'miRNA', 'Resources/miRNA.txt')
            self.settings.set('locations', 'TF', 'Resources/TF.txt')

            self.updateSettings()

        try: # Set recent data locations
            self.recentDataLoc = self.settings.get('recentData','Locations').split(',')

            for location in self.recentDataLoc:
                if not os.access(location,os.R_OK): # Check if each location still exists
                    self.recentDataLoc.remove(location) # If location no longer exists, remove from the list

            for location in self.recentDataLoc:
                location += '/' if location[-1] != '/' else '' # Add forward slash to end of path if necessary (for consistency)
                gene = location.split('/')[-2] # Split on forward slash, take the second to last element as gene name
                vars()[gene] = QAction(str(gene),self)
                vars()[gene].triggered.connect(lambda a, y=location: self.viewData(y))
                self.recentDataMenu.addAction(vars()[gene]) # Add each gene name to the list of recent data

        except ConfigParser.NoSectionError: # If the recent data section was not formatted correctly, set to empty default
            self.recentDataLoc = []
            self.settings.add_section('recentData')
            self.settings.set('recentData','Locations','')
            self.updateSettings()

    def analyse(self):
        """Begin analysis of next gene member of the queue."""

        # Find the next gene ready for analysis (ie. progress is set to 0)
        if self.dataImported:
            geneFound = False
            self.outputSet = False
            self.analyseButton.setDisabled(False) # Make analysis button enabled (in case gene to analyse cannot be found)
            for gene in self.geneList:
                if not gene.progress and not geneFound: # If the progress is 0 and an earlier gene has not been found
                    geneFound = True
                    gene.finished.connect(lambda: self.finishedAnalysis(gene)) # Link the end of the thread object to this function
                    gene.start() # Begin the analysis thread

                    self.analyseButton.setDisabled(True) # Prevent the user from trying to analyse data while process is running

                    self.connect(gene, SIGNAL("updateStatuses()"), self.updateStatuses)
                    # Connect emission of status update signal from thread to the actual status update in the Application object
        else:
            print "Data not imported!" #TODO: add feedback

    def finishedAnalysis(self, gene):
        """Executes when analysis thread has terminated, takes an AnalyserThread object. Adds the
        generated data to the list of recent data and begins the analysis of the next gene in the queue."""
        if gene.progress == 2: # If the gene analysis finished successfully
            self.addRecentLoc(gene.destination) # Add the gene path to recently generated data list
        self.analyse()

    def importData(self):
        self.settings.set('locations', 'miRNA', self.miRNAFileInput.text())
        self.settings.set('locations', 'TF', self.TFFileInput.text())
        self.updateSettings() # Update the settings file with new locations (if changed)

        self.dataImported = False
        self.analyseButton.setDisabled(True)

        self.databaseImportButton.hide()
        self.databaseProgress.show()

        self.analyserThread = ImportThread(self.miRNAFileInput.text(), self.TFFileInput.text(), self.analyser)

        self.analyserThread.finished.connect(self.imported)
        self.analyserThread.start()

    def imported(self):
        self.dataImported = True
        self.databaseImportButton.show()
        self.databaseProgress.hide()
        self.analyseButton.setDisabled(False)

    def addToQueue(self):
        """Adds a new gene member (AnalyserThread object) to the queue based on data in textboxes."""

        genesToAdd = self.geneNameInput.text() # Get the gene(s) from the user's input
        
        for splitCharacter in self.geneSeparationCharacters: # Interpret the input as a list of genes if required
            genesToAdd = genesToAdd.replace(splitCharacter, ",") # Replace all valid separators with a comma

        genes = genesToAdd.split(',') # Split the genes on commas

        for gene in genes: # Create a thread object for each gene and add to the end of the queue
            self.geneList += [AnalyserThread(gene, str(self.outputFolderInput.text()).replace("[gene]", gene), self, self.analyser)]
            self.queueTabs.insertTab(-1, gene)

        self.geneNameInput.clear()
        self.outputFolderInput.clear() # Clear the form for the next submission

    def removeGene(self, geneId):
        """Removes the appropriate gene member from the queue. Takes an integer representing the gene's
        position in the queue."""
        if self.geneList[geneId].progress != 1: # If the analaysis is not in progress
            self.queueTabs.removeTab(geneId) # Remove the tab itself from the interface
            del self.geneList[geneId] # Remove the thread object
            self.updateStatuses()

    def moveGene(self, initial, final):
        """Changes the order of a certain gene in the gene queue. Takes two integers representing the gene's
        initial and final positions in the queue."""
        self.geneList.insert(final, self.geneList.pop(initial))

    def updateStatuses(self):
        """Refresh the status messages such that they reflect the status of the currently
        selected gene."""
        self.dataViewButton.hide() # Hide view data button in case the gene has not been analysed
        if len(self.geneList) > 0: # If the queue is not empty
            self.statuses.setText("<br />".join(self.geneList[self.queueTabs.currentIndex()].statuses))
            # Update the status message with text from the thread object
            if self.geneList[self.queueTabs.currentIndex()].progress == 2: # If the analysis has finished
                self.dataViewButton.show() # Show the button to view the results
        else:
            self.statuses.setText("") # Show no messages if no genes are in the queue

    def viewDataButton(self):
        """Opens the data window showing the data generated from the currently selected gene."""
        self.viewData(self.geneList[self.queueTabs.currentIndex()].destination)

    def viewDataOpen(self):
        """Opens the data window using information from a user-chosen folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select folder") # Allow the user to choose path to data
        if len(folder):
            self.viewData(folder)
            if not folder in self.recentDataLoc:
                self.addRecentLoc(folder) # Add the path to recently opened data list if not already present

    def viewData(self, destination):
        """Opens the data window using information from the passed folder."""
        if os.access(destination,os.R_OK): # If data is valid
            varName = 'dataWindow'
            name = varName + str(self.dataWindowCount)
            vars(self)[name] = DataRep.DataRep(destination) # Create separate variable for each results window
            vars(self)[name].show()
            self.dataWindowCount+=1
        else:
            errorBox = QMessageBox() # If data not found, display error message
            errorBox.setText("File not found")
            errorBox.setInformativeText("The gene data could not be found at " + destination + ".")
            errorBox.setIcon(QMessageBox.Warning)
            errorBox.setStandardButtons(QMessageBox.Ok)
            errorBox.exec_()


    def addRecentLoc(self,folder):
        """Adds the passed folder to the list of recent data (for the menu bar)."""
        folder += '/' if folder[-1] != '/' else '' # Add forward slash if required for consistency
        gene = folder.split('/')[-2] # Split on forward slash and take second last element as gene name
        while len(self.recentDataLoc) > 10: # Limit recent data to 10 elements
            self.recentDataLoc.pop(0)
        if len(self.recentDataLoc) > 9 and not folder in self.recentDataLoc:
            self.recentDataLoc.pop(0)
        if not folder in self.recentDataLoc: # If not already present
            self.recentDataLoc += [folder] # Add the recent data to the list
        string = ''
        for location in self.recentDataLoc: # Generate string for settings.ini
            string += ',' if string != '' else ''
            string += location
        self.settings.set('recentData','Locations',string) # Store data string to settings
        self.updateSettings() # Update settings.ini

        vars()[gene] = QAction(str(gene),self)
        vars()[gene].triggered.connect(lambda a:self.viewData(folder)) # Connect menu item to action of opening window
        self.recentDataMenu.addAction(vars()[gene])

    def updateOutput(self, geneName):
        """Change the output folder textbox value to reflect the value in the gene name textbox. Takes a string containing
        the gene name or list of genes."""
        if not len(self.outputFolderInput.text()): # If no destination is in the textbox, allow it to be dynamically generated
            self.outputSet = False
        if not self.outputSet: # If the user has not already set the destination, dynamically generate it
            multipleGenes = False
            for separationCharacter in self.geneSeparationCharacters: # Check if multiple genes are present
                if separationCharacter in geneName:
                    multipleGenes = True
            self.outputFolderInput.setText("Output/" + ("[gene]" if multipleGenes else geneName) + "/")
            # Show either template for gene destination (if multiple) or location with folder being the gene name

    def chooseFile(self, textbox):
        """Opens a dialog box in which the user can choose a file, the location of which is then added to the textbox
        passed to the function."""
        file = QFileDialog.getOpenFileName(self, "Select file") # Allows user to choose a file
        if len(file): # If a file has been successfully chosen
            textbox.setText(file) # Set value of textbox to chosen file path

    def chooseFolder(self, textbox):
        """Opens a dialog box in which the user can choose a folder, the path to which is then added to the passed
        textbox."""
        folder = QFileDialog.getExistingDirectory(self, "Select folder") # Allows user to choose a folder
        if len(folder): # If a folder has been successfully chosen
            textbox.setText(folder) # Set value of textbox to chosen folder path
            self.outputSet = True # Prevent the user's selection from being overwritten by a dynamically generated destination

    def updateSettings(self):
        """Updates the settings file with the new settings."""
        settingsFile = open(settingsLocation, "wb")
        self.settings.write(settingsFile)
#        with open(settingsLocation, "wb") as settingsFile:
#            self.settings.write(settingsFile) # Write the updated settings to the file from the settings object

    def keyPressEvent(self, event):
        """Handle the user pressing the enter key -- add a new gene member to the queue."""
        if type(event) == QKeyEvent:
            if event.key() == 16777220: # If enter is pressed
                self.addToQueue() # Add current gene to the queue

    def help(self):
        """Opens the help window."""
        self.helpWindow = HelpDocumentation()
        self.helpWindow.show() # Show the help window

    def about(self):
        """Opens the about window."""
        self.aboutWindow = About()
        self.aboutWindow.show() # Show the about window

class ImportThread(QThread):
    def __init__(self, miRNA, TF, analyser):
        QThread.__init__(self)
        self.miRNA, self.TF, self.analyser = miRNA, TF, analyser

    def run(self):
        self.analyser.importData(self.miRNA, self.TF)

    

class AnalyserThread(QThread):
    def __init__(self, geneName, destination, window, analyser):
        """Creates the thread object with the properties as passed to the function."""
        QThread.__init__(self)

        # Initialise variables
        self.geneName, self.destination, self.window, self.analyser = str(geneName), str(destination), window, analyser
        self.statuses = [ "Waiting..." ] # Default initial status
        self.progress = 0 # Waiting progress

    def feedback(self, string):
        """"Updates the status list for the analysis thread."""
        self.statuses += [ string ] # Show status message
        self.emit(SIGNAL("updateStatuses()")) # Send message to main thread to update status display

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
        self.progress = 1 # Show that the analysis is in progress

        if self.analyser.Program(self.geneName, self.destination, self):
            self.progress = 2 # Show that the analysis has finished successfully
        else:
            self.progress = -1 # Show that analysis has finished unsuccessfully


class HelpDocumentation(QWidget):
    def __init__(self):
        # Initialise help window and layout
        QWidget.__init__(self)
        grid = QGridLayout(self)
        self.setWindowTitle("Help")
        QWidget.setMinimumSize(self,600,400)

        # Initialise window fonts
        TitleFont = QFont("Times",20)
        SubHeadingFont = QFont('Times',14)
        TextFont = QFont('Times',10)

        # Create title
        Title = QLabel('Gene Analysis Documentation:')
        Title.setFont(TitleFont)
        grid.addWidget(Title,0,0)

        # Create labels with introductory information
        Subtitle1 = QLabel('Purpose:')
        Subtitle1.setFont(SubHeadingFont)
        grid.addWidget(Subtitle1,1,0)
        #This text1 isjust an example, and is not by any means what I intend to put in.
        Text1 = QLabel('The purpose of this program is to provide data that represents the most common TF sites and mirna binding sites to the user.\n Based on these, users may be able to determine other genes with simmilar functions.')
        Text1.setFont(TextFont)
        grid.addWidget(Text1,2,0)

        # Create labels with a setting up guide
        Subtitle2 = QLabel('Setting Up:')
        Subtitle2.setFont(SubHeadingFont)
        grid.addWidget(Subtitle2,3,0)
        #This text2 is also just an example.
        Text2 = QLabel('In this application, the files "Mirna.txt" and "TF.txt" will automatically be looked for from the location of the Main.exe file.\n If you don\'t have these files under "Resources/..." then you will have to select the locations using the file option.\n Once you have selected these options, you can select a gene to process, such as TNFAIP3, IRAK1, RNF11 or PTEN.\nThe program will then create a set of files with data under the location of the executible, unless a destination is specified otherwise.')
        Text2.setFont(TextFont)
        grid.addWidget(Text2,4,0)

        # Create labels with further information
        Subtitle3 = QLabel('What is the "Enrichment Score"?')
        Subtitle3.setFont(SubHeadingFont)
        grid.addWidget(Subtitle3,5,0)
        #Not sure if the science is correct. :P
        Text3 = QLabel('The Enrichment Score produced is a factor of relevance, being the amount of genes that a miRNA targets with a TF,\n divided by the total amound of genes for that miRNA. This gives an indication of how relevant the two factors are to each other.')
        Text3.setFont(TextFont)
        grid.addWidget(Text3,6,0)

        # Create a close button
        Exit = QPushButton("Close")
        grid.addWidget(Exit,7,0)
        self.connect(Exit,SIGNAL('clicked()'),self.Cancel)

    def Cancel(self):
        self.close() # Close window if the close button is pressed

class About(QWidget):
    def __init__(self):
        # Initialise window and layout
        QWidget.__init__(self)
        grid = QGridLayout(self)
        self.setWindowTitle("About")

        # Choose fonts and output information to window
        programTitle = QLabel("Gene Analyser")
        programTitle.setFont(QFont("Arial", 12))
        grid.addWidget(programTitle, 0, 0)
        grid.addWidget(QLabel("Matt Gebert and Chris Whittle"), 1, 0)
        grid.addWidget(QLabel("Working with Doctor Gantier"), 2, 0)
        grid.addWidget(QLabel('Version: '+__version__), 3, 0)


app = QApplication(sys.argv) # Initialise main application

window = Application()
window.show()
window.raise_() # Focus on the window

app.exec_()