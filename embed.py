import subprocess
import time
import Xlib
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from Xlib.display import Display

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        exePath = "gnome-terminal"
        subprocess.Popen(exePath)
        xlib = Display().screen().root
        # lid = len(xlib.query_tree().children)
        # for i in range(0,lid): print(i), print(xlib.query_tree().children[i].get_wm_class())
        # xlib.query_tree().children[i].id
        hwnd = 35651585
        window = QtGui.QWindow.fromWinId(hwnd)
        self.createWindowContainer(window,self)
        self.setGeometry(500, 500, 450, 400)
        self.setWindowTitle('File dialog')
        self.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    form = MainWindow()
    #form.setGeometry(100, 100, 600, 500)
    form.show()

    sys.exit(app.exec_())