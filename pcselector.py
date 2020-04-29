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
from   PyQt5 import QtWidgets, QtGui, QtCore
from   Xlib.display import Display
from   PIL import Image

# GLOBAL VARIABLES
# ID of pptk window for embeding procedure
winId = 0
# Path to main directory
root  = os.path.dirname(os.path.abspath(__file__)) + '/'
# Path to temporary folder
pathToSlices = root + '.selecao_teste/'
# Path to cached point cloud
pathToCachedPC = root + '.selected.txt'
# Flag to detect changes of point cloud
flagModification = False

# Search for a window called "viewer"
def findViewer(window, indent):
    # Modified global variables
    global winId
    children = window.query_tree().children
    for w in children:
        findViewer(w, indent+'-')
        if w.get_wm_class() is not None:
            if ("viewer" in w.get_wm_class()):
                # Save "viewer" window ID
                winId = w.id

# Display a dummy point cloud to start the interface
def getPC():
    # Changing global variables
    global v

    # Dummy point cloud
    v = pptk.viewer([1,1,1])
    v.set(bg_color=[1.0,1.0,1.0,0.0])
    v.set(floor_color=[1.0,1.0,1.0,0.0])

# Main window code
class MainWindow(QtWidgets.QMainWindow):
    # Initialization function
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
        
        # Creating a dummy pptk window
        getPC()
        self.embedPC()
    
    def embedPC(self):
        # Find pptk window ID
        self.xlib = Display().screen().root
        findViewer(self.xlib, '-')
        # Creating a window object
        self.window = QtGui.QWindow.fromWinId(winId)
        # Defining container object
        self.windowcontainer = self.createWindowContainer(self.window, self.mywidget)
        # Setting container to layout
        self.mylayout.addWidget(self.windowcontainer, 0, 1, 8, 10)

    # Load new point cloud
    def loadClick(self):
        # Modified global variables
        global v, xyz

        # Status message
        self.dialogBox.clear()
        self.dialogBox.textCursor().insertText('Escolhendo nuvem de pontos...\n')

        # Open a dialog box
        fname = QtWidgets.QFileDialog.getOpenFileName(self, "Escolher nuvem de pontos", root, "Arquivos de nuvem de pontos (*.txt)")
        # If nothing is selected: return
        if fname ==('',''):
            self.dialogBox.clear()
            self.dialogBox.textCursor().insertText('Nenhuma nuvem escolhida!\n')
            return
        # Get file name
        nuvem = fname[0]
        # Status message
        self.dialogBox.clear()
        self.dialogBox.textCursor().insertText('Arquivo: ' + nuvem + '.')
        # Try to load the txt point cloud into a numpy float matrix.
        try:
            xyz = np.loadtxt(nuvem, delimiter= ' ')
        except:
            self.dialogBox.textCursor().insertText('\nErro: Arquivo inválido!\n')
            getPC()
            self.embedPC()
            return

        # Status message
        self.dialogBox.textCursor().insertText(' Ok!')
        # Filter x, y and z coordinates
        xyz = xyz[:,:3]
        # Register z values (used to coloring)
        z = xyz[:,2]

        # Filter z data to exclude outliers and help colouring
        bxplt = plt.boxplot(z)
        m1 = bxplt['whiskers'][0]._y[0] # Minimum value of the minimum range
        M2 = bxplt['whiskers'][1]._y[1] # Maximum value of the maximum range
        # plt.show() # displays boxplot

        # Load point cloud to pptk viewer referencing z axis to colors
        v = pptk.viewer(xyz,z)
        v.color_map('jet',scale=[m1,M2])
        v.set(bg_color = [1.0,1.0,1.0,0.0])
        v.set(floor_color = [1.0,1.0,1.0,0.0])
        # Embed pptk
        self.embedPC()
        self.buttonConfirm.setEnabled(True)

    # Save current point cloud
    def saveClick(self):
        # Modified global variables
        global flagModification
        
        self.dialogBox.textCursor().insertText('Salvando nuvem de pontos...')
        fname = QtWidgets.QFileDialog.getSaveFileName(self, 'Salvar nuvem de pontos', root, "Arquivos de nuvem de pontos (*.txt)")
        if fname == ('',''):
            self.dialogBox.textCursor().insertText(' Cancelar!')
            return
        file = open(fname[0],'w')
        text = open(pathToCachedPC,'r').read()
        file.write(text)
        file.close()
        self.dialogBox.textCursor().insertText('Ok!\n')
        self.dialogBox.textCursor().insertText('Nuvem de pontos salva em: '+fname[0]+'\n')
        flagModification = False

    # Return to previous modification state
    def undoClick(self):
        self.dialogBox.moveCursor(QtGui.QTextCursor.End)
        self.dialogBox.textCursor().insertText('Undo')
        self.buttonRedo.setEnabled(True)

    # Return to later modification state after Undo
    def redoClick(self):
        self.dialogBox.moveCursor(QtGui.QTextCursor.End)
        self.dialogBox.textCursor().insertText('Redo')

    # Close application
    def closeClick(self):
        self.close()
        
    # Confirm modification
    def confirmClick(self):
        # Modified global variables
        global xyz, v, root, flagModification
        
        # Status message
        self.dialogBox.clear()
        self.dialogBox.textCursor().insertText('Buscando ponto selecionados... ')

        ##### Segmentar Nuvem de Pontos #####
        # Collects selected points indexes
        sel = v.get('selected')
        len(sel)
        # Create a numpy matrixes of selected points
        if len(sel) == 0:
            # Status message
            self.dialogBox.moveCursor(QtGui.QTextCursor.End)
            self.dialogBox.textCursor().insertText('Nenhum ponto selecionado!\nUtilize o botão esquerdo do mouse (BEM) com a tecla Control para efetuar seleção no campo de nuvem de pontos: BEM+Ctrl')
            return
        else:
            self.dialogBox.textCursor().insertText('Ok!\n')
            # Path to slices
            try:
                # Tries to make temporary directory
                os.mkdir(pathToSlices)
                # Status message
                self.dialogBox.textCursor().insertText('Criando diretório temporário... Ok!\n')
            except:
                pass
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
        self.embedPC()
        
        # Save archive with selected points
        np.savetxt(pathToCachedPC, xyz) # Transposta dos dados

        flagModification = True
        self.buttonVolume.setEnabled(True)
        self.buttonSave.setEnabled(True)
        self.buttonUndo.setEnabled(True)
    
    def calcClick(self):
        global xyz, pathToSlices
        self.dialogBox.clear()
        self.dialogBox.textCursor().insertText('Calculando...\n')
        # LER NUVEM DE PONTOS
        # Set root path to selected points
        try:
            # Try to load the txt point cloud into a numpy float matrix
            dados_df = np.loadtxt(pathToCachedPC, delimiter= ' ')
        except:
            dados_df = xyz
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
            fig.savefig(pathToSlices+'/fig_{}.png'.format(i))
            print(i) 

            points_slice = [(x,y,z) for x,y,z in zip(dados_x[i*intervalo: (i+1)*intervalo],dados_y[i*intervalo: (i+1)*intervalo],dados_z[i*intervalo: (i+1)*intervalo])]
            np.savetxt(pathToSlices+'/points_fig_{}.txt'.format(i), points_slice, delimiter=' ') 

            plt.close()

        # Identificar o numero de slices na path
        filepaths = glob.glob(pathToSlices+ "/*.png", recursive= True)
        print(len(filepaths)) # Número de arquivos na path

        total = 0

        for i in range(len(filepaths)):
            img = np.asarray(Image.open(pathToSlices + "fig_{}.png".format(i)).convert('L'))
            img = 1 * (img < 255)
            m,n = img.shape
            total += img.sum() 
            print("{} white pixels, out of {} pixels in total.".format(img.sum(), m*n)) 
            
        print("Número total de pixels {}".format(total))

        somaslices = total
        volumeareaporpixels= somaslices*0.005657 #relação pixels to m3 
        
        self.dialogBox.textCursor().insertText("Volume total = {} m³".format(volumeareaporpixels))
        print("Volume total = {} m³".format(volumeareaporpixels))

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

    def clearTempFiles(self):
        os.system('rm -fr '+root+'.selecao_teste 2> /dev/null')
        os.system('rm '+root+'.selected.txt 2> /dev/null')



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    form = MainWindow()
    form.setWindowTitle('Editor de Nuvem de Pontos')
    form.setGeometry(100, 100, 600, 500)
    form.show()

    sys.exit(app.exec_())