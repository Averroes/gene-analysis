__author__ = 'cwhi19 and mgeb1'

import sys, os
from PyQt4.Qt import *

class DataRep(QWidget):
    """Creates a QWidget window for viewing data generated from main.py
    Users can sort by the different columns, and copy the data in tab
    demented formatting. A filter bar also allows users to easily access
    specific combinations they are interested in."""
    def __init__(self, geneFolder):
        """Initial Function, creates a data table with the data in columns,
        default is organised by the intersections Length. """

        geneFolder += "" if geneFolder[-1] == '/' else "/" #Provides a consistency for the form of the Destination
        geneName = geneFolder.replace('\\','/')
        geneName = geneName.split('/')[-2] #Takes the last bit of string of Destination, ie The Gene Name.

        QWidget.__init__(self)
        self.setWindowTitle("Gene Data - " + geneName)
        QWidget.setMinimumSize(self,400,200) #Sets a minimum size, smaller wouldn't be any benefit.
        self.grid = QGridLayout(self)

        self.processedData = [] #String for Data from File
        self.writeableData = [] #String for Filtered Data
        self.filterStr = '' #Variable for String that Data has been filtered from. Is used for speeding up filter function

        dataFile = open(geneFolder + geneName +  " - Spreadsheet.csv") #Opens the Data file of the gene name.
        headers = dataFile.readline().replace("\n", "").split(",") #Obtains First Line of Data, which has Headers.
        for line in dataFile: #Takes all remaining data lines
            line = line.split(',')
            newLine = []
            for element in line:
                try:
                    element = float(element)
                except ValueError:
                    pass
                newLine.append(element)
            self.processedData.append(newLine)
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
        size =  (int(str(QWidget.size(self)).split("(")[1].split(',')[0])-80)/self.dataTable.columnCount() #The 80 compensates for the scroll bar.
        for head in range(0,self.dataTable.columnCount()):
            self.dataTable.setColumnWidth(head,size)

    def filterData(self):
        """Filters results in table based on filter input."""
        currentText = str(self.filterInput.displayText())
        newData = []
        if self.filterStr in currentText: #Tests if what is needed to be sorted is part of what has been sorted, so save time.
            for data in self.processedData:
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
