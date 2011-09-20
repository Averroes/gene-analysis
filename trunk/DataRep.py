__author__ = 'cwhi19 and mgeb1'

import sys, os
from PyQt4.Qt import *

class DataRep(QWidget):
    def __init__(self, geneFolder, geneName):
        QWidget.__init__(self)
        self.setWindowTitle("Gene Data")
        self.grid = QGridLayout(self)

        self.processedData = []

        dataFile = open(geneFolder + geneName + " - Spreadsheet.csv")
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

        self.dataTable = QTableWidget(len(self.processedData), len(headers))
        self.grid.addWidget(self.dataTable, 1, 0, 1, 4)
        self.dataTable.setHorizontalHeaderLabels(headers)

        self.orderOptions.setCurrentIndex(3)    
        self.connect(self.orderOptions,SIGNAL("currentIndexChanged(int)"),self.sortBy)
        self.filterData()

    def filterData(self):
        self.writeableData = []
        currentText = str(self.filterInput.displayText())
        for data in self.processedData:
            if currentText in str(data):
                self.writeableData.append(data)
        self.sortBy()

    def sortBy(self):
        #TODO: It would be handy perhaps to intake data as lists within lists. IE [[Mirna,TF,Enrich,Size],[Mirna,TF,Enrich,Size]...]
        index = self.orderOptions.currentIndex()
        self.writeableData = sorted(self.writeableData,key=lambda x: x[index],reverse=True if index > 1 else False)
        self.dataTable.clearContents()
        row = 0
        for set in self.writeableData:
            column = 0
            for data in set:
                Item = QTableWidgetItem(str(data))
                self.dataTable.setItem(row,column,Item)
                column +=1
            row+=1

app = QApplication(sys.argv)

window = DataRep("Output/tnfaip3/", "tnfaip3")
window.show()

app.exec_()