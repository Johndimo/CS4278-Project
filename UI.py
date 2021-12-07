#!/usr/bin/env python
# coding: utf-8

import sys
import os
import plotly
import tkinter

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from plotly.graph_objects import Figure, Scatter
from tkinter import ttk
from tkinter import simpledialog

from TSNE_Algorithm.tsneAlgo import TsnePlot

styles = """
        QWidget {
          Background: '#a8d0e6';
        }
        QLabel {
          padding-top: 10px;
          padding-bottom: 30px;
          font-family: 'Helvetica';
          font-size: 15px  
        }
        QPushButton {
          Background: #80aaff;
          color: 'black';
          font-size: 15px;
          border-radius: 20px;
          border: 2px solid '#6699ff'
        }
        QPushButton:hover {
          Background: #b3ccff;
          color: 'black';
          font-size: 15px;
          border-radius: 20px;
        }
        """

recentFileList = []
figure = None

def readRecentFiles():
    global recentFileList
    file1 = open('.\\recentFiles.txt', 'r')
    Lines = file1.readlines()
    non_empty_lines = [line for line in Lines if line.strip() != ""]
    for line in non_empty_lines:
        recentFileList.append(line)
        
def writeRecentFiles():
    global recentFileList
    file1 = open('.\\recentFiles.txt', 'w')
    i = 0
    while i < len(recentFileList) and i < 10:
        file1.write(recentFileList[i])
        i += 1
    file1.close()

