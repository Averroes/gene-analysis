__author__ = 'cwhi19 and mgeb1'

import sys, os, re
import time
from PyQt4.Qt import *

class DataRep(QWidget):
    """Creates a QWidget window for viewing data generated from main.py
    Users can sort by the different columns, and copy the data in tab
    demented formatting. A filter bar also allows users to easily access
    specific combinations they are interested in."""
    def __init__(self, geneFolder):
        """Initial Function, creates a data table with the data in columns,
        default is organised by the intersections Length. """
        QWidget.__init__(self)
        grid1 = QGridLayout(self)
        tabs = QTabWidget(self)
        tabs.setMovable(True)
        grid1.addWidget(tabs,0,0)


        geneFolder += "" if geneFolder[-1] == '/' else "/" #Provides a consistency for the form of the Destination
        geneName = geneFolder.replace('\\','/')
        geneName = geneName.split('/')[-2] #Takes the last bit of string of Destination, ie The Gene Name.

        self.setWindowTitle("Gene Data - " + geneName)
        QWidget.setMinimumSize(self,500,200) #Sets a minimum size, smaller wouldn't be any benefit.


#        self.miRNATab = QWidget()

#        for dir,dirs,files in os.walk(geneFolder):
#            fileNames = files
#            break
#        try:
#            a = fileNames
#        except AttributeError:
#            fileNames = ''
#        search = re.search(' - Top([0-9]*?)Mirna\'s\.txt',str(fileNames),re.IGNORECASE)
#        percent = search.group(1) if search else '[unknown]'
#        mirnaFile = open(geneFolder + geneName +  " - Top"+search.group(1)+"Mirna\'s.txt") #Opens the Data file of the gene name.
#        mirnaHeaders = mirnaFile.readline().replace('\n','').split('\t')
#        mirnaData = []
#        for line in mirnaFile:
#            mirnaData += [line.replace('\n','').split('\t')]
#        mirnaData = sorted(mirnaData,key=lambda x: int(x[1]),reverse=True)
#        self.grid2 = QGridLayout(self.miRNATab)
#        self.mirnaTable = QTableWidget()
#        for row in range(0,len(mirnaHeaders)):
#            self.mirnaTable.insertColumn(0)
#        for column in range(0,len(mirnaData)):
#            self.mirnaTable.insertRow(0)
#        for row in range(0,len(mirnaData)):
#            for column in range(0,len(mirnaHeaders)):
#                item = QTableWidgetItem(str(mirnaData[row][column]))
#                self.mirnaTable.setItem(row,column,item)
#        self.mirnaTable.setHorizontalHeaderLabels(mirnaHeaders)
#        self.grid2.addWidget(self.mirnaTable,0,0)

        self.TableDataTab = QWidget()

        self.grid = QGridLayout(self.TableDataTab)
        self.processedData = [] #String for Data from File
        self.writeableData = [] #String for Filtered Data
        self.geneData = {}
        self.filterStr = '' #Variable for String that Data has been filtered from. Is used for speeding up filter function
        self.geneDataWindows = []

        dataFile = open(geneFolder + geneName +  " - Results.txt") #Opens the Data file of the gene name.)
        headers = dataFile.readline().replace("\n", "").split("\t") #Obtains First Line of Data, which has Headers.
        headers = headers[0:4]
        for line in dataFile:
            line = line.split('\t')
            genes = line[-1]
            line = line[0:4]
            newLine = []
            for element in line:
                try:
                    element = float(element)
                except ValueError:
                    pass
                newLine.append(element)
            self.processedData.append(newLine)
            self.geneData.update({(line[0],line[1]):genes})
        dataFile.close()

        self.grid.addWidget(QLabel("Order by:"), 0, 0)
        self.orderOptions = QComboBox() #Selection Box for Ordering Data.
        for header in headers:
            self.orderOptions.addItem(header)
        self.grid.addWidget(self.orderOptions, 0, 1)

        self.grid.addWidget(QLabel("Filter:"), 0, 2)
        self.filterInput = QLineEdit() #Input Box for Filtering Data, based on string and/or numbers.
        self.grid.addWidget(self.filterInput, 0, 3)
        self.connect(self.filterInput,SIGNAL("textChanged(QString)"),self.filterData)

        self.dataTable = QTableWidget(1, len(headers)) #The table for the data of the file.
        self.grid.addWidget(self.dataTable, 1, 0, 1, 4)
        self.dataTable.setHorizontalHeaderLabels(headers)

        self.orderOptions.setCurrentIndex(3)    
        self.connect(self.orderOptions,SIGNAL("currentIndexChanged(int)"),self.sortBy)
        self.filterData() #Doesn't really filter data, as filter string = '', but goes on and sorts it.
        self.setColumnSizes() #Creates column sizes based on the size of the widget, when initially run.

        #Creates the Copy action of the Table widget, as copy only copied individual cells previously.
        self.copyAction = QAction("Copy",self)
        self.copyAction.setShortcut("Ctrl+C")
        self.addAction(self.copyAction)
        self.connect(self.copyAction,SIGNAL("triggered()"),self.copyCells)

        tabs.addTab(self.TableDataTab,"Intersection Data")
