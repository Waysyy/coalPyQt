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
            self.soil_height.append(abs(start_height-end_height))
        if layer_name == 'Гранит':
            color = 'gray'
            self.granite_height.append(abs(start_height - end_height))
        if layer_name == 'Песчаник':
            color = 'yellow'
            self.sandstone_height.append(abs(start_height - end_height))
        if layer_name == 'Глина':
            color = 'blue'
            self.clay_height.append(abs(start_height - end_height))
        if layer_name == 'Кварцит':
            color = 'pink'
            self.quartzite_height.append(abs(start_height - end_height))
        if layer_name == 'Уголь':
            color = 'black'
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
                df = pd.read_excel(path)
                df = df.replace(',', '.', regex=True)
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
                df = pd.read_excel(path)
                df = df.replace(',', '.', regex=True)
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
                df = pd.read_excel(path)
                df = df.replace(',', '.', regex=True)
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
        self.canvas.draw()

    def showDialog(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'выбрать файл', 'C:\\Users\\ntart\\PycharmProjects\\pythonProject3')
        return fname





    def CalcSubsidence(self):
        try:
            def generate_symmetric_matrix(min_value, max_value, W):

                def sigmoid(x, a=0.002):
                    return 1 / (1 + math.exp(-a * x))
                check_max = 0
                fix_value = 0
                size = W*100
                midpoint = (size - 1) / 2
                values = []
                for i in range(int(size)):
                    row = []
                    for j in range(int(size)):
                        distance_from_midpoint = math.sqrt((i - midpoint) ** 2 + (j - midpoint) ** 2)
                        value = sigmoid(distance_from_midpoint) * (max_value - min_value) + min_value
                        if value >= W and check_max == 0:
                            fix_value = value
                            check_max = 1
                        if value >= W and check_max > 0:
                            value = fix_value
                            row.append(value)
                        else:
                            row.append(value)
                    values.append(row)
                return values

            long_plast, ok1 = QInputDialog.getDouble(self, "Длина срезаемого пласта", "длина:")
            if not ok1:
                return
            width_plast, ok2 = QInputDialog.getDouble(self, "Ширина срезаемого пласта", "ширина:")
            if not ok2:
                return
            height_plast, ok3 = QInputDialog.getDouble(self, "Высота срезаемого пласта", "высота:")
            if not ok3:
                return
            C = float(long_plast) * float(width_plast) * float(height_plast) # срезаемое количество угля, м3/м2
            k = math.pow(10, -7) # коэффициент фильтрации грунта, м/с
            h1 = self.coal_height[0] # толщина пласта угля, м
            p = 1.3 * (abs(float(self.textbox_long.text()) - float(self.textbox_long_2.text())) * abs(float(self.textbox_height.text()) - float(self.textbox_height_2.text())) * self.coal_height[0]) # плотность угля, кг/м3
            S = k * C * h1 / p # оседание
            h = S * p / (k * C) # глубина оседания
            O = 10 # угол наклона поверхности восстановления
            L = 0.5 * 10 / k # длина области воздействия, которая определяется конфигурацией системы

            W = (2 * S * L) / (h1 * math.tan(O))

            ylim = self.ax2d.get_ylim()
            max_value = float(ylim[1])
            min_value = float(ylim[1]) - h

            self.matrix = generate_symmetric_matrix(min_value, max_value, W)

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

# df = pd.read_excel('tableTest.xlsx')
# df = df.replace(',', '.', regex=True)
# Y = df.values.astype(np.float64)
# #
# # Y = df.array([[10,10,10,10,10,10,10,10,10,10],
# #      [10,9,9,9,9,9,9,9,9,10],
# #      [10,9,8,8,8,8,8,8,9,10],
# #      [10,9,8,8,8,8,8,8,9,10],
# #      [10,9,8,7,7,7,7,8,9,10],
# #      [10,9,8,7,6,6,7,8,9,10]])
#
#
# X = [1,2,3,4,5,6,7,8,9,10]
# for row in Y:
#     plt.plot(row)
#
# # Show the plot
# plt.show()


