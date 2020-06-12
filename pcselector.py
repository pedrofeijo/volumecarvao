import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import alphashape
import platform
import requests
import random
import shutil
import string
import glob
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
    from Xlib.display import Display
elif OS == 'Windows':
    import win32gui

# GLOBAL VARIABLES
# ID of pptk window for embeding procedure
winId = 0
# Path to main directory
root  = os.path.dirname(os.path.abspath(__file__)) + '/'
# Path to temporary folder
pathToTemp = root + '.temp/'
# Register for file currently open
fname = ''
if os.path.exists(pathToTemp):
    shutil.rmtree(pathToTemp)
    os.mkdir(pathToTemp)
else:
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
        for x in subchildren:
            if x.get_wm_class() is not None:
                if ("viewer" in x.get_wm_class()):
                    # print(q)
                    # print(w.id)
                    print(x.id)
                    # Save "viewer" window ID
                    winId = x.id
                    pass
        q += 1
    pass

# Main window code
class MainWindow(QtWidgets.QMainWindow):
    # INITIALIZATION FUNCTION
    def __init__(self):
        super(MainWindow, self).__init__()

        # Widget object
        self.mywidget = QtWidgets.QWidget()
        # Layout object
        self.mylayout = QtWidgets.QGridLayout(self.mywidget)
        self.setCentralWidget(self.mywidget)
        
        # Creating button objects
        self.buttonLoad    = QtWidgets.QPushButton("Carregar nuvem")
        self.buttonConfirm = QtWidgets.QPushButton("Confirmar seleção")
        self.buttonVolume  = QtWidgets.QPushButton("Calcular volume")
        self.buttonSave    = QtWidgets.QPushButton("Salvar nuvem")
        self.buttonUndo    = QtWidgets.QPushButton("Desfazer última seleção")
        self.buttonRedo    = QtWidgets.QPushButton("Refazer seleção")
        self.buttonClose   = QtWidgets.QPushButton("Fechar")

        # Disabling buttons for latter usage
        self.buttonVolume.setEnabled(False)
        self.buttonConfirm.setEnabled(False)
        self.buttonSave.setEnabled(False)
        self.buttonUndo.setEnabled(False)
        self.buttonRedo.setEnabled(False)
        
        # Defining button functions
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
        self.mylayout.setColumnStretch(1, 3)
        self.mylayout.addWidget(self.buttonLoad     , 0, 0)
        self.mylayout.addWidget(self.buttonConfirm  , 1, 0)
        self.mylayout.addWidget(self.buttonVolume   , 2, 0)
        self.mylayout.addWidget(self.buttonSave     , 3, 0)
        self.mylayout.addWidget(self.buttonUndo     , 4, 0)
        self.mylayout.addWidget(self.buttonRedo     , 5, 0)
        self.mylayout.addWidget(self.buttonClose    , 6, 0)
        self.mylayout.addWidget(self.dialogBox      , 7, 0)
        self.setMinimumSize(1000,500)
        # Creating a dummy pptk window
        self.setPointCloud([1,1,1],[1])


    def setPointCloud(self,pcVector,filter):
        global v
        # Filter z data to exclude outliers and help colouring
        bxplt = plt.boxplot(filter)
        m1 = bxplt['whiskers'][0]._y[0] # Minimum value of the minimum range
        M2 = bxplt['whiskers'][1]._y[1] # Maximum value of the maximum range

        v = pptk.viewer(pcVector,filter)
        v.color_map('jet',scale=[m1,M2])
        # v.set(bg_color = [1.0,1.0,1.0,0.0])
        # v.set(floor_color = [1.0,1.0,1.0,0.0])
        self.embedPC()
        pass

    # FUNCTION: Embed point cloud
    def embedPC(self):
        # Find pptk window ID
        if OS == 'Windows':
            global winId
            winId = win32gui.FindWindowEx(0, 0, None, "viewer")
        elif OS == 'Linux':
            self.xlibList = Display().screen().root
            findViewer(self.xlibList)
        # Creating a window object
        self.window = QtGui.QWindow.fromWinId(winId)
        self.window.setFlags(QtCore.Qt.FramelessWindowHint)
        # self.window.setFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.X11BypassWindowManagerHint)
        # Defining container object
        self.windowcontainer = self.createWindowContainer(self.window, self.mywidget)
        # Setting container to layout
        time.sleep(.1)
        self.mylayout.addWidget(self.windowcontainer, 0, 1, 8, 5)

    # FUNCTION: Clear temporary files
    def clearTempFiles(self):
        if os.path.exists(pathToTemp):
            shutil.rmtree(pathToTemp)
        if os.path.exists(pathToCachedPC):
            os.remove(pathToCachedPC)

    # CLICK: Load new point cloud
    def loadClick(self):
        # Modified global variables
        global v, xyz, fname

        # Status message
        self.dialogBox.clear()
        self.dialogBox.textCursor().insertText('Escolhendo nuvem de pontos...\n')
        self.repaint()

        # Open a dialog box
        fname = QtWidgets.QFileDialog.getOpenFileName(self, "Escolher nuvem de pontos", root, "Arquivos de nuvem de pontos (*.txt)")
        # If nothing is selected: return
        if fname ==('',''):
            self.dialogBox.textCursor().insertText('Nenhuma nuvem escolhida!\n')
            self.repaint()
            return
        # Get file name
        nuvem = fname[0]
        # Status message
        self.dialogBox.clear()
        self.dialogBox.textCursor().insertText('Arquivo: ' + nuvem + '.\n')
        self.repaint()
        # Try to load the txt point cloud into a numpy float matrix.
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

        # Load point cloud to pptk viewer referencing z axis to colors
        self.setPointCloud(xyz,z)
        self.buttonConfirm.setEnabled(True)
        self.buttonVolume.setEnabled(True)
    

    # CLICK: Confirm modification
    def confirmClick(self):
        # Modified global variables
        global xyz, v, flagModification, counter, index, history, historyAfter, historyBefore
        
        # Status message
        self.dialogBox.clear()
        self.dialogBox.textCursor().insertText('Buscando ponto selecionados...\n')
        self.repaint()

        ##### Segmentar Nuvem de Pontos #####
        # Collects selected points indexes
        sel = v.get('selected')
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
        self.setPointCloud(xyz,z)
        
        # Manage action history
        counter += 1
        index = counter
        history.append(index)
        historyBefore = history

        # Save current cloud in cache
        np.savetxt(pathToCachedPC, xyz)
        np.savetxt(pathToTemp+ID+counter.__str__(),xyz)

        # Set modification flag
        flagModification = True
        # Enable folowing buttons
        self.buttonVolume.setEnabled(True)
        self.buttonSave.setEnabled(True)
        self.buttonUndo.setEnabled(True)

        # Status message
        self.dialogBox.textCursor().insertText(str(nSel)+' pontos selecionados.\n')
        self.repaint()

   
    # CLICK: Volume calculation
    def calcClick(self):
        # LER NUVEM DE PONTOS
        # Set root path to selected points
        try:
            # Try to load the txt point cloud into a numpy float matrix
            dados_df = np.loadtxt(pathToCachedPC, delimiter= ' ')
        except:
            # Use entire cloud
            dados_df = xyz
        # Status message
        self.dialogBox.textCursor().insertText('Calculando...\n')
        self.repaint()

        # Ajustar arquivo txt - (linha , coluna)
        dados_df = dados_df[:,:3]
        # Ordenar eixo x
        dados   = dados_df[dados_df[:,0].argsort()]
        # Armazena cada eixo em uma variavel
        dados_x = dados[:,0]
        dados_y = dados[:,1]
        dados_z = dados[:,2]
        
        # Path to slices
        if os.path.exists(pathToTemp):
            shutil.rmtree(pathToTemp)
        else:
            # Status message
            self.dialogBox.textCursor().insertText('Criando diretório temporário...\n')
            self.repaint()

        # SEPARAR EM SLICES NO EIXO X COM INTERVALOR DE 1000
        intervalo = 1000 # se ficar menor não fecha o polígono
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
            fig.savefig(pathToTemp+'/fig_{}.png'.format(i))
            print(i) 

            points_slice = [(x,y,z) for x,y,z in zip(dados_x[i*intervalo: (i+1)*intervalo],dados_y[i*intervalo: (i+1)*intervalo],dados_z[i*intervalo: (i+1)*intervalo])]
            np.savetxt(pathToTemp+'/points_fig_{}.txt'.format(i), points_slice, delimiter=' ') 

            plt.close()

        # Identificar o numero de slices na path
        filepaths = glob.glob(pathToTemp+ "*.png", recursive= True)
        print(len(filepaths)) # Número de arquivos na path

        total = 0

        for i in range(len(filepaths)):
            img = np.asarray(Image.open(pathToTemp + "fig_{}.png".format(i)).convert('L'))
            img = 1 * (img < 255)
            m,n = img.shape
            total += img.sum() 
            print("{} white pixels, out of {} pixels in total.".format(img.sum(), m*n)) 
            
        print("Número total de pixels {}".format(total))

        somaslices = total
        volumeareaporpixels= somaslices*0.005657 #relação pixels to m3 
        
        self.dialogBox.textCursor().insertText("Volume total = {} m³".format(volumeareaporpixels)+'.\n')
        self.repaint()
        print("Volume total = {} m³".format(volumeareaporpixels))


    # CLICK: Save current point cloud
    def saveClick(self):
        # Modified global variables
        global flagModification
        
        self.dialogBox.textCursor().insertText('Salvando nuvem de pontos...\n')
        self.repaint()
        fname = QtWidgets.QFileDialog.getSaveFileName(self, 'Salvar nuvem de pontos', root, "Arquivos de nuvem de pontos (*.txt)")
        if fname == ('',''):
            self.dialogBox.textCursor().insertText('Operação "salvar" cancelada!\n')
            self.repaint()
            return
        file = open(fname[0],'w')
        text = open(pathToCachedPC,'r').read()
        file.write(text)
        file.close()
        flagModification = False
        r = requests.post()
        self.dialogBox.textCursor().insertText('Nuvem de pontos salva em:\n'+fname[0]+'\n')
        self.repaint()


    # CLICK: Return to previous modification state
    def undoClick(self):
        global index, historyAfter, historyBefore
        # Manage action history
        historyAfter.insert(0,historyBefore.pop())
        if not historyBefore:
            index = -1
            nuvem = fname[0]
            self.buttonUndo.setEnabled(False)
        else:
            index = historyBefore[-1]
            nuvem = pathToTemp+ID+index.__str__()
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
        self.setPointCloud(xyz,z)
        self.repaint()
        self.buttonRedo.setEnabled(True)


    # CLICK: Return to later modification state after Undo
    def redoClick(self):
        global index, historyAfter, historyBefore
        historyBefore.append(historyAfter.pop(0))
        index = historyBefore[-1]
        nuvem = pathToTemp+ID+index.__str__()
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
        self.setPointCloud(xyz,z)
        if not historyAfter:
            self.buttonRedo.setEnabled(False)
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
            reply = QtWidgets.QMessageBox.question(self, 'Modificações pendentes!', quit_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.saveClick()
            else:
                self.clearTempFiles()
                event.accept()
             
        else:
            self.clearTempFiles()
            event.accept()



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    form = MainWindow()
    form.setWindowTitle('Editor de Nuvem de Pontos')
    #form.setGeometry(100, 100, 600, 500)
    form.show()

    sys.exit(app.exec_())
