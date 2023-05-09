"""Desktop application for point cloud manipulation"""
import json
import os
import random
import string
import sys
from time import sleep

import matplotlib.pyplot as plt
import numpy as np
import requests
import Xlib
import Xlib.display
from PyQt5 import QtCore, QtGui

from PyQt5.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QWidget,
)

import pptk


class Second(QMainWindow):
    """Database selection window"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_widget = QWidget()

        self.setWindowTitle("Banco de dados")

        self.data_widget = QWidget()
        self.buttons_widget = QWidget()

        self.main_layout = QGridLayout(self.main_widget)
        self.data_layout = QGridLayout(self.data_widget)
        self.buttons_layout = QGridLayout(self.buttons_widget)

        self.setCentralWidget(self.main_widget)
        # pylint: disable=line-too-long
        payload = {
            "responseType": "fieldList",
            "initDate": "2010-01-01 00:00:00",
            "endDate": "2100-10-31 23:59:59",
        }
        db_request = requests.get(
            "http://localhost:8503/pointCloudData", params=payload, timeout=5
        )
        self.db_datas = json.loads(db_request.text)
        mission_id_list = []
        id_list = []
        init_list = []
        mission_list = []
        self.number_rows = len(self.db_datas)
        for i in range(0, self.number_rows):
            mission_id_list.append(self.db_datas[i]["mission_id"])
            init_list.append(self.db_datas[i]["flight_init"])
            mission_list.append(self.db_datas[i]["mission"])
            id_list.append(self.db_datas[i]["id"])

        self.create_table(mission_id_list, init_list, mission_list, id_list)

        self.button_cancel = QPushButton("Cancelar")
        self.button_select = QPushButton("Selecionar")

        self.button_cancel.clicked.connect(self.cancel_action)
        self.button_select.clicked.connect(self.select_action)

        if self.table_widget.rowCount() == 0:
            self.button_select.setEnabled(False)
        else:
            self.table_widget.selectRow(0)

        self.data_layout.addWidget(self.table_widget)

        self.buttons_layout.addWidget(self.button_select, 0, 0)
        self.buttons_layout.addWidget(self.button_cancel, 0, 1)

        self.main_layout.setColumnStretch(1, 2)
        self.main_layout.addWidget(self.data_widget, 0, 0, 1, 2)
        self.main_layout.addWidget(self.buttons_widget, 1, 0)

        self.setGeometry(0, 0, 370, 400)
        self.setMaximumWidth(370)

    def create_table(self, mission_id_list, init_list, mission_list, id_list):
        """Create database table"""

        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(self.number_rows)
        self.table_widget.setColumnCount(4)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        if self.number_rows > 0:
            for i in range(self.number_rows - 1, -1, -1):
                date = (
                    init_list[i].split("-")[2].split("T")[0]
                    + "/"
                    + init_list[i].split("-")[1]
                    + "/"
                    + init_list[i].split("-")[0]
                    + " "
                    + init_list[i].split("-")[2].split("T")[1][:-5]
                )
                self.table_widget.setItem(
                    self.number_rows - i - 1,
                    0,
                    QTableWidgetItem(str(mission_id_list[i])),
                )
                self.table_widget.setItem(
                    self.number_rows - i - 1, 1, QTableWidgetItem(date)
                )
                self.table_widget.setItem(
                    self.number_rows - i - 1,
                    2,
                    QTableWidgetItem(mission_list[i][:-4]),
                )
                self.table_widget.setItem(
                    self.number_rows - i - 1,
                    3,
                    QTableWidgetItem(str(id_list[i])),
                )
                self.table_widget.move(10, 20)
        self.table_widget.setHorizontalHeaderLabels(
            ["#", "data e hora", "pilhas", "índice"]
        )
        self.table_widget.resizeColumnsToContents()
        self.table_widget.resizeRowsToContents()

    def cancel_action(self):
        """Handles cancel action confirmation"""

        form.dialog_box.clear()
        form.dialog_box.textCursor().insertText("Nenhuma nuvem escolhida!\n")
        form.repaint()
        form.main_widget.setDisabled(False)
        self.close()

    def select_action(self):
        """Handles data selection action"""

        if self.debug_mode:
            print("Select load action")
        pcd_id = self.table_widget.selectedItems()[3].text()
        mission_id = self.table_widget.selectedItems()[0].text()
        lmid = len(mission_id)
        if lmid == 1:
            mission_id = "000" + mission_id
        elif lmid == 2:
            mission_id = "00" + mission_id
        elif lmid == 3:
            mission_id = "0" + mission_id
        form.db_id = pcd_id
        payload = {"responseType": "pcdFile", "id": pcd_id, "pcdFile": "raw"}
        response = requests.get(
            "http://localhost:8503/pointCloudData", params=payload, timeout=5
        )
        header_data = json.dumps(dict(response.headers))
        header_data = json.loads(header_data)
        file_path = "/var/tmp/trms/crops" + mission_id + "/"
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        raw_file_name = os.path.join(file_path, mission_id + ".pcd")
        with open(raw_file_name, "wb") as file_obj:
            for chunk in response.iter_content(chunk_size=128):
                file_obj.write(chunk)
        crop_list = [
            "fn_stp1a",
            "fn_stp1b",
            "fn_stp2a",
            "fn_stp2b",
            "fn_stp2c",
            "fn_stp2d",
            "fn_stp3a",
            "fn_stp3b",
        ]
        for crop in crop_list:
            if (
                self.db_datas[
                    self.number_rows
                    - self.table_widget.selectedIndexes()[0].row()
                    - 1
                ][crop]
                != ""
            ):
                crop_id = crop[-2] + crop[-1].capitalize()
                payload = {
                    "responseType": "pcdFile",
                    "id": pcd_id,
                    "pcdFile": crop_id,
                }
                response = requests.get(
                    "http://localhost:8503/pointCloudData",
                    params=payload,
                    timeout=5,
                )
                header_data = json.dumps(dict(response.headers))
                header_data = json.loads(header_data)
                file_name = os.path.join(
                    file_path, mission_id + "_" + crop_id + ".pcd"
                )
                with open(file_name, "wb") as file_obj:
                    for chunk in response.iter_content(chunk_size=128):
                        file_obj.write(chunk)
        form.load_click(raw_file_name)
        form.main_widget.setEnabled(True)
        self.close()

    def close_event(self, event):
        """Closes database window"""
        form.main_widget.setDisabled(False)
        event.accept()


# Main window code
class MainWindow(QMainWindow):
    """Main window class"""

    def __init__(self, review_mode, debug_mode):
        super().__init__()

        # Widget object
        self.main_widget = QWidget()

        self.review_mode = review_mode
        self.debug_mode = debug_mode

        # Flag to detect changes of point cloud
        self.flag_modification = False
        self.flag_wait = False
        self.mission_id = 0
        self.available_piles = []
        self.view = ""
        self.counter = -1
        self.nuvem_txt = ""
        # self.database = Second(self)
        self.pc_temp = []
        self.xlib_list = []
        self.window = []
        self.window_container = []
        self.xyz_data = []
        self.z_data = []
        self.database = []
        self.dialog_save = []
        self.btn_save_db = []
        self.cmb_save_db = []
        self.choose_pile_warning = []
        self.crop_files = ""
        self.fname = ("", "")
        self.db_id = ""
        self.crop_dict = {}
        # Action index
        self.index = 0
        # Id of pptk window for embeding procedure
        self.win_id = 0
        self.win_pid = 0
        # Action history
        self.history = []
        # Action history before
        self.history_before = []
        # Action history after
        self.history_after = []
        # Path to main directory
        self.application_root = (
            os.path.dirname(os.path.abspath(__file__)) + "/"
        )
        # Browser root
        self.browser_root = "/home/"
        # Path to temporary folder
        self.path_to_temp = "/var/tmp/trms/"
        # Register for file currently open
        if not os.path.exists(self.path_to_temp):
            os.mkdir(self.path_to_temp)
        # Random vector to create program ID
        rand_id_vec = string.ascii_letters + "0123456789"
        # Select 3 elements from randIdVec at random as ID
        self.rand_id = (
            random.choice(rand_id_vec)
            + random.choice(rand_id_vec)
            + random.choice(rand_id_vec)
        )
        # Path to cache folder
        self.path_to_cache = os.path.join(self.path_to_temp, self.rand_id)
        while os.path.exists(self.path_to_cache):
            self.rand_id = (
                random.choice(rand_id_vec)
                + random.choice(rand_id_vec)
                + random.choice(rand_id_vec)
            )
            # Path to cache folder
            self.path_to_cache = os.path.join(self.path_to_temp, self.rand_id)
        os.mkdir(self.path_to_cache)

        # Path to cached point cloud
        self.path_to_cached_pc = os.path.join(
            self.path_to_cache, "selected.txt"
        )

        self.stock_widget = QWidget(self.main_widget)
        self.buttons_widget = QWidget(self.main_widget)
        self.view_widget = QWidget(self.main_widget)

        self.edit_pcd = ""

        self.main_widget.setStyleSheet("background-color:#333333;")
        self.stock_widget.setStyleSheet("background-color:#373f49;")
        self.view_widget.setStyleSheet("background-color:#373f49;")
        self.buttons_widget.setStyleSheet("background-color:#373f49;")

        # Layout object
        self.main_layout = QGridLayout(self.main_widget)

        self.buttons_layout = QGridLayout(self.buttons_widget)
        self.stock_layout = QGridLayout(self.stock_widget)
        self.view_layout = QGridLayout(self.view_widget)

        self.setCentralWidget(self.main_widget)

        # Creating button objects
        self.current_stock = "0"
        self.button_stock_1a = QPushButton("1A")
        self.button_stock_1b = QPushButton("1B")
        self.button_stock_2a = QPushButton("2A")
        self.button_stock_2b = QPushButton("2B")
        self.button_stock_2c = QPushButton("2C")
        self.button_stock_2d = QPushButton("2D")
        self.button_stock_3a = QPushButton("3A")
        self.button_stock_3b = QPushButton("3B")

        self.button_top = QPushButton("Topo")
        self.button_side = QPushButton("Lado")
        self.button_front = QPushButton("Frente")

        self.button_load = QPushButton("Carregar nuvem")
        self.button_confirm = QPushButton("Confirmar seleção")
        self.button_volume = QPushButton("Calcular volume")
        self.button_save = QPushButton("Salvar nuvem")
        self.button_undo = QPushButton("Desfazer última seleção")
        self.button_redo = QPushButton("Refazer seleção")
        self.button_close = QPushButton("Fechar")

        # Disabling buttons for latter usage
        for button in [
            self.button_stock_1a,
            self.button_stock_1b,
            self.button_stock_2a,
            self.button_stock_2b,
            self.button_stock_2c,
            self.button_stock_2d,
            self.button_stock_3a,
            self.button_stock_3b,
            self.button_volume,
            self.button_confirm,
            self.button_save,
            self.button_undo,
            self.button_redo,
        ]:
            button.setStyleSheet("color: #373f49; background: #373f49;")
            button.setEnabled(False)

        # Defining button functions
        self.button_stock_1a.clicked.connect(self.stock_1_a_click)
        self.button_stock_1b.clicked.connect(self.stock_1_b_click)
        self.button_stock_2a.clicked.connect(self.stock_2_a_click)
        self.button_stock_2b.clicked.connect(self.stock_2_b_click)
        self.button_stock_2c.clicked.connect(self.stock_2_c_click)
        self.button_stock_2d.clicked.connect(self.stock_2_d_click)
        self.button_stock_3a.clicked.connect(self.stock_3_a_click)
        self.button_stock_3b.clicked.connect(self.stock_3_b_click)

        self.button_top.clicked.connect(self.top_click)
        self.button_front.clicked.connect(self.front_click)
        self.button_side.clicked.connect(self.side_click)

        self.button_load.clicked.connect(self.load_click)
        self.button_confirm.clicked.connect(self.confirm_click)
        self.button_volume.clicked.connect(self.calc_click)
        self.button_save.clicked.connect(self.save_click)
        self.button_undo.clicked.connect(self.undo_click)
        self.button_redo.clicked.connect(self.redo_click)
        self.button_close.clicked.connect(self.close_click)

        # Creating a dialog box object
        self.dialog_box = QTextEdit("Área de informações")
        self.dialog_box.setReadOnly(True)

        # Layout setup (except pptk container)
        self.stock_layout.addWidget(self.button_stock_3b, 0, 0, 1, 2)
        self.stock_layout.addWidget(self.button_stock_3a, 0, 2, 1, 2)
        self.stock_layout.addWidget(self.button_stock_2d, 1, 0, 1, 1)
        self.stock_layout.addWidget(self.button_stock_2c, 1, 1, 1, 1)
        self.stock_layout.addWidget(self.button_stock_2b, 1, 2, 1, 1)
        self.stock_layout.addWidget(self.button_stock_2a, 1, 3, 1, 1)
        self.stock_layout.addWidget(self.button_stock_1b, 2, 0, 1, 2)
        self.stock_layout.addWidget(self.button_stock_1a, 2, 2, 1, 2)

        self.view_layout.addWidget(self.button_top, 0, 0)
        self.view_layout.addWidget(self.button_side, 0, 1)
        self.view_layout.addWidget(self.button_front, 0, 2)

        self.buttons_layout.addWidget(self.button_load)
        self.buttons_layout.addWidget(self.button_confirm)
        self.buttons_layout.addWidget(self.button_volume)
        self.buttons_layout.addWidget(self.button_save)
        self.buttons_layout.addWidget(self.button_undo)
        self.buttons_layout.addWidget(self.button_redo)
        self.buttons_layout.addWidget(self.button_close)
        self.buttons_layout.addWidget(self.dialog_box)

        self.main_layout.setColumnStretch(1, 3)
        self.main_layout.addWidget(self.stock_widget, 0, 0)
        self.main_layout.addWidget(self.view_widget, 1, 0)
        self.main_layout.addWidget(self.buttons_widget, 3, 0)
        self.setMinimumSize(1000, 500)
        # Creating a dummy pptk window
        self.set_point_cloud([1, 1, 1], [1], [])

    def find_viewer(self, xlib_list):
        """Find pptk viewport"""
        children = xlib_list.query_tree().children
        counter = 0
        for child in children:
            subchildren = child.query_tree().children
            for xwin in subchildren:
                if xwin.get_wm_class() is None:
                    continue
                if "viewer" not in xwin.get_wm_class():
                    continue
                self.win_id = xwin.id
                self.win_pid = os.popen(
                    "xprop -id "
                    + str(self.win_id)
                    + ' | grep "PID" | sed "s/_NET_WM_PID(CARDINAL) = //"'
                ).read()[:-1]
            counter += 1

    def load_point_cloud(self, nuvem_txt):
        """Loads point cloud"""
        # Try to load the txt point cloud into a numpy float matrix.
        try:
            self.xyz_data = np.loadtxt(nuvem_txt, delimiter=" ")

            # Filter x, y and z coordinates
            self.xyz_data = self.xyz_data[:, :3]
            # Register z values (used to coloring)
            self.z_data = self.xyz_data[:, 2]

            # Load point cloud to pptk viewer referencing z axis to colors
            self.set_point_cloud(self.xyz_data, self.z_data, self.view)
        except Exception as exc:
            self.dialog_box.textCursor().insertText(
                f"Erro: arquivo inválido! Exception {exc}\n"
            )
            self.repaint()

    def set_point_cloud(self, pc_vector, filter_data, new_view):
        """Display a point cloud into viewport"""
        if new_view:
            # Filter z data to exclude outliers and help colouring
            box_plot = plt.boxplot(filter_data)
            min_value = box_plot["whiskers"][0]._y[
                0
            ]  # Minimum value of the minimum range
            max_value = box_plot["whiskers"][1]._y[
                1
            ]  # Maximum value of the maximum range
            new_view.clear()
            new_view.load(pc_vector, filter_data)
            new_view.color_map("jet", scale=[min_value, max_value])
            # view.set(phi = 0, theta = np.pi/2)
            self.view.set(phi=-(np.pi / 2 - 0.1933), theta=np.pi / 2)
        else:
            self.view = pptk.viewer(pc_vector)
            self.embed_pc()

    def embed_pc(self):
        """Dock point cloud into MainWindow viewport"""

        self.xlib_list = Xlib.display.Display().screen().root
        self.find_viewer(self.xlib_list)
        # Creating a window object
        self.window = QtGui.QWindow.fromWinId(self.win_id)
        # self.window.setFlags(QtCore.Qt.FramelessWindowHint)
        self.window.setFlags(
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.X11BypassWindowManagerHint
        )
        # Defining container object
        self.window_container = self.createWindowContainer(
            self.window, self.main_widget
        )
        self.window_container.setFocusPolicy(QtCore.Qt.TabFocus)
        # Setting container to layout
        sleep(0.3)
        self.main_layout.addWidget(self.window_container, 0, 1, 4, 5)

    def clear_temp_files(self):
        """Kills pptk process and delete temporary files from file system"""
        os.system("kill -9 " + self.win_pid)

    def stock_1_a_click(self):
        """Click action for stock pile 1 A"""
        if self.current_stock_manager(self.button_stock_1a, "1A"):
            for pc_file in self.pc_temp:
                if "_1A.txt" in pc_file:
                    self.nuvem_txt = pc_file
            # Try to load the txt point cloud into a numpy float matrix.
            self.load_point_cloud(self.nuvem_txt)

    def stock_1_b_click(self):
        """Click action for stock pile 1 B"""
        if self.current_stock_manager(self.button_stock_1b, "1B"):
            for pc_file in self.pc_temp:
                if "_1B.txt" in pc_file:
                    self.nuvem_txt = pc_file
            # Try to load the txt point cloud into a numpy float matrix.
            self.load_point_cloud(self.nuvem_txt)

    def stock_2_a_click(self):
        """Click action for stock pile 2 A"""
        if self.current_stock_manager(self.button_stock_2a, "2A"):
            for pc_file in self.pc_temp:
                if "_2A.txt" in pc_file:
                    self.nuvem_txt = pc_file
            # Try to load the txt point cloud into a numpy float matrix.
            self.load_point_cloud(self.nuvem_txt)

    def stock_2_b_click(self):
        """Click action for stock pile 2 B"""
        if self.current_stock_manager(self.button_stock_2b, "2B"):
            for pc_file in self.pc_temp:
                if "_2B.txt" in pc_file:
                    self.nuvem_txt = pc_file
            # Try to load the txt point cloud into a numpy float matrix.
            self.load_point_cloud(self.nuvem_txt)

    def stock_2_c_click(self):
        """Click action for stock pile 2 C"""
        if self.current_stock_manager(self.button_stock_2c, "2C"):
            for pc_file in self.pc_temp:
                if "_2C.txt" in pc_file:
                    self.nuvem_txt = pc_file
            # Try to load the txt point cloud into a numpy float matrix.
            self.load_point_cloud(self.nuvem_txt)

    def stock_2_d_click(self):
        """Click action for stock pile 2 D"""
        if self.current_stock_manager(self.button_stock_2d, "2D"):
            for pc_file in self.pc_temp:
                if "_2D.txt" in pc_file:
                    self.nuvem_txt = pc_file
            # Try to load the txt point cloud into a numpy float matrix.
            self.load_point_cloud(self.nuvem_txt)

    def stock_3_a_click(self):
        """Click action for stock pile 3 A"""
        if self.current_stock_manager(self.button_stock_3a, "3A"):
            for pc_file in self.pc_temp:
                if "_3A.txt" in pc_file:
                    self.nuvem_txt = pc_file
            # Try to load the txt point cloud into a numpy float matrix.
            self.load_point_cloud(self.nuvem_txt)

    def stock_3_b_click(self):
        """Click action for stock pile 3 B"""
        if self.current_stock_manager(self.button_stock_3b, "3B"):
            for pc_file in self.pc_temp:
                if "_3B.txt" in pc_file:
                    self.nuvem_txt = pc_file
            # Try to load the txt point cloud into a numpy float matrix.
            self.load_point_cloud(self.nuvem_txt)

    def current_stock_manager(self, button, current_stock_selection):
        """Holds information about the selected stock pile"""
        self.dialog_box.clear()
        for butt in [
            self.button_stock_1a,
            self.button_stock_1b,
            self.button_stock_2a,
            self.button_stock_2b,
            self.button_stock_2c,
            self.button_stock_2d,
            self.button_stock_3a,
            self.button_stock_3b,
        ]:
            if butt.isEnabled():
                butt.setStyleSheet("color: black; background: #373f49;")

        if self.flag_modification:
            quit_msg = "Deseja salvar as últimas modificações?"
            msg_box = QMessageBox(self)
            msg_box.setStandardButtons(
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            msg_box.setWindowTitle("Modificações pendentes!")
            msg_box.setText(quit_msg)
            btn_yes = msg_box.button(QMessageBox.Yes)
            btn_yes.setText("Sim")
            btn_no = msg_box.button(QMessageBox.No)
            btn_no.setText("Não")
            btn_cancel = msg_box.button(QMessageBox.Cancel)
            btn_cancel.setText("Cancelar")
            reply = msg_box.exec()
            if reply == QMessageBox.Yes:
                self.save_click()
            elif reply == QMessageBox.Cancel:
                return False
            elif reply == QMessageBox.No:
                self.flag_modification = False
                self.history_before = []
                self.history = []
                self.history_after = []
                self.index = 0
                self.counter = -1
                self.button_undo.setStyleSheet(
                    "color: #373f49; background: #373f49;"
                )
                self.button_undo.setEnabled(False)
                self.button_redo.setStyleSheet(
                    "color: #373f49; background: #373f49;"
                )
                self.button_redo.setEnabled(False)
                self.button_save.setStyleSheet(
                    "color: #373f49; background: #373f49;"
                )
                self.button_save.setEnabled(False)
                os.popen(
                    "find "
                    + self.path_to_cache
                    + ' ! -name "selected.txt" -type f -exec rm -f {} +'
                )

        if current_stock_selection == self.current_stock:
            self.current_stock = "0"
            self.load_point_cloud(self.pc_temp[0])
            button.setStyleSheet("color: black; background: #373f49;")
            self.setWindowTitle(
                "Editor de Nuvem de Pontos: Missão " + self.mission_id
            )
            return False

        # button.setStyleSheet("color: white; background: darkgreen;")
        button.setStyleSheet("color: black; background: #9A7D0A;")
        self.setWindowTitle(
            "Editor de Nuvem de Pontos: Missão "
            + self.mission_id
            + " Pilha "
            + current_stock_selection
        )
        self.current_stock = current_stock_selection
        return True

    def top_click(self):
        """Change viewport perspective to top view"""
        # self.view.set(phi = 0, theta = np.pi/2)
        self.view.set(phi=-(np.pi / 2 - 0.1933), theta=np.pi / 2)

    def front_click(self):
        """Change viewport perspective to front view"""
        # self.view.set(phi = 0, theta = 0)
        self.view.set(phi=np.pi / 2 - (np.pi / 2 - 0.1933), theta=0)

    def side_click(self):
        """Change viewport perspective to side view"""
        self.view.set(phi=-(np.pi / 2 - 0.1933), theta=0)

    def browse_files(self):
        """Open browse window to search point cloud files"""
        if self.debug_mode:
            print("browse files")
        self.flag_wait = False
        self.dialog_load.close()
        # Open a dialog box
        self.fname = QFileDialog.getOpenFileName(
            self,
            "Escolher nuvem de pontos",
            self.browser_root,
            "Arquivos de nuvem de pontos (*.pcd)",
        )

    def browse_db(self):
        """Display database"""
        if self.debug_mode:
            print("browse database")
        self.flag_wait = True
        self.fname = ("", "")
        # self.dialogLoad.close()
        self.database = Second(self)
        self.database.show()
        self.main_widget.setDisabled(True)

    def load_click(self, cloud_path):
        """Load new pointcloud on click"""
        if self.flag_modification:
            quit_msg = "Deseja salvar as últimas modificações?"
            msg_box = QMessageBox(self)
            msg_box.setStandardButtons(
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            msg_box.setWindowTitle("Modificações pendentes!")
            msg_box.setText(quit_msg)
            btn_yes = msg_box.button(QMessageBox.Yes)
            btn_yes.setText("Sim")
            btn_no = msg_box.button(QMessageBox.No)
            btn_no.setText("Não")
            btn_cancel = msg_box.button(QMessageBox.Cancel)
            btn_cancel.setText("Cancelar")
            reply = msg_box.exec()
            if reply == QMessageBox.Yes:
                self.save_click()
            elif reply == QMessageBox.Cancel:
                return

        # Status message
        self.dialog_box.clear()
        self.dialog_box.textCursor().insertText(
            "Escolhendo nuvem de pontos...\n"
        )
        self.repaint()

        if cloud_path:
            self.fname = [cloud_path, 0]
            self.mission_id = cloud_path.split("/")[-1].split(".")[0]
        else:
            self.dialog_load = QDialog()
            self.btn_harddrive = QPushButton("Disco rígido", self.dialog_load)
            self.btn_harddrive.move(10,15)
            self.btn_harddrive.clicked.connect(self.browse_files)
            self.btn_database = QPushButton("Banco de dados", self.dialog_load)
            self.btn_database.move(110,15)
            self.btn_database.clicked.connect(self.browse_db)
            # self.dialogLoad.setGeometry(600,300,235,50)
            self.dialog_load.setFixedSize(235, 50)
            self.dialog_load.setWindowTitle("Fonte de arquivos")
            self.dialog_load.exec()

            # self.browse_db()

            if self.flag_wait:
                self.dialog_box.clear()
                self.dialog_box.textCursor().insertText(
                    "Escolhendo nuvem do banco de dados...\n"
                )
                self.repaint()
                return
            if not self.fname == ("", ""):
                print(self.mission_id)
                self.mission_id = (
                    self.fname[0].split("/")[-2].split("missao")[1]
                )

        # If nothing is selected: return
        if self.fname == ("", ""):
            self.dialog_box.clear()
            self.dialog_box.textCursor().insertText(
                "Nenhuma nuvem escolhida!\n"
            )
            self.repaint()
            return
        nuvem_pcd = self.fname[0]

        crop_path = os.path.join(self.path_to_temp, "crops" + self.mission_id)
        if not os.path.exists(crop_path):
            os.mkdir(crop_path)

        self.crop_dict = {}

        if nuvem_pcd == "":
            return
        self.nuvem_txt = os.path.join(
            crop_path, nuvem_pcd.split("/")[-1].split(".")[0] + ".txt"
        )
        if os.path.exists(self.nuvem_txt):
            if self.debug_mode:
                print(
                    "Cloud " + nuvem_pcd.split("/")[-1] + " loaded from cache!"
                )
        else:
            if self.debug_mode:
                print("Creating " + nuvem_pcd + " txt temporary file")
            os.system("./extconverter " + nuvem_pcd + " -D " + crop_path)
            os.rename(nuvem_pcd, self.nuvem_txt)

        # Status message
        self.dialog_box.clear()
        self.dialog_box.textCursor().insertText("Nuvem carregada.\n")
        self.repaint()

        # Try to load the txt point cloud into a numpy float matrix.
        try:
            self.xyz_data = np.loadtxt(self.nuvem_txt, delimiter=" ")
        except OSError as exc:
            self.dialog_box.textCursor().insertText(
                f"Erro: arquivo inválido! Exception {exc}\n"
            )
            self.repaint()
            return

        self.pc_temp = []
        self.pc_temp.append(self.nuvem_txt)

        # Filter x, y and z coordinates
        self.xyz_data = self.xyz_data[:, :3]
        # Register z values (used to coloring)
        self.z_data = self.xyz_data[:, 2]

        # Load point cloud to pptk viewer referencing z axis to colors
        self.set_point_cloud(self.xyz_data, self.z_data, self.view)

        self.flag_modification = False
        self.history_before = []
        self.history = []
        self.history_after = []
        self.index = 0
        self.counter = -1

        # # Disabling buttons for latter usage
        self.available_piles = []
        for button in [
            self.button_stock_1a,
            self.button_stock_1b,
            self.button_stock_2a,
            self.button_stock_2b,
            self.button_stock_2c,
            self.button_stock_2d,
            self.button_stock_3a,
            self.button_stock_3b,
            self.button_save,
            self.button_undo,
            self.button_redo,
        ]:
            button.setStyleSheet("color: #373f49; background: #373f49;")
            button.setEnabled(False)

        if not os.path.exists(crop_path):
            os.mkdir(crop_path)

        self.crop_files = (
            os.popen("ls " + crop_path + " | grep .pcd")
            .read()
            .split("\n")[0:-1]
        )
        for crop in self.crop_files:
            crop_txt = os.path.join(crop_path, crop.split(".")[0] + ".txt")
            crop_pcd = os.path.join(crop_path, crop)
            self.pc_temp.append(crop_txt)
            if os.path.exists(crop_txt):
                if self.debug_mode:
                    print("Crop " + crop + " loaded from cache!")
            else:
                if self.debug_mode:
                    print("Creating " + crop + " txt file")
                os.system(
                    "./extconverter "
                    + os.path.join(crop_path, crop)
                    + " -D "
                    + crop_path
                )
            if "_1A.pcd" in crop:
                self.button_stock_1a.setStyleSheet(
                    "color: black; background: #373f49;"
                )
                self.button_stock_1a.setEnabled(True)
                self.available_piles.append("1A")
                self.crop_dict["1A"] = crop_pcd
            elif "_1B.pcd" in crop:
                self.button_stock_1b.setStyleSheet(
                    "color: black; background: #373f49;"
                )
                self.button_stock_1b.setEnabled(True)
                self.available_piles.append("1B")
                self.crop_dict["1B"] = crop_pcd
            elif "_2A.pcd" in crop:
                self.button_stock_2a.setStyleSheet(
                    "color: black; background: #373f49;"
                )
                self.button_stock_2a.setEnabled(True)
                self.available_piles.append("2A")
                self.crop_dict["2A"] = crop_pcd
            elif "_2B.pcd" in crop:
                self.button_stock_2b.setStyleSheet(
                    "color: black; background: #373f49;"
                )
                self.button_stock_2b.setEnabled(True)
                self.available_piles.append("2B")
                self.crop_dict["2B"] = crop_pcd
            elif "_2C.pcd" in crop:
                self.button_stock_2c.setStyleSheet(
                    "color: black; background: #373f49;"
                )
                self.button_stock_2c.setEnabled(True)
                self.available_piles.append("2C")
                self.crop_dict["2C"] = crop_pcd
            elif "_2D.pcd" in crop:
                self.button_stock_2d.setStyleSheet(
                    "color: black; background: #373f49;"
                )
                self.button_stock_2d.setEnabled(True)
                self.available_piles.append("2D")
                self.crop_dict["2D"] = crop_pcd
            elif "_3A.pcd" in crop:
                self.button_stock_3a.setStyleSheet(
                    "color: black; background: #373f49;"
                )
                self.button_stock_3a.setEnabled(True)
                self.available_piles.append("3A")
                self.crop_dict["3A"] = crop_pcd
            elif "_3B.pcd" in crop:
                self.button_stock_3b.setStyleSheet(
                    "color: black; background: #373f49;"
                )
                self.button_stock_3b.setEnabled(True)
                self.available_piles.append("3B")
                self.crop_dict["3B"] = crop_pcd

        ### Ajustar título da janela pra ser compatível com o sub-pilha alvo
        subpile = self.fname[0][-6:][:-4]
        # mission = '0001'
        # subpile = '3B'
        if subpile in pileNames:
            self.setWindowTitle(
                "Editor de Nuvem de Pontos: Missão "
                + self.mission_id
                + " Pilha "
                + subpile
            )
        else:
            self.setWindowTitle(
                "Editor de Nuvem de Pontos: Missão " + self.mission_id
            )

        self.button_confirm.setStyleSheet("color: black; background: #373f49;")
        self.button_volume.setStyleSheet("color: black; background: #373f49;")
        self.button_confirm.setEnabled(True)
        self.button_volume.setEnabled(True)

    def confirm_click(self):
        """Confirm modification on click"""
        # Status message
        self.dialog_box.clear()
        self.dialog_box.textCursor().insertText(
            "Buscando ponto selecionados...\n"
        )
        self.repaint()

        ## Segmentar Nuvem de Pontos ##
        # Collects selected points indexes
        sel = self.view.get("selected")
        number_selection = len(sel)
        # Create a numpy matrixes of selected points
        if number_selection == 0:
            # Status message
            self.dialog_box.moveCursor(QtGui.QTextCursor.End)
            self.dialog_box.textCursor().insertText(
                """Alerta: nenhum ponto selecionado!\n
                Utilize o botão esquerdo do mouse (BEM) com a tecla Control\n
                para efetuar seleção no campo de nuvem de pontos: BEM+Ctrl"""
            )
            self.repaint()
            return

        # Create a vector of selected points
        self.xyz_data = self.xyz_data[sel, :]
        # Register z values (used to coloring)
        self.z_data = self.xyz_data[:, 2]

        # Embed pptk
        self.set_point_cloud(self.xyz_data, self.z_data, self.view)

        # Manage action history
        self.counter += 1
        self.index = self.counter
        self.history.append(self.index)
        self.history_before = self.history

        # Save current cloud in cache
        np.savetxt(self.path_to_cached_pc, self.xyz_data)
        current_pc = os.path.join(
            self.path_to_cache, self.rand_id + str(self.counter)
        )
        np.savetxt(current_pc, self.xyz_data)

        # Set modification flags
        self.flag_modification = True
        # Enable folowing buttons
        self.button_volume.setStyleSheet("color: black; background: #373f49;")
        self.button_save.setStyleSheet("color: black; background: #373f49;")
        self.button_undo.setStyleSheet("color: black; background: #373f49;")
        self.button_volume.setEnabled(True)
        self.button_save.setEnabled(True)
        self.button_undo.setEnabled(True)

        # Status message
        self.dialog_box.clear()
        self.dialog_box.textCursor().insertText(
            str(number_selection) + " pontos selecionados.\n"
        )
        self.repaint()

    def calc_click(self):
        """Volume calculation on click"""
        self.dialog_box.clear()
        self.dialog_box.textCursor().insertText("Calculando...\n")
        self.main_widget.setDisabled(True)
        self.repaint()
        if self.counter == -1:
            np.savetxt(self.path_to_cached_pc, self.xyz_data)
        volume = (
            os.popen(
                "python3 "
                + os.path.join(self.application_root, "mainh.py ")
                + self.path_to_cached_pc
            )
            .read()
            .split("\n")[0]
        )
        self.dialog_box.textCursor().insertText(
            "Volume total = " + volume + " m³.\n"
        )
        self.repaint()
        self.main_widget.setDisabled(False)
        if self.debug_mode:
            print("Volume total = " + volume + " m³.\n")
        return volume

    def save_click(self):
        """Save current point cloud on click"""
        if not self.review_mode:
            self.dialog_save = QDialog()
            self.btn_save_db = QPushButton(
                "Salvar no banco de dados", self.dialog_save
            )
            self.btn_save_db.move(10, 15)
            self.btn_save_db.clicked.connect(self.save_database)
            self.cmb_save_db = QComboBox(self.dialog_save)
            self.cmb_save_db.insertItems(
                0, ["Selecionar pilha"] + self.available_piles
            )
            self.cmb_save_db.move(10, 50)
            self.dialog_save.setFixedSize(200, 80)
            self.dialog_save.setWindowTitle("Escolher nuvem alvo")
            self.dialog_save.exec()
        else:
            self.save_hard_drive()

    def save_hard_drive(self):
        """Save point cloud on hard drive"""
        self.dialog_box.clear()
        self.dialog_box.textCursor().insertText(
            "Salvando nuvem de pontos...\n"
        )
        self.repaint()
        # path_pcd = (
        #     "/var/tmp/trms/crops"
        #     + self.mission_id
        #     + "/"
        #     + self.mission_id
        #     + "_"
        #     + self.current_stock
        #     + ".pcd"
        # )
        path_txt = (
            "/var/tmp/trms/crops"
            + self.mission_id
            + "/"
            + self.mission_id
            + "_"
            + self.current_stock
            + ".txt"
        )
        path_png = (
            "/var/tmp/trms/crops"
            + self.mission_id
            + "/"
            + self.mission_id
            + "_"
            + self.current_stock
            + ".png"
        )
        with open(self.path_to_cached_pc, "r", encoding="utf-8") as cache_file:
            text = cache_file.read()
        with open(path_txt, "w", encoding="utf-8") as txt_file:
            txt_file.write(text)

        os.system(
            "./extconverter "
            + path_txt
            + " -D /var/tmp/trms/crops"
            + self.mission_id
            + "/"
        )

        xyz_points = np.loadtxt(path_txt, delimiter=" ")
        xyz_points = xyz_points[:, :3]
        z_points = xyz_points[:, 2]
        viewer = pptk.viewer(xyz_points, z_points)
        viewer.set(phi=-(np.pi / 2 - 0.1933), theta=np.pi / 2)
        if self.current_stock in ["1A", "3A"]:
            viewer.w_Resize()
            viewer.set(r=75)
        elif self.current_stock in ["1B", "3B"]:
            viewer.w_Resize()
            viewer.set(r=90)
        else:
            viewer.w_resize()
            viewer.set(r=150)
        box_plot = plt.boxplot(z_points)
        min_value = box_plot["whiskers"][0]._y[
            0
        ]  # Minimum value of the minimum range
        max_value = box_plot["whiskers"][1]._y[
            1
        ]  # Maximum value of the maximum range
        viewer.color_map("jet", scale=[min_value, max_value])
        viewer.set(show_info=False)
        sleep(1.5)
        viewer.capture(path_png)
        sleep(0.5)
        viewer.close()
        volume = float(self.calc_click())
        modification_file_path = os.path.join(
            "/var/tmp/trms/crops" + self.mission_id, "changes"
        )
        with open(modification_file_path, "w", encoding="utf-8") as changes:
            changes.write(self.current_stock + " " + str(volume))

        if self.review_mode:
            self.dialog_box.clear()
            self.dialog_box.textCursor().insertText(
                "Nuvem de pontos revisada!\n"
            )
        else:
            self.dialog_box.clear()
            self.dialog_box.textCursor().insertText("Nuvem de pontos salva!\n")
        self.flag_modification = False
        self.repaint()

    def save_database(self):
        """Save point cloud on database"""
        stock_name = self.cmb_save_db.currentText()
        if self.cmb_save_db.currentIndex() == 0:
            if self.debug_mode:
                print("Escolha uma pilha")
            self.choose_pile_warning = QMessageBox(
                QMessageBox.Warning,
                "Aviso",
                "Selecione uma pilha!",
                QMessageBox.Ok,
            )
            self.choose_pile_warning.exec_()
        else:
            if self.debug_mode:
                print("Salvar pilha " + stock_name)
            self.dialog_box.clear()
            self.dialog_box.textCursor().insertText(
                "Pilha " + stock_name + " atualizada no banco de dados"
            )
            self.flag_modification = False
            self.repaint()
            self.dialog_save.close()
            ## Update database
            name = self.crop_dict[stock_name]
            crop_dir = os.path.dirname(self.crop_dict[stock_name])
            os.system(
                "./extconverter " + self.path_to_cached_pc + " -D " + crop_dir
            )
            os.system("cp " + crop_dir + "/selected.pcd " + name)
            os.system(
                "cp "
                + self.path_to_cached_pc
                + " "
                + name.replace(".pcd", ".txt")
            )
            volume = float(self.calc_click())
            md5hash = os.popen("md5sum " + name).read().split(" ")[0]
            payload = f'{{"id":{self.db_id},"edited_by":0,'\
                f'"stp_volume":{volume}.2f,"md5Hash":"{md5hash}"}}'

            with open(name, "rb") as binary_data:
                files = {
                    "jsonData": ("", payload, "application/json"),
                    "pcdFile": (
                        stock_name + ".pcd",
                        binary_data,
                        "application/octet-stream",
                    ),
                }
            resp = requests.put(
                "http://localhost:8503/pointCloudData", files=files, timeout=5
            )
            if self.debug_mode:
                print(resp.text)

            ## Save on database
            # name = self.fname[0].split('/')[-1]
            # md5hash = os.popen('md5sum '+name).read().split(' ')[0]
            # headers = {'md5hash':md5hash,'user':'1'}
            # files = {'file': (name, open(name, 'rb'), 'text/plain')}
            # r = requests.post(
            #     'http://localhost:8503/pointCloudData',
            #     headers=headers, files=files
            # )
            # self.flagModification = False
            # self.dialogBox.textCursor().insertText(
            #     'Nuvem de pontos salva em:\n'+r.text+'\n'
            # )

    def undo_click(self):
        """Return to previous modification state on click"""
        # Manage action history
        self.history_after.insert(0, self.history_before.pop())
        self.dialog_box.clear()
        self.dialog_box.textCursor().insertText("Desfazer")
        if not self.history_before:
            self.index = -1
            nuvem = self.nuvem_txt  ###
            self.button_undo.setStyleSheet(
                "color: #373f49; background: #373f49;"
            )
            self.button_undo.setEnabled(False)
        else:
            self.index = self.history_before[-1]
            # nuvem = self.pathToTemp+self.randID+str(self.index)
            nuvem = os.path.join(
                self.path_to_cache, self.rand_id + str(self.index)
            )
        try:
            self.xyz_data = np.loadtxt(nuvem, delimiter=" ")
        except Exception as exc:
            self.dialog_box.textCursor().insertText(
                f"Erro: arquivo inválido! Exception {exc}\n"
            )
            self.repaint()

        # Filter x, y and z coordinates
        self.xyz_data = self.xyz_data[:, :3]
        # Register z values (used to coloring)
        self.z_data = self.xyz_data[:, 2]
        # Save current cloud in cache
        np.savetxt(self.path_to_cached_pc, self.xyz_data)

        # Load point cloud to pptk viewer referencing z axis to colors
        self.set_point_cloud(self.xyz_data, self.z_data, self.view)
        self.repaint()
        self.button_redo.setStyleSheet("color: black; background: #373f49;")
        self.button_redo.setEnabled(True)

    def redo_click(self):
        """Return to later modification state after Undo"""
        self.dialog_box.clear()
        self.dialog_box.textCursor().insertText("Refazer")
        self.history_before.append(self.history_after.pop(0))
        self.index = self.history_before[-1]
        # nuvem = self.pathToTemp+self.randID+str(self.index)
        nuvem = os.path.join(
            self.path_to_cache, self.rand_id + str(self.index)
        )
        try:
            self.xyz_data = np.loadtxt(nuvem, delimiter=" ")
        except Exception as exc:
            self.dialog_box.textCursor().insertText(
                f"Erro: arquivo inválido! Exception {exc}\n"
            )
            self.repaint()

        # Filter x, y and z coordinates
        self.xyz_data = self.xyz_data[:, :3]
        # Register z values (used to coloring)
        self.z_data = self.xyz_data[:, 2]
        # Save current cloud in cache
        np.savetxt(self.path_to_cached_pc, self.xyz_data)
        # Load point cloud to pptk viewer referencing z axis to colors
        self.set_point_cloud(self.xyz_data, self.z_data, self.view)
        if not self.history_after:
            self.button_redo.setStyleSheet(
                "color: #373f49; background: #373f49;"
            )
            self.button_redo.setEnabled(False)
        self.button_undo.setStyleSheet("color: black; background: #373f49;")
        self.button_undo.setEnabled(True)
        self.repaint()

    def close_click(self):
        """Close application on click"""
        self.close()

    def close_event(self, event):
        """Close window event"""
        if self.flag_modification:
            quit_msg = "Deseja salvar as últimas modificações?"
            msg_box = QMessageBox(self)
            msg_box.setStandardButtons(
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            msg_box.setWindowTitle("Modificações pendentes!")
            msg_box.setText(quit_msg)
            btn_yes = msg_box.button(QMessageBox.Yes)
            btn_yes.setText("Sim")
            btn_no = msg_box.button(QMessageBox.No)
            btn_no.setText("Não")
            btn_cancel = msg_box.button(QMessageBox.Cancel)
            btn_cancel.setText("Cancelar")
            reply = msg_box.exec()
            if reply == QMessageBox.Yes:
                self.save_click()
            elif reply == QMessageBox.No:
                self.clear_temp_files()
                event.accept()
            elif reply == QMessageBox.Cancel:
                event.ignore()
        else:
            self.clear_temp_files()
            event.accept()


def main(review_mode):
    """Entry point"""
    if len(argv) > 1:
        try:
            args = argv[1].split()
            index_edit = args.index("--edit")
            if DEBUG_MODE:
                print(args[index_edit + 1])
            index_id = args.index("--id")
            if DEBUG_MODE:
                print(args[index_id + 1])
            index_mission = args.index("--mission")
            if DEBUG_MODE:
                print(args[index_mission + 1])

            form.edit_pcd = args[index_edit + 1]
            subpile = args[index_id + 1]
            get_mission = args[index_mission + 1]
            form.load_click(form.edit_pcd)
            review_mode = True
            if DEBUG_MODE:
                print("Review mode.")
        except Exception as exc:
            if DEBUG_MODE:
                print(f"Invalid point cloud argument. Exception {exc}")
    else:
        if DEBUG_MODE:
            print("Edit database mode.")

    if review_mode:  ###fname
        form.button_load.setEnabled(False)
        form.button_load.setStyleSheet("color: #373f49; background: #373f49;")
        form.mission_id = get_mission
        form.current_stock = subpile
        form.button_save.setText("Finalizar revisão")
        if subpile in pileNames:
            form.setWindowTitle(
                "Editor de Nuvem de Pontos: Missão "
                + form.mission_id
                + " Pilha "
                + subpile
            )
        else:
            form.setWindowTitle(
                "Editor de Nuvem de Pontos: Missão " + form.mission_id
            )
    else:
        form.setWindowTitle("Editor de Nuvem de Pontos")
    # form.setGeometry(100, 100, 600, 500)
    form.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    DEBUG_MODE = True
    REVIEW_MODE = False
    # sys.argv.append('--edit /var/tmp/trms/nuvem_2020-09-14T10:31:00_3A.txt')
    pileNames = ["1A", "1B", "2A", "2B", "2C", "2D", "3A", "3B"]
    argv = sys.argv
    if DEBUG_MODE:
        print(argv)

    # argv = [
    #     '/home/adriano/git/volumecarvao/pcselector.py',
    #     '--edit /var/tmp/trms/crop0003/0003.pcd --id 3B --mission 0003']
    # argv = [
    #     '/home/adriano/git/volumecarvao/pcselector.py',
    #     '--edit /var/tmp/trms/crop0003/0003.pcd --id 3B --mission 0003']

    app = QApplication(argv)
    app.setStyle("fusion")
    form = MainWindow(REVIEW_MODE, DEBUG_MODE)
    main(REVIEW_MODE)
