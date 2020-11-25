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
import glob
import json
import pptk
import sys
import os
from   PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QApplication, QAbstractItemView
from   descartes import PolygonPatch
from   PIL import Image
import time

# Search for a window called "viewer"
def findViewer(list):
    # Modified global variables
    global winId, winPID
    children = list.query_tree().children
    q = 0
    for w in children:
        subchildren = w.query_tree().children
        for xwin in subchildren:
            if xwin.get_wm_class() is not None:
                if ("viewer" in xwin.get_wm_class()):
                    winId  = xwin.id
                    winPID = os.popen('xprop -id '+str(winId)+' | grep "PID" | sed "s/_NET_WM_PID(CARDINAL) = //"').read()[:-1]
        q += 1
    pass

def currentStockManager(self, button, currentStockSelection):
    global flagModification, history, historyAfter, historyBefore, index, counter
    if flagModification:
        quit_msg = "Deseja salvar as últimas modificações?"
        mBox = QtWidgets.QMessageBox(self)
        mBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
        mBox.setWindowTitle('Modificações pendentes!')
        mBox.setText(quit_msg)
        buttonYes = mBox.button(QtWidgets.QMessageBox.Yes)
        buttonYes.setText('Sim')
        buttonNo = mBox.button(QtWidgets.QMessageBox.No)
        buttonNo.setText('Não')
        buttonCancel = mBox.button(QtWidgets.QMessageBox.Cancel)
        buttonCancel.setText('Cancelar')
        reply = mBox.exec()
        if reply == QtWidgets.QMessageBox.Yes:
            self.saveClick()
        elif reply == QtWidgets.QMessageBox.Cancel:
            return False
        elif reply == QtWidgets.QMessageBox.No:
            flagModification = False
            historyBefore = []
            history = []
            historyAfter = []
            index = 0
            counter = -1
            self.buttonUndo.setStyleSheet("color: #373f49; background: #373f49;")
            self.buttonUndo.setEnabled(False)
            self.buttonRedo.setStyleSheet("color: #373f49; background: #373f49;")
            self.buttonRedo.setEnabled(False)
            self.buttonSave.setStyleSheet("color: #373f49; background: #373f49;")
            self.buttonSave.setEnabled(False)
            

    if self.buttonStock1.isEnabled():
        self.buttonStock1.setStyleSheet( "color: black; background: #373f49;")
        self.buttonStock1A.setStyleSheet("color: black; background: #373f49;")
        self.buttonStock1B.setStyleSheet("color: black; background: #373f49;")
    else:
        self.buttonStock1.setStyleSheet( "color: #373f49; background: #373f49;")
        self.buttonStock1A.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonStock1B.setStyleSheet("color: #373f49; background: #373f49;")

    if self.buttonStock2.isEnabled():
        self.buttonStock2.setStyleSheet( "color: black; background: #373f49;")
        self.buttonStock2A.setStyleSheet("color: black; background: #373f49;")
        self.buttonStock2B.setStyleSheet("color: black; background: #373f49;")
        self.buttonStock2C.setStyleSheet("color: black; background: #373f49;")
        self.buttonStock2D.setStyleSheet("color: black; background: #373f49;")
    else:
        self.buttonStock2.setStyleSheet( "color: #373f49; background: #373f49;")
        self.buttonStock2A.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonStock2B.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonStock2C.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonStock2D.setStyleSheet("color: #373f49; background: #373f49;")
    if self.buttonStock3.isEnabled():
        self.buttonStock3.setStyleSheet( "color: black; background: #373f49;")
        self.buttonStock3A.setStyleSheet("color: black; background: #373f49;")
        self.buttonStock3B.setStyleSheet("color: black; background: #373f49;")
    else:
        self.buttonStock3.setStyleSheet( "color: #373f49; background: #373f49;")
        self.buttonStock3A.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonStock3B.setStyleSheet("color: #373f49; background: #373f49;")
    if currentStockSelection == self.currentStock:
        self.currentStock = '0'
        self.loadPointCloud(pcTemp[0])
        return False

    else:
        if currentStockSelection == '1':
            self.buttonStock1A.setStyleSheet("color: white; background: darkgreen;")
            self.buttonStock1B.setStyleSheet("color: white; background: darkgreen;")
        elif currentStockSelection == '2':
            self.buttonStock2A.setStyleSheet("color: white; background: darkgreen;")
            self.buttonStock2B.setStyleSheet("color: white; background: darkgreen;")
            self.buttonStock2C.setStyleSheet("color: white; background: darkgreen;")
            self.buttonStock2D.setStyleSheet("color: white; background: darkgreen;")
        elif currentStockSelection == '3':
            self.buttonStock3A.setStyleSheet("color: white; background: darkgreen;")
            self.buttonStock3B.setStyleSheet("color: white; background: darkgreen;")

        button.setStyleSheet("color: white; background: darkgreen;")
        mission = fname[0].split('/missao')[1][:4]
        if currentStockSelection in ['1','2','3','1A', '1B', '2A', '2B', '2C', '2D', '3A', '3B']:
            self.setWindowTitle('PC Selector: Missão ' + mission + ' Pilha ' + currentStockSelection)
        else:
            self.setWindowTitle('PC Selector: Missão ' + currentStockSelection)
        self.currentStock = currentStockSelection
        return True

