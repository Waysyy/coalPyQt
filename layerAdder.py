import sys
import threading
from tkinter import Tk, filedialog
import io
from PIL import Image

import pymongo
import numpy as np
import pandas as pd
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, \
    QColorDialog, QInputDialog, QCheckBox, QFileDialog, QMessageBox, QRadioButton, QComboBox, QHBoxLayout, \
    QProgressDialog
from PyQt5.QtCore import Qt
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches
import openpyxl
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from webcolors import rgb_to_name



# Send a ping to confirm a successful connection
#db = client['BazaProv']
#collection_density = db['Plotnosti']
#collection_krepi = db['Krepi']
#docs = collection_density.distinct('Породы')
#plot = collection_density.distinct('Плотность')
#name_krep = collection_krepi.distinct('Название')
uri = "mongodb+srv://vovabalaxoncev:Thcvovan7777@cluster0.u499jdc.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
#client = MongoClient(uri, server_api=ServerApi('1'))
class MongoConnection:
    def __init__(self, uri):
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.db = self.client['BazaProv']
        self.collection_density = self.db['Plotnosti']
        self.collection_krepi = self.db['Krepi']
        self.docs = self.collection_density.distinct('Породы')
        self.plot = self.collection_density.distinct('Плотность')
        self.name_krep = self.collection_krepi.distinct('Название')
        
    def get_docs(self):
        return self.docs
    def get_plot(self):
        return self.plot
    def get_name_krep(self):
        return self.name_krep
    def get_density_collection(self):
        return self.collection_density
    def get_krepi_collection(self):
        return self.collection_krepi
     
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        got_mongo = MongoConnection(uri)
        docs = got_mongo.get_docs()
        plot = got_mongo.get_plot()
        name_krep = got_mongo.get_name_krep()
        self.collection_krepi = got_mongo.get_krepi_collection()
        self.collection_density = got_mongo.get_density_collection()

        self.setWindowTitle("График со слоями")
        self.setGeometry(100, 100, 800, 800)

        # self.checkbox_net = QCheckBox("Сеточное разбиение", self)
        # self.checkbox_net.setGeometry(10, 0, 150, 40)
        # self.checkbox_net.stateChanged.connect(self.toggle_net)

        # Создание компоновщиков
        main_layout = QVBoxLayout()
        top_panel_layout = QHBoxLayout()
        graph_panel_layout = QHBoxLayout()

        # виджеты интерфейса
        self.label_thickness = QLabel("Толщина:", self)
        self.label_thickness.setGeometry(10, 11, 100, 30)
        self.line_edit_thickness = QLineEdit(self)
        self.line_edit_thickness.setGeometry(30, 10, 30, 30)

        # self.label_width = QLabel("Ширина разбиений:", self)
        # self.label_width.setGeometry(10, 50, 100, 30)
        # self.line_edit_width = QLineEdit(self)
        # self.line_edit_width.setGeometry(120, 50, 30, 30)
        # self.line_edit_width.setVisible(True)

        self.label_density = QLabel("Плотность:", self)
        self.label_density.setGeometry(10, 130, 100, 30)

        self.label_part = QLabel("Длина участка в метрах:", self)
        self.label_part.setGeometry(10, 90, 150, 30)
        self.line_edit_part = QLineEdit(self)
        self.line_edit_part.setGeometry(30, 90, 30, 30)

        # self.checkbox_auto = QCheckBox("Авто", self)
        # self.checkbox_auto.setGeometry(10, 170, 100, 30)
        # self.checkbox_auto.stateChanged.connect(self.toggle_auto_save)
        # self.checkbox_auto.setVisible(True)

        self.button_add = QPushButton("Добавить слой", self)
        self.button_add.setGeometry(10, 210, 210, 30)
        self.button_add.clicked.connect(self.add_layer)

        # self.button_next = QPushButton("Следующее разбиение", self)
        # self.button_next.setGeometry(10, 250, 210, 30)
        # self.button_next.clicked.connect(self.next_partition)
        # self.button_next.setVisible(True)

        # self.progress_dialog = QProgressDialog()
        # self.progress_dialog.setLabelText("Progress")
        # self.progress_dialog.setCancelButtonText("Cancel")
        # self.progress_dialog.setMinimumDuration(0)
        # self.progress_dialog.setWindowModality(Qt.WindowModal)
        # self.progress_dialog.setAutoReset(False)

        # self.total_iterations = 0
        # # Установите максимальное значение прогресс-бара
        # self.progress_dialog.setMaximum(self.total_iterations)
        #
        # # Показать прогресс-диалог только при необходимости
        # if self.total_iterations > 0:
        #     self.progress_dialog.show()

        # Установите максимальное значение прогресс-бара


        self.button_auto_part = QPushButton("Автоматическое разбиение", self)
        self.button_auto_part.setGeometry(10, 250, 210, 30)
        self.button_auto_part.clicked.connect(self.auto_part)
        #self.button_auto_part.setVisible(False)

        self.button_undo = QPushButton("Отмена", self)
        self.button_undo.setGeometry(10, 290, 210, 30)
        self.button_undo.clicked.connect(self.undo_action)

        thread_create_grid = threading.Thread(target=self.create_grid)
        self.button_edit_grid = QPushButton("Подготовка к редактированию", self)
        self.button_edit_grid.setGeometry(10, 210, 210, 30)
        self.button_edit_grid.clicked.connect(self.create_grid)
        #self.button_edit_grid.setVisible(False)

        # self.button_save = QPushButton("Сохранить разбиения", self)
        # self.button_save.setGeometry(10, 330, 210, 30)
        # self.button_save.clicked.connect(self.save_partitions)
        # self.button_save.setEnabled(False)
        # self.button_save.setVisible(True)
        save1 = Save()
        self.info_layers = []
        self.triangle_coordinates = []
        self.button_save_1 = QPushButton("Сохранить", self)
        self.button_save_1.setGeometry(10, 330, 210, 30)
        self.button_save_1.clicked.connect(lambda: save1.save_grid_information(self.triangle_coordinates, self.info_layers))

        #self.button_save_1.setVisible(False)

        self.radio_vertical = QRadioButton("Вертикальная линия", self)
        self.radio_vertical.setGeometry(10, 370, 150, 40)
        self.radio_vertical.toggled.connect(self.toggle_vertical_line)
        #self.radio_vertical.setVisible(False)

        self.radio_horizontal = QRadioButton("Горизонтальная линия", self)
        self.radio_horizontal.setGeometry(10, 410, 150, 40)
        self.radio_horizontal.toggled.connect(self.toggle_horizontal_line)
        #self.radio_horizontal.setVisible(False)

        self.radio_edit = QRadioButton("Режим редактирования сетки", self)
        self.radio_edit.setGeometry(10, 410, 150, 40)
        self.radio_edit.toggled.connect(self.toggle_edit)
        #self.radio_edit.setVisible(False)

        # слои
        self.combobox_layer = QComboBox()
        self.combobox_layer.addItems(docs)

        self.label_krep = QLabel("Крепь:", self)
        # self.label_krep.setGeometry(10, 130, 100, 30)
        self.combobox_krep = QComboBox()
        self.combobox_krep.addItems(name_krep)
        #self.label_krep.setVisible(False)
       # self.combobox_krep.setVisible(False)

        self.button_add_krep = QPushButton("Добавить крепи автоматически", self)
        self.button_add_krep.setGeometry(10, 330, 210, 30)
        self.button_add_krep.clicked.connect(self.add_krep)
        #self.button_add_krep.setVisible(False)

        self.radio_krep = QRadioButton("Добавить крепи", self)
        self.radio_krep.setGeometry(10, 370, 150, 40)
        self.radio_krep.toggled.connect(self.toggle_krep)
        #self.radio_vertical.setVisible(False)
        #self.radio_krep.setVisible(False)

        self.label_width_krep = QLabel("Расстояние между крепями:", self)
        self.label_width_krep.setGeometry(10, 90, 150, 30)
        self.line_edit_width_krep = QLineEdit(self)
        self.line_edit_width_krep.setGeometry(30, 90, 30, 30)
        #self.line_edit_width_krep.setVisible(False)
        #self.label_width_krep.setVisible(False)

        self.label_coordinate = QLabel("Координаты:", self)

        # объект для графика Matplotlib
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)
        self.figure.set_animated(True)
        self.background = self.canvas.copy_from_bbox(self.axes.bbox)

        # список для хранения слоев
        self.rectangles = []

        # список для хранения разбиений
        self.partitions = []

        # вертикальый компоновщик и добавление виджетов
        layout = QVBoxLayout()
        krepi_layout = QHBoxLayout()

        #top_panel_layout.addWidget(self.checkbox_net)
        top_panel_layout.addWidget(self.combobox_layer)
        top_panel_layout.addWidget(self.label_thickness)
        top_panel_layout.addWidget(self.line_edit_thickness)
        #top_panel_layout.addWidget(self.label_width)
        #top_panel_layout.addWidget(self.line_edit_width)
        top_panel_layout.addWidget(self.label_part)
        top_panel_layout.addWidget(self.line_edit_part)
        top_panel_layout.addWidget(self.label_density)
        # layout.addWidget(self.line_edit_density)
        graph_panel_layout.addWidget(self.label_coordinate)
        #graph_panel_layout.addWidget(self.checkbox_auto)
        graph_panel_layout.addWidget(self.radio_vertical)
        graph_panel_layout.addWidget(self.radio_horizontal)
        graph_panel_layout.addWidget(self.radio_edit)
        top_panel_layout.addWidget(self.button_add)
        #top_panel_layout.addWidget(self.button_next)
        graph_panel_layout.addWidget(self.button_auto_part)
        top_panel_layout.addWidget(self.button_undo)
        graph_panel_layout.addWidget(self.button_edit_grid)
        #top_panel_layout.addWidget(self.button_save)
        top_panel_layout.addWidget(self.button_save_1)
        krepi_layout.addWidget(self.label_krep)
        krepi_layout.addWidget(self.combobox_krep)
        krepi_layout.addWidget(self.radio_krep)
        krepi_layout.addWidget(self.label_width_krep)
        krepi_layout.addWidget(self.line_edit_width_krep)
        krepi_layout.addWidget(self.button_add_krep)

        layout.addLayout(top_panel_layout)
        layout.addLayout(krepi_layout)
        layout.addLayout(graph_panel_layout)
        layout.addWidget(self.canvas)

        # виджет для размещения компоновки
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.final_Y = 0
        self.check_first = 0

        # Инициализация переменных
        self.is_width_locked = False
        self.auto_save_enabled = False
        self.net_enabled = False

        # Создание книги Excel и листа
        self.workbook = openpyxl.Workbook()
        self.sheet = self.workbook.active
        self.current_partitions = []
        # Заголовки столбцов в Excel
        self.sheet.cell(row=1, column=1).value = "Номер разбиения"
        self.sheet.cell(row=1, column=2).value = "Номер подразбиения"
        self.sheet.cell(row=1, column=3).value = "Название"
        self.sheet.cell(row=1, column=4).value = "Плотность"
        self.sheet.cell(row=1, column=5).value = "Толщина"
        self.sheet.cell(row=1, column=6).value = "Цвет"

        # Добавление обработчиков событий мыши на FigureCanvas
        self.canvas.mpl_connect("button_press_event", self.on_mouse_press)
        self.canvas.mpl_connect("motion_notify_event", self.on_motion_notify)
        self.canvas.mpl_connect("button_release_event", self.on_mouse_release)
        self.canvas.mpl_connect('scroll_event', self.on_scroll)

        self.first_coordinate_line_y = 0
        self.horizontal_lines = []  # Список координат горизонтальных линий
        self.vertical_lines = []  # Список координат вертикальных линий


        self.info_krep = []

        self.first_line_horizontal_check = True
        self.first_line_vertical_check = True

        self.dragging = False
        self.x_grid_edit = 0
        self.y_grid_edit = 0
        self.current_x = 0
        self.current_y = 0

        self.pressed = False
        self.prev_x = None
        self.prev_y = None
        self.translation_factor = 0.005  # Коэффициент перемещения
        self.current_x_lim = None
        self.current_y_lim = None

        self.krep_coordinate = []
        self.index_edit_triangle = []



    def thread_auto_part(self):
        # Создаем объект Thread и передаем целевой метод
        thread_auto_part = threading.Thread(target=self.auto_part)

        # Запускаем поток
        thread_auto_part.start()

        # Ждем, пока поток завершится (опционально)
        thread_auto_part.join()

    def wait(self):
        msg_wait = QMessageBox()
        msg_wait.setText("Выполнение")
        # msg.setIcon(QMessageBox.Warning)
        #msg_wait.exec_()

    def auto_part(self):
        if self.info_layers:
            if (self.line_edit_part.text()).isdigit():
                height = int(self.line_edit_part.text())

            else:
                msg = QMessageBox()
                msg.setWindowTitle("Ошибка")
                msg.setText("Для начала постройте слои!")
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()
                return
            distance, ok = QInputDialog.getDouble(self, "Расстояние разбиения", "Расстояние:")
            if not ok:
                return
            full_height = abs(self.info_layers[0]['y0']) + abs(self.info_layers[len(self.info_layers) - 1]['y1'])
            full_width = abs(self.info_layers[0]['x0']) + abs(self.info_layers[len(self.info_layers) - 1]['x1'])
            if ok:
                height_sum = sum(partition['thickness'] for partition in self.current_partitions)
                ylim = height_sum
                x = 0
                y = self.first_coordinate_line_y
                self.total_iterations = int(ylim) + int(height)
                for i in range(int(ylim)):
                    if self.first_line_horizontal_check == True:
                        if self.info_krep:
                            info_krep = self.info_krep[0]
                            line_info = {
                                'x0': 0,
                                'x1': height,
                                'y0': info_krep['point8_y'],
                                'y1': info_krep['point8_y']
                            }
                            self.horizontal_lines.append(line_info)
                            # Рисование линии по всей ширине графика
                            self.axes.plot([0, height], [info_krep['point8_y'],
                                                         info_krep['point8_y']], color='red')
                            line_info = {
                                'x0': 0,
                                'x1': height,
                                'y0': info_krep['point1_y'],
                                'y1': info_krep['point1_y']
                            }
                            self.horizontal_lines.append(line_info)
                            # Рисование линии по всей ширине графика
                            self.axes.plot([0, height], [info_krep['point1_y'],
                                                         info_krep['point1_y']], color='red')
                        line_info = {
                            'x0': 0,
                            'x1': height,
                            'y0': self.first_coordinate_line_y,
                            'y1': self.first_coordinate_line_y
                        }
                        self.horizontal_lines.append(line_info)
                        # Рисование линии по всей ширине графика
                        self.axes.plot([0, height], [self.first_coordinate_line_y, self.first_coordinate_line_y],
                                       color='red')
                        line_info = {
                            'x0': 0,
                            'x1': height,
                            'y0': self.first_coordinate_line_y + ylim,
                            'y1': self.first_coordinate_line_y + ylim
                        }
                        self.horizontal_lines.append(line_info)
                        # Рисование линии по всей ширине графика
                        self.axes.plot([0, height],
                                       [self.first_coordinate_line_y + ylim, self.first_coordinate_line_y + ylim],
                                       color='red')
                        self.first_line_horizontal_check = False
                    if y + distance <= full_height:
                        line_info = {
                            'x0': 0,
                            'x1': height,
                            'y0': y,
                            'y1': y
                        }
                        self.horizontal_lines.append(line_info)
                        # Рисование линии по всей ширине графика
                        self.axes.plot([0, height], [y, y], color='red')
                        #self.canvas.draw()

                        y += distance
                    # self.progress_dialog.setValue(i)  # текущее значение прогресс-бара
                    # app.processEvents()  # Обновление интерфейса
                    #
                    # if self.progress_dialog.wasCanceled():
                    #     # Действие при отмене
                    #     break



                for i in range(height):
                    if self.first_line_vertical_check == True:
                        if self.info_krep:
                            for index, info_krep in enumerate(self.info_krep):
                                for i in range(4):
                                    key = 'point{}_x'.format(i + 1)
                                    line_info = {
                                        'x0': info_krep[key],
                                        'x1': info_krep[key],
                                        'y0': self.first_coordinate_line_y,
                                        'y1': self.first_coordinate_line_y + ylim
                                    }
                                    self.vertical_lines.append(line_info)
                                    # Рисование линии по всей ширине графика
                                    self.axes.plot([info_krep[key], info_krep[key]],
                                                   [self.first_coordinate_line_y, self.first_coordinate_line_y + ylim],
                                                   color='blue')
                        line_info = {
                            'x0': 0,
                            'x1': 0,
                            'y0': self.first_coordinate_line_y,
                            'y1': self.first_coordinate_line_y + ylim
                        }
                        self.vertical_lines.append(line_info)
                        # Рисование линии по всей ширине графика
                        self.axes.plot([0, 0], [self.first_coordinate_line_y, self.first_coordinate_line_y + ylim],
                                       color='blue')
                        line_info = {
                            'x0': height,
                            'x1': height,
                            'y0': self.first_coordinate_line_y,
                            'y1': self.first_coordinate_line_y + ylim
                        }
                        self.vertical_lines.append(line_info)
                        # Рисование линии по всей ширине графика
                        self.axes.plot([height, height],
                                       [self.first_coordinate_line_y, self.first_coordinate_line_y + ylim],
                                       color='blue')
                        self.first_line_vertical_check = False
                    if x + distance <= full_width:
                        line_info = {
                            'x0': x,
                            'x1': x,
                            'y0': self.first_coordinate_line_y,
                            'y1': self.first_coordinate_line_y + ylim
                        }
                        self.vertical_lines.append(line_info)
                        # Рисование линии по всей ширине графика
                        self.axes.plot([x, x], [self.first_coordinate_line_y, self.first_coordinate_line_y + ylim],
                                       color='blue')
                        x += distance
                #     self.progress_dialog.setValue(i)  # Установите текущее значение прогресс-бара
                #     app.processEvents()  # Обновление интерфейса
                #
                #     if self.progress_dialog.wasCanceled():
                #         # Действие при отмене
                #         break
                # self.progress_dialog.close()
                self.canvas.draw()

        else:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка")
            msg.setText("Возникли проблемы со слоями!")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def on_mouse_press(self, event):
        if event.button == MouseButton.MIDDLE:
            self.pressed = True
            self.prev_x = event.x
            self.prev_y = event.y
        if self.radio_edit.isChecked() and event.button == MouseButton.LEFT:
            x = round(event.xdata, 1)
            y = round(event.ydata, 1)
            self.index_edit_triangle = []
            if float(self.line_edit_part.text()) > 500:
                radius = 0.1
                x = round(event.xdata, 1)
                y = round(event.ydata, 1)
            else:
                radius = 0.1
                x = round(event.xdata, 1)
                y = round(event.ydata, 1)
            for index, coordinate in enumerate(self.triangle_coordinates):
                if float(self.line_edit_part.text()) > 500:
                    x0 = round(coordinate['x0'],1)
                    x1 = round(coordinate['x1'],1)
                    x2 = round(coordinate['x2'],1)
                    y0 = round(coordinate['y0'],1)
                    y1 = round(coordinate['y1'],1)
                    y2 = round(coordinate['y2'],1)
                else:
                    x0 = round(coordinate['x0'], 1)
                    x1 = round(coordinate['x1'], 1)
                    x2 = round(coordinate['x2'], 1)
                    y0 = round(coordinate['y0'], 1)
                    y1 = round(coordinate['y1'], 1)
                    y2 = round(coordinate['y2'], 1)
                if (x == x0 or x == x1 or x == x2 or x == x0+radius or x == x1+radius or x == x2+radius or x == x0-radius or x == x1-radius or x == x2-radius) and (y == y0 or y == y1 or y == y2 or y == y0+radius or y == y1+radius or y == y2+radius or y == y0-radius or y == y1-radius or y == y2-radius):
                    self.dragging = True
                    self.x_grid_edit = x
                    self.y_grid_edit = y
                    self.index_edit_triangle.append(index)
        if self.radio_krep.isChecked() and self.rectangles and event.button == MouseButton.LEFT:
            result = self.collection_krepi.find({'Название': str(self.combobox_krep.currentText())})
            image_data = None
            long = None
            for doc in result:
                image_data = doc['Изображение']
                long = doc['Козырек длина']
                height = doc['Высота']
                point1_x = (doc['Точка в.л.у'])[0]
                point1_y = (doc['Точка в.л.у'])[1]
                point2_x = (doc['Точка в.л.у.2'])[0]
                point2_y = (doc['Точка в.л.у.2'])[1]
                point3_x = (doc['Точка в.п.у'])[0]
                point3_y = (doc['Точка в.п.у'])[1]
                point4_x = (doc['Точка в.п.у.2'])[0]
                point4_y = (doc['Точка в.п.у.2'])[1]
                point5_x = (doc['Точка н.л.у'])[0]
                point5_y = (doc['Точка н.л.у'])[1]
                point6_x = (doc['Точка н.л.у.2'])[0]
                point6_y = (doc['Точка н.л.у.2'])[1]
                point7_x = (doc['Точка н.п.у'])[0]
                point7_y = (doc['Точка н.п.у'])[1]
                point8_x = (doc['Точка н.п.у.2'])[0]
                point8_y = (doc['Точка н.п.у.2'])[1]

            layer = self.info_layers[0]

            img = Image.open(io.BytesIO(image_data))
            img = img.convert('RGBA')
            x1 = event.xdata
            x = x1+long
            y1 = layer['y0']
            y = layer['y1']
            edit_height = abs(abs(y1)-abs(y) - height)
            y1_edit = y1 - edit_height

            point1_x += x1
            point1_y += y1_edit
            point2_x += x1
            point2_y += y1_edit
            point3_x += x1
            point3_y += y1_edit
            point4_x += x1
            point4_y += y1_edit
            point5_x += x1
            point5_y += y1
            point6_x += x1
            point6_y += y1
            point7_x += x1
            point7_y += y1
            point8_x += x1
            point8_y += y1

            coordinate_info = {
                'название':str(self.combobox_krep.currentText()),
                'x1':x1,
                'x':x,
                'y1':y1,
                'y':y,
                'image':img,
                'point1_x': point1_x,
                'point1_y': point1_y,
                'point2_x': point2_x,
                'point2_y': point2_y,
                'point3_x': point3_x,
                'point3_y': point3_y,
                'point4_x': point4_x,
                'point4_y': point4_y,
                'point5_x': point5_x,
                'point5_y': point5_y,
                'point6_x': point6_x,
                'point6_y': point6_y,
                'point7_x': point7_x,
                'point7_y': point7_y,
                'point8_x': point8_x,
                'point8_y': point8_y,
            }
            self.info_krep.append(coordinate_info)
            self.axes.imshow(img, extent=([x1, x, y1, y]), aspect='equal', zorder=10)
            x_min, x_max = self.current_x_lim
            y_min, y_max = self.current_y_lim

            self.figure.tight_layout()
            self.axes.set_aspect('auto')
            self.canvas.draw()


        else:
            if self.info_layers:
                # Обработка нажатия кнопки мыши
                if event.button == 1:  # Левая кнопка мыши
                    x = event.xdata
                    y = event.ydata
                    if x is not None and y is not None:
                        if (self.line_edit_part.text()).isdigit():
                            height = int(self.line_edit_part.text())
                        else:
                            msg = QMessageBox()
                            msg.setWindowTitle("Ошибка")
                            msg.setText("Для начала постройте слои!")
                            msg.setIcon(QMessageBox.Warning)
                            msg.exec_()
                            return
                        height_sum = sum(partition['thickness'] for partition in self.current_partitions)
                        ylim = height_sum
                        if self.radio_horizontal.isChecked():
                            if self.first_line_horizontal_check == True:
                                if self.info_krep:
                                    info_krep = self.info_krep[0]
                                    line_info = {
                                        'x0': 0,
                                        'x1': height,
                                        'y0': info_krep['point8_y'],
                                        'y1': info_krep['point8_y']
                                    }
                                    self.horizontal_lines.append(line_info)
                                    # Рисование линии по всей ширине графика
                                    self.axes.plot([0, height], [info_krep['point8_y'],
                                                                 info_krep['point8_y']], color='red')
                                    line_info = {
                                        'x0': 0,
                                        'x1': height,
                                        'y0': info_krep['point1_y'],
                                        'y1': info_krep['point1_y']
                                    }
                                    self.horizontal_lines.append(line_info)
                                    # Рисование линии по всей ширине графика
                                    self.axes.plot([0, height], [info_krep['point1_y'],
                                                                 info_krep['point1_y']], color='red')

                                line_info = {
                                    'x0': 0,
                                    'x1': height,
                                    'y0': self.first_coordinate_line_y + ylim,
                                    'y1': self.first_coordinate_line_y + ylim
                                }
                                self.horizontal_lines.append(line_info)
                                # Рисование линии по всей ширине графика
                                self.axes.plot([0, height], [self.first_coordinate_line_y + ylim,
                                                             self.first_coordinate_line_y + ylim], color='red')
                                for layer in self.info_layers:
                                    line_info = {
                                        'x0': 0,
                                        'x1': height,
                                        'y0': layer['y0'],
                                        'y1': layer['y0']
                                    }
                                    self.horizontal_lines.append(line_info)
                                    # Рисование линии по всей ширине графика
                                    self.axes.plot([0, height], [layer['y0'], layer['y0']], color='red')
                                self.first_line_horizontal_check = False

                            line_info = {
                                'x0': 0,
                                'x1': height,
                                'y0': y,
                                'y1': y
                            }
                            self.horizontal_lines.append(line_info)
                            # Рисование линии по всей ширине графика
                            self.axes.plot([0, height], [y, y], color='red')
                            self.canvas.draw()

                        if self.radio_vertical.isChecked():
                            if self.first_line_vertical_check == True:
                                if self.info_krep:
                                    for index, info_krep in enumerate(self.info_krep):
                                        for i in range(4):
                                            key = 'point{}_x'.format(i+1)
                                            line_info = {
                                                'x0': info_krep[key],
                                                'x1': info_krep[key],
                                                'y0': self.first_coordinate_line_y,
                                                'y1': self.first_coordinate_line_y + ylim
                                            }
                                            self.vertical_lines.append(line_info)
                                            # Рисование линии по всей ширине графика
                                            self.axes.plot([info_krep[key], info_krep[key]],
                                                           [self.first_coordinate_line_y, self.first_coordinate_line_y + ylim],
                                                           color='blue')

                                line_info = {
                                    'x0': 0,
                                    'x1': 0,
                                    'y0': self.first_coordinate_line_y,
                                    'y1': self.first_coordinate_line_y + ylim
                                }
                                self.vertical_lines.append(line_info)
                                # Рисование линии по всей ширине графика
                                self.axes.plot([0, 0],
                                               [self.first_coordinate_line_y, self.first_coordinate_line_y + ylim],
                                               color='blue')
                                line_info = {
                                    'x0': height,
                                    'x1': height,
                                    'y0': self.first_coordinate_line_y,
                                    'y1': self.first_coordinate_line_y + ylim
                                }
                                self.vertical_lines.append(line_info)
                                # Рисование линии по всей ширине графика
                                self.axes.plot([height, height],
                                               [self.first_coordinate_line_y, self.first_coordinate_line_y + ylim],
                                               color='blue')
                                self.first_line_vertical_check = False

                            line_info = {
                                'x0': x,
                                'x1': x,
                                'y0': self.first_coordinate_line_y,
                                'y1': self.first_coordinate_line_y + ylim
                            }
                            self.vertical_lines.append(line_info)
                            # Рисование линии по всей ширине графика
                            self.axes.plot([x, x], [self.first_coordinate_line_y, self.first_coordinate_line_y + ylim],
                                           color='blue')

                            self.canvas.draw()
                        pass
                    else:
                        msg = QMessageBox()
                        msg.setWindowTitle("Ошибка")
                        msg.setText("Возникли проблемы со слоями!")
                        msg.setIcon(QMessageBox.Warning)
                        msg.exec_()

    def on_scroll(self, event):
        if event.button == 'up':
            # Увеличение масштаба при прокрутке вверх
            self.current_x_lim = [self.axes.get_xlim()[0] * 0.9, self.axes.get_xlim()[1] * 0.9]
            self.current_y_lim = [self.axes.get_ylim()[0] * 0.9, self.axes.get_ylim()[1] * 0.9]
            self.axes.set_xlim(self.axes.get_xlim()[0] * 0.9, self.axes.get_xlim()[1] * 0.9)
            self.axes.set_ylim(self.axes.get_ylim()[0] * 0.9, self.axes.get_ylim()[1] * 0.9)
        elif event.button == 'down':
            # Уменьшение масштаба при прокрутке вниз
            self.current_x_lim = [self.axes.get_xlim()[0] * 1.1, self.axes.get_xlim()[1] * 1.1]
            self.current_y_lim = [self.axes.get_ylim()[0] * 1.1, self.axes.get_ylim()[1] * 1.1]
            self.axes.set_xlim(self.axes.get_xlim()[0] * 1.1, self.axes.get_xlim()[1] * 1.1)
            self.axes.set_ylim(self.axes.get_ylim()[0] * 1.1, self.axes.get_ylim()[1] * 1.1)

        # Restore the cached background
        self.canvas.restore_region(self.background)

        # Redraw the updated canvas
        self.canvas.blit(self.axes.bbox)
        self.canvas.draw()

    def on_motion_notify(self, event):
        if event.xdata is not None:
            self.label_coordinate.setText(f'Координаты: x {round(event.xdata,2)} y {round(event.ydata,2)}')
        if self.pressed:
            dx = (event.x - self.prev_x) * self.translation_factor
            dy = (event.y - self.prev_y) * self.translation_factor
            self.current_x_lim = [self.axes.get_xlim()[0] - dx, self.axes.get_xlim()[1] - dx]
            self.current_y_lim = [self.axes.get_ylim()[0] + dy, self.axes.get_ylim()[1] + dy]
            self.axes.set_xlim(self.axes.get_xlim()[0] - dx, self.axes.get_xlim()[1] - dx)
            self.axes.set_ylim(self.axes.get_ylim()[0] + dy, self.axes.get_ylim()[1] + dy)
            self.prev_x = event.x
            self.prev_y = event.y
            self.canvas.draw()
        if self.radio_edit.isChecked() and self.dragging == True:

            x = event.xdata
            y = event.ydata
            x_grid_edit = self.x_grid_edit
            y_grid_edit = self.y_grid_edit
            if float(self.line_edit_part.text()) > 500:
                radius = 0.1
                y_grid_edit = round(y_grid_edit,1)
                x_grid_edit = round(x_grid_edit,1)

            else:
                radius = 0.1
                y_grid_edit = round(y_grid_edit, 1)
                x_grid_edit = round(x_grid_edit, 1)
            for index in self.index_edit_triangle:
                triangle = self.triangle_coordinates[index]
                if float(self.line_edit_part.text()) > 500:
                    x0 = round(triangle['x0'],1)
                    x1 = round(triangle['x1'],1)
                    x2 = round(triangle['x2'],1)
                    y0 = round(triangle['y0'],1)
                    y1 = round(triangle['y1'],1)
                    y2 = round(triangle['y2'],1)
                else:
                    x0 = round(triangle['x0'], 1)
                    x1 = round(triangle['x1'], 1)
                    x2 = round(triangle['x2'], 1)
                    y0 = round(triangle['y0'], 1)
                    y1 = round(triangle['y1'], 1)
                    y2 = round(triangle['y2'], 1)
                if (y0 == y_grid_edit and x0 == x_grid_edit) or (y0 == y_grid_edit+radius and x0 == x_grid_edit+radius) or (y0 == y_grid_edit-radius and x0 == x_grid_edit-radius) or (y0 == y_grid_edit-radius and x0 == x_grid_edit+radius) or (y0 == y_grid_edit+radius and x0 == x_grid_edit-radius):
                    triangle['y0'] = y
                    triangle['x0'] = x
                    self.y_grid_edit = y
                    self.x_grid_edit = x

                if (y1 == y_grid_edit and x1 == x_grid_edit) or (y1 == y_grid_edit+radius and x1 == x_grid_edit+radius) or (y1 == y_grid_edit-radius and x1 == x_grid_edit-radius) or (y1 == y_grid_edit-radius and x1 == x_grid_edit+radius) or (y1 == y_grid_edit+radius and x1 == x_grid_edit-radius):
                    triangle['y1'] = y
                    triangle['x1'] = x
                    self.y_grid_edit = y
                    self.x_grid_edit = x

                if (y2 == y_grid_edit and x2 == x_grid_edit) or (y2 == y_grid_edit+radius and x2 == x_grid_edit+radius) or (y2 == y_grid_edit-radius and x2 == x_grid_edit-radius) or (y2 == y_grid_edit-radius and x2 == x_grid_edit+radius) or (y2 == y_grid_edit+radius and x2 == x_grid_edit-radius):
                    triangle['y2'] = y
                    triangle['x2'] = x
                    self.y_grid_edit = y
                    self.x_grid_edit = x

            for index in self.index_edit_triangle:
                triangle = self.triangle_coordinates[index]
                x = [triangle['x0'], triangle['x1'], triangle['x2']]
                y = [triangle['y0'], triangle['y1'], triangle['y2']]
                line = self.axes.lines[index]
                line.set_data(x + [x[0]], y + [y[0]])

                # Перерисовать только измененную линию или точку
                self.axes.draw_artist(line)
            self.canvas.blit(self.axes.bbox)
            self.canvas.draw()

    def on_mouse_release(self, event):
        if event.button == MouseButton.MIDDLE:
            self.pressed = False
        self.dragging = False

    def toggle_auto_save(self, state):
        self.auto_save_enabled = state == Qt.Checked
        self.button_save.setEnabled(self.auto_save_enabled)

    def toggle_vertical_line(self, checked):
        return

    def toggle_krep(self, checked):
        return

    def toggle_horizontal_line(self, checked):
        return

    def toggle_edit(self, checked):
        return

    def add_krep(self):
        self.line_edit_part.setReadOnly(True)
        if self.info_layers:
            all_width = float(self.line_edit_part.text())
            distance = float(self.line_edit_width_krep.text())
            coordinate_x1_distance = 0
            while coordinate_x1_distance < all_width:
                result = self.collection_krepi.find({'Название': str(self.combobox_krep.currentText())})
                image_data = None
                long = None
                for doc in result:
                    image_data = doc['Изображение']
                    long = doc['Козырек длина']
                    height = doc['Высота']
                    point1_x = (doc['Точка в.л.у'])[0]
                    point1_y = (doc['Точка в.л.у'])[1]
                    point2_x = (doc['Точка в.л.у.2'])[0]
                    point2_y = (doc['Точка в.л.у.2'])[1]
                    point3_x = (doc['Точка в.п.у'])[0]
                    point3_y = (doc['Точка в.п.у'])[1]
                    point4_x = (doc['Точка в.п.у.2'])[0]
                    point4_y = (doc['Точка в.п.у.2'])[1]
                    point5_x = (doc['Точка н.л.у'])[0]
                    point5_y = (doc['Точка н.л.у'])[1]
                    point6_x = (doc['Точка н.л.у.2'])[0]
                    point6_y = (doc['Точка н.л.у.2'])[1]
                    point7_x = (doc['Точка н.п.у'])[0]
                    point7_y = (doc['Точка н.п.у'])[1]
                    point8_x = (doc['Точка н.п.у.2'])[0]
                    point8_y = (doc['Точка н.п.у.2'])[1]

                layer = self.info_layers[0]

                img = Image.open(io.BytesIO(image_data))
                img = img.convert('RGBA')
                x1 = coordinate_x1_distance
                x = x1 + long
                y1 = layer['y0']
                y = layer['y1']
                edit_height = abs(abs(y1) - abs(y) - height)
                y1_edit = y1 - edit_height

                point1_x += x1
                point1_y += y1_edit
                point2_x += x1
                point2_y += y1_edit
                point3_x += x1
                point3_y += y1_edit
                point4_x += x1
                point4_y += y1_edit
                point5_x += x1
                point5_y += y1
                point6_x += x1
                point6_y += y1
                point7_x += x1
                point7_y += y1
                point8_x += x1
                point8_y += y1

                coordinate_info = {
                    'название': str(self.combobox_krep.currentText()),
                    'x1': x1,
                    'x': x,
                    'y1': y1,
                    'y': y,
                    'image': img,
                    'point1_x': point1_x,
                    'point1_y': point1_y,
                    'point2_x': point2_x,
                    'point2_y': point2_y,
                    'point3_x': point3_x,
                    'point3_y': point3_y,
                    'point4_x': point4_x,
                    'point4_y': point4_y,
                    'point5_x': point5_x,
                    'point5_y': point5_y,
                    'point6_x': point6_x,
                    'point6_y': point6_y,
                    'point7_x': point7_x,
                    'point7_y': point7_y,
                    'point8_x': point8_x,
                    'point8_y': point8_y,
                }
                self.info_krep.append(coordinate_info)
                self.axes.imshow(img, extent=([x1, x, y1, y]), aspect='equal', zorder=10)
                x_min, x_max = self.current_x_lim
                y_min, y_max = self.current_y_lim
                self.axes.set_xlim([x_min, x_max])
                self.axes.set_ylim(
                    [y_min+(x_max/2), y_max+(x_max/2)])
                coordinate_x1_distance += distance + long
            self.figure.tight_layout()
            self.axes.set_aspect('auto')
            self.canvas.draw()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка")
            msg.setText("Возникли проблемы со слоями!")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

    def add_layer(self):
        rect_name = self.combobox_layer.currentText()

        self.info_krep = []
        self.horizontal_lines = []
        self.vertical_lines = []
        self.triangle_coordinates = []
        self.first_line_horizontal_check = True
        self.first_line_vertical_check = True
        self.current_x_lim = [self.axes.get_xlim()[0] * 0.9, self.axes.get_xlim()[1] * 0.9]
        self.current_y_lim = [self.axes.get_ylim()[0] * 0.9, self.axes.get_ylim()[1] * 0.9]
        if (self.line_edit_thickness.text()).isdigit():
            height = float(self.line_edit_thickness.text())
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка")
            msg.setText("Некорректное значение")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return
        if (self.line_edit_part.text()).isdigit():
            width = float(self.line_edit_part.text())
            self.line_edit_part.setReadOnly(True)
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка")
            msg.setText("Некорректное значение")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return
        rr = self.combobox_layer.currentText()
        result = self.collection_density.find({'Породы': str(self.combobox_layer.currentText())})
        rect_color = None
        density = None
        for doc in result:
            density = doc['Плотность']
            rect_color = doc['Цвет']
        self.label_density.setText(f'Плотность: {density}')

        if self.check_first != 0:
            x = 0
            y = self.final_Y
            self.final_Y = y + height
        if self.check_first == 0:
            x = 0
            y = 0 - height
            self.check_first += 1
            self.first_coordinate_line_y = y

        rect = patches.Rectangle((x, y), width, height, facecolor=rect_color)
        rect.set_label(rect_name)
        self.rectangles.append(rect)
        self.draw_layer()

        if float(self.line_edit_part.text()) == 1:
            self.button_save.setEnabled(True)

        # Добавление информации о слое в текущее разбиение
        current_partition = {
            'name': rect_name,
            'density': density,
            'thickness': height,
            'color': rect_color
        }
        self.current_partitions.append(current_partition)
        layer_info = {
            'name': rect_name,
            'x0': x,
            'y0': y,
            'x1': x + width,
            'y1': y + height,
            'color': rect_color,
            'density': density
        }
        self.info_layers.append(layer_info)

    def undo_action(self):
        if self.rectangles:
            self.info_krep = []
            self.rectangles.pop()
            self.draw_layer()
            self.final_Y = self.final_Y - float(self.line_edit_thickness.text())
            self.current_partitions.pop()
            self.horizontal_lines = []
            self.vertical_lines = []
            self.triangle_coordinates = []
            self.first_line_horizontal_check = True
            self.first_line_vertical_check = True

    def draw_layer(self):
        if self.radio_edit.isChecked():
            self.axes.clear()
            for index, info_krep in enumerate(self.info_krep):
                self.axes.imshow(info_krep['image'], extent=([info_krep['x1'], info_krep['x'], info_krep['y1'], info_krep['y']]), aspect='equal', zorder=10)
            for rect in self.rectangles:
                self.axes.add_patch(rect)
                self.axes.annotate(rect.get_label(),
                                   (rect.get_x() + rect.get_width() / 2, rect.get_y() + rect.get_height() / 2),
                                   ha='center', va='center')
            x_min, x_max = self.current_x_lim
            y_min, y_max = self.current_y_lim
            self.axes.set_xlim([x_min, x_max])
            self.axes.set_ylim(
                [y_min, y_max])
            self.figure.tight_layout()
            self.axes.set_aspect('auto')
            # self.axes.autoscale(enable=False, axis='both')
            self.canvas.draw()
        if not self.radio_edit.isChecked():
            self.axes.clear()
            for rect in self.rectangles:
                self.axes.add_patch(rect)
                self.axes.annotate(rect.get_label(),
                                   (rect.get_x() + rect.get_width() / 2, rect.get_y() + rect.get_height() / 2),
                                   ha='center', va='center')
            self.current_x_lim = [0, float(self.line_edit_part.text())]
            self.current_y_lim = [0 - float(self.line_edit_thickness.text()) * 2,
                                  self.final_Y + float(self.line_edit_thickness.text())]
            self.axes.set_xlim([0, float(self.line_edit_part.text())])
            self.axes.set_ylim(
                [0 - float(self.line_edit_thickness.text()) * 2, self.final_Y + float(self.line_edit_thickness.text())])
            self.figure.tight_layout()
            self.axes.set_aspect('auto')
            self.canvas.draw()


    def save_partitions(self):
        if self.save_current_partition():
            self.save_current_partition()  # Сохранение информации о последнем разбиении
            file_name, _ = QFileDialog.getSaveFileName(self, "Сохранить разбиения", "", "Excel Files (*.xlsx)")
            if file_name:
                self.workbook.save(file_name)
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка")
            msg.setText("Сохранение невозможно")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

    def create_grid(self):
        if self.vertical_lines and self.horizontal_lines:
            self.vertical_lines = sorted(self.vertical_lines, key=lambda line: line['x0'])
            self.horizontal_lines = sorted(self.horizontal_lines, key=lambda line: line['y0'])

            vert_wall = []
            horiz_wall = []

            first_w = 0
            x_pred = 0

            for line_vertical in self.vertical_lines:

                x1_vert = line_vertical['x1']

                if first_w == 0:
                    x_pred = x1_vert
                    first_w += 1
                    continue
                if first_w > 0:
                    vert_wall.append([x_pred, x1_vert])
                    x_pred = x1_vert
                    continue
                first_w += 1

            first_w = 0

            for line_horizontal in self.horizontal_lines:

                y1_hor = line_horizontal['y1']

                if first_w == 0:
                    y_pred = y1_hor
                    first_w += 1
                    continue
                if first_w > 0:
                    horiz_wall.append([y_pred, y1_hor])
                    y_pred = y1_hor
                    continue
                first_w += 1

            all_coordinates = []
            for line_horizontal in horiz_wall:
                for line_vertical in vert_wall:
                    all_coordinates.append([line_horizontal[0], line_vertical[0], line_horizontal[1], line_vertical[1]])
            self.draw_triangles(all_coordinates)

        else:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка")
            msg.setText("Возникли проблемы со линиями сетки!")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def draw_triangles(self, all_coordinates):
        number_triangle = 0
        for coordinates in all_coordinates:
            number_triangle += 1
            triangle_info = {
                'number': number_triangle,
                'x0': coordinates[1],
                'x1': coordinates[3],
                'x2': coordinates[1],
                'y0': coordinates[0],
                'y1': coordinates[2],
                'y2': coordinates[2],

            }
            number_triangle += 1
            self.triangle_coordinates.append(triangle_info)
            triangle_info = {
                'number': number_triangle,
                'x0': coordinates[1],
                'x1': coordinates[3],
                'x2': coordinates[3],
                'y0': coordinates[0],
                'y1': coordinates[2],
                'y2': coordinates[0],

            }
            self.triangle_coordinates.append(triangle_info)
        self.draw_layer()
        # self.canvas.draw()
        info_krep_images = []
        for index, info_krep in enumerate(self.info_krep):
            info_krep_images.append(info_krep['image'])
            self.axes.imshow(info_krep['image'],
                             extent=([info_krep['x1'], info_krep['x'], info_krep['y1'], info_krep['y']]),
                             aspect='equal', zorder=10)

        for index, triangle in enumerate(self.triangle_coordinates):
            x_coords = [triangle['x0'], triangle['x1'], triangle['x2']]
            y_coords = [triangle['y0'], triangle['y1'], triangle['y2']]
            self.axes.plot(x_coords + [x_coords[0]], y_coords + [y_coords[0]], color='red', zorder=11)

        self.figure.tight_layout()
        self.axes.set_aspect('auto')
        self.canvas.draw()



    def save_current_partition(self):
        if (self.line_edit_part.text()).isdigit():
            partition_number = int(float(self.line_edit_part.text()))
            if self.auto_save_enabled:
                real_row = 1
                for row in range(partition_number):
                    for i, partition in enumerate(self.current_partitions):

                        if float(partition['thickness']) > float(self.line_edit_width.text()):
                            for j in range(round(float(partition['thickness']) / float(self.line_edit_width.text()))):
                                self.sheet.cell(row=real_row, column=1).value = row + 1
                                self.sheet.cell(row=real_row, column=2).value = j
                                self.sheet.cell(row=real_row, column=3).value = partition['name']
                                self.sheet.cell(row=real_row, column=4).value = partition['density']
                                self.sheet.cell(row=real_row, column=5).value = str(float(self.line_edit_width.text()))
                                self.sheet.cell(row=real_row, column=6).value = partition['color']
                                real_row += 1
                        else:
                            self.sheet.cell(row=real_row, column=1).value = row + 1
                            self.sheet.cell(row=real_row, column=2).value = i
                            self.sheet.cell(row=real_row, column=3).value = partition['name']
                            self.sheet.cell(row=real_row, column=4).value = partition['density']
                            self.sheet.cell(row=real_row, column=5).value = partition['thickness']
                            self.sheet.cell(row=real_row, column=6).value = partition['color']
                        real_row += 1

            else:
                for i, partition in enumerate(self.current_partitions):
                    row = i + (partition_number - 1) * len(self.current_partitions) + 2
                    if float(partition['thickness']) > float(self.line_edit_width.text()):
                        for j in range(round(float(partition['thickness']) / float(self.line_edit_width.text()))):
                            self.sheet.cell(row=row, column=1).value = partition_number
                            self.sheet.cell(row=row, column=2).value = j
                            self.sheet.cell(row=row, column=3).value = partition['name']
                            self.sheet.cell(row=row, column=4).value = partition['density']
                            self.sheet.cell(row=row, column=5).value = str(float(self.line_edit_width.text()))
                            self.sheet.cell(row=row, column=6).value = partition['color']
                            row += 1
                    else:
                        self.sheet.cell(row=row, column=1).value = partition_number
                        self.sheet.cell(row=row, column=2).value = i
                        self.sheet.cell(row=row, column=3).value = partition['name']
                        self.sheet.cell(row=row, column=4).value = partition['density']
                        self.sheet.cell(row=row, column=5).value = partition['thickness']
                        self.sheet.cell(row=row, column=6).value = partition['color']
                self.current_partitions = []
            return True
        else:
            return False

