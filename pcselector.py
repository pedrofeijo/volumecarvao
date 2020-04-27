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
root  = os.path.dirname(os.path.abspath(__file__)) + '/'

def findViewer(window, indent):
    global winId
    children = window.query_tree().children
    for w in children:
        findViewer(w, indent+'-')
        if w.get_wm_class() is not None:
            if ("viewer" in w.get_wm_class()):
                winId = w.id

def getPC():
    global v, xyz, root, pathToSlices
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

    v = pptk.viewer([1,1,1])
    # Displays point cloud
    v.set(bg_color=[1.0,1.0,1.0,0.0])
    v.set(floor_color=[1.0,1.0,1.0,0.0])

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.mywidget = QtWidgets.QWidget()
        self.mylayout = QtWidgets.QGridLayout(self.mywidget)
        self.setCentralWidget(self.mywidget)

        getPC()
        self.xlib = Display().screen().root
        findViewer(self.xlib, '-')
        self.window = QtGui.QWindow.fromWinId(winId)
        self.windowcontainer = self.createWindowContainer(self.window, self.mywidget)
        self.buttonLoad    = QtWidgets.QPushButton("Carregar nuvem")
        self.buttonConfirm = QtWidgets.QPushButton("Confirmar alterações")
        self.buttonVolume  = QtWidgets.QPushButton("Calcular volume")
        self.buttonSave    = QtWidgets.QPushButton("Salvar")
        self.buttonUndo    = QtWidgets.QPushButton("Desfazer")
        self.buttonClose   = QtWidgets.QPushButton("Fechar")
        self.dialogBox = QtWidgets.QTextEdit("Área de informações")
        
        self.buttonLoad.clicked.connect(self.loadClick)
        self.buttonConfirm.clicked.connect(self.confirmClick)
        self.buttonVolume.clicked.connect(self.calcClick)
        self.buttonSave.clicked.connect(self.saveClick)
        self.buttonUndo.clicked.connect(self.undoClick)
        self.buttonClose.clicked.connect(self.closeClick)

        self.mylayout.addWidget(self.windowcontainer, 0, 1, 7, 10)
        self.mylayout.addWidget(self.buttonLoad     , 0, 0)
        self.mylayout.addWidget(self.buttonConfirm  , 1, 0)
        self.mylayout.addWidget(self.buttonVolume   , 2, 0)
        self.mylayout.addWidget(self.buttonSave     , 3, 0)
        self.mylayout.addWidget(self.buttonUndo     , 4, 0)
        self.mylayout.addWidget(self.buttonClose    , 5, 0)
        self.mylayout.addWidget(self.dialogBox      , 6, 0)
        self.mylayout.setColumnStretch(1, 3)

    def loadClick(self):
        global v, xyz, root, pathToSlices
        fname = QtWidgets.QFileDialog.getOpenFileName(self, "Escolher nuvem de pontos", root, "Arquivos de nuvem de pontos (*.txt)")
        nuvem = fname[0]

        # Path to slices figures
        pathToSlices = root + 'selecao_teste' # path dos slices
        try:
            # Tries to make the directory "selecao_teste"
            os.mkdir(pathToSlices)
        except:
            pass
        ##### Segmentar Nuvem de Pontos

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
        M2 = bxplt['whiskers'][1]._y[1] # Maximum value of the maximum range
        # plt.show() # displays boxplot

        # Load point cloud to viewer referencing z axis to colors
        v = pptk.viewer(xyz,z)
        # Displays point cloud
        v.color_map('jet',scale=[m1,M2])
        v.set(bg_color=[1.0,1.0,1.0,0.0])
        v.set(floor_color=[1.0,1.0,1.0,0.0])
        self.xlib = Display().screen().root
        findViewer(self.xlib, '-')
        self.window = QtGui.QWindow.fromWinId(winId)
        self.windowcontainer = self.createWindowContainer(self.window, self.mywidget)
        self.mylayout.addWidget(self.windowcontainer, 0, 1, 7, 10)


    def saveClick(self):
        self.dialogBox.moveCursor(QtGui.QTextCursor.End)
        self.dialogBox.textCursor().insertText('Save')

    def undoClick(self):
        self.dialogBox.textCursor().insertText('Undo')

    def closeClick(self):
        self.dialogBox.textCursor().insertText('Close')
        self.close()
        
    def confirmClick(self):
        global xyz, v, root, pathToSlices
        self.dialogBox.textCursor().insertText('Confirm')
        self.dialogBox.clear()
        self.dialogBox.textCursor().insertText('Calculando...\n')
        pathToSlices = root + 'selecao_teste'
        # Collects selected points indexes
        sel = v.get('selected')
        len(sel)
        # Create a numpy matrixes of selected points
        if len(sel)==0:
            return
        xyz = xyz[sel,:]
        # Register z values (used to coloring)
        z = xyz[:,2]

        # Filter z data to exclude outliers and help colouring
        bxplt = plt.boxplot(z)
        m1 = bxplt['whiskers'][0]._y[0] # Minimum value of the minimum range
        M2 = bxplt['whiskers'][1]._y[1] # Maximum value of the maximum range

        # Load point cloud to viewer referencing z axis to colors
        v = pptk.viewer(xyz,z)
        # Displays point cloud
        v.color_map('jet',scale=[m1,M2])
        v.set(bg_color=[1.0,1.0,1.0,0.0])
        v.set(floor_color=[1.0,1.0,1.0,0.0])
        self.xlib = Display().screen().root
        findViewer(self.xlib, '-')
        self.window = QtGui.QWindow.fromWinId(winId)
        self.windowcontainer = self.createWindowContainer(self.window, self.mywidget)
        self.mylayout.addWidget(self.windowcontainer, 0, 1, 7, 10)
        
        # Save archive with selected points
        np.savetxt('selected.txt', xyz) # Transposta dos dados
    
    def calcClick(self):
        # LER NUVEM DE PONTOS
        # Set root path to selected points
        arquivo  = root + "selected.txt"
        # Try to load the txt point cloud into a numpy float matrix
        dados_df = np.loadtxt(arquivo, delimiter= ' ')
        dados_df = dados_df[:,:3] # ajustar arquivo txt - (linha , coluna)

        dados   = dados_df[dados_df[:,0].argsort()] # ordenar eixo x
        dados_x = dados[:,0]
        dados_y = dados[:,1]
        dados_z = dados[:,2]

        # SEPARAR EM SLICES NO EIXO X COM INTERVALOR DE 1000
        intervalo= 1000 # se ficar menor não fecha o polígono
        for i in range(len(dados_x)//intervalo):
            points = [(y,z) for y,z in zip(dados_y[i*intervalo: (i+1)*intervalo],dados_z[i*intervalo: (i+1)*intervalo])]

            # DEFININDO ALPHA
            alpha_shape = alphashape.alphashape(points, 0.)
            # alpha_shape = alphashape.alphashape(points) # calculo do alpha automatico
            
            fig, ax = plt.subplots()
            ax.scatter(*zip(*points))
            
            plt.xlim([np.min(dados_y), np.max(dados_y)])
            plt.ylim([np.min(dados_z), np.max(dados_z)])
            plt.axis("off") 

            ax.add_patch(PolygonPatch(alpha_shape, alpha=0.2))
            plt.xlim([np.min(dados_y), np.max(dados_y)]) # limitando o espaço de plotar em y
            plt.ylim([np.min(dados_z), np.max(dados_z)]) # limitando o espaço de plotar em z
            plt.axis("off") # sem eixos
            
            # Plotar arquivo .txt de cada slice
            fig.savefig(root+'selecao_teste/fig_{}.png'.format(i))
            print(i) 

            points_slice = [(x,y,z) for x,y,z in zip(dados_x[i*intervalo: (i+1)*intervalo],dados_y[i*intervalo: (i+1)*intervalo],dados_z[i*intervalo: (i+1)*intervalo])]
            np.savetxt(root+'selecao_teste/points_fig_{}.txt'.format(i), points_slice, delimiter=' ') 

            plt.close()

        # Identificar o numero de slices na path
        filepaths = glob.glob(pathToSlices+ "/*.png", recursive= True)
        print(len(filepaths)) # Número de arquivos na path

        total = 0

        for i in range(len(filepaths)):
            img = np.asarray(Image.open(root + "/selecao_teste/fig_{}.png".format(i)).convert('L'))
            img = 1 * (img < 255)
            m,n = img.shape
            total += img.sum() 
            print("{} white pixels, out of {} pixels in total.".format(img.sum(), m*n)) 
            
        print("Número total de pixels {}".format(total))

        somaslices = total
        volumeareaporpixels= somaslices*0.005657 #relação pixels to m3 
        
        self.dialogBox.textCursor().insertText("Volume total = {} m³".format(volumeareaporpixels))
        print("Volume total = {} m³".format(volumeareaporpixels))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    form = MainWindow()
    form.setWindowTitle('Editor de Nuvem de Pontos')
    form.setGeometry(100, 100, 600, 500)
    form.show()

    sys.exit(app.exec_())