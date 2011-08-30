__author__ = 'cwhi19 and mgeb1'

from Tkinter import *
from tkFileDialog import *

class Application:

    def __init__(self, root):
        self.font = ("Verdana", 8)
        self.fontBold = ("Verdana", 8, "bold")

        self.analyserForm = Frame(root)
        self.analyserForm.grid(row=0, column=0, sticky=W)

        Label(self.analyserForm, text="Gene Name:", font=self.font).grid(row=0, column=0, sticky=W)
        self.geneName = Entry(self.analyserForm)
        self.geneName.grid(row=0, column=1, columnspan=2, sticky=W)

        Label(self.analyserForm, text="Simplified miRNA File:", font=self.font).grid(row=1, column=0, sticky=W)
        self.miRNAFile = Entry(self.analyserForm)
        self.miRNAFile.grid(row=1, column=1, sticky=W)
        Button(self.analyserForm, text="Browse", command=self.choosemiRNA).grid(row=1, column=2, sticky=W)

        Label(self.analyserForm, text="Simplified TF File:", font=self.font).grid(row=2, column=0, sticky=W)
        self.TFFile = Entry(self.analyserForm)
        self.TFFile.grid(row=2, column=1, sticky=W)
        Button(self.analyserForm, text="Browse", command=self.chooseTF).grid(row=2, column=2, sticky=W)

        Button(self.analyserForm, text="Analyse", font=self.fontBold).grid(row=3, column=0, columnspan=3, padx=20, pady=20, ipadx=10, ipady=5, sticky=E)

    def choosemiRNA(self):
        self.miRNAFile.delete(0, END)
        self.miRNAFile.insert(0, askopenfilename())

    def chooseTF(self):
        self.TFFile.delete(0, END)
        self.TFFile.insert(0, askopenfilename())

root = Tk()
root.title("Gene Analyser")
window = Application(root)
root.mainloop()