class Second(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Second, self).__init__(parent)

        self.mywidget = QtWidgets.QWidget()

        self.dataWidget    = QtWidgets.QWidget()
        self.buttonsWidget = QtWidgets.QWidget()

        self.mylayout      = QtWidgets.QGridLayout(self.mywidget)
        self.dataLayout    = QtWidgets.QGridLayout(self.dataWidget)
        self.buttonsLayout = QtWidgets.QGridLayout(self.buttonsWidget)
        
        self.setCentralWidget(self.mywidget)
        
        payload = {"responseType":"fieldList","initDate":"2010-01-01 00:00:00","endDate":"2100-10-31 23:59:59"}
        r = requests.get('http://localhost:8503/pointCloudData', params=payload)
        self.dbDatas = json.loads(r.text)
        self.dbData = self.dbDatas[0]
        self.dbData['id']
        print('browse database')
        idList      = list()
        initList    = list()
        missionList = list()
        self.nRows = len(self.dbDatas)
        for i in range(0, self.nRows):
            idList.append(self.dbDatas[i]['id'])
            initList.append(self.dbDatas[i]['flight_init'])
            missionList.append(self.dbDatas[i]['mission'])

        self.createTable(idList, initList, missionList)

        self.buttonCancel = QtWidgets.QPushButton('Cancelar')
        self.buttonSelect = QtWidgets.QPushButton('Selecionar')

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
        self.close()

    def selectAction(self):
        print('Select action')
        pcdId = self.tableWidget.selectedItems()[0].text()
        payload = {"responseType":"pcdFile","id":pcdId,"pcdFile":"raw"}
        r = requests.get('http://localhost:8503/pointCloudData', params=payload)
        headerData = json.dumps(dict(r.headers))
        headerData = json.loads(headerData)
        pcdName = self.tableWidget.selectedItems()[1].text().replace('/','-').replace(':','')
        fileName = '/var/tmp/trms/'+pcdId+'m_'+pcdName+'.pcd'
        with open(fileName, 'wb') as fd:
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
                fileName = "/var/tmp/trms/"+pcdId+'m_'+pcdName+'_'+cropId+'.pcd'
                with open(fileName, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=128):
                        fd.write(chunk)