class UI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        global recentFileList
        recentFileList.clear()
        readRecentFiles()

        self.resize(1500, 750)
        self.center()
        # self.setWindowTitle('no title')
        self.setWindowIcon(QIcon(".\\app-icon.ico"))
        self.setStyleSheet(styles)
        
        label1 = QLabel('<h1>t-SNE Clustering Analysis</h1>')
        label1.setAlignment(Qt.AlignHCenter)
        
        label2 = QLabel('<h3>Open a file to run the t-SNE algorithm on:</h3>')
        label2.setAlignment(Qt.AlignCenter)

        
        openFileBtn = QPushButton("Open File", self)
        openFileBtn.setToolTip('Click here to upload a file')
        openFileBtn.setFixedSize(220, 50)

        helpBtn = QPushButton("Help", self)
        helpBtn.setToolTip('Click here to read instructions')
        helpBtn.setFixedSize(220, 50)
        
        quitBtn = QPushButton("Quit", self)
        quitBtn.setToolTip('Click here to quit')
        quitBtn.setFixedSize(220, 50)
        
        recentFileListWidget = QListWidget()
        recentFileListWidget.setFixedSize(450, 350)
        recentFileListWidget.setStyleSheet('QListWidget'
                                            '{'
                                            'border: 3px solid #d7eaf4;'
                                            'padding: 10px;'
                                            'border-radius: 15px'
                                            '}')
        
        for line in recentFileList:
            QListWidgetItem(os.path.basename(line), recentFileListWidget)

        placeholder = QPushButton(' ', self)
        placeholder.setFixedSize(450, 450)
        placeholder.setStyleSheet('background: #a8d0e6;'
                                  'border-color: #a8d0e6;')
        
        outer_layout = QHBoxLayout()
        self.layout = QVBoxLayout()
        self.layout.addWidget(label1)
        self.layout.addStretch()
        self.layout.addWidget(label2)
        self.layout.addWidget(openFileBtn, alignment=Qt.AlignCenter)
        self.layout.addWidget(helpBtn, alignment=Qt.AlignCenter)
        self.layout.addWidget(quitBtn, alignment=Qt.AlignCenter)
        self.layout.addStretch()

        recentFilesLabel = QLabel('<h3>Recently Used Files</h3>')

        sideLayout = QVBoxLayout()
        sideLayout.addStretch()
        sideLayout.addWidget(recentFilesLabel, alignment=Qt.AlignCenter)
        sideLayout.addWidget(recentFileListWidget, alignment=Qt.AlignRight)

        outer_layout.addWidget(placeholder, alignment=Qt.AlignLeft)
        outer_layout.addLayout(self.layout)
        outer_layout.addLayout(sideLayout)

        self.setLayout(outer_layout)
        openFileBtn.clicked.connect(lambda: self.open())
        helpBtn.clicked.connect(self.open_instructions_window)
        quitBtn.clicked.connect(self.close)
        recentFileListWidget.itemDoubleClicked.connect(lambda listItem: self.open(listItem))
        
        self.show()

    def center(self):
        # geometry of the main window
        qr = self.frameGeometry()

        # center point of screen
        cp = QDesktopWidget().availableGeometry().center()

        # move rectangle's center point to screen's center point
        qr.moveCenter(cp)

        # top left of rectangle becomes top left of window centering it
        self.move(qr.topLeft())
        
    def open(self, itemWidget=False):
        global recentFileList
        path=[]
        if not itemWidget:
           path = QFileDialog.getOpenFileName(self, 'Open a file', '',
                                        'All Files (*.*)')
        else:
           path.append(recentFileList[itemWidget.listWidget().currentRow()][ : -1])
        
        if path != ('', ''):
            print("File path : "+ path[0])
            
            pathStr = path[0] + "\n"
            if pathStr not in recentFileList:
                recentFileList.insert(0, pathStr)
            else:
                index = recentFileList.index(pathStr)
                recentFileList.pop(index)
                recentFileList.insert(0, pathStr)
        
        tsneClass = TsnePlot(path[0])
        sheets = tsneClass.getSheets()
        tk = tkinter.Tk()
        tk.withdraw()
        val = ChoiceDialog(tk, "Pick a sheet",
                              text = "Pick a sheet",
                              items = sheets)
        tsneClass.setSheet(val.selection)
        sheets.clear()
            
        columns = tsneClass.getColumns()
        weightedColumns = weightedColumnSelection(tk, 
                                                    title="Pick the columns that you want to be weighted",
                                                    text="Pick the columns that you want to be weighted", 
                                                      items=columns)
            
        tsneClass.setPrioCols(weightedColumns.selection)
                                                      
        column1 = OptionsDialog(tk, "Pick the symbol output column", text="Pick the symbol output column", columns=columns)
        column1Selection = column1.colSelect.get()
            
        newColumns = columns
        newColumns.remove(str(column1Selection))
            
        column2 = OptionsDialog(tk, "Pick the color output column", text="Pick the color output column", columns=newColumns)
        column2Selection = column2.colSelect.get()
            
        tsneClass.setOutputColumns(str(column1Selection), str(column2Selection))
        
        self.label = QLabel()
        self.movie = QMovie(".\\loader-symbol.gif")
        self.label.setMovie(self.movie)
        self.movie.start()
        self.layout.addWidget(self.label, alignment=Qt.AlignCenter)

        self.worker = Worker(tsneClass)
        self.worker.start()
        self.worker.finished.connect(lambda: self.display_output(tsneClass, weightedColumns.selection))
    
    def display_output(self, tsneClass, weightedColumns):
        global figure
        if figure is None:
            self.movie.stop()
            self.layout.removeWidget(self.label)
            self.label.deleteLater()
            self.label = None
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)

            msg.setText("One of the proposed output columns has invalid or corrupt data")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            self.w = ClusteringAlgorithmWindow(tsneClass, weightedColumns)
            self.w.show()
            self.close()
        
    def open_instructions_window(self, checked):
        self.w = InstructionsWindow()
        self.w.show()
        self.close()
        
    def closeEvent(self, event):
        writeRecentFiles()
        self.close()
        
