__author__ = 'cwhi19 and mgeb1'

import sys, os
from PyQt4.Qt import *

class DataRep(QWidget):
    def __init__(self, geneFolder):
        geneFolder += "" if geneFolder[-1] == '/' else "/"
        geneName = geneFolder.replace('\\','/')
        geneName = geneName.split('/')[-2]
        QWidget.__init__(self)
        self.setWindowTitle("Gene Data - " + geneName)
        QWidget.setMinimumSize(self,800,400)
        self.grid = QGridLayout(self)

        self.processedData = []

        dataFile = open(geneFolder + geneName +  " - Spreadsheet.csv")
        headers = dataFile.readline().replace("\n", "").split(",")
        for line in dataFile:
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
        self.orderOptions = QComboBox()
        for header in headers:
            self.orderOptions.addItem(header)
        self.grid.addWidget(self.orderOptions, 0, 1)

        self.grid.addWidget(QLabel("Filter:"), 0, 2)
        self.filterInput = QLineEdit()
        self.grid.addWidget(self.filterInput, 0, 3)
        self.connect(self.filterInput,SIGNAL("textChanged(QString)"),self.filterData)

        self.dataTable = QTableWidget(1, len(headers))
        self.grid.addWidget(self.dataTable, 1, 0, 1, 4)
        self.dataTable.setHorizontalHeaderLabels(headers)

        self.orderOptions.setCurrentIndex(3)    
        self.connect(self.orderOptions,SIGNAL("currentIndexChanged(int)"),self.sortBy)
        self.filterData()
        self.setColumnSizes()

        self.copyAction = QAction("Copy",self)
        self.copyAction.setShortcut("Ctrl+C")
        self.addAction(self.copyAction)
        self.connect(self.copyAction,SIGNAL("triggered()"),self.copyCells)

    def copyCells(self):
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
        size =  (int(str(QWidget.size(self)).split("(")[1].split(',')[0])-80)/self.dataTable.columnCount()
        for head in range(0,self.dataTable.columnCount()):
            self.dataTable.setColumnWidth(head,size)

    def filterData(self):
        self.writeableData = []
        currentText = str(self.filterInput.displayText())
        for data in self.processedData:
            if currentText in str(data):
                self.writeableData.append(data)
        self.sortBy()

    def sortBy(self):
        index = self.orderOptions.currentIndex()
        self.writeableData = sorted(self.writeableData,key=lambda x: x[index],reverse=True if index > 1 else False)
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
        self.setColumnSizes()