class Save:
    def save_grid_information(self, triangle_coordinates, info_layers):
        if triangle_coordinates:
            # self.vertical_lines = sorted(self.vertical_lines, key=lambda line: line['x0'])
            # self.horizontal_lines = sorted(self.horizontal_lines, key=lambda line: line['y0'])
            #
            # vert_wall = []
            # horiz_wall = []
            #
            #
            #
            # first_w = 0
            # x_pred = 0
            #
            # for line_vertical in self.vertical_lines:
            #
            #     x1_vert = line_vertical['x1']
            #
            #     if first_w == 0:
            #
            #         x1_cell = x1_vert
            #         x_pred = x1_vert
            #         first_w += 1
            #         continue
            #     if first_w > 0:
            #         vert_wall.append([x_pred, x1_vert])
            #         x_pred = x1_vert
            #         continue
            #     first_w += 1
            #
            # first_w = 0
            # x_pred = 0
            #
            # for line_horizontal in self.horizontal_lines:
            #
            #     y1_hor = line_horizontal['y1']
            #
            #     if first_w == 0:
            #         y_pred = y1_hor
            #         first_w += 1
            #         continue
            #     if first_w > 0:
            #         horiz_wall.append([y_pred, y1_hor])
            #         y_pred = y1_hor
            #         continue
            #     first_w += 1
            #
            # all_coordinates = []
            # for line_horizontal in horiz_wall:
            #     for line_vertical in vert_wall:
            #         all_coordinates.append([line_horizontal[0],line_vertical[0],line_horizontal[1],line_vertical[1]])

            cells = []

            # сохранение клеток
            # for layer in self.info_layers:
            #     x0_layer = layer['x0']
            #     x1_layer = layer['x1']
            #     y0_layer = layer['y0']
            #     y1_layer = layer['y1']
            #     for coordinates in all_coordinates:
            #         if coordinates[1] >= x0_layer and coordinates[0] >= y0_layer and coordinates[3] <= x1_layer and coordinates[2] <= y1_layer:
            #             cell_info = {
            #                 'name': layer['name'],
            #                 'color': layer['color'],
            #                 'x0': coordinates[1],
            #                 'x1': coordinates[3],
            #                 'y0': coordinates[0],
            #                 'y1': coordinates[2]
            #
            #             }
            #             cells.append(cell_info)

            for layer in info_layers:
                x0_layer = layer['x0']
                x1_layer = layer['x1']
                y0_layer = layer['y0']
                y1_layer = layer['y1']
                for index, coordinates in enumerate(triangle_coordinates):
                    if coordinates['x0'] >= x0_layer and coordinates['y0'] >= y0_layer and coordinates[
                        'x1'] <= x1_layer and coordinates['y1'] <= y1_layer \
                            and coordinates['x2'] >= x0_layer and coordinates['x2'] <= x1_layer and coordinates[
                        'y2'] >= y0_layer and coordinates['y2'] <= y1_layer:
                        cell_info = {
                            'name': layer['name'],
                            'color': layer['color'],
                            'x0': coordinates['x0'],
                            'x1': coordinates['x1'],
                            'x2': coordinates['x2'],
                            'y0': coordinates['y0'],
                            'y1': coordinates['y1'],
                            'y2': coordinates['y2'],
                            'density': layer['density']

                        }
                        cells.append(cell_info)

            workbook = openpyxl.Workbook()
            sheet = workbook.active

            headers = ['Name', 'Color', 'x0', 'x1', 'x2', 'y0', 'y1', 'y2','density']

            for col, header in enumerate(headers, start=1):
                sheet.cell(row=1, column=col).value = header

            for index, cell_info in enumerate(cells, start=2):
                sheet.cell(row=index, column=1).value = cell_info['name']
                sheet.cell(row=index, column=2).value = cell_info['color']
                sheet.cell(row=index, column=3).value = cell_info['x0']
                sheet.cell(row=index, column=4).value = cell_info['x1']
                sheet.cell(row=index, column=5).value = cell_info['x2']
                sheet.cell(row=index, column=6).value = cell_info['y0']
                sheet.cell(row=index, column=7).value = cell_info['y1']
                sheet.cell(row=index, column=8).value = cell_info['y2']
                sheet.cell(row=index, column=9).value = cell_info['density']

            root = Tk()
            root.withdraw()
            file_path = filedialog.asksaveasfilename(defaultextension='.xlsx')

            if file_path:

                workbook.save(file_path)
                print("Excel file saved successfully.")
            else:
                print("Save operation canceled.")

            root.destroy()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка")
            msg.setText("кажется нечего сохранять!")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
