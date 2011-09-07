__author__ = 'cwhi19 and mgeb1'

import sys
from PyQt4.Qt import *

class Application(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Gene Analysis")
        self.grid = QGridLayout(self)

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

        self.grid.addWidget(QPushButton("Add to queue"), 4, 0, 1, 3)

        self.connect(self.geneNameInput, SIGNAL('textChanged(QString)'), (lambda x: self.updateOutput(x)))
        self.connect(self.miRNABrowse, SIGNAL('clicked()'), lambda: self.chooseFile(self.miRNAFileInput))
        self.connect(self.TFBrowse, SIGNAL('clicked()'), lambda: self.chooseFile(self.TFFileInput))
        self.connect(self.outputBrowse, SIGNAL('clicked()'), lambda: self.chooseFolder(self.outputFolderInput))

    def updateOutput(self, x):
        self.outputFolderInput.setText("Output/" + x + "/")

    def chooseFile(self, textbox):
        textbox.setText(QFileDialog.getOpenFileName(self, "Select file"))

    def chooseFolder(self, textbox):
        textbox.setText(QFileDialog.getExistingDirectory(self, "Select folder"))

app = QApplication(sys.argv)

window = Application()
window.show()

app.exec_()