# Main window code
class MainWindow(QtWidgets.QMainWindow):
    # INITIALIZATION FUNCTION
    def __init__(self):
        super(MainWindow, self).__init__()

        # Widget object
        self.mywidget = QtWidgets.QWidget()

        self.nuvemTxt = ''
        self.database = Second(self)

        self.stockWidget = QtWidgets.QWidget()
        self.buttonsWidget = QtWidgets.QWidget()
        self.viewWidget  = QtWidgets.QWidget()

        self.mywidget.setStyleSheet("background-color:#333333;")
        self.stockWidget.setStyleSheet("background-color:#373f49;")
        self.viewWidget.setStyleSheet("background-color:#373f49;")
        self.buttonsWidget.setStyleSheet("background-color:#373f49;")

        # Layout object
        self.mylayout      = QtWidgets.QGridLayout(self.mywidget)

        self.buttonsLayout = QtWidgets.QGridLayout(self.buttonsWidget)
        self.stockLayout   = QtWidgets.QGridLayout(self.stockWidget)
        self.viewLayout    = QtWidgets.QGridLayout(self.viewWidget)

        self.setCentralWidget(self.mywidget)

        # Creating button objects
        self.currentStock  = "0"
        self.buttonStock1A = QtWidgets.QPushButton("1A")
        self.buttonStock1B = QtWidgets.QPushButton("1B")
        self.buttonStock1  = QtWidgets.QPushButton("1")
        self.buttonStock2A = QtWidgets.QPushButton("2A")
        self.buttonStock2B = QtWidgets.QPushButton("2B")
        self.buttonStock2C = QtWidgets.QPushButton("2C")
        self.buttonStock2D = QtWidgets.QPushButton("2D")
        self.buttonStock2  = QtWidgets.QPushButton("2")
        self.buttonStock3A = QtWidgets.QPushButton("3A")
        self.buttonStock3B = QtWidgets.QPushButton("3B")
        self.buttonStock3  = QtWidgets.QPushButton("3")

        self.buttonTop   = QtWidgets.QPushButton("Topo")
        self.buttonSide  = QtWidgets.QPushButton("Lado")
        self.buttonFront = QtWidgets.QPushButton("Frente")

        self.buttonLoad    = QtWidgets.QPushButton("Carregar nuvem")
        self.buttonConfirm = QtWidgets.QPushButton("Confirmar seleção")
        self.buttonVolume  = QtWidgets.QPushButton("Calcular volume")
        self.buttonSave    = QtWidgets.QPushButton("Salvar nuvem")
        self.buttonUndo    = QtWidgets.QPushButton("Desfazer última seleção")
        self.buttonRedo    = QtWidgets.QPushButton("Refazer seleção")
        self.buttonClose   = QtWidgets.QPushButton("Fechar")

        # Disabling buttons for latter usage
        self.buttonStock1.setStyleSheet( "color: #373f49; background: #373f49;")
        self.buttonStock1A.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonStock1B.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonStock2.setStyleSheet( "color: #373f49; background: #373f49;")
        self.buttonStock2A.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonStock2B.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonStock2C.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonStock2D.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonStock3.setStyleSheet( "color: #373f49; background: #373f49;")
        self.buttonStock3A.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonStock3B.setStyleSheet("color: #373f49; background: #373f49;")

        self.buttonStock1.setEnabled(False)
        self.buttonStock1A.setEnabled(False)
        self.buttonStock1B.setEnabled(False)
        self.buttonStock2.setEnabled(False)
        self.buttonStock2A.setEnabled(False)
        self.buttonStock2B.setEnabled(False)
        self.buttonStock2C.setEnabled(False)
        self.buttonStock2D.setEnabled(False)
        self.buttonStock3.setEnabled(False)
        self.buttonStock3A.setEnabled(False)
        self.buttonStock3B.setEnabled(False)

        self.buttonVolume.setStyleSheet( "color: #373f49; background: #373f49;")
        self.buttonConfirm.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonSave.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonUndo.setStyleSheet( "color: #373f49; background: #373f49;")
        self.buttonRedo.setStyleSheet("color: #373f49; background: #373f49;")

        self.buttonVolume.setEnabled(False)
        self.buttonConfirm.setEnabled(False)
        self.buttonSave.setEnabled(False)
        self.buttonUndo.setEnabled(False)
        self.buttonRedo.setEnabled(False)
        
        # Defining button functions
        self.buttonStock1.clicked.connect( self.stock1Click )
        self.buttonStock1A.clicked.connect(self.stock1AClick)
        self.buttonStock1B.clicked.connect(self.stock1BClick)
        self.buttonStock2.clicked.connect( self.stock2Click )
        self.buttonStock2A.clicked.connect(self.stock2AClick)
        self.buttonStock2B.clicked.connect(self.stock2BClick)
        self.buttonStock2C.clicked.connect(self.stock2CClick)
        self.buttonStock2D.clicked.connect(self.stock2DClick)
        self.buttonStock3.clicked.connect( self.stock3Click )
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
        self.dialogBox = QtWidgets.QTextEdit("Área de informações")
        self.dialogBox.setReadOnly(True)

        # Layout setup (except pptk container)
        self.stockLayout.addWidget(self.buttonStock3B, 0, 0, 1, 2)
        self.stockLayout.addWidget(self.buttonStock3A, 0, 2, 1, 2)
        self.stockLayout.addWidget(self.buttonStock3 , 0, 4, 1, 1)
        self.stockLayout.addWidget(self.buttonStock2D, 1, 0, 1, 1)
        self.stockLayout.addWidget(self.buttonStock2C, 1, 1, 1, 1)
        self.stockLayout.addWidget(self.buttonStock2B, 1, 2, 1, 1)
        self.stockLayout.addWidget(self.buttonStock2A, 1, 3, 1, 1)
        self.stockLayout.addWidget(self.buttonStock2 , 1, 4, 1, 1)
        self.stockLayout.addWidget(self.buttonStock1B, 2, 0, 1, 2)
        self.stockLayout.addWidget(self.buttonStock1A, 2, 2, 1, 2)
        self.stockLayout.addWidget(self.buttonStock1 , 2, 4, 1, 1)

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
        if editPCD:
            self.loadClick(editPCD)

    def loadPointCloud(self, nuvemTxt):
        # Try to load the txt point cloud into a numpy float matrix.
        global xyz, z, view
        try:
            xyz = np.loadtxt(nuvemTxt, delimiter= ' ')

            # Filter x, y and z coordinates
            xyz = xyz[:,:3]
            # Register z values (used to coloring)
            z = xyz[:,2]

            # Load point cloud to pptk viewer referencing z axis to colors
            self.setPointCloud(xyz, z, view)
        except:
            self.dialogBox.textCursor().insertText('Erro: arquivo inválido!\n')
            self.repaint()

    def setPointCloud(self, pcVector, filter, newView):
        global view
        if newView:
            # Filter z data to exclude outliers and help colouring
            bxplt = plt.boxplot(filter)
            m1 = bxplt['whiskers'][0]._y[0] # Minimum value of the minimum range
            M2 = bxplt['whiskers'][1]._y[1] # Maximum value of the maximum range
            newView.clear()
            newView.load(pcVector, filter)
            newView.color_map('jet',scale=[m1, M2])
            # view.set(phi = 0, theta = np.pi/2)
            view.set(phi=-(np.pi/2-0.1933), theta=np.pi/2)
        else:
            view = pptk.viewer(pcVector)
            self.embedPC()

    # FUNCTION: Embed point cloud
    def embedPC(self):
        self.xlibList = Xlib.display.Display().screen().root
        findViewer(self.xlibList)
        # Creating a window object
        self.window = QtGui.QWindow.fromWinId(winId)
        self.window.setFlags(QtCore.Qt.FramelessWindowHint)
        # self.window.setFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.X11BypassWindowManagerHint)
        # Defining container object
        self.windowcontainer = self.createWindowContainer(self.window, self.mywidget)
        # Setting container to layout
        time.sleep(.1)
        self.mylayout.addWidget(self.windowcontainer, 0, 1, 4, 5)

    # FUNCTION: Clear temporary files
    def clearTempFiles(self):
        os.system('kill -9 ' + winPID)
        # if os.path.exists(pathToTemp):
            # print("Clearing cached files!")
            # shutil.rmtree(pathToTemp)

    def stock1Click(self):
        if currentStockManager(self, self.buttonStock1B, '1'):
            for pcFile in pcTemp:
                if '_1.txt' in pcFile:
                    self.nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(self.nuvemTxt)
            
    def stock1AClick(self):
        if currentStockManager(self, self.buttonStock1B, '1A'):
            for pcFile in pcTemp:
                if '_1A.txt' in pcFile:
                    self.nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(self.nuvemTxt)
            
    def stock1BClick(self):
        if currentStockManager(self, self.buttonStock1B, '1B'):
            for pcFile in pcTemp:
                if '_1B.txt' in pcFile:
                    self.nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(self.nuvemTxt)
            
    def stock2Click(self):
        if currentStockManager(self, self.buttonStock2, '2'):
            for pcFile in pcTemp:
                if '_2.txt' in pcFile:
                    self.nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(self.nuvemTxt)
            
    def stock2AClick(self):
        if currentStockManager(self, self.buttonStock2A, '2A'):
            for pcFile in pcTemp:
                if '_2A.txt' in pcFile:
                    self.nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(self.nuvemTxt)
            
    def stock2BClick(self):
        if currentStockManager(self, self.buttonStock2B, '2B'):
            for pcFile in pcTemp:
                if '_2B.txt' in pcFile:
                    self.nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(self.nuvemTxt)
            
    def stock2CClick(self):
        if currentStockManager(self, self.buttonStock2C, '2C'):
            for pcFile in pcTemp:
                if '_2C.txt' in pcFile:
                    self.nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(self.nuvemTxt)
            
    def stock2DClick(self):
        if currentStockManager(self, self.buttonStock2D, '2D'):
            for pcFile in pcTemp:
                if '_2D.txt' in pcFile:
                    self.nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(self.nuvemTxt)

    def stock3Click(self):
        if currentStockManager(self, self.buttonStock3, '3'):
            for pcFile in pcTemp:
                if '_3.txt' in pcFile:
                    self.nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(self.nuvemTxt)

    def stock3AClick(self):
        if currentStockManager(self, self.buttonStock3A, '3A'):
            for pcFile in pcTemp:
                if '_3A.txt' in pcFile:
                    self.nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(self.nuvemTxt)

    def stock3BClick(self):
        if currentStockManager(self, self.buttonStock3B, '3B'):
            for pcFile in pcTemp:
                if '_3B.txt' in pcFile:
                    self.nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(self.nuvemTxt)

    def topClick(self):
        global view
        view.set(phi = 0, theta = np.pi/2)

    def frontClick(self):
        global view
        view.set(phi = 0, theta = 0)

    def sideClick(self):
        global view
        view.set(phi = np.pi/2, theta = 0)
    
    def browseFiles(self):
        global fname
        self.dialogLoad.close()
        print('browse files')
        # Open a dialog box
        fname = QtWidgets.QFileDialog.getOpenFileName(self, "Escolher nuvem de pontos", browserRoot, "Arquivos de nuvem de pontos (*.pcd)")
        # If nothing is selected: return
        if fname ==('',''):
            self.dialogBox.textCursor().insertText('Nenhuma nuvem escolhida!\n')
            self.repaint()
            return

    def browseDB(self):
        global fname
        self.dialogLoad.close()
        self.database.show()

    # CLICK: Load new point cloud
    def loadClick(self, cloudPath):
        # Modified global variables
        global view, xyz, fname, cropFiles, historyAfter, history, historyBefore, counter, index, pcTemp, flagModification

        if flagModification:
            quit_msg = "Deseja salvar as últimas modificações?"
            mBox = QtWidgets.QMessageBox(self)
            mBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
            mBox.setWindowTitle('Modificações pendentes!')
            mBox.setText(quit_msg)
            buttonYes = mBox.button(QtWidgets.QMessageBox.Yes)
            buttonYes.setText('Sim')
            buttonNo = mBox.button(QtWidgets.QMessageBox.No)
            buttonNo.setText('Não')
            buttonCancel = mBox.button(QtWidgets.QMessageBox.Cancel)
            buttonCancel.setText('Cancelar')
            reply = mBox.exec()
            if reply == QtWidgets.QMessageBox.Yes:
                self.saveClick()
            elif reply == QtWidgets.QMessageBox.Cancel:
                return

        # Status message
        self.dialogBox.clear()
        self.dialogBox.textCursor().insertText('Escolhendo nuvem de pontos...\n')
        self.repaint()

        if cloudPath:
            fname = [cloudPath,0]
        else:
            self.dialogLoad = QtWidgets.QDialog()
            self.buttonHD = QtWidgets.QPushButton("Disco rígido", self.dialogLoad)
            self.buttonHD.move(10,15)
            self.buttonHD.clicked.connect(self.browseFiles)
            self.buttonDB = QtWidgets.QPushButton("Banco de dados", self.dialogLoad)
            self.buttonDB.move(110,15)
            self.buttonDB.clicked.connect(self.browseDB)
            self.dialogLoad.setGeometry(600,300,235,50)
            self.dialogLoad.setWindowTitle("Fonte de arquivos")
            self.dialogLoad.exec()
        nuvemPcd = fname[0]
        
        if nuvemPcd == '':
            return
        self.nuvemTxt = os.path.join(pathToTemp, nuvemPcd.split('/')[-1].split('.')[0]+'.txt')
        if os.path.exists(self.nuvemTxt):
            print("Cloud " + nuvemPcd.split('/')[-1] + " loaded from cache!")
        else:
            os.system('extconverter '+nuvemPcd+' -D '+pathToTemp)

        # Status message
        self.dialogBox.clear()
        self.dialogBox.textCursor().insertText('Arquivo: ' + nuvemPcd + '.\n')
        self.repaint()

        # Try to load the txt point cloud into a numpy float matrix.
        try:
            xyz = np.loadtxt(self.nuvemTxt, delimiter= ' ')
        except:
            self.dialogBox.textCursor().insertText('Erro: arquivo inválido!\n')
            self.repaint()
            return

        pcTemp = []
        pcTemp.append(self.nuvemTxt)

        # Filter x, y and z coordinates
        xyz = xyz[:,:3]
        # Register z values (used to coloring)
        z = xyz[:,2]

        # Load point cloud to pptk viewer referencing z axis to colors
        self.setPointCloud(xyz, z, view)
        
        flagModification = False
        historyBefore = []
        history = []
        historyAfter = []
        index = 0
        counter = -1
        self.buttonUndo.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonUndo.setEnabled(False)
        self.buttonRedo.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonRedo.setEnabled(False)
        self.buttonSave.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonSave.setEnabled(False)

        cropPath = os.path.join(os.path.dirname(nuvemPcd),'crops')
        self.buttonStock1.setStyleSheet( "color: #373f49; background: #373f49;")
        self.buttonStock1A.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonStock1B.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonStock2.setStyleSheet( "color: #373f49; background: #373f49;")
        self.buttonStock2A.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonStock2B.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonStock2C.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonStock2D.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonStock3.setStyleSheet( "color: #373f49; background: #373f49;")
        self.buttonStock3A.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonStock3B.setStyleSheet("color: #373f49; background: #373f49;")
        self.buttonStock1.setEnabled(False)
        self.buttonStock1A.setEnabled(False)
        self.buttonStock1B.setEnabled(False)
        self.buttonStock2.setEnabled(False)
        self.buttonStock2A.setEnabled(False)
        self.buttonStock2B.setEnabled(False)
        self.buttonStock2C.setEnabled(False)
        self.buttonStock2D.setEnabled(False)
        self.buttonStock3.setEnabled(False)
        self.buttonStock3A.setEnabled(False)
        self.buttonStock3B.setEnabled(False)

        if os.path.exists(cropPath):
            self.dialogBox.textCursor().insertText('Carregando crops!\n')
            self.repaint()
            cropFiles = os.popen('ls '+cropPath).read().split('\n')[0:-1]
            for crop in cropFiles:
                cropTxt = os.path.join(pathToTemp,crop.split('.')[0]+'.txt')
                pcTemp.append(cropTxt)
                if os.path.exists(cropTxt):
                    print("Crop " + crop + " loaded from cache!")
                else:
                    os.system('extconverter '+os.path.join(cropPath,crop)+' -D '+pathToTemp)
                if "_1.pcd" in crop:
                    self.buttonStock1.setStyleSheet( "color: black; background: #373f49;")
                    self.buttonStock1A.setStyleSheet("color: black; background: #373f49;")
                    self.buttonStock1B.setStyleSheet("color: black; background: #373f49;")
                    self.buttonStock1.setEnabled(True)
                    self.buttonStock1A.setEnabled(True)
                    self.buttonStock1B.setEnabled(True)
                elif "_2.pcd" in crop:
                    self.buttonStock2.setStyleSheet( "color: black; background: #373f49;")
                    self.buttonStock2A.setStyleSheet("color: black; background: #373f49;")
                    self.buttonStock2B.setStyleSheet("color: black; background: #373f49;")
                    self.buttonStock2C.setStyleSheet("color: black; background: #373f49;")
                    self.buttonStock2D.setStyleSheet("color: black; background: #373f49;")
                    self.buttonStock2.setEnabled(True)
                    self.buttonStock2A.setEnabled(True)
                    self.buttonStock2B.setEnabled(True)
                    self.buttonStock2C.setEnabled(True)
                    self.buttonStock2D.setEnabled(True)
                elif "_3.pcd" in crop:
                    self.buttonStock3.setStyleSheet( "color: black; background: #373f49;")
                    self.buttonStock3A.setStyleSheet("color: black; background: #373f49;")
                    self.buttonStock3B.setStyleSheet("color: black; background: #373f49;")
                    self.buttonStock3.setEnabled(True)
                    self.buttonStock3A.setEnabled(True)
                    self.buttonStock3B.setEnabled(True)
        
        ### Ajustar título da janela pra ser compatível com o sub-pilha alvo
        mission = fname[0].split('/missao')[1][:4]
        subpile = fname[0][-6:][:-4]
        # mission = '0001'
        # subpile = '3B'
        if subpile in ['1A', '1B', '2A', '2B', '2C', '2D', '3A', '3B']:
            self.setWindowTitle('PC Selector: Missão ' + mission + ' Pilha ' + subpile)
        else:
            self.setWindowTitle('PC Selector: Missão ' + mission)
            
        self.buttonConfirm.setStyleSheet("color: black; background: #373f49;")
        self.buttonVolume.setStyleSheet("color: black; background: #373f49;")
        self.buttonConfirm.setEnabled(True)
        self.buttonVolume.setEnabled(True)
    

    # CLICK: Confirm modification
    def confirmClick(self):
        # Modified global variables
        global xyz, view, flagModification, counter, index, history, historyAfter, historyBefore
        
        # Status message
        self.dialogBox.clear()
        self.dialogBox.textCursor().insertText('Buscando ponto selecionados...\n')
        self.repaint()

        ## Segmentar Nuvem de Pontos ##
        # Collects selected points indexes
        sel = view.get('selected')
        nSel = len(sel)
        # Create a numpy matrixes of selected points
        if nSel == 0:
            # Status message
            self.dialogBox.moveCursor(QtGui.QTextCursor.End)
            self.dialogBox.textCursor().insertText('Alerta: nenhum ponto selecionado!\nUtilize o botão esquerdo do mouse (BEM) com a tecla Control para efetuar seleção no campo de nuvem de pontos: BEM+Ctrl')
            self.repaint()
            return

        # Create a vector of selected points
        xyz = xyz[sel,:]
        # Register z values (used to coloring)
        z = xyz[:,2]

        # Embed pptk
        self.setPointCloud(xyz, z, view)
        
        # Manage action history
        counter += 1
        index = counter
        history.append(index)
        historyBefore = history

        # Save current cloud in cache
        np.savetxt(pathToCachedPC, xyz)
        np.savetxt(pathToTemp+ID+str(counter),xyz)

        # Set modification flags
        flagModification = True
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
        if counter == -1:
            np.savetxt(pathToCachedPC, xyz)
        volume = os.popen('python3 ' + os.path.join(applicationRoot,'mainh.py ') + pathToCachedPC).read().split('\n')[0]
        self.dialogBox.textCursor().insertText("Volume total = " + volume + " m³.\n")
        self.repaint()
        print("Volume total = " + volume + " m³.\n")

    # CLICK: Save current point cloud
    def saveClick(self):
        # Modified global variables
        global flagModification

        self.dialogBox.textCursor().insertText('Salvando nuvem de pontos...\n')
        self.repaint()

        ## Save on HD
        fname = QtWidgets.QFileDialog.getSaveFileName(self, 'Salvar nuvem de pontos', browserRoot, "Arquivos de nuvem de pontos (*.pcd)")
        if fname == ('',''):
            self.dialogBox.textCursor().insertText('Operação "salvar" cancelada!\n')
            self.repaint()
            return
        file = open(fname[0],'w') ### Transformat em .pcd
        text = open(pathToCachedPC,'r').read()
        file.write(text)
        file.close()
        self.dialogBox.textCursor().insertText('Nuvem de pontos salva em:\n'+fname[0]+'\n')
        flagModification = False

        ## Save on database
        # name = fname[0].split('/')[-1]
        # md5hash = os.popen('md5sum '+name).read().split(' ')[0]
        # headers = {'md5hash':md5hash,'user':'1'}
        # files = {'file': (name, open(name, 'rb'), 'text/plain')}
        # r = requests.post('http://localhost:8503/pointCloudData', headers=headers, files=files)
        # flagModification = False
        # self.dialogBox.textCursor().insertText('Nuvem de pontos salva em:\n'+r.text+'\n')

        self.repaint()


    # CLICK: Return to previous modification state
    def undoClick(self):
        global index, historyAfter, historyBefore
        # Manage action history
        historyAfter.insert(0, historyBefore.pop())
        if not historyBefore:
            index = -1
            nuvem = self.nuvemTxt###
            self.buttonUndo.setStyleSheet("color: #373f49; background: #373f49;")
            self.buttonUndo.setEnabled(False)
        else:
            index = historyBefore[-1]
            nuvem = pathToTemp+ID+str(index)
        try:
            xyz = np.loadtxt(nuvem, delimiter= ' ')
        except:
            self.dialogBox.textCursor().insertText('Erro: arquivo inválido!\n')
            self.repaint()
            pass

        # Filter x, y and z coordinates
        xyz = xyz[:,:3]
        # Register z values (used to coloring)
        z = xyz[:,2]
        # Save current cloud in cache
        np.savetxt(pathToCachedPC, xyz)

        # Load point cloud to pptk viewer referencing z axis to colors
        self.setPointCloud(xyz, z, view)
        self.repaint()
        self.buttonRedo.setStyleSheet("color: black; background: #373f49;")
        self.buttonRedo.setEnabled(True)


    # CLICK: Return to later modification state after Undo
    def redoClick(self):
        global index, historyAfter, historyBefore
        historyBefore.append(historyAfter.pop(0))
        index = historyBefore[-1]
        nuvem = pathToTemp+ID+str(index)
        try:
            xyz = np.loadtxt(nuvem, delimiter= ' ')
        except:
            self.dialogBox.textCursor().insertText('Erro: arquivo inválido!\n')
            self.repaint()
            pass

        # Filter x, y and z coordinates
        xyz = xyz[:,:3]
        # Register z values (used to coloring)
        z = xyz[:,2]
        # Save current cloud in cache
        np.savetxt(pathToCachedPC, xyz)
        # Load point cloud to pptk viewer referencing z axis to colors
        self.setPointCloud(xyz, z, view)
        if not historyAfter:
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
        global flagModification
        if flagModification:
            quit_msg = "Deseja salvar as últimas modificações?"
            mBox = QtWidgets.QMessageBox(self)
            mBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
            mBox.setWindowTitle('Modificações pendentes!')
            mBox.setText(quit_msg)
            buttonYes = mBox.button(QtWidgets.QMessageBox.Yes)
            buttonYes.setText('Sim')
            buttonNo = mBox.button(QtWidgets.QMessageBox.No)
            buttonNo.setText('Não')
            buttonCancel = mBox.button(QtWidgets.QMessageBox.Cancel)
            buttonCancel.setText('Cancelar')
            reply = mBox.exec()
            if reply == QtWidgets.QMessageBox.Yes:
                self.saveClick()
            elif reply == QtWidgets.QMessageBox.No:
                self.clearTempFiles()
                event.accept()
            elif reply == QtWidgets.QMessageBox.Cancel:
                event.ignore()
        else:
            self.clearTempFiles()
            event.accept()


