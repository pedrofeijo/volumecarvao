#!/bin/python3
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import alphashape
import platform
import requests
import random
import shutil
import string
import PyQt5
import Xlib
import Xlib.display
import glob
import json
import pptk
import sys
import os
from   PyQt5 import QtWidgets, QtGui, QtCore
from   PyQt5.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QApplication, QAbstractItemView, QWidget, QGridLayout, QPushButton, QTextEdit, QMessageBox, QFileDialog, QDialog, QComboBox
from   descartes import PolygonPatch
from   PIL import Image
import time

class Second(QMainWindow):
    def __init__(self, parent=None):
        super(Second, self).__init__(parent)

        self.mywidget = QWidget()

        self.dataWidget    = QWidget()
        self.buttonsWidget = QWidget()

        self.mylayout      = QGridLayout(self.mywidget)
        self.dataLayout    = QGridLayout(self.dataWidget)
        self.buttonsLayout = QGridLayout(self.buttonsWidget)

        self.setCentralWidget(self.mywidget)
        # pylint: disable=line-too-long
        payload = {"responseType":"fieldList", "initDate":"2010-01-01 00:00:00", "endDate":"2100-10-31 23:59:59"}
        dbRequest = requests.get('http://localhost:8503/pointCloudData', params=payload)
        self.dbDatas = json.loads(dbRequest.text)
        idList      = list()
        initList    = list()
        missionList = list()
        self.nRows = len(self.dbDatas)
        for i in range(0, self.nRows):
            idList.append(self.dbDatas[i]['id'])
            initList.append(self.dbDatas[i]['flight_init'])
            missionList.append(self.dbDatas[i]['mission'])

        self.createTable(idList, initList, missionList)

        self.buttonCancel = QPushButton('Cancelar')
        self.buttonSelect = QPushButton('Selecionar')

        self.buttonCancel.clicked.connect(self.cancelAction)
        self.buttonSelect.clicked.connect(self.selectAction)

        if self.tableWidget.rowCount() == 0:
            self.buttonSelect.setEnabled(False)
        else:
            self.tableWidget.selectRow(0)

        self.dataLayout.addWidget(self.tableWidget)

        self.buttonsLayout.addWidget(self.buttonSelect, 0, 0)
        self.buttonsLayout.addWidget(self.buttonCancel, 0, 1)

        self.mylayout.setColumnStretch(1, 2)
        self.mylayout.addWidget(self.dataWidget, 0, 0, 1, 2)
        self.mylayout.addWidget(self.buttonsWidget, 1, 0)

        self.setGeometry(0,0,337,300)
        self.setMaximumWidth(350)

    def createTable(self, idList, initList, missionList):
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(self.nRows)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        if self.nRows > 0:
            for i in range(self.nRows-1,-1,-1):
                date = initList[i].split('-')[2].split('T')[0]+'/'+initList[i].split('-')[1]+'/'+initList[i].split('-')[0] + ' ' + initList[i].split('-')[2].split('T')[1][:-5]
                self.tableWidget.setItem(self.nRows-i-1, 0, QTableWidgetItem(str(idList[i])))
                self.tableWidget.setItem(self.nRows-i-1, 1, QTableWidgetItem(date))
                self.tableWidget.setItem(self.nRows-i-1, 2, QTableWidgetItem(missionList[i][:-4]))
                self.tableWidget.move(10,20)
        self.tableWidget.setHorizontalHeaderLabels(['id', 'data e hora','missão'])
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    def cancelAction(self):
        form.dialogBox.clear()
        form.dialogBox.textCursor().insertText('Nenhuma nuvem escolhida!\n')
        form.repaint()
        form.mywidget.setEnabled(True)
        self.close()

    def selectAction(self):
        if self.debugMode:
            print('Select load action')
        pcdId = self.tableWidget.selectedItems()[0].text()
        form.dbId = pcdId
        payload = {"responseType":"pcdFile","id":pcdId,"pcdFile":"raw"}
        r = requests.get('http://localhost:8503/pointCloudData', params=payload)
        headerData = json.dumps(dict(r.headers))
        headerData = json.loads(headerData)
        filePath = '/var/tmp/trms/crops' + pcdId + '/'
        if not os.path.exists(filePath):
            os.mkdir(filePath)
        rawFileName = os.path.join(filePath, pcdId+'.pcd')
        with open(rawFileName, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
        cropList = ['fn_stp1a','fn_stp1b','fn_stp2a','fn_stp2b','fn_stp2c','fn_stp2d','fn_stp3a','fn_stp3b']
        for crop in cropList:
            if self.dbDatas[self.nRows-self.tableWidget.selectedIndexes()[0].row()-1][crop] != '':
                cropId = crop[-2]+crop[-1].capitalize()
                payload = {"responseType":"pcdFile","id":pcdId,"pcdFile":cropId}
                r = requests.get('http://localhost:8503/pointCloudData', params=payload)
                headerData = json.dumps(dict(r.headers))
                headerData = json.loads(headerData)
                fileName = os.path.join(filePath, pcdId+'_'+cropId+'.pcd')
                with open(fileName, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=128):
                        fd.write(chunk)
        form.loadClick(rawFileName)
        form.mywidget.setEnabled(True)
        self.close()
    
    def closeEvent(self, event):
        event.accept()


# Main window code
class MainWindow(QMainWindow):
    # INITIALIZATION FUNCTION
    def __init__(self):
        super(MainWindow, self).__init__()

        # Widget object
        self.mywidget = QWidget()

        # Flag to detect changes of point cloud
        self.flagModification = False
        self.flagWait         = False
        self.missionId = 0
        self.availablePiles = []
        self.view = ''
        self.counter = -1
        self.nuvemTxt = ''
        self.database = Second(self)
        self.pcTemp = []
        self.xyzData = []
        self.zData   = []
        self.cropFiles = ''
        self.fname = ('','')
        self.dbId = ''
        self.cropDict = dict()
        self.debugMode = True
        # Action index
        self.index = 0
        # Id of pptk window for embeding procedure
        self.winId  = 0
        self.winPID = 0
        # Action history
        self.history = []
        # Action history before
        self.historyBefore = []
        # Action history after
        self.historyAfter = []
        # Path to main directory
        self.applicationRoot  = os.path.dirname(os.path.abspath(__file__)) + '/'
        # Browser root
        self.browserRoot = '/home/adriano/git/drone-server/files/'
        # Path to temporary folder
        self.pathToTemp = '/var/tmp/trms/'
        # Register for file currently open
        if not os.path.exists(self.pathToTemp):
            os.mkdir(self.pathToTemp)
        # Path to cached point cloud
        self.pathToCachedPC = self.pathToTemp + 'selected.txt'
        # Random vector to create program ID
        randIdVec = string.ascii_letters+'0123456789'
        # Select 3 elements from randIdVec at random as ID
        self.randID = random.choice(randIdVec)+random.choice(randIdVec)+random.choice(randIdVec)

        self.stockWidget   = QWidget()
        self.buttonsWidget = QWidget()
        self.viewWidget    = QWidget()

        self.editPCD = ''

        self.mywidget.setStyleSheet("background-color:#333333;")
        self.stockWidget.setStyleSheet("background-color:#373f49;")
        self.viewWidget.setStyleSheet("background-color:#373f49;")
        self.buttonsWidget.setStyleSheet("background-color:#373f49;")

        # Layout object
        self.mylayout      = QGridLayout(self.mywidget)

        self.buttonsLayout = QGridLayout(self.buttonsWidget)
        self.stockLayout   = QGridLayout(self.stockWidget)
        self.viewLayout    = QGridLayout(self.viewWidget)

        self.setCentralWidget(self.mywidget)

        # Creating button objects
        self.currentStock  = "0"
        self.buttonStock1A = QPushButton("1A")
        self.buttonStock1B = QPushButton("1B")
        self.buttonStock2A = QPushButton("2A")
        self.buttonStock2B = QPushButton("2B")
        self.buttonStock2C = QPushButton("2C")
        self.buttonStock2D = QPushButton("2D")
        self.buttonStock3A = QPushButton("3A")
        self.buttonStock3B = QPushButton("3B")

        self.buttonTop   = QPushButton("Topo")
        self.buttonSide  = QPushButton("Lado")
        self.buttonFront = QPushButton("Frente")

        self.buttonLoad    = QPushButton("Carregar nuvem")
        self.buttonConfirm = QPushButton("Confirmar seleção")
        self.buttonVolume  = QPushButton("Calcular volume")
        self.buttonSave    = QPushButton("Salvar nuvem")
        self.buttonUndo    = QPushButton("Desfazer última seleção")
        self.buttonRedo    = QPushButton("Refazer seleção")
        self.buttonClose   = QPushButton("Fechar")

        # Disabling buttons for latter usage
        for button in [self.buttonStock1A, self.buttonStock1B, self.buttonStock2A, self.buttonStock2B, self.buttonStock2C, self.buttonStock2D, self.buttonStock3A, self.buttonStock3B, self.buttonVolume, self.buttonConfirm, self.buttonSave, self.buttonUndo, self.buttonRedo]:
            button.setStyleSheet("color: #373f49; background: #373f49;")
            button.setEnabled(False)
        
        # Defining button functions
        self.buttonStock1A.clicked.connect(self.stock1AClick)
        self.buttonStock1B.clicked.connect(self.stock1BClick)
        self.buttonStock2A.clicked.connect(self.stock2AClick)
        self.buttonStock2B.clicked.connect(self.stock2BClick)
        self.buttonStock2C.clicked.connect(self.stock2CClick)
        self.buttonStock2D.clicked.connect(self.stock2DClick)
        self.buttonStock3A.clicked.connect(self.stock3AClick)
        self.buttonStock3B.clicked.connect(self.stock3BClick)

        self.buttonTop.clicked.connect(self.topClick)
        self.buttonFront.clicked.connect(self.frontClick)
        self.buttonSide.clicked.connect(self.sideClick)

        self.buttonLoad.clicked.connect(self.loadClick)
        self.buttonConfirm.clicked.connect(self.confirmClick)
        self.buttonVolume.clicked.connect(self.calcClick)
        self.buttonSave.clicked.connect(self.saveClick)
        self.buttonUndo.clicked.connect(self.undoClick)
        self.buttonRedo.clicked.connect(self.redoClick)
        self.buttonClose.clicked.connect(self.closeClick)

        # Creating a dialog box object
        self.dialogBox = QTextEdit("Área de informações")
        self.dialogBox.setReadOnly(True)

        # Layout setup (except pptk container)
        self.stockLayout.addWidget(self.buttonStock3B, 0, 0, 1, 2)
        self.stockLayout.addWidget(self.buttonStock3A, 0, 2, 1, 2)
        self.stockLayout.addWidget(self.buttonStock2D, 1, 0, 1, 1)
        self.stockLayout.addWidget(self.buttonStock2C, 1, 1, 1, 1)
        self.stockLayout.addWidget(self.buttonStock2B, 1, 2, 1, 1)
        self.stockLayout.addWidget(self.buttonStock2A, 1, 3, 1, 1)
        self.stockLayout.addWidget(self.buttonStock1B, 2, 0, 1, 2)
        self.stockLayout.addWidget(self.buttonStock1A, 2, 2, 1, 2)

        self.viewLayout.addWidget(self.buttonTop  , 0, 0)
        self.viewLayout.addWidget(self.buttonSide , 0, 1)
        self.viewLayout.addWidget(self.buttonFront, 0, 2)

        self.buttonsLayout.addWidget(self.buttonLoad)
        self.buttonsLayout.addWidget(self.buttonConfirm)
        self.buttonsLayout.addWidget(self.buttonVolume)
        self.buttonsLayout.addWidget(self.buttonSave)
        self.buttonsLayout.addWidget(self.buttonUndo)
        self.buttonsLayout.addWidget(self.buttonRedo)
        self.buttonsLayout.addWidget(self.buttonClose)
        self.buttonsLayout.addWidget(self.dialogBox)

        self.mylayout.setColumnStretch(1, 3)
        self.mylayout.addWidget(self.stockWidget, 0, 0)
        self.mylayout.addWidget(self.viewWidget, 1, 0)
        self.mylayout.addWidget(self.buttonsWidget, 3, 0)
        self.setMinimumSize(1000,500)
        # Creating a dummy pptk window
        self.setPointCloud([1,1,1],[1], [])

    # Search for a window called "viewer"
    def findViewer(self, list):
        children = list.query_tree().children
        q = 0
        for w in children:
            subchildren = w.query_tree().children
            for xwin in subchildren:
                if xwin.get_wm_class() is not None:
                    if ("viewer" in xwin.get_wm_class()):
                        self.winId  = xwin.id
                        self.winPID = os.popen('xprop -id '+str(self.winId)+' | grep "PID" | sed "s/_NET_WM_PID(CARDINAL) = //"').read()[:-1]
            q += 1

    def loadPointCloud(self, nuvemTxt):
        # Try to load the txt point cloud into a numpy float matrix.
        try:
            self.xyzData = np.loadtxt(nuvemTxt, delimiter= ' ')

            # Filter x, y and z coordinates
            self.xyzData = self.xyzData[:,:3]
            # Register z values (used to coloring)
            self.zData = self.xyzData[:,2]

            # Load point cloud to pptk viewer referencing z axis to colors
            self.setPointCloud(self.xyzData, self.zData, self.view)
        except:
            self.dialogBox.textCursor().insertText('Erro: arquivo inválido!\n')
            self.repaint()

    def setPointCloud(self, pcVector, filter, newView):
        if newView:
            # Filter z data to exclude outliers and help colouring
            bxplt = plt.boxplot(filter)
            m1 = bxplt['whiskers'][0]._y[0] # Minimum value of the minimum range
            M2 = bxplt['whiskers'][1]._y[1] # Maximum value of the maximum range
            newView.clear()
            newView.load(pcVector, filter)
            newView.color_map('jet',scale=[m1, M2])
            # view.set(phi = 0, theta = np.pi/2)
            self.view.set(phi=-(np.pi/2-0.1933), theta=np.pi/2)
        else:
            self.view = pptk.viewer(pcVector)
            self.embedPC()

    # FUNCTION: Embed point cloud
    def embedPC(self):
        self.xlibList = Xlib.display.Display().screen().root
        self.findViewer(self.xlibList)
        # Creating a window object
        self.window = QtGui.QWindow.fromWinId(self.winId)
        # self.window.setFlags(QtCore.Qt.FramelessWindowHint)
        self.window.setFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.X11BypassWindowManagerHint)
        # Defining container object
        self.windowcontainer = self.createWindowContainer(self.window, self.mywidget)
        self.windowcontainer.setFocusPolicy(QtCore.Qt.TabFocus)
        # Setting container to layout
        time.sleep(.3)
        self.mylayout.addWidget(self.windowcontainer, 0, 1, 4, 5)
        pass
    # FUNCTION: Clear temporary files
    def clearTempFiles(self):
        os.system('kill -9 ' + self.winPID)
            
    def stock1AClick(self):
        if self.currentStockManager(self.buttonStock1A, '1A'):
            for pcFile in self.pcTemp:
                if '_1A.txt' in pcFile:
                    self.nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(self.nuvemTxt)
            
    def stock1BClick(self):
        if self.currentStockManager(self.buttonStock1B, '1B'):
            for pcFile in self.pcTemp:
                if '_1B.txt' in pcFile:
                    self.nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(self.nuvemTxt)

    def stock2AClick(self):
        if self.currentStockManager(self.buttonStock2A, '2A'):
            for pcFile in self.pcTemp:
                if '_2A.txt' in pcFile:
                    self.nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(self.nuvemTxt)

    def stock2BClick(self):
        if self.currentStockManager(self.buttonStock2B, '2B'):
            for pcFile in self.pcTemp:
                if '_2B.txt' in pcFile:
                    self.nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(self.nuvemTxt)
            
    def stock2CClick(self):
        if self.currentStockManager(self.buttonStock2C, '2C'):
            for pcFile in self.pcTemp:
                if '_2C.txt' in pcFile:
                    self.nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(self.nuvemTxt)
            
    def stock2DClick(self):
        if self.currentStockManager(self.buttonStock2D, '2D'):
            for pcFile in self.pcTemp:
                if '_2D.txt' in pcFile:
                    self.nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(self.nuvemTxt)

    def stock3AClick(self):
        if self.currentStockManager(self.buttonStock3A, '3A'):
            for pcFile in self.pcTemp:
                if '_3A.txt' in pcFile:
                    self.nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(self.nuvemTxt)

    def stock3BClick(self):
        if self.currentStockManager(self.buttonStock3B, '3B'):
            for pcFile in self.pcTemp:
                if '_3B.txt' in pcFile:
                    self.nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(self.nuvemTxt)
    
    def currentStockManager(self, button, currentStockSelection):
        for butt in [self.buttonStock1A, self.buttonStock1B, self.buttonStock2A, self.buttonStock2B, self.buttonStock2C, self.buttonStock2D, self.buttonStock3A, self.buttonStock3B]:
            if butt.isEnabled():
                butt.setStyleSheet("color: black; background: #373f49;")

        if self.flagModification:
            quit_msg = "Deseja salvar as últimas modificações?"
            mBox = QMessageBox(self)
            mBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            mBox.setWindowTitle('Modificações pendentes!')
            mBox.setText(quit_msg)
            buttonYes = mBox.button(QMessageBox.Yes)
            buttonYes.setText('Sim')
            buttonNo = mBox.button(QMessageBox.No)
            buttonNo.setText('Não')
            buttonCancel = mBox.button(QMessageBox.Cancel)
            buttonCancel.setText('Cancelar')
            reply = mBox.exec()
            if reply == QMessageBox.Yes:
                self.saveClick()
            elif reply == QMessageBox.Cancel:
                return False
            elif reply == QMessageBox.No:
                self.flagModification = False
                self.historyBefore = []
                self.history = []
                self.historyAfter = []
                self.index = 0
                self.counter = -1
                self.buttonUndo.setStyleSheet("color: #373f49; background: #373f49;")
                self.buttonUndo.setEnabled(False)
                self.buttonRedo.setStyleSheet("color: #373f49; background: #373f49;")
                self.buttonRedo.setEnabled(False)
                self.buttonSave.setStyleSheet("color: #373f49; background: #373f49;")
                self.buttonSave.setEnabled(False)
                
        if currentStockSelection == self.currentStock:
            self.currentStock = '0'
            self.loadPointCloud(self.pcTemp[0])
            button.setStyleSheet("color: black; background: #373f49;")
            self.setWindowTitle('PC Selector: Missão ' + self.missionId)
            return False
        else:
            button.setStyleSheet("color: white; background: darkgreen;")
            self.setWindowTitle('PC Selector: Missão ' + self.missionId + ' Pilha ' + currentStockSelection)
            self.currentStock = currentStockSelection
            return True

    def topClick(self):
        self.view.set(phi = 0, theta = np.pi/2)

    def frontClick(self):
        self.view.set(phi = 0, theta = 0)

    def sideClick(self):
        self.view.set(phi = np.pi/2, theta = 0)
    
    def browseFiles(self):
        if self.debugMode:
            print('browse files')
        self.flagWait = False
        self.dialogLoad.close()
        # Open a dialog box
        self.fname = QFileDialog.getOpenFileName(self, "Escolher nuvem de pontos", self.browserRoot, "Arquivos de nuvem de pontos (*.pcd)")

    def browseDB(self):
        if self.debugMode:
            print('browse database')
        self.flagWait = True
        self.fname = ('','')
        self.dialogLoad.close()
        self.database.show()
        self.mywidget.setDisabled(True)
        

    # CLICK: Load new point cloud
    def loadClick(self, cloudPath):
        if self.flagModification:
            quit_msg = "Deseja salvar as últimas modificações?"
            mBox = QMessageBox(self)
            mBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            mBox.setWindowTitle('Modificações pendentes!')
            mBox.setText(quit_msg)
            buttonYes = mBox.button(QMessageBox.Yes)
            buttonYes.setText('Sim')
            buttonNo = mBox.button(QMessageBox.No)
            buttonNo.setText('Não')
            buttonCancel = mBox.button(QMessageBox.Cancel)
            buttonCancel.setText('Cancelar')
            reply = mBox.exec()
            if reply == QMessageBox.Yes:
                self.saveClick()
            elif reply == QMessageBox.Cancel:
                return

        # Status message
        self.dialogBox.clear()
        self.dialogBox.textCursor().insertText('Escolhendo nuvem de pontos...\n')
        self.repaint()

        if cloudPath:
            self.fname = [cloudPath, 0]
            self.missionId = cloudPath.split('/')[-1].split('.')[0]
        else:
            self.dialogLoad = QDialog()
            self.buttonHD = QPushButton("Disco rígido", self.dialogLoad)
            self.buttonHD.move(10,15)
            self.buttonHD.clicked.connect(self.browseFiles)
            self.buttonDB = QPushButton("Banco de dados", self.dialogLoad)
            self.buttonDB.move(110,15)
            self.buttonDB.clicked.connect(self.browseDB)
            # self.dialogLoad.setGeometry(600,300,235,50)
            self.dialogLoad.setFixedSize(235, 50)
            self.dialogLoad.setWindowTitle("Fonte de arquivos")
            self.dialogLoad.exec()
            if self.flagWait:
                self.dialogBox.clear()
                self.dialogBox.textCursor().insertText('Escolhendo nuvem do banco de dados...\n')
                self.repaint()
                return
            if not self.fname == ('',''):
                self.missionId = self.fname[0].split('/')[-2].split('missao')[1]
        
        # If nothing is selected: return
        if self.fname == ('',''):
            self.dialogBox.clear()
            self.dialogBox.textCursor().insertText('Nenhuma nuvem escolhida!\n')
            self.repaint()
            return
        nuvemPcd = self.fname[0]

        cropPath = os.path.join(self.pathToTemp, 'crops' + self.missionId)
        self.cropDict = dict()
        
        if nuvemPcd == '':
            return
        self.nuvemTxt = os.path.join(self.pathToTemp, nuvemPcd.split('/')[-1].split('.')[0]+'.txt')
        if os.path.exists(self.nuvemTxt):
            if self.debugMode:
                print("Cloud " + nuvemPcd.split('/')[-1] + " loaded from cache!")
        else:
            if self.debugMode:
                print('Creating ' + nuvemPcd + ' txt temporary file')
            os.system('extconverter '+ nuvemPcd +' -D '+self.pathToTemp)

        # Status message
        self.dialogBox.clear()
        self.dialogBox.textCursor().insertText('Arquivo: ' + nuvemPcd + '.\n')
        self.repaint()

        # Try to load the txt point cloud into a numpy float matrix.
        try:
            self.xyzData = np.loadtxt(self.nuvemTxt, delimiter= ' ')
        except:
            self.dialogBox.textCursor().insertText('Erro: arquivo inválido!\n')
            self.repaint()
            return

        self.pcTemp = []
        self.pcTemp.append(self.nuvemTxt)

        # Filter x, y and z coordinates
        self.xyzData = self.xyzData[:,:3]
        # Register z values (used to coloring)
        self.zData = self.xyzData[:,2]

        # Load point cloud to pptk viewer referencing z axis to colors
        self.setPointCloud(self.xyzData, self.zData, self.view)
        
        self.flagModification = False
        self.historyBefore = []
        self.history = []
        self.historyAfter = []
        self.index = 0
        self.counter = -1

        # # Disabling buttons for latter usage
        self.availablePiles = []
        for button in [self.buttonStock1A, self.buttonStock1B, self.buttonStock2A, self.buttonStock2B, self.buttonStock2C, self.buttonStock2D, self.buttonStock3A, self.buttonStock3B, self.buttonSave, self.buttonUndo, self.buttonRedo]:
            button.setStyleSheet("color: #373f49; background: #373f49;")
            button.setEnabled(False)

        if not os.path.exists(cropPath):
            os.mkdir(cropPath)
        
        self.dialogBox.textCursor().insertText('Carregando crops!\n')
        self.repaint()
        self.cropFiles = os.popen('ls ' + cropPath + ' | grep .pcd').read().split('\n')[0:-1]
        for crop in self.cropFiles:
            cropTxt = os.path.join(cropPath, crop.split('.')[0]+'.txt')
            cropPcd = os.path.join(cropPath, crop)
            self.pcTemp.append(cropTxt)
            if os.path.exists(cropTxt):
                if self.debugMode:
                    print("Crop " + crop + " loaded from cache!")
            else:
                if self.debugMode:
                    print('Creating ' + crop + ' txt file')
                os.system('extconverter '+os.path.join(cropPath, crop) + ' -D ' + cropPath)
            if "_1A.pcd" in crop:
                self.buttonStock1A.setStyleSheet("color: black; background: #373f49;")
                self.buttonStock1A.setEnabled(True)
                self.availablePiles.append('1A')
                self.cropDict['1A'] = cropPcd
            elif "_1B.pcd" in crop:
                self.buttonStock1B.setStyleSheet("color: black; background: #373f49;")
                self.buttonStock1B.setEnabled(True)
                self.availablePiles.append('1B')
                self.cropDict['1B'] = cropPcd
            elif "_2A.pcd" in crop:
                self.buttonStock2A.setStyleSheet("color: black; background: #373f49;")
                self.buttonStock2A.setEnabled(True)
                self.availablePiles.append('2A')
                self.cropDict['2A'] = cropPcd
            elif "_2B.pcd" in crop:
                self.buttonStock2B.setStyleSheet("color: black; background: #373f49;")
                self.buttonStock2B.setEnabled(True)
                self.availablePiles.append('2B')
                self.cropDict['2B'] = cropPcd
            elif "_2C.pcd" in crop:
                self.buttonStock2C.setStyleSheet("color: black; background: #373f49;")
                self.buttonStock2C.setEnabled(True)
                self.availablePiles.append('2C')
                self.cropDict['2C'] = cropPcd
            elif "_2D.pcd" in crop:
                self.buttonStock2D.setStyleSheet("color: black; background: #373f49;")
                self.buttonStock2D.setEnabled(True)
                self.availablePiles.append('2D')
                self.cropDict['2D'] = cropPcd
            elif "_3A.pcd" in crop:
                self.buttonStock3A.setStyleSheet("color: black; background: #373f49;")
                self.buttonStock3A.setEnabled(True)
                self.availablePiles.append('3A')
                self.cropDict['3A'] = cropPcd
            elif "_3B.pcd" in crop:
                self.buttonStock3B.setStyleSheet("color: black; background: #373f49;")
                self.buttonStock3B.setEnabled(True)
                self.availablePiles.append('3B')
                self.cropDict['3B'] = cropPcd
        
        ### Ajustar título da janela pra ser compatível com o sub-pilha alvo
        subpile = self.fname[0][-6:][:-4]
        # mission = '0001'
        # subpile = '3B'
        if subpile in pileNames:
            self.setWindowTitle('PC Selector: Missão ' + self.missionId + ' Pilha ' + subpile)
        else:
            self.setWindowTitle('PC Selector: Missão ' + self.missionId)
            
        self.buttonConfirm.setStyleSheet("color: black; background: #373f49;")
        self.buttonVolume.setStyleSheet("color: black; background: #373f49;")
        self.buttonConfirm.setEnabled(True)
        self.buttonVolume.setEnabled(True)
    

    # CLICK: Confirm modification
    def confirmClick(self):
        # Status message
        self.dialogBox.clear()
        self.dialogBox.textCursor().insertText('Buscando ponto selecionados...\n')
        self.repaint()

        ## Segmentar Nuvem de Pontos ##
        # Collects selected points indexes
        sel = self.view.get('selected')
        nSel = len(sel)
        # Create a numpy matrixes of selected points
        if nSel == 0:
            # Status message
            self.dialogBox.moveCursor(QtGui.QTextCursor.End)
            self.dialogBox.textCursor().insertText('Alerta: nenhum ponto selecionado!\nUtilize o botão esquerdo do mouse (BEM) com a tecla Control para efetuar seleção no campo de nuvem de pontos: BEM+Ctrl')
            self.repaint()
            return

        # Create a vector of selected points
        self.xyzData = self.xyzData[sel,:]
        # Register z values (used to coloring)
        self.zData = self.xyzData[:,2]

        # Embed pptk
        self.setPointCloud(self.xyzData, self.zData, self.view)
        
        # Manage action history
        self.counter += 1
        self.index = self.counter
        self.history.append(self.index)
        self.historyBefore = self.history

        # Save current cloud in cache
        np.savetxt(self.pathToCachedPC, self.xyzData)
        np.savetxt(self.pathToTemp+self.randID+str(self.counter),self.xyzData)

        # Set modification flags
        self.flagModification = True
        # Enable folowing buttons
        self.buttonVolume.setStyleSheet("color: black; background: #373f49;")
        self.buttonSave.setStyleSheet("color: black; background: #373f49;")
        self.buttonUndo.setStyleSheet("color: black; background: #373f49;")
        self.buttonVolume.setEnabled(True)
        self.buttonSave.setEnabled(True)
        self.buttonUndo.setEnabled(True)

        # Status message
        self.dialogBox.textCursor().insertText(str(nSel)+' pontos selecionados.\n')
        self.repaint()

   
    # CLICK: Volume calculation
    def calcClick(self):
        self.dialogBox.clear()
        self.dialogBox.textCursor().insertText("Calculando...\n")
        self.repaint()
        if self.counter == -1:
            np.savetxt(self.pathToCachedPC, self.xyzData)
        volume = os.popen('python3 ' + os.path.join(self.applicationRoot,'mainh.py ') + self.pathToCachedPC).read().split('\n')[0]
        self.dialogBox.textCursor().insertText("Volume total = " + volume + " m³.\n")
        self.repaint()
        if self.debugMode:
            print("Volume total = " + volume + " m³.\n")
        return volume

    # CLICK: Save current point cloud
    def saveClick(self):
        self.dialogSave = QDialog()
        self.dialogSave.setWindowTitle("Salvar nuvem em:")
        self.buttonSaveHD = QPushButton("Disco rígido", self.dialogSave)
        self.buttonSaveHD.move(10, 15)
        self.buttonSaveHD.clicked.connect(self.saveHD)
        self.buttonSaveDB = QPushButton("Banco de dados", self.dialogSave)
        self.buttonSaveDB.move(110, 15)
        self.buttonSaveDB.clicked.connect(self.saveDB)
        self.comboSaveDB = QComboBox(self.dialogSave)
        self.comboSaveDB.insertItems(0, ['Selecionar pilha'] + self.availablePiles)
        self.comboSaveDB.move(110, 50)
        self.dialogSave.setFixedSize(250, 80)
        self.dialogSave.setWindowTitle("Fonte de arquivos")
        self.dialogSave.exec()

    def saveHD(self):
        self.dialogBox.textCursor().insertText('Salvando nuvem de pontos...\n')
        self.repaint()

        ## Save on HD
        self.fname = QFileDialog.getSaveFileName(self, 'Salvar nuvem de pontos', self.browserRoot, "Arquivos de nuvem de pontos (*.pcd)")
        if self.fname == ('',''):
            self.dialogBox.textCursor().insertText('Operação "salvar" cancelada!\n')
            self.repaint()
            return
        pcdFile = open(self.fname[0],'w') ### Transformat em .pcd
        text = open(self.pathToCachedPC,'r').read()
        pcdFile.write(text)
        pcdFile.close()
        self.dialogBox.textCursor().insertText('Nuvem de pontos salva em:\n'+self.fname[0]+'\n')
        self.flagModification = False
        self.repaint()
        self.dialogSave.close()
        
    def saveDB(self):
        stockName = self.comboSaveDB.currentText()
        if self.comboSaveDB.currentIndex() == 0:
            if self.debugMode:
                print('Escolha uma pilha')
            self.choosePileWarning = QMessageBox(QMessageBox.Warning, 'Aviso', 'Selecione uma pilha!', QMessageBox.Ok)
            self.choosePileWarning.exec_()
        else:
            if self.debugMode:
                print('Salvar pilha ' + stockName)
            self.dialogBox.textCursor().insertText('Pilha ' + stockName + ' atualizada no banco de dados')
            self.flagModification = False
            self.repaint()
            self.dialogSave.close()
            ## Update database
            name   = self.cropDict[stockName]
            cropDir = os.path.dirname(self.cropDict[stockName])
            os.system('extconverter ' + self.pathToCachedPC + ' -D ' + cropDir)
            os.system('cp ' + cropDir + '/selected.pcd ' + name)
            os.system('cp ' + self.pathToCachedPC + ' ' + name.replace('.pcd','.txt'))
            volume = float(self.calcClick())
            md5hash = os.popen('md5sum '+name).read().split(' ')[0]
            payload = """{"id":%s,"edited_by":0,"stp_volume":%.2f,"md5Hash":"%s"}"""%(self.dbId,volume,md5hash)
            files = {'jsonData': ('',payload, 'application/json'),'pcdFile': (stockName+'.pcd', open(name, 'rb'), 'application/octet-stream')}
            r = requests.put('http://localhost:8503/pointCloudData', files=files)
            if self.debugMode:
                print(r.text)

            ## Save on database
            # name = self.fname[0].split('/')[-1]
            # md5hash = os.popen('md5sum '+name).read().split(' ')[0]
            # headers = {'md5hash':md5hash,'user':'1'}
            # files = {'file': (name, open(name, 'rb'), 'text/plain')}
            # r = requests.post('http://localhost:8503/pointCloudData', headers=headers, files=files)
            # self.flagModification = False
            # self.dialogBox.textCursor().insertText('Nuvem de pontos salva em:\n'+r.text+'\n')


    # CLICK: Return to previous modification state
    def undoClick(self):
        # Manage action history
        self.historyAfter.insert(0, self.historyBefore.pop())
        if not self.historyBefore:
            self.index = -1
            nuvem = self.nuvemTxt###
            self.buttonUndo.setStyleSheet("color: #373f49; background: #373f49;")
            self.buttonUndo.setEnabled(False)
        else:
            self.index = self.historyBefore[-1]
            nuvem = self.pathToTemp+self.randID+str(self.index)
        try:
            self.xyzData = np.loadtxt(nuvem, delimiter= ' ')
        except:
            self.dialogBox.textCursor().insertText('Erro: arquivo inválido!\n')
            self.repaint()

        # Filter x, y and z coordinates
        self.xyzData = self.xyzData[:,:3]
        # Register z values (used to coloring)
        self.zData = self.xyzData[:,2]
        # Save current cloud in cache
        np.savetxt(self.pathToCachedPC, self.xyzData)

        # Load point cloud to pptk viewer referencing z axis to colors
        self.setPointCloud(self.xyzData, self.zData, self.view)
        self.repaint()
        self.buttonRedo.setStyleSheet("color: black; background: #373f49;")
        self.buttonRedo.setEnabled(True)


    # CLICK: Return to later modification state after Undo
    def redoClick(self):
        self.historyBefore.append(self.historyAfter.pop(0))
        self.index = self.historyBefore[-1]
        nuvem = self.pathToTemp+self.randID+str(self.index)
        try:
            self.xyzData = np.loadtxt(nuvem, delimiter= ' ')
        except:
            self.dialogBox.textCursor().insertText('Erro: arquivo inválido!\n')
            self.repaint()

        # Filter x, y and z coordinates
        self.xyzData = self.xyzData[:,:3]
        # Register z values (used to coloring)
        self.zData = self.xyzData[:,2]
        # Save current cloud in cache
        np.savetxt(self.pathToCachedPC, self.xyzData)
        # Load point cloud to pptk viewer referencing z axis to colors
        self.setPointCloud(self.xyzData, self.zData, self.view)
        if not self.historyAfter:
            self.buttonRedo.setStyleSheet("color: #373f49; background: #373f49;")
            self.buttonRedo.setEnabled(False)
        self.buttonUndo.setStyleSheet("color: black; background: #373f49;")
        self.buttonUndo.setEnabled(True)
        self.repaint()


    # CLICK: Close application
    def closeClick(self):
        self.close()
    

    # EVENT: Close window event
    def closeEvent(self, event):
        if self.flagModification:
            quit_msg = "Deseja salvar as últimas modificações?"
            mBox = QMessageBox(self)
            mBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            mBox.setWindowTitle('Modificações pendentes!')
            mBox.setText(quit_msg)
            buttonYes = mBox.button(QMessageBox.Yes)
            buttonYes.setText('Sim')
            buttonNo = mBox.button(QMessageBox.No)
            buttonNo.setText('Não')
            buttonCancel = mBox.button(QMessageBox.Cancel)
            buttonCancel.setText('Cancelar')
            reply = mBox.exec()
            if reply == QMessageBox.Yes:
                self.saveClick()
            elif reply == QMessageBox.No:
                self.clearTempFiles()
                event.accept()
            elif reply == QMessageBox.Cancel:
                event.ignore()
        else:
            self.clearTempFiles()
            event.accept()