class InstructionsWindow(QWidget):
  
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.resize(1250, 750)
        self.center()
        self.setStyleSheet(styles)
        self.setWindowTitle('')
        
        label1 = QLabel('<h1>Instructions & Help</h1>')
        label1.setAlignment(Qt.AlignHCenter)
        label1.setGeometry(470, 70, 111, 21)
        
        label2 = QLabel('''<h3>Instructions for file upload:</h3>''')
        label2.setWordWrap(True) 
        label2.setGeometry(120, 80, 161, 21)

        label5 = QLabel('''<h3>The algorithm only runs on .csv-type files. If you provide a file of a 
        different type, it will give the 'select sheet' pop up, but will be blank. You can cancel 
        out of this window and reselect a valid file. If the file was directly imported from the 
        Vanderbilt SD, there is nothing else for you to do. The format should work automatically.</h3>''')
        label5.setWordWrap(True)
        label5.setGeometry(160, 130, 771, 71)

        label3 = QLabel('''<h3>If the csv has been doctored recently,
        then make sure that the file has its title/attribute names in the first row only.\n
        Then the data below it must be continuous, without any random blank rows. 
        Blank rows may lead to data below not being included in the clustering algorithm. </h3>''')
        label3.setWordWrap(True) 
        label3.setGeometry(160, 180, 751, 41)
        
        label4 = QLabel('''<h3>This application has not been created to edit or reformat the data itself,
        so if the format/data is not valid, the program will not produce the output you are looking for.
        It will notify you if one of the two input columns for either the algorithm weighting function
        or the output display are invalid, though it will not specify which of the two it was. 
        You can use this to begin troubleshooting the file, and hopefully clean up any errors. </h3>''')
        label4.setWordWrap(True) 
        label4.setGeometry(160, 220, 741, 61)

        label6 = QLabel('''<h3>It is also worth keeping in mind that sometimes this application can be useful
        for spotting strange nuances in how the data has been edited or presented.
        For example, if you expect an attribute to be a binary 0 or 1, 
        but find it plots as a gradient from -9 to 1, then you may find edge-case data that is out of date. 
        In this example, -9 may have been used as a null indicator. </h3>''')
        label6.setWordWrap(True)
        label6.setGeometry(160, 310, 631, 41)

        layout = QVBoxLayout()
        layout.addWidget(label1)
        layout.addWidget(label2)
        layout.addWidget(label5)
        layout.addWidget(label3)
        layout.addWidget(label4)
        layout.addWidget(label6)
        # self.resize(1500, 750)

        self.setLayout(layout)
        
        self.show()
        
    def center(self):
        # geometry of the main window
        qr = self.frameGeometry()

        # center point of screen
        cp = QDesktopWidget().availableGeometry().center()

        # move rectangle's center point to screen's center point
        qr.moveCenter(cp)

        # top left of rectangle becomes top left of window centering it
        self.move(qr.topLeft())
        
    def closeEvent(self, event):
        self.w = UI()
        self.w.show()
        self.close()
        
class ClusteringAlgorithmWindow(QWidget):
  
    def __init__(self, tsneClass, weightedColumns):
        super().__init__()
        self.init_ui(tsneClass, weightedColumns)
        
    def init_ui(self, tsneClass, weightedColumns):
        global figure
        self.setStyleSheet("background-color: #d7eaf4;")
        self.resize(1500, 750)
        self.center()
        self.setWindowTitle('t-SNE output')
        
        label1 = QLabel('<h1>Select new columns to be shown in the output below</h1>')
        label1.setAlignment(Qt.AlignHCenter)
        
        cbStyle = """
                QComboBox { 
                    border: 1px solid #000000; 
                    border-radius: 3px;
                    background-color: #e5ecf6;
                    padding: 1px 23px 1px 3px; 
                    min-width: 6em; 
                    color: #000000;
                }
                """
        btnStyle = """
                QPushButton {
                    border: 1px solid #000000; 
                    border-radius: 3px;
                    background-color: #e5ecf6;
                    padding: 1px 23px 1px 3px; 
                    min-width: 6em; 
                    color: #000000;
                }
        """
        cols = tsneClass.getColumns()
        comboBox = QComboBox()
        comboBox.addItems(cols)
        comboBox.setFixedSize(150, 40)
        comboBox.setStyleSheet(cbStyle)
        
        comboBox2 = QComboBox()
        comboBox2.addItems(cols)
        comboBox2.setFixedSize(150, 40)
        comboBox2.setStyleSheet(cbStyle)
        
        submitBtn = QPushButton("Submit")
        submitBtn.setToolTip('Click here to submit your column selection')
        submitBtn.setFixedSize(150, 40)
        submitBtn.setStyleSheet(btnStyle)

        
        self.html = '<html><body>'
        self.html += plotly.offline.plot(figure, output_type='div', include_plotlyjs='cdn')
        self.html += '</body></html>'

        # we create an instance of QWebEngineView and set the html code
        self.plot_widget = QWebEngineView()
        self.plot_widget.setHtml(self.html)

        weightedColumnsWidget = QListWidget()
        weightedColumnsWidget.setFixedSize(160, 110)
        weightedColumnsWidget.setStyleSheet('QListWidget'
                                            '{'
                                            'border: 1px solid #000000;'
                                            'padding: 10px;'
                                            'border-radius: 15px;'
                                            'background-color: #e5ecf6'
                                            '}')
        
        for line in weightedColumns:
            QListWidgetItem(line, weightedColumnsWidget)
            
        label2 = QLabel('<h4>Weighted Columns</h4>')
        
        layoutV = QVBoxLayout()
        layoutV.addWidget(label2, alignment=Qt.AlignCenter)
        layoutV.addWidget(weightedColumnsWidget)
        layout = QVBoxLayout()
        layoutH = QHBoxLayout()
        layout.addWidget(label1)
        layoutH.addLayout(layoutV)
        layoutH.addWidget(comboBox)
        layoutH.addWidget(comboBox2)
        layoutH.addWidget(submitBtn)
        layout.addLayout(layoutH)
        layout.addWidget(self.plot_widget)

        submitBtn.clicked.connect(lambda: self.runAlgorithmOnNewColumns([comboBox.currentText(), comboBox2.currentText()], tsneClass))
        self.setLayout(layout)
        self.show()
        
    def runAlgorithmOnNewColumns(self, columns, tsneClass):
        tsneClass.setOutputColumns(columns[0], columns[1])
        res = tsneClass.getFigure()
        print(type(res))
        if res is None:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)

            msg.setText("One of the proposed output columns has invalid or corrupt data")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            newFig = tsneClass.getFigure()
            self.html = '<html><body>'
            self.html += plotly.offline.plot(newFig, output_type='div', include_plotlyjs='cdn')
            self.html += '</body></html>'
            self.plot_widget.setHtml(self.html)
    
    def center(self):
        # geometry of the main window
        qr = self.frameGeometry()

        # center point of screen
        cp = QDesktopWidget().availableGeometry().center()

        # move rectangle's center point to screen's center point
        qr.moveCenter(cp)

        # top left of rectangle becomes top left of window centering it
        self.move(qr.topLeft())
        
    def closeEvent(self, event):
        self.w = UI()
        self.w.show()
        self.close()

