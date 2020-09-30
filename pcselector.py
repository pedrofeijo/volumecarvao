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
from   descartes import PolygonPatch
from   PIL import Image
import time

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
historyBefore =[]
# Action history after
historyAfter =[]
# Detect operational system
OS = platform.system()
if OS == 'Linux':
    # from Xlib.display import Display
    import Xlib
    import Xlib.display
elif OS == 'Windows':
    import win32gui

# GLOBAL VARIABLES
# Id of pptk window for embeding procedure
winId = 0
# Path to main directory
root  = os.path.dirname(os.path.abspath(__file__)) + '/'
# Path to temporary folder
pathToTemp = '/var/tmp/trms/'
# Register for file currently open
fname = ''
nuvemTxt = ''
cropFiles = ''
pcTemp = []
if not os.path.exists(pathToTemp):
    os.mkdir(pathToTemp)
# Path to cached point cloud
pathToCachedPC = pathToTemp + 'selected.txt'
# Flag to detect changes of point cloud
flagModification = False

# Search for a window called "viewer"
def findViewer(list):
    # Modified global variables
    global winId
    children = list.query_tree().children
    q = 0
    for w in children:
        subchildren = w.query_tree().children
        for xwin in subchildren:
            display = Xlib.display.Display()
            # print(xwin.get_wm_class())
            # print(xwin.get_wm_name())
            # print(xwin.get_full_property(display.intern_atom('_NET_WM_PID'), Xlib.X.AnyPropertyType))
            # print(xwin.get_full_property(display.intern_atom('_NET_WM_NAME'), Xlib.X.AnyPropertyType))
            # print(xwin.get_full_property(display.intern_atom('_NET_WM_VISIBLE_NAME'), Xlib.X.AnyPropertyType))
            # print(xwin.get_wm_class())
            if xwin.get_wm_class() is not None:
                if ("viewer" in xwin.get_wm_class()):
                    # print(q)
                    # print(w.id)
                    # print(xwin.id)
                    # Save "viewer" window id
                    winId = xwin.id
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
        self.currentStock = '00000000'
        self.loadPointCloud(pcTemp[0])
        return False

    else:
        if currentStockSelection == '11000000':
            self.buttonStock1A.setStyleSheet("color: white; background: darkgreen;")
            self.buttonStock1B.setStyleSheet("color: white; background: darkgreen;")
        elif currentStockSelection == '00111100':
            self.buttonStock2A.setStyleSheet("color: white; background: darkgreen;")
            self.buttonStock2B.setStyleSheet("color: white; background: darkgreen;")
            self.buttonStock2C.setStyleSheet("color: white; background: darkgreen;")
            self.buttonStock2D.setStyleSheet("color: white; background: darkgreen;")
        elif currentStockSelection == '00000011':
            self.buttonStock3A.setStyleSheet("color: white; background: darkgreen;")
            self.buttonStock3B.setStyleSheet("color: white; background: darkgreen;")

        button.setStyleSheet("color: white; background: darkgreen;")
        self.currentStock = currentStockSelection
        return True