#        tabs.addTab(self.miRNATab,'Top '+ str(percent) +' MiRNAs')

        self.dataTable.connect(self.dataTable,SIGNAL("cellDoubleClicked(int, int)"),self.cellDoubleClickedEvent)
        #TODO: See below - this is the connection call.

#        self.dataTable.connect(self.dataTable,SIGNAL("cellChanged(int, int)"),self.sortBy) #For some reason this code causes a maximum depth/
#    #Recursion error. Even when using filter function, recursion somehow occurs in a different part of the function. 

    def copyCells(self):
        """The Copy Function for the DataTable. Copies a tab-demented form of the table to the windows clipboard.
        Can be interpreted in excel, but not many other programs."""
        clpStr = ''
        selection = self.dataTable.selectedRanges()[0]
        Bottom = selection.bottomRow()
        Left = selection.leftColumn()
        Right = selection.rightColumn()
        Top = selection.topRow()
        for row in range(Top,Bottom+1):
            for column in range(Left,Right+1):
                cell = self.dataTable.item(row,column).text()
                clpStr+=cell
                if not column == Right:
                    clpStr+='\t'
            clpStr+='\n'
        clipboard = QApplication.clipboard()
        clipboard.setText(clpStr)
        return

    def setColumnSizes(self):
        """To resize the column sizes based on percentage values"""
        size =  (int(str(QWidget.size(self)).split("(")[1].split(',')[0])-103)/self.dataTable.columnCount() #The 80 compensates for the scroll bar.
        for head in range(0,self.dataTable.columnCount()):
            self.dataTable.setColumnWidth(head,size)
#        size2 = (int(str(QWidget.size(self)).split("(")[1].split(',')[0])-90)/self.mirnaTable.columnCount()
#        for head in range(0,self.mirnaTable.columnCount()):
#            self.mirnaTable.setColumnWidth(head,size2)
        

    def filterData(self):
        """Filters results in table based on filter input."""
        currentText = str(self.filterInput.displayText())
        newData = []
        if self.filterStr in currentText and self.filterStr != '': #Tests if what is needed to be sorted is part of what has been sorted, so save time.
            for data in self.writeableData:
                if currentText in str(data):
                    newData.append(data)
        else: #Filters the data based on the original data.
            for data in self.processedData:
                if currentText in str(data):
                    newData.append(data)
        self.writeableData = newData
        self.sortBy() #Sorts the new writable data by the Sort Option.
        self.filterStr = currentText #Sets a variable to remember what has already been filtered.

    def sortBy(self):
        index = self.orderOptions.currentIndex() #Takes the element that we are sorting by.
        self.writeableData = sorted(self.writeableData,key=lambda x: x[index],reverse=True if index > 1 else False) #Sorts the data.
        #Re-inserts the new data.
        self.dataTable.clearContents()
        if self.dataTable.rowCount():
            for row in range(0,self.dataTable.rowCount()-1):
                self.dataTable.removeRow(0)
        for row in range(0,len(self.writeableData)-1):
            self.dataTable.insertRow(0)
        row = 0
        for set in self.writeableData:
            column = 0
            for data in set:
                Item = QTableWidgetItem(str(data))
                self.dataTable.setItem(row,column,Item)
                column +=1
            row+=1

    def resizeEvent(self, *args, **kwargs):
        """Catches the resizeEvent call of QWidget, allowing us to respecify the column sizes."""
        self.setColumnSizes()

    def cellDoubleClickedEvent(self, *args):
        """Should Catch Event Of QTableWidget to edit"""
        #TODO: Make this function occur after the Signal of a double click of a cell creates an edit instance.
        item = self.dataTable.item(args[0],args[1])
        self.dataTable.closePersistentEditor(item)
        geneSet = tuple(self.writeableData[args[0]][0:2])
        geneViewer = ViewGenes(self.geneData[geneSet],geneSet)
        self.geneDataWindows.append(geneViewer)
        self.geneDataWindows[-1].show()

