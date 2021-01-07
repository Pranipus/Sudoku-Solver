import sys
from PyQt5.QtWidgets import(
    QMainWindow, 
    QApplication, 
    QWidget, 
    QAction, 
    QTableWidget, 
    QTableWidgetItem, 
    QVBoxLayout, 
    QHBoxLayout, 
    QPushButton, 
    QStyledItemDelegate, 
    QFileDialog,
    QDialog,
    QSlider,
    QGridLayout,
    QLabel,
    )

from PyQt5.QtGui import QIcon, QFont, QPen
from PyQt5.QtCore import pyqtSlot, Qt, QDir
import numpy as np 
from time import sleep


#paints the lines of soduko board
class Delegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        painter.setPen(QPen(Qt.black, 3))

        if (index.row() == 2 or index.row() == 5):
            painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())

        if (index.column() == 2 or index.column() == 5): 
            painter.drawLine(option.rect.topRight(), option.rect.bottomRight())

class App(QWidget):
    

    def __init__(self):
        super().__init__()
        self.title = 'Sudoku Solver'
        self.setWindowIcon(QIcon('icon.svg'))
        self.left = 0
        self.top = 0
        self.width = 474
        self.height = 555

        self.grid = np.array([[8, 7, 6, 9, 0, 0, 0, 0, 0],
                             [0, 1, 0, 0, 0, 6, 0, 0, 0],
                             [0, 4, 0, 3, 0, 5, 8, 0, 0],
                             [4, 0, 0, 0, 0, 0, 2, 1, 0],
                             [0, 9, 0, 5, 0, 0, 0, 0, 0],
                             [0, 5, 0, 0, 4, 0, 3, 0, 6],
                             [0, 2, 9, 0, 0, 0, 0, 0, 8],
                             [0, 0, 4, 6, 9, 0, 1, 7, 3],
                             [0, 0, 0, 0, 0, 1, 0, 0, 4]])
        self.initUI()
        
        

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        #self.setMinimumWidth(474); self.setMinimumHeight(504)
        self.setFixedSize(self.size())
        
        self.createTable()

        self.vLayout = QVBoxLayout(); self.setLayout(self.vLayout)
        self.vLayout.addWidget(self.table) 

        self.optionsGrid = QGridLayout()
        self.optionsGrid.setColumnStretch(0, 1); self.optionsGrid.setColumnStretch(1, 1)#makes sure slider doesnt take extra space in grid.
        self.vLayout.addLayout(self.optionsGrid)

        self.openButton = QPushButton('Open')
        self.solveButton = QPushButton('Solve')
        #self.stopButton = QPushButton('Stop')
        #self.sliderLayout = QHBoxLayout()
        
        self.optionsGrid.addWidget(self.openButton, 0, 0)
        self.optionsGrid.addWidget(self.solveButton, 0, 1)
        #self.optionsGrid.addWidget(self.stopButton, 1, 0)
        #self.optionsGrid.addLayout(self.sliderLayout, 1, 1)
        
        """
        self.delaySlider = QSlider(Qt.Horizontal)
        self.sliderLabel = QLabel('Delay')
        self.sliderInner = QVBoxLayout()
        self.ticksLabel = QLabel('Ticks')
        self.sliderInner.addWidget(self.delaySlider); self.sliderInner.addWidget(self.ticksLabel)
        self.sliderLayout.addWidget(self.sliderLabel); self.sliderLayout.addLayout(self.sliderInner)

        #slider config
        self.delaySlider.setMinimum(1); self.delaySlider.setMaximum(5)
        self.delaySlider.setValue(3)
        self.delaySlider.setTickPosition(QSlider.TicksBelow)
        self.delaySlider.setTickInterval(1)
        """
        fnt = QFont(); fnt.setPointSize(10)
        self.openButton.setFont(fnt)
        self.solveButton.setFont(fnt)
        #self.stopButton.setFont(fnt)
        #self.sliderLabel.setFont(fnt)

        self.solveButton.clicked.connect(self.solve)
        self.openButton.clicked.connect(self.openFromFile)
        #TODO connect Stop button and Slider to functions

        # Show widget
        self.show()

    def createTable(self):
        self.table = QTableWidget()
        self.table.setRowCount(9)
        self.table.setColumnCount(9)
        #self.table.move(round(self.height/2), round(self.width/2))
        self.table.setMaximumWidth(452); self.table.setMaximumHeight(452)
        self.table.setMaximumHeight(452); self.table.setMinimumHeight(452)
        
        #headers and cell sizes 
        hHeader = self.table.horizontalHeader(); hHeader.setDefaultSectionSize(50)
        vHeader = self.table.verticalHeader()  ; vHeader.setDefaultSectionSize(50)
        hHeader.setVisible(False); vHeader.setVisible(False)

        #font 
        fnt = self.table.font()
        fnt.setPointSize(36)
        self.table.setFont(fnt)
        
        self.generateStartTable()
        self.table.setItemDelegate(Delegate(self.table))
    
    #Takes the default sudoku puzzle in file and adds it to the board
    def generateStartTable(self):
        for y in range(9):
            for x in range(9):

                toSet = self.grid[y,x]
                if toSet == 0: 
                    item = QTableWidgetItem('')
                    item.setFlags(Qt.ItemIsEnabled)
                    self.table.setItem(y, x, item)

                else:
                    #make font bold 
                    bold = QFont(); bold.setBold(True)
                    item = QTableWidgetItem(str(toSet))
                    item.setFlags(Qt.ItemIsEnabled)
                    self.table.setItem(y, x, item)
                    item.setFont(bold)
        

    def updateTable(self, y, x, n):
        item = QTableWidgetItem(str(n))
        item.setFlags(Qt.ItemIsEnabled)
        self.table.setItem(y,x, item)
        QApplication.processEvents()
        

    def findEmpty(self):
        for y in range(9):
            for x in range(9):
                if self.grid[y,x] == 0:
                    return (y, x)
        return None

    @pyqtSlot()
    def solve(self):
        found = self.findEmpty()

        if not found:
            print(np.matrix(self.grid))
            return True
        else:
            y, x = found

        for n in range(1,10):
            if self.possible(y, x, n):
                self.grid[y,x] = n; self.updateTable(y, x, n)

                if self.solve():
                    return True

                self.grid[y,x] = 0; self.updateTable(y, x, '')
        return False        

    def possible(self, y, x, n):
        row = self.grid[y]
        col = self.grid[:,x]
        if n in row or n in col:
            return False
        
        y0 = y//3 * 3
        x0 = x//3 * 3
        block = self.grid[y0:y0+3, x0:x0+3]
        if n in block:
            return False
        
        return True


    @pyqtSlot()
    def openFromFile(self):
        print("open from file clicked")

        dialog = QFileDialog(self)
        dialog.setWindowTitle('Open Sudoku puzzle')
        dialog.setNameFilter('Text files (*.txt)')
        dialog.setDirectory(QDir.currentPath())
        dialog.setFileMode(QFileDialog.ExistingFile)

        if dialog.exec_() == QDialog.Accepted:
            filePath = str(dialog.selectedFiles()[0])
            filePath = QDir.toNativeSeparators(filePath)
            print(filePath)
            self.loadFromFile(filePath)
        else:
            return None

    def loadFromFile(self, path):
        f = open(path, 'r')

        self.grid = np.array([[int(n) for n in line.split()] for line in f], dtype=object)

        if np.shape(self.grid) == (9,9):
            self.generateStartTable()
        else: 
            self.showMsg("file format is incorrect")


    def showMsg(self, msg):
        print(msg)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = App()
    sys.exit(app.exec_())  