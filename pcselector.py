import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import alphashape
import random
import pptk
import glob
import sys
import os
from   descartes import PolygonPatch
from   PyQt5 import QtWidgets, QtGui
from   Xlib.display import Display
from   PIL import Image

winId = 0

def findViewer(window, indent):
    global winId
    children = window.query_tree().children
    for w in children:
        findViewer(w, indent+'-')
        if w.get_wm_class() is not None:
            if ("viewer" in w.get_wm_class()):
                winId = w.id

def getPC():
    # Get script file's root name
    root = os.path.dirname(os.path.abspath(__file__)) + '/'

    # Path to slices figures
    pathToSlices = root + 'selecao_teste' # path dos slices
    try:
        # Tries to make the directory "selecao_teste"
        os.mkdir(pathToSlices)
    except:
        pass
    ##### Segmentar Nuvem de Pontos

    # Choose a txt point cloud file
    # nuvem = root + 'pontos.txt'
    # nuvem = root + 'ensaio9teste15.txt'
    nuvem = root + 'ensaio9alinhado.txt'

    try:
        # Try to load the txt point cloud into a numpy float matrix
        xyz = np.loadtxt(nuvem, delimiter= ' ')
    except:
        # Display error message if load fails
        sys.exit('Error loading ' + nuvem + '!')

    # Filter x, y and z coordinates
    xyz = xyz[:,:3]
    # Register z values (used to coloring)
    z = xyz[:,2]

    # Filter z data to exclude outliers and help colouring
    bxplt = plt.boxplot(z)
    m1 = bxplt['whiskers'][0]._y[0] # Minimum value of the minimum range
    m2 = bxplt['whiskers'][0]._y[1] # Maximum value of the minimum range
    M1 = bxplt['whiskers'][1]._y[0] # Minimum value of the maximum range
    M2 = bxplt['whiskers'][1]._y[1] # Maximum value of the maximum range
    # plt.show() # displays boxplot

    # Load point cloud to viewer referencing z axis to colors
    return pptk.viewer(xyz,z)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout(widget)
        self.setCentralWidget(widget)

        self.v = getPC()
        self.xlib = Display().screen().root
        findViewer(self.xlib, '-')
        self.window = QtGui.QWindow.fromWinId(winId)
        self.windowcontainer = self.createWindowContainer(self.window, widget)

        layout.addWidget(self.windowcontainer, 0, 0)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    form = MainWindow()
    form.setWindowTitle('PPTK Embed')
    form.setGeometry(100, 100, 600, 500)
    form.show()
    sys.exit(app.exec_())