class ChoiceDialog(simpledialog.Dialog):
    def __init__(self, parent, title, text, items):
        self.selection = None
        self._items = items
        self._text = text
        super().__init__(parent, title=title)

    def body(self, parent):
        self._message = tkinter.Message(parent, text=self._text, aspect=400)
        self._message.pack(expand=1, fill=tkinter.BOTH)
        self._list = tkinter.Listbox(parent)
        self._list.pack(expand=1, fill=tkinter.BOTH, side=tkinter.TOP)
        for item in self._items:
            self._list.insert(tkinter.END, item)
        return self._list

    def validate(self):
        if not self._list.curselection():
            return 0
        return 1

    def apply(self):
        self.selection = self._items[self._list.curselection()[0]]
        
class OptionsDialog(simpledialog.Dialog):
    def __init__(self, parent, title, text, columns):
        self.colSelect = tkinter.StringVar(parent)
        self._columns = columns
        self._text = text
        super().__init__(parent, title = title)
    
    def body(self, parent):
        self._message = tkinter.Message(parent, text = self._text, aspect=400)
        self._message.pack(expand=1, fill=tkinter.BOTH)
        self.colSelectMenu = ttk.OptionMenu(
            parent,
            self.colSelect,
            self._columns[0],
            *self._columns)
        self.colSelectMenu.pack(expand=1, fill=tkinter.BOTH)

class weightedColumnSelection(simpledialog.Dialog):
    def __init__(self, parent, title, text, items):
        self.selection = []
        self._items = items
        self._text = text
        super().__init__(parent, title=title)

    def body(self, parent):
        self._message = tkinter.Message(parent, text=self._text, aspect=400)
        self._message.pack(expand=1, fill=tkinter.BOTH)
        self._list = tkinter.Listbox(parent, selectmode = "multiple")
        self._list.pack(expand=1, fill=tkinter.BOTH, side=tkinter.TOP)
        for item in self._items:
            self._list.insert(tkinter.END, item)
        return self._list

    def validate(self):
        if not self._list.curselection():
            return 0
        return 1

    def apply(self):
        temp = self._list.curselection()
        for i in temp:
            self.selection.append(self._items[i])
            
class Worker(QThread):
    
    def __init__(self, tsneClass):
        super(Worker, self).__init__()
        self.tsneClass = tsneClass
        
    def run(self):
        global figure
        figure = self.tsneClass.getPlot()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = UI()
    sys.exit(app.exec_())