# import numpy as np
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
#
# # Generate random data
# np.random.seed(123)
# n = 50
# x = np.linspace(0, 20, n)
# y = np.linspace(0, 20, n)
# X, Y = np.meshgrid(x, y)
# Z = np.random.uniform(-15, 0, size=(n, n))
# W = -Z / 15 + np.random.normal(0, 0.5, size=(n, n))
#
# # Generate land subsidence data
# depth = np.linspace(0, 5, n)
# sub = np.zeros((n, n))
# for i in range(n):
#     sub[:, i] = depth[i]
#
# # Add land subsidence data to Z coordinate
# Z = Z - sub
#
# # Set up the figure
# fig = plt.figure(figsize=(10, 10))
# ax = fig.add_subplot(111, projection='3d')
#
# # Create a 3D surface plot
# surf = ax.plot_surface(X, Y, Z, facecolors=plt.cm.coolwarm(W), shade=False)
#
# # Add labels and colorbar
# ax.set_xlabel('X (m)')
# ax.set_ylabel('Y (m)')
# ax.set_zlabel('Depth (m)')
# cb = fig.colorbar(surf)
# cb.set_label('W (m)')
#
# # Set limits for the axes
# ax.set_xlim3d(0, 20)
# ax.set_ylim3d(0, 20)
# ax.set_zlim3d(-20, 0)
#
# # Save the plot
# plt.show()


# from math import sqrt
# import matplotlib.pyplot as plt
# import pandas as pd
# import numpy as np
# import openpyxl
#
# df = pd.read_excel('table2.xlsx')
# df = df.replace(',', '.', regex=True)
#
# # Convert the dataframe to a numpy array
# arr = df.values.astype(np.float64)
#
# x = arr[:, 0]
# y = arr[:, 1]
# y2 = arr[:, 3]
# y3 = arr[:, 4]
#
# x2 = arr[:, 5]
# y21 = arr[:, 6]
# y22 = arr[:, 8]
# y23 = arr[:, 9]
#
#
# plt.plot(x, y, x, y2, x, y3)
# plt.plot(x2, y21, x2, y22, x2, y23)
#
# plt.plot(x, y, color='red',  marker='o', linestyle='-', label='S(0mm)')
# plt.plot(x, y2, color='blue', marker='o', linestyle='-', label='Sz1(0mm)')
# plt.plot(x, y3, color='green',marker='o', linestyle='-', label='Sz2(0mm)')
# plt.plot(x2, y21, color='purple',marker='o', linestyle='-', label='S(15mm)')
# plt.plot(x2, y22, color='cyan',marker='o', linestyle='-', label='Sz1(15mm)')
# plt.plot(x2, y23, color='pink',marker='o', linestyle='-', label='Sz2(15mm)')
#
# plt.xlabel('Z')
# plt.ylabel('S(0mm), Sz1(0mm),Sz2(0mm),S(15mm),Sz1(15mm),Sz2(15mm)')
# plt.legend()
# plt.show()


# D = [990, 160, 110, 320, 90]
# H = [466, 493, 477, 417, 465]
# l = 0.1
#
# for i in range(len(D)):
#     D[i] = D[i]/1000
#
#
# Dp = []
# Dv = []
# Dpr = []
# Dopr = []
#
#
#
# for h in H:
#     Dp.append(0.1 - 0.25*l/h)
#     Dv.append(0.1 - 0.25*l/h)
#     Dpr.append(0.1 - 0.25*l/h)
#     Dopr.append(0.1 - 0.25*l/h)
#
# N1 = []
#
# for i in range(len(D)):
#     N1i = sqrt(0.9*((D[i]/H[i])+Dp[i]+Dv[i]))
#     N1.append(N1i)
#
# N2 = []
#
# for i in range(len(D)):
#     N2i = sqrt(0.9*((D[i]/H[i])+Dpr[i]+Dopr[i]))
#     N2.append(N2i)
#
# print(N1)
# print(N2)
#
# plt.plot(D, N1, 'ro-', label='N1')
# plt.plot(D, N2, 'bo-', label='N2')
#
# plt.title('N1 and N2 vs D')
# plt.xlabel('D')
# plt.ylabel('N1, N2')
#
# plt.legend()
#
# plt.show()
