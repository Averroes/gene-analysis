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
        headers = dataFile.readline().replace("\n", "").split("\t")
        dataFile.close()

        self.grid.addWidget(QLabel("Order by:"), 0, 0)
        self.orderOptions = QComboBox()
        for header in headers:
            self.orderOptions.addItem(header)
        self.grid.addWidget(self.orderOptions, 0, 1)

        self.grid.addWidget(QLabel("Filter:"), 0, 2)
        self.filterInput = QLineEdit()
        self.grid.addWidget(self.filterInput, 0, 3)

        self.dataTable = QTableWidget(5, len(headers))
        self.grid.addWidget(self.dataTable, 1, 0, 1, 4)
        self.dataTable.setHorizontalHeaderLabels(headers)
        self.connect(self.orderOptions,SIGNAL("currentIndexChanged(int)"),self.sortBy)

    def sortBy(self):
        #TODO: It would be handy perhaps to intake data as lists within lists. IE [[Mirna,TF,Enrich,Size],[Mirna,TF,Enrich,Size]...]
        index = self.orderOptions.currentIndex()
        self.processedData = sorted(self.processedData,key=lambda x: x[index],reverse=True if index > 1 else False)
        self.dataTable.clearContents()
        row = 0
        for set in self.processedData:
            column = 0
            for data in set:
                Item = QTableWidgetItem(data)
                self.dataTable.setItem(row,column,Item)
                column +=1
            row+=1

    def test(self):
        print self.dataTable.currentColumn()


app = QApplication(sys.argv)

window = DataRep("Output/tnfaip3/", "tnfaip3")
window.show()

app.exec_()