# Main window code
class MainWindow(QtWidgets.QMainWindow):
    # INITIALIZATION FUNCTION
    def __init__(self):
        super(MainWindow, self).__init__()

        # Widget object
        self.mywidget = QtWidgets.QWidget()

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
        self.currentStock  = "00000000"
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
        self.stockLayout.addWidget(self.buttonStock1A, 0, 0, 1, 2)
        self.stockLayout.addWidget(self.buttonStock1B, 0, 2, 1, 2)
        self.stockLayout.addWidget(self.buttonStock1 , 0, 4, 1, 1)
        self.stockLayout.addWidget(self.buttonStock2A, 1, 0, 1, 1)
        self.stockLayout.addWidget(self.buttonStock2B, 1, 1, 1, 1)
        self.stockLayout.addWidget(self.buttonStock2C, 1, 2, 1, 1)
        self.stockLayout.addWidget(self.buttonStock2D, 1, 3, 1, 1)
        self.stockLayout.addWidget(self.buttonStock2 , 1, 4, 1, 1)
        self.stockLayout.addWidget(self.buttonStock3A, 2, 0, 1, 2)
        self.stockLayout.addWidget(self.buttonStock3B, 2, 2, 1, 2)
        self.stockLayout.addWidget(self.buttonStock3 , 2, 4, 1, 1)

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
        else:
            view = pptk.viewer(pcVector)
            self.embedPC()

    # FUNCTION: Embed point cloud
    def embedPC(self):
        # Find pptk window id
        if OS == 'Windows':
            global winId
            winId = win32gui.FindWindowEx(0, 0, None, "viewer")
        elif OS == 'Linux':
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
        # if os.path.exists(pathToCachedPC):
        #     print("Clearing temporary files!")
        #     os.remove(pathToCachedPC)
        if os.path.exists(pathToTemp):
            print("Clearing cached files!")
            shutil.rmtree(pathToTemp)

    def stock1Click(self):
        global nuvemTxt
        if currentStockManager(self, self.buttonStock1B,'11000000'):
            for pcFile in pcTemp:
                if '_1.txt' in pcFile:
                    nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(nuvemTxt)
            
    def stock1AClick(self):
        global nuvemTxt
        if currentStockManager(self, self.buttonStock1B,'10000000'):
            for pcFile in pcTemp:
                if '_1A.txt' in pcFile:
                    nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(nuvemTxt)
            
    def stock1BClick(self):
        global nuvemTxt
        if currentStockManager(self, self.buttonStock1B,'01000000'):
            for pcFile in pcTemp:
                if '_1B.txt' in pcFile:
                    nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(nuvemTxt)
            
    def stock2Click(self):
        global nuvemTxt
        if currentStockManager(self, self.buttonStock2 ,'00111100'):
            for pcFile in pcTemp:
                if '_2.txt' in pcFile:
                    nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(nuvemTxt)
            
    def stock2AClick(self):
        global nuvemTxt
        if currentStockManager(self, self.buttonStock2A,'00100000'):
            for pcFile in pcTemp:
                if '_2A.txt' in pcFile:
                    nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(nuvemTxt)
            
    def stock2BClick(self):
        global nuvemTxt
        if currentStockManager(self, self.buttonStock2B,'00010000'):
            for pcFile in pcTemp:
                if '_2B.txt' in pcFile:
                    nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(nuvemTxt)
            
    def stock2CClick(self):
        global nuvemTxt
        if currentStockManager(self, self.buttonStock2C,'00001000'):
            for pcFile in pcTemp:
                if '_2C.txt' in pcFile:
                    nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(nuvemTxt)
            
    def stock2DClick(self):
        global nuvemTxt
        if currentStockManager(self, self.buttonStock2D,'00000100'):
            for pcFile in pcTemp:
                if '_2D.txt' in pcFile:
                    nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(nuvemTxt)

    def stock3Click(self):
        global nuvemTxt
        if currentStockManager(self, self.buttonStock3 ,'00000011'):
            for pcFile in pcTemp:
                if '_3.txt' in pcFile:
                    nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(nuvemTxt)

    def stock3AClick(self):
        global nuvemTxt
        if currentStockManager(self, self.buttonStock3A,'00000010'):
            for pcFile in pcTemp:
                if '_3A.txt' in pcFile:
                    nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(nuvemTxt)

    def stock3BClick(self):
        global nuvemTxt
        if currentStockManager(self, self.buttonStock3B,'00000001'):
            for pcFile in pcTemp:
                if '_3B.txt' in pcFile:
                    nuvemTxt = pcFile
            # Try to load the txt point cloud into a numpy float matrix.
            self.loadPointCloud(nuvemTxt)

    def topClick(self):
        global view
        view.set(phi = 0, theta = np.pi/2)

    def frontClick(self):
        global view
        view.set(phi = 0, theta = 0)

    def sideClick(self):
        global view
        view.set(phi = np.pi/2, theta = 0)

    # CLICK: Load new point cloud
    def loadClick(self, cloudPath):
        # Modified global variables
        global view, xyz, fname, nuvemTxt, cropFiles, historyAfter, history, historyBefore, counter, index, pcTemp, flagModification

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

        # Open a dialog box
        # fname = QtWidgets.QFileDialog.getOpenFileName(self, "Escolher nuvem de pontos", root, "Arquivos de nuvem de pontos (*.pcd)")
        fname = QtWidgets.QFileDialog.getOpenFileName(self, "Escolher nuvem de pontos", '/home/adriano/git/drone-server/files/', "Arquivos de nuvem de pontos (*.pcd)")
        # If nothing is selected: return
        if fname ==('',''):
            self.dialogBox.textCursor().insertText('Nenhuma nuvem escolhida!\n')
            self.repaint()
            return
        # Get file name
        nuvemPcd = fname[0]
        
        nuvemTxt = os.path.join(pathToTemp, nuvemPcd.split('/')[-1].split('.')[0]+'.txt')
        if os.path.exists(nuvemTxt):
            print("Cloud " + nuvemPcd.split('/')[-1] + " loaded from cache!")
        else:
            os.system('extconverter '+nuvemPcd+' -D '+pathToTemp)

        # Status message
        self.dialogBox.clear()
        self.dialogBox.textCursor().insertText('Arquivo: ' + nuvemPcd + '.\n')
        self.repaint()

        # Try to load the txt point cloud into a numpy float matrix.
        try:
            xyz = np.loadtxt(nuvemTxt, delimiter= ' ')
        except:
            self.dialogBox.textCursor().insertText('Erro: arquivo inválido!\n')
            self.repaint()
            return

        pcTemp = []
        pcTemp.append(nuvemTxt)

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
        volume = os.popen('python3 ' + os.path.join(root,'mainh.py ') + pathToCachedPC).read().split('\n')[0]
        self.dialogBox.textCursor().insertText("Volume total = " + volume + " m³.\n")
        self.repaint()
        print("Volume total = " + volume + " m³.\n")

        # # LER NUVEM DE PONTOS
        # # Set root path to selected points
        # try:
        #     # Try to load the txt point cloud into a numpy float matrix
        #     dados_df = np.loadtxt(pathToCachedPC, delimiter= ' ')
        # except:
        #     # Use entire cloud
        #     dados_df = xyz
        # # Status message
        # self.dialogBox.textCursor().insertText('Calculando...\n')
        # self.repaint()

        # # Ajustar arquivo txt - (linha , coluna)
        # dados_df = dados_df[:,:3]
        # # Ordenar eixo x
        # dados   = dados_df[dados_df[:,0].argsort()]
        # # Armazena cada eixo em uma variavel
        # dados_x = dados[:,0]
        # dados_y = dados[:,1]
        # dados_z = dados[:,2]
        
        # # Path to slices
        # if os.path.exists(pathToTemp):
        #     shutil.rmtree(pathToTemp)
        #     print("Clearing cache!")
        # else:
        #     # Status message
        #     self.dialogBox.textCursor().insertText('Criando diretório temporário...\n')
        #     self.repaint()

        # # SEPARAR EM SLICES NO EIXO X COM INTERVALOR DE 1000
        # intervalo = 1000 # se ficar menor não fecha o polígono
        # for i in range(len(dados_x)//intervalo):
        #     points = [(y,z) for y,z in zip(dados_y[i*intervalo: (i+1)*intervalo],dados_z[i*intervalo: (i+1)*intervalo])]

        #     # DEFININDO ALPHA
        #     alpha_shape = alphashape.alphashape(points, 0.)
        #     # alpha_shape = alphashape.alphashape(points) # calculo do alpha automatico
            
        #     fig, ax = plt.subplots()
        #     ax.scatter(*zip(*points))
            
        #     plt.xlim([np.min(dados_y), np.max(dados_y)])
        #     plt.ylim([np.min(dados_z), np.max(dados_z)])
        #     plt.axis("off") 

        #     ax.add_patch(PolygonPatch(alpha_shape, alpha=0.2))
        #     plt.xlim([np.min(dados_y), np.max(dados_y)]) # limitando o espaço de plotar em y
        #     plt.ylim([np.min(dados_z), np.max(dados_z)]) # limitando o espaço de plotar em z
        #     plt.axis("off") # sem eixos
            
        #     # Plotar arquivo .txt de cada slice
        #     fig.savefig(pathToTemp+'/fig_{}.png'.format(i))
        #     print(i) 

        #     points_slice = [(x,y,z) for x,y,z in zip(dados_x[i*intervalo: (i+1)*intervalo],dados_y[i*intervalo: (i+1)*intervalo],dados_z[i*intervalo: (i+1)*intervalo])]
        #     np.savetxt(pathToTemp+'/points_fig_{}.txt'.format(i), points_slice, delimiter=' ') 

        #     plt.close()

        # # Identificar o numero de slices na path
        # filepaths = glob.glob(pathToTemp+ "*.png", recursive= True)
        # print(len(filepaths)) # Número de arquivos na path

        # total = 0

        # for i in range(len(filepaths)):
        #     img = np.asarray(Image.open(pathToTemp + "fig_{}.png".format(i)).convert('L'))
        #     img = 1 * (img < 255)
        #     m,n = img.shape
        #     total += img.sum() 
        #     print("{} white pixels, out of {} pixels in total.".format(img.sum(), m*n)) 
            
        # print("Número total de pixels {}".format(total))

        # somaslices = total
        # volumeareaporpixels= somaslices*0.005657 #relação pixels to m3 
        
        # self.dialogBox.textCursor().insertText("Volume total = {} m³".format(volumeareaporpixels)+'.\n')
        # self.repaint()
        # print("Volume total = {} m³".format(volumeareaporpixels))


    # CLICK: Save current point cloud
    def saveClick(self):
        # Modified global variables
        global flagModification

        self.dialogBox.textCursor().insertText('Salvando nuvem de pontos...\n')
        self.repaint()

        ## Save on HD
        fname = QtWidgets.QFileDialog.getSaveFileName(self, 'Salvar nuvem de pontos', root, "Arquivos de nuvem de pontos (*.pcd)")
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
            nuvem = nuvemTxt###
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
                os.system('killall viewer')
                event.accept()
            elif reply == QtWidgets.QMessageBox.Cancel:
                event.ignore()
        else:
            self.clearTempFiles()
            os.system('killall viewer')
            event.accept()



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    form = MainWindow()
    form.setWindowTitle('Editor de Nuvem de Pontos')
    #form.setGeometry(100, 100, 600, 500)
    form.show()

    sys.exit(app.exec_())
