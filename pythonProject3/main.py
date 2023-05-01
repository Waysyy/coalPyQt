import math
import sys
from tkinter import Image

import PIL
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QPushButton, QFileDialog, QMainWindow, QVBoxLayout, \
    QGraphicsScene, QGraphicsView, QComboBox, QLineEdit, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy, QRadioButton, \
    QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QInputDialog
import random

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # self.scene = QtWidgets.QGraphicsScene(self)
        #
        # self.canvas = FigureCanvas(plt.figure())

        # Set button properties

        self.pushButton_2 = QPushButton("3D График", self)
        self.pushButton_2.setMinimumSize(QtCore.QSize(0, 40))
        self.pushButton_3 = QPushButton("2D График", self)
        self.pushButton_3.setMinimumSize(QtCore.QSize(0, 40))
        self.pushButton_clear = QPushButton("Очистить", self)
        self.pushButton_clear.setMinimumSize(QtCore.QSize(0, 40))
        self.pushButton_add_layer = QPushButton("Добавить слой", self)
        self.pushButton_add_layer.setMinimumSize(QtCore.QSize(0, 40))
        self.radioButton3d = QRadioButton("3D слои", self)
        self.radioButton3d.setMaximumSize(QtCore.QSize(60, 40))
        self.radioButton2d = QRadioButton("2D слои", self)
        self.radioButton2d.setMaximumSize(QtCore.QSize(60, 40))
        self.pushButton_add_elipses = QPushButton("Круговой график", self)
        self.pushButton_add_elipses.setMinimumSize(QtCore.QSize(0, 40))
        self.pushButton_add_image = QPushButton("Добавить карту", self)
        self.pushButton_add_image.setMinimumSize(QtCore.QSize(0, 40))
        self.pushButton_calc = QPushButton("Расчитать оседание", self)
        self.pushButton_calc.setMinimumSize(QtCore.QSize(0, 40))


        # Set layout properties
        layout = QVBoxLayout()
        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.pushButton_2)
        layout_buttons.addWidget(self.pushButton_3)
        layout_buttons.addWidget(self.pushButton_clear)
        layout_buttons.addWidget(self.pushButton_add_layer)
        layout_buttons.addWidget(self.radioButton3d)
        layout_buttons.addWidget(self.radioButton2d)
        layout_buttons.addWidget(self.pushButton_add_elipses)
        layout_buttons.addWidget(self.pushButton_add_image)
        layout_buttons.addWidget(self.pushButton_calc)
        layout_buttons.setSpacing(5)  # <-- set spacing between elements to 5 pixels

        layout.addLayout(layout_buttons)

        # Set text input and combo box for adding layers
        self.label_height = QLabel("Ширина области:")
        self.textbox_height = QLineEdit()
        self.textbox_height_2 = QLineEdit()
        self.label_long = QLabel("Длина области:")
        self.textbox_long = QLineEdit()
        self.textbox_long_2 = QLineEdit()
        self.label_layer = QLabel("Название слоя:")
        self.combobox_layer = QComboBox()
        self.combobox_layer.addItems(["Почва", "Гранит", "Песчаник", "Глина", "Кварцит", "Уголь"])
        layout_input = QHBoxLayout()
        layout_input.addWidget(self.label_height)
        layout_input.addWidget(self.textbox_height)
        layout_input.addWidget(self.textbox_height_2)
        layout_input.addWidget(self.label_long)
        layout_input.addWidget(self.textbox_long)
        layout_input.addWidget(self.textbox_long_2)
        layout_input.addWidget(self.label_layer)
        layout_input.addWidget(self.combobox_layer)
        layout.addLayout(layout_input)

        # Add spacer item to push buttons to top
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Set central widget layout
        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        # Connect buttons to functions
        self.pushButton_2.clicked.connect(self.Graph3D)
        self.pushButton_3.clicked.connect(self.Graph2D)
        self.pushButton_clear.clicked.connect(self.clearGraph)
        self.pushButton_add_layer.clicked.connect(self.addLayer)
        self.pushButton_add_elipses.clicked.connect(self.GraphElips2D)
        self.pushButton_add_image.clicked.connect(self.AddImage)
        self.pushButton_calc.clicked.connect(self.CalcSubsidence)

        # Set window properties
        self.setGeometry(50, 50, 1300, 1000)
        self.setWindowTitle("MainWindow")

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setGeometry(50, 130, 1200, 800)
        self.view.setStyleSheet("background-color: white;")
        self.view.setHorizontalScrollBarPolicy(1)
        self.view.setVerticalScrollBarPolicy(1)

        self.fig = plt.Figure(figsize=(10, 5))

        # Create two subplots with 1 row and 2 columns
        self.ax2d = self.fig.add_subplot(121)
        self.ax3d = self.fig.add_subplot(122, projection='3d')

        # Adjust the spacing between the subplots
        self.fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05, wspace=0.1)

        # Create a canvas for the Figure object
        self.canvas = FigureCanvas(self.fig)
        self.scene.addWidget(self.canvas)

        # Add navigation toolbar
        toolbar = NavigationToolbar(self.canvas, self)
        self.addToolBar(toolbar)


        self.layers = []

        self.soil_height = []
        self.granite_height = []
        self.sandstone_height = []
        self.clay_height = []
        self.quartzite_height = []
        self.coal_height = []
        self.h = 0
        self.matrix = None
        self.layout_count = 0
        self.layer_at_graph = []

    button2D = 0
    button3D = 0
    def addLayer(self):
        layer_name = self.combobox_layer.currentText()
        # Get layer height from user input
        start_height, ok1 = QInputDialog.getDouble(self, "Enter Start Height", "Start Height:")
        if not ok1:
            return
        end_height, ok2 = QInputDialog.getDouble(self, "Enter End Height", "End Height:")
        if not ok2:
            return

        color = 'red'
        if layer_name == 'Почва':
            color = 'brown'
            self.layer_at_graph.append(layer_name)
            self.soil_height.append(abs(start_height-end_height))
        if layer_name == 'Гранит':
            color = 'gray'
            self.layer_at_graph.append(layer_name)
            self.granite_height.append(abs(start_height - end_height))
        if layer_name == 'Песчаник':
            color = 'yellow'
            self.layer_at_graph.append(layer_name)
            self.sandstone_height.append(abs(start_height - end_height))
        if layer_name == 'Глина':
            color = 'blue'
            self.layer_at_graph.append(layer_name)
            self.clay_height.append(abs(start_height - end_height))
        if layer_name == 'Кварцит':
            color = 'pink'
            self.layer_at_graph.append(layer_name)
            self.quartzite_height.append(abs(start_height - end_height))
        if layer_name == 'Уголь':
            color = 'black'
            self.layer_at_graph.append(layer_name)
            self.coal_height.append(abs(start_height - end_height))
        if self.radioButton2d.isChecked():


            layer_name = self.combobox_layer.currentText()
            self.layers.append((layer_name, start_height, end_height))

            # Plot all layers
            for i, layer in enumerate(self.layers):
                start, end = layer[1], layer[2]
                # Use a color from the list or repeat if necessary
                self.ax2d.axhspan(start, end,  facecolor=color, alpha=0.2)
            # Modify x-axis limits
            if self.textbox_long.text() and self.textbox_long_2.text():
                try:
                    self.ax2d.set_xlim([float(self.textbox_long.text()), float(self.textbox_long_2.text())])
                except ValueError:
                    QtWidgets.QMessageBox.critical(self, "Ошибка", "Проверьте правильность ввода координат")
                    return
            else:
                QtWidgets.QMessageBox.critical(self, "Ошибка", "Введите значения координат")
                return

            self.canvas.draw()
            self.layout_count+=1
        if self.radioButton3d.isChecked():
            # создать пустой список для текущего слоя
            current_layer = []
            layer_name = self.combobox_layer.currentText()

            start_height = float(start_height)
            current_layer.append(start_height)

            end_height = float(end_height)
            current_layer.append(end_height)

            # добавить текущий слой в список слоев
            self.layers.append(current_layer)

            # нарисовать текущий слой
            if self.textbox_long.text() and self.textbox_long_2.text() and self.textbox_height.text() and self.textbox_height_2.text():
                try:
                    xlim = float(self.textbox_long.text().replace(',', '.'))
                    xlim2 = float(self.textbox_long_2.text().replace(',', '.'))
                    ylim = float(self.textbox_height.text().replace(',', '.'))
                    ylim2 = float(self.textbox_height_2.text().replace(',', '.'))
                except ValueError:
                    QtWidgets.QMessageBox.critical(self, "Ошибка", "Проверьте правильность ввода координат")
                    return
            else:
                QtWidgets.QMessageBox.critical(self, "Ошибка", "Введите значения координат")
                return
            x = [xlim, xlim2, xlim2, xlim]
            y = [ylim, ylim, ylim2, ylim2]
            z = [start_height, start_height, end_height, end_height]
            z_data = np.array([[start_height] * 4, [end_height] * 4])



            # Построение поверхности с прозрачностью alpha=0.2
            self.ax3d.plot_surface(x, y, z_data, alpha=0.2, color=color)
            self.ax3d.plot(x, y, z, alpha=0.2)

            self.canvas.draw()

    def Graph2D(self):
        path = self.showDialog()
        if path:
            self.button2D = 1
            try:
                df = pd.read_excel(path, header=None)
                df = df.replace(',', '.', regex=True)
                df = df.iloc[1:, :]
                Y = df.values.astype(np.float64)
                for row in Y:
                    self.ax2d.plot(row)
                self.canvas.draw()
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка формата",
                                    "Не удалось прочитать файл. Проверьте, что данные в файле имеют правильный формат. Ошибка: {}".format(
                                        str(e)))

    def Graph3D(self):
        path = self.showDialog()
        if path:
            self.button3D = 1
            try:
                df = pd.read_excel(path, header=None)
                df = df.replace(',', '.', regex=True)
                df = df.iloc[1:,:]
                X, Y = np.meshgrid(range(df.shape[1]), range(df.shape[0]))
                Z = df.values.astype(np.float64)
                # fig = self.canvas.figure
                # fig.clear()  # Очистить график
                # ax = fig.add_subplot(111, projection='3d')
                self.ax3d.plot_surface(X, Y, Z, cmap='viridis')
                self.canvas.draw()  # Перерисовать график на FigureCanvas
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка формата",
                                    "Не удалось прочитать файл. Проверьте, что данные в файле имеют правильный формат. Ошибка: {}".format(
                                        str(e)))


    def GraphElips2D(self):
        path = self.showDialog()
        if path:
            try:
                df = pd.read_excel(path, header=None)
                df = df.replace(',', '.', regex=True)
                df = df.iloc[1:, :]
                cols_to_drop = df.columns[(df == 0).all()]

                # Удаляем выбранные столбцы
                df = df.drop(cols_to_drop, axis=1)
                X, Y = np.meshgrid(range(df.shape[1]), range(df.shape[0]))
                Z = df.values.astype(np.float64)
                self.ax2d.contour(X, Y, Z)

                self.canvas.draw()
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка формата",
                                    "Не удалось прочитать файл. Проверьте, что данные в файле имеют правильный формат. Ошибка: {}".format(
                                        str(e)))

    def AddImage(self):
        path = self.showDialog()
        if path:
            try:
                img = PIL.Image.open(path)
                img.verify()
                img = np.asarray(PIL.Image.open(path))
                # self.ax2d.imshow(img)

                # Prompt user for x and y coordinates

                x1, ok = QInputDialog.getDouble(self, "координата ", "X1:", 0.0, -1e6, 1e6, 2)
                x, ok = QInputDialog.getDouble(self, "координата", "X2:", 0.0, -1e6, 1e6, 2)
                if ok:
                    x = float(x)
                    x1 = float(x1)
                    y1, y_ok = QInputDialog.getDouble(self, "координата", "Y1:", 0.0, -1e6, 1e6, 2)
                    y, y_ok = QInputDialog.getDouble(self, "координата", "Y2:", 0.0, -1e6, 1e6, 2)

                    if y_ok:
                        y = float(y)
                        y1 = float(y1)
                        self.ax2d.imshow(img, extent=[x1, x, y1, y], aspect='equal')
                        # self.ax2d.scatter(x, y, marker='o', color='r')

                        self.canvas.draw()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e), QMessageBox.Ok)

    def clearGraph(self):
        self.ax2d.clear()
        self.ax3d.clear()
        self.layers = []

        self.soil_height = []
        self.granite_height = []
        self.sandstone_height = []
        self.clay_height = []
        self.quartzite_height = []
        self.coal_height = []
        self.h = 0
        self.matrix = None
        self.layout_count = 0
        self.layer_at_graph = []
        self.canvas.draw()

    def showDialog(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'выбрать файл', 'C:\\Users\\ntart\\PycharmProjects\\pythonProject3')
        return fname





    def CalcSubsidence(self):
        try:
            # def generate_symmetric_matrix(min_value, max_value, W):
            #
            #     def sigmoid(x, a=0.002):
            #         return 1 / (1 + math.exp(-a * x))
            #     check_max = 0
            #     fix_value = 0
            #     size = W*100
            #     midpoint = (size - 1) / 2
            #     values = []
            #     for i in range(int(size)):
            #         row = []
            #         for j in range(int(size)):
            #             distance_from_midpoint = math.sqrt((i - midpoint) ** 2 + (j - midpoint) ** 2)
            #             value = sigmoid(distance_from_midpoint) * (max_value - min_value) + min_value
            #             if value >= W and check_max == 0:
            #                 fix_value = value
            #                 check_max = 1
            #             if value >= W and check_max > 0:
            #                 value = fix_value
            #                 row.append(value)
            #             else:
            #                 row.append(value)
            #         values.append(row)
            #     return values

            # def generate_symmetric_matrix(min_value, max_value):
            #     height = self.ax2d.get_ylim()
            #
            #     height1 = abs(abs(abs(height[0])-(self.layout_count*0.5)) + abs(abs(height[1])-(self.layout_count*0.5)))
            #
            #
            #     size = int(self.textbox_long_2.text().replace(',', '.'))
            #     def sigmoid(x, a=(height1/size)):
            #         return 1 / (1 + math.exp(-a * x))
            #     midpoint = (size - 1) / 2
            #     values = []
            #     for i in range(int(size)):
            #         row = []
            #         for j in range(int(size)):
            #             distance_from_midpoint = math.sqrt((i - midpoint) ** 2 + (j - midpoint) ** 2)
            #             value = sigmoid(distance_from_midpoint) * (max_value - min_value) + min_value
            #             row.append(value)
            #         values.append(row)
            #     return values

            def generate_symmetric_matrix1(min_value, max_value, W):
                matrix = []
                height = self.ax2d.get_ylim()
                height1 = abs(abs(abs(height[0]) + abs(abs(height[1]))))
                size = abs(abs(int(self.textbox_long_2.text().replace(',', '.'))) - abs(int(self.textbox_long.text().replace(',', '.'))))
                step = 0
                # W = 10 #максимальная длина/ширина
                if min_value < float(height[0]):
                    min_value = float(height[0])
                max = max_value
                min1 = min_value
                line = []
                for i in range(round((size/1.5))):
                    line.append(max)
                    min1 += (height1 / size)
                reversed_line = line[::-1]
                first_end_line = reversed_line + line
                # new_size = size/2
                new_size = len(line)
                if W < min1:
                    W = min1
                for i in range(int(new_size)): #ДЛИНА или ширина
                    line = []
                    check_first = 0
                    max = max_value
                    min1 = min_value + step
                    if min1 > W or min1 >= max:
                        line.append(max)
                    else:
                        line.append(min1)
                    if W > size:
                        W = size
                    for j in range(int(new_size-1)):
                        if min1 > W or min1 >= max:
                            line.append(max)
                            min1 += (height1/(new_size-1))
                        # if check_first == 0:
                        #     line.append(min1)
                        #     line.append(min1)
                        #     line.append(min1)
                        #     check_first = 1
                        #     min1 += (height1 / size)
                        else:
                            line.append(min1)
                            min1 += (height1/(new_size-1))
                    reversed_line = line[::-1]
                    new_line = reversed_line + line
                    step+= (height1/(new_size-1))
                    matrix.append(new_line)



                reversed_matrix = matrix[::-1]
                new_matrix = reversed_matrix + matrix
                # step+=0.2
                # matrix.append(new_line)
                #
                new_matrix.append(first_end_line)
                new_matrix = new_matrix[::-1]
                new_matrix.append(first_end_line)
                return new_matrix

            def generate_symmetric_matrix(min_value, max_value, W, num_lines=10):
                # Вычисляем высоту графика
                size = round(int(self.textbox_long_2.text().replace(',', '.')) / 2)
                height = abs(max_value - min_value)
                # Создаем матрицу
                matrix = np.zeros((num_lines, 2 * size))
                # Заполняем первую строку
                W = round(W,5)
                for i in range(size):
                    x = i / (size - 1) * W / 2
                    x = round(x, 5)
                    y = np.tan(np.pi * (x / min_value))
                    y = round(y,5)
                    if i == size-1 or i == size:
                        y = min_value
                    matrix[0, i] = max_value - height * y / 2
                    matrix[0, 2 * size - 1 - i] = max_value - height * y / 2
                # Заполняем остальные строки
                for i in range(1, num_lines):
                    for j in range(2 * size):
                        matrix[i, j] = (matrix[0, j] + matrix[0, 2 * size - 1 - j]) / 2 - (i - 1) * height / (
                                    num_lines - 1)
                        if matrix[i, j] < min_value:
                            matrix[i, j] = min_value
                return matrix

            D1, ok1 = QInputDialog.getDouble(self, "Длина срезаемого пласта", "длина:")
            if not ok1:
                return
            D2, ok2 = QInputDialog.getDouble(self, "Ширина срезаемого пласта", "ширина:")
            if not ok2:
                return
            H, ok3 = QInputDialog.getDouble(self, "Введите среднюю глубину разработки", "высота:")
            if not ok3:
                return
            # C = float(long_plast) * float(width_plast) * float(height_plast) # срезаемое количество угля, м3/м2
            # k = math.pow(10, -7) # коэффициент фильтрации грунта, м/с
            # h1 = self.coal_height[0] # толщина пласта угля, м
            # p = 1.3 * (abs(float(self.textbox_long.text()) - float(self.textbox_long_2.text())) * abs(float(self.textbox_height.text()) - float(self.textbox_height_2.text())) * self.coal_height[0]) # плотность угля, кг/м3
            # S = k * C * h1 / p # оседание
            # h = S * p / (k * C) # глубина оседания
            # O = 10 # угол наклона поверхности восстановления
            # L = 0.5 * 10 / k # длина области воздействия, которая определяется конфигурацией системы
            #
            # W = (2 * S * L) / (h1 * math.tan(O))

            alpha, ok4 = QInputDialog.getDouble(self, "Введите угол падения пласта", "alpha:")
            if not ok4:
                return
            deltaDn = 0
            deltaDv = 0
            N1 = math.sqrt(0.9 * ((D1/H)+deltaDn+deltaDv))
            N2 = math.sqrt(0.9 * ((D2 / H) + deltaDn + deltaDv))
            q0 = 0.9
            m = 1 # мощность пластов
            n_osedanie = q0 * m * (math.cos(alpha) * N1 * N2)
            k = H*0.015

            v_arr = []
            v_arr1 = []
            v_total = 0

            x_1 = float(self.textbox_long.text().replace(',', '.'))
            x_2 = float(self.textbox_long_2.text().replace(',', '.'))
            y_1 = float(self.textbox_height.text().replace(',', '.'))
            y_2 = float(self.textbox_height_2.text().replace(',', '.'))
            y_final = abs(abs(y_1) - abs(y_2))
            x_final = abs(abs(x_1) - abs(x_2))

            Q_total = 0
            all_heght = []
            for layer_name in self.layer_at_graph:
                if layer_name == 'Почва':
                    all_heght.append(float(self.soil_height[0]))
                    #v = v_soil*0.3
                    #v_arr.append(v)
                    #v_total += 50
                    Q_soil = self.soil_height[0] * y_final * x_final #объем
                    v_arr1.append(Q_soil)
                    Q_total+=Q_soil
                if layer_name == 'Гранит':
                    all_heght.append(float(self.granite_height[0]))
                    # v = 70 * 0.2
                    # v_arr.append(v)
                    # v_total += 70
                    Q_granite = self.granite_height[0] * y_final * x_final  # объем
                    Q_total += Q_granite
                    v_arr1.append(Q_granite)
                if layer_name == 'Песчаник':
                    all_heght.append(float(self.sandstone_height[0]))
                    # v = 30 * 0.2
                    # v_arr.append(v)
                    # v_total += 30
                    Q_sandstone = self.sandstone_height[0] * y_final * x_final  # объем
                    Q_total += Q_sandstone
                    v_arr1.append(Q_sandstone)
                if layer_name == 'Глина':
                    all_heght.append(float(self.clay_height[0]))
                    # v = 50 * 0.3
                    # v_arr.append(v)
                    # v_total += 50
                    Q_clay = self.clay_height[0] * y_final * x_final  # объем
                    v_arr1.append(Q_clay)
                    Q_total += Q_clay
                if layer_name == 'Кварцит':
                    all_heght.append(float(self.quartzite_height[0]))
                    # v = 50 * 0.3
                    # v_arr.append(v)
                    # v_total += 50
                    Q_quartzite = self.quartzite_height[0] * y_final * x_final  # объем
                    v_arr1.append(Q_quartzite)
                    Q_total += Q_quartzite
                if layer_name == 'Уголь':
                    # all_heght.append(float(self.coal_height[0]))
                    # v = 5 * 0.2
                    # v_arr.append(v)
                    # v_total += 5
                    Q_coal = self.coal_height[0] * y_final * x_final  # объем
                    v_arr1.append(Q_coal)
                    Q_total += Q_coal
            mount_weight = 0
            koef_P = 0
            all_E = []
            for layer_name in self.layer_at_graph:
                if layer_name == 'Почва':
                    v = (Q_soil/sum(v_arr1)*100)*0.3
                    koef_P += ((float(self.soil_height[0]) * 100) / sum(all_heght))*0.3
                    v_arr.append(v)
                    v_total += v
                    mount_weight += 1300
                    all_E.append(0.1)
                if layer_name == 'Гранит':
                    koef_P += ((float(self.granite_height[0]) * 100) / sum(all_heght)) * 0.2
                    v = (Q_granite/sum(v_arr1)*100) * 0.2
                    v_arr.append(v)
                    v_total += v
                    all_E.append(50)
                mount_weight += 2600
                if layer_name == 'Песчаник':
                    koef_P += ((float(self.sandstone_height[0]) * 100) / sum(all_heght)) * 0.2
                    v = (Q_sandstone/sum(v_arr1)*100) * 0.2
                    v_arr.append(v)
                    v_total += v
                    all_E.append(20)
                mount_weight += 2600
                if layer_name == 'Глина':
                    koef_P += ((float(self.clay_height[0]) * 100) / sum(all_heght)) * 0.3
                    v = (Q_clay/sum(v_arr1)*100) * 0.3
                    v_arr.append(v)
                    v_total += v
                    all_E.append(10)
                mount_weight += 1800
                if layer_name == 'Кварцит':
                    koef_P += ((float(self.quartzite_height[0]) * 100) / sum(all_heght)) * 0.3
                    v = (Q_quartzite/sum(v_arr1)*100) * 0.3
                    v_arr.append(v)
                    v_total += v
                    all_E.append(70)
                mount_weight += 2600
                if layer_name == 'Уголь':
                    # koef_P += ((float(self.clay_coal) * 100) / sum(all_heght)) * 0.2
                    v_coal = (Q_coal/sum(v_arr1)*100) * 0.2
                    v_arr.append(v_coal)
                    v_total += v_coal
                    all_E.append(1)



            ylim = self.ax2d.get_ylim()

            k = 1/(1+2*(D1/D2))
            m_coal = ((D1*D2*H)*1100)/100000
            Q = m_coal * 9.81 * H * math.cos(alpha)
            E_avg  =  sum(v_arr)/v_total
            v_avg = (v_total/ (len(v_arr)+1))
            deltaDn = (N1 * N2 * m * q0 * D1 * math.cos(alpha)) / (E_avg * ( 1- math.pow(v_avg, 2)))
            deltaDv = (Q * math.pow(H, 2)) / ((E_avg * (1 - math.pow(0.2, 2))))

            # deltaDn = math.sqrt((0.9 * ((D1 / H) + deltaDv + deltaDn)) ** 2 - (math.sin(alpha) * N1 * N2) ** 2) - (0.9 * (D1 / H))
            L = 2 * k * deltaDv
            W = 2 * k * deltaDn
            coal_width = float(self.coal_height[0])
            W = (coal_width * H) / (2 * math.tan(alpha))

            p = mount_weight/Q_total

            P = p * 9.81 * H

            h = (P * math.pow(H, 2)) / (2 * E_avg * (1 - math.pow(v_avg, 2)))


            Q_coal_srez = (H/10) * ((D1/10)*(D2/10))
            avg_E = sum(all_E)/(len(all_E)+1)
            h1 = self.coal_height[0]
            h_0 = H
            e = (h1 - h_0) / h_0
            sigma = avg_E*e
            E = sigma/e

            h_max = ((Q_coal_srez * (self.coal_height[0]/10)) / (2 * E * (1- math.pow((koef_P/100) ,2))))/10 #глубина

            w_max = (h_max * (D1/10)) / (2 * math.sin(alpha)) #ширина

            Q_coal_srez_full = ((self.coal_height[0]-1) / 10) * (((y_final-1) / 10) * ((x_final-1) / 10))
            h_max_full = ((Q_coal_srez_full * (self.coal_height[0] / 10)) / (2 * E * (1 - math.pow((koef_P / 100), 2)))) / 10

            full_srez = (h_max_full * ((y_final-1)/10)) / (2 * math.sin(alpha))
            max_shirina = (w_max * y_final) / full_srez
            xlim = abs(abs(self.ax2d.get_xlim()[0]) - abs(self.ax2d.get_xlim()[1]))
            ylim1 = abs(abs(self.ax2d.get_ylim()[0]) - abs(self.ax2d.get_ylim()[1]))
            max_glubina =(h_max * (xlim + ylim1))/ h_max_full

            if float(ylim[1]) > 0:
                max_value = float(ylim[1])
            else:
                max_value = float(ylim[1])

            # min_value = (abs(float(ylim[1])) - 1.5) - abs(n_osedanie)

            min_value = max_value - max_glubina
            print(n_osedanie)
            print(deltaDv)
            print(h)
            self.matrix = generate_symmetric_matrix1(min_value, max_value, max_shirina) # 



            df = pd.DataFrame(self.matrix)

            file_name, ok = QInputDialog.getText(self, "Введите название файла для сохранения", "Имя файла:")
            if ok:
                file_name = str(file_name) + '.xlsx'
                df.to_excel(file_name, index=False)
            else:
                return

        except Exception as e:
            print(f"Ошибка: {e}")
            return


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