# Random vector to create program ID
randIdVec = string.ascii_letters+'0123456789'
# Select 3 elements from randIdVec at random as ID
ID = random.choice(randIdVec)+random.choice(randIdVec)+random.choice(randIdVec)
# Action counter
counter = -1
# Action index
index = 0
# Action history
history = []
# Action history before
historyBefore = []
# Action history after
historyAfter = []
# Detect operational system
OS = platform.system()
if OS == 'Linux':
    import Xlib
    import Xlib.display
else:
    print("This application is Linux exclusive")
    sys.exit()

# GLOBAL VARIABLES
# Id of pptk window for embeding procedure
winId = 0
winPID = 0
# Path to main directory
applicationRoot  = os.path.dirname(os.path.abspath(__file__)) + '/'
# Browser root
browserRoot = '/home/adriano/git/drone-server/files/'
# Path to temporary folder
pathToTemp = '/var/tmp/trms/'
# Register for file currently open
fname = ('','')
cropFiles = ''
pcTemp = []
if not os.path.exists(pathToTemp):
    os.mkdir(pathToTemp)
# Path to cached point cloud
pathToCachedPC = pathToTemp + 'selected.txt'
# Flag to detect changes of point cloud
flagModification = False

editPCD = ''
# sys.argv.append('--edit /var/tmp/trms/nuvem_2020-09-14T10:31:00_3A.txt')
argv = sys.argv
# argv = ['/home/adriano/git/volumecarvao/pcselector.py', '--edit /home/adriano/git/drone-server/files/missao0001/crops/nuvem_2020-09-14T10:31:00_3B.pcd']
try:
    args      = argv[1].split()
    indexEdit = args.index('--edit')
    editPCD   = args[indexEdit+1]
except:
    print('Invalid point cloud argument.')

if __name__ == '__main__':
    app = QtWidgets.QApplication(argv)
    app.setStyle("fusion")
    form = MainWindow()
    if editPCD:
        mission = fname[0].split('/missao')[1][:4]
        subpile = fname[0][-6:][:-4]
        if subpile in ['1A', '1B', '2A', '2B', '2C', '2D', '3A', '3B']:
            form.setWindowTitle('PC Selector: Missão ' + mission + ' Pilha ' + subpile)
        else:
            form.setWindowTitle('PC Selector: Missão ' + mission)
    else:
        form.setWindowTitle('PC Selector')
    #form.setGeometry(100, 100, 600, 500)
    form.show()

    sys.exit(app.exec_())