def main():
    try:
        args      = argv[1].split()
        indexEdit = args.index('--edit')
        form.editPCD   = args[indexEdit+1]
        form.loadClick(form.editPCD)
    except:
        if self.debugMode:
            print('Invalid point cloud argument.')

    if form.editPCD:###fname
        form.missionId = form.fname[0].split('/missao')[1][:4]###fname, will fail, fname=('','')
        subpile = form.fname[0][-6:][:-4]
        if subpile in pileNames:
            form.setWindowTitle('PC Selector: Missão ' + form.missionId + ' Pilha ' + subpile)
        else:
            form.setWindowTitle('PC Selector: Missão ' + form.missionId)
    else:
        form.setWindowTitle('PC Selector')
    #form.setGeometry(100, 100, 600, 500)
    form.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    # sys.argv.append('--edit /var/tmp/trms/nuvem_2020-09-14T10:31:00_3A.txt')
    pileNames = ['1A', '1B', '2A', '2B', '2C', '2D', '3A', '3B']
    argv = sys.argv
    # argv = ['/home/adriano/git/volumecarvao/pcselector.py', '--edit /home/controle/git/gpar-drone-server/files/missao0001/nuvem_2020-09-14T10:31:00.pcd']
    
    app = QApplication(argv)
    app.setStyle("fusion")
    form = MainWindow()
    main()