import sys

import public as public
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QMainWindow, QTextEdit, QVBoxLayout, \
    QGraphicsScene, QGraphicsView, QComboBox, QLineEdit, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.uic.properties import QtGui
from matplotlib import cm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from numpy import var
import matplotlib.colors as mcolors


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

        # Set layout properties
        layout = QVBoxLayout()
        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.pushButton_2)
        layout_buttons.addWidget(self.pushButton_3)
        layout_buttons.addWidget(self.pushButton_clear)
        layout_buttons.addWidget(self.pushButton_add_layer)
        layout.addLayout(layout_buttons)

        # Set text input and combo box for adding layers
        self.label_height = QLabel("Высота слоя:")
        self.textbox_height = QLineEdit()
        self.label_layer = QLabel("Название слоя:")
        self.combobox_layer = QComboBox()
        self.combobox_layer.addItems(["Слой 1", "Слой 2", "Слой 3", "Слой 4", "Слой 5"])
        layout_input = QHBoxLayout()
        layout_input.addWidget(self.label_height)
        layout_input.addWidget(self.textbox_height)
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

        # Set window properties
        self.setGeometry(50, 50, 1300, 1000)
        self.setWindowTitle("MainWindow")

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setGeometry(50, 100, 1200, 800)
        self.view.setStyleSheet("background-color: white;")
        self.view.setHorizontalScrollBarPolicy(1)
        self.view.setVerticalScrollBarPolicy(1)

        self.fig = plt.Figure()
        self.fig = plt.Figure(figsize=(10, 5))

        # Create two subplots with 1 row and 2 columns
        self.ax2d = self.fig.add_subplot(121)
        self.ax3d = self.fig.add_subplot(122, projection='3d')

        # Adjust the spacing between the subplots
        self.fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05, wspace=0.1)

        # Create a canvas for the Figure object
        self.canvas = FigureCanvas(self.fig)
        self.scene.addWidget(self.canvas)

        self.layers = []

    button2D = 0
    button3D = 0
    def addLayer(self):
        if self.button2D == 1:
            layer_height = float(self.textbox_height.text())
            layer_name = self.combobox_layer.currentText()
            self.layers.append((layer_name, layer_height))

            # Plot all layers
            heights = [layer[1] for layer in self.layers]
            xlim = self.ax2d.get_xlim()  # Получаем значения оси x графика
            self.ax2d.plot(xlim, [heights[0], heights[0]], label=self.layers[0][0])
            for i in range(1, len(self.layers)):
                self.ax2d.plot(xlim, [heights[i], heights[i]], label=self.layers[i][0])
                self.ax2d.fill_between(xlim, heights[i - 1], heights[i], alpha=0.2)
            self.canvas.draw()
        if self.button3D == 1:
            layer_height = float(self.textbox_height.text())
            layer_name = self.combobox_layer.currentText()
            self.layers.append((layer_name, layer_height))
            xlim = self.ax3d.get_xlim()
            ylim = self.ax3d.get_ylim()
            x = [xlim[0], xlim[1], xlim[1], xlim[0]]
            y = [ylim[0], ylim[0], ylim[1], ylim[1]]
            z = [layer_height, layer_height, layer_height, layer_height]
            z_data = []
            for layer in self.layers:
                layer_height = layer[1]
                z_data.append([layer_height] * 4)  # 4 - количество вершин квадрата на грани

            # Преобразование в массив NumPy для использования с plot_surface
            z_data = np.array(z_data)

            # Построение поверхности с прозрачностью alpha=0.2
            # Список цветовых значений
            colors = ["red", "orange", "yellow", "green", "blue", "purple"]

            # Создаем colormap на основе списка цветов
            cmap = mcolors.ListedColormap(colors)
            self.ax3d.plot_surface(x, y, z_data, alpha=0.2, cmap='jet')
            self.ax3d.plot(x, y, z, alpha=0.2)
            self.canvas.draw()

    def Graph2D(self):
            path = self.showDialog()
            if path:
                self.button2D = 1
                df = pd.read_excel(path)
                df = df.replace(',', '.', regex=True)
                Y = df.values.astype(np.float64)
                for row in Y:
                    self.ax2d.plot(row)
                self.canvas.draw()

    def Graph3D(self):
        path = self.showDialog()
        if path:
            self.button3D = 1
            df = pd.read_excel(path)
            df = df.replace(',', '.', regex=True)
            X, Y = np.meshgrid(range(df.shape[1]), range(df.shape[0]))
            Z = df.values.astype(np.float64)
            # fig = self.canvas.figure
            # fig.clear()  # Очистить график
            # ax = fig.add_subplot(111, projection='3d')
            self.ax3d.plot_surface(X, Y, Z, cmap='viridis')
            self.canvas.draw()  # Перерисовать график на FigureCanvas

    def clearGraph(self):
        self.ax.clear()
        self.layers = []
        self.canvas.draw()

    def showDialog(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'выбрать файл', 'C:\\Users\\ntart\\PycharmProjects\\pythonProject3')
        return fname


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