class ViewGenes(QWidget):
    def __init__(self,genes,geneSet):
        QWidget.__init__(self)
        self.setWindowTitle('miRNA "' + str(geneSet[0]) + '" and TF "' + str(geneSet[1])+'" - Intersecting Genes.')
        self.setMinimumSize(QSize(300,150))
        self.resize(QSize(400,500))
        grid = QGridLayout(self)
        grid.addWidget(QLabel('Genes:'), 0, 0)
        self.filterInput = QLineEdit()
        self.connect(self.filterInput,SIGNAL("textChanged(QString)"),self.filterData)
        grid.addWidget(self.filterInput,0,1)
        self.table = QTableWidget()
        self.table.insertColumn(0)
        self.table.insertRow(0)
        self.table.setHorizontalHeaderLabels(['Genes'])
        grid.addWidget(self.table,1,0,1,2)

        self.genes = genes.replace('[','').replace(']','').replace("'",'').replace(" ","").replace("\n",'').split(',')
        self.writeableData = self.genes
        self.filterStr = ''

        self.sort()

    def resizeEvent(self, *args):
        self.setColumnSizes()

    def setColumnSizes(self):
        size = (int(str(QWidget.size(self)).split("(")[1].split(',')[0])-80)
        self.table.setColumnWidth(0,size)

    def filterData(self):
        """Filters results in table based on filter input."""
        currentText = str(self.filterInput.displayText())
        newData = []
        if self.filterStr in currentText and self.filterStr != '': #Tests if what is needed to be sorted is part of what has been sorted, so save time.
            for data in self.writeableData:
                if currentText in str(data):
                    newData.append(data)
        else: #Filters the data based on the original data.
            for data in self.genes:
                if currentText in str(data):
                    newData.append(data)
        self.writeableData = newData
        self.sort() #Sorts the new writable data by the Sort Option.
        self.filterStr = currentText #Sets a variable to remember what has already been filtered.

    def sort(self):
        self.writeableData = sorted(self.writeableData)
        self.table.clearContents()
        if self.table.rowCount():
            for row in range(0,self.table.rowCount()-1):
                self.table.removeRow(0)
        for row in range(0,len(self.writeableData)-1):
            self.table.insertRow(0)
        row = 0
        for gene in self.writeableData:
            Item = QTableWidgetItem(str(gene))
            self.table.setItem(row,0,Item)
            row+=1

class StackResults(QWidget):
    """A widget viewer to view the results of a merged Top MiRNA file.
    Same code as used in MiRNA generation above, but able to stand alone."""
    def __init__(self, mirnaFileLoc):
        QWidget.__init__(self)
        self.setWindowTitle('Combined Top-Mirna Results')
        self.grid1 = QGridLayout(self)
        mirnaFile = open(mirnaFileLoc) #Opens the Data file of the gene name.
        mirnaContributingGenes = mirnaFile.readline().replace('\n','')
        self.grid1.addWidget(QLabel(mirnaContributingGenes),0,0)
        mirnaHeaders = mirnaFile.readline().replace('\n','').split('\t')
        mirnaData = []
        for line in mirnaFile:
            mirnaData += [line.replace('\n','').split('\t')]
        mirnaData = sorted(mirnaData,key=lambda x: int(x[1]),reverse=True)
        self.mirnaTable = QTableWidget()
        for row in range(0,len(mirnaHeaders)):
            self.mirnaTable.insertColumn(0)
        for column in range(0,len(mirnaData)):
            self.mirnaTable.insertRow(0)
        for row in range(0,len(mirnaData)):
            for column in range(0,len(mirnaHeaders)):
                item = QTableWidgetItem(str(mirnaData[row][column]))
                self.mirnaTable.setItem(row,column,item)
        self.mirnaTable.setHorizontalHeaderLabels(mirnaHeaders)
        self.grid1.addWidget(self.mirnaTable,1,0)
        self.resize(QSize(400,200))
        self.setColumnSizes()

    def resizeEvent(self, *args, **kwargs):
        """Catches the resizeEvent call of QWidget, allowing us to respecify the column sizes."""
        self.setColumnSizes()

    def setColumnSizes(self):
        size2 = (int(str(QWidget.size(self)).split("(")[1].split(',')[0])-70)/self.mirnaTable.columnCount()
        for head in range(0,self.mirnaTable.columnCount()):
            self.mirnaTable.setColumnWidth(head,size2)