import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, \
    QColorDialog, QInputDialog, QCheckBox, QFileDialog
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches
import openpyxl


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("График с прямоугольниками")
        self.setGeometry(100, 100, 800, 600)

        # виджеты интерфейса
        self.label_thickness = QLabel("Толщина:", self)
        self.label_thickness.setGeometry(10, 10, 100, 30)
        self.line_edit_thickness = QLineEdit(self)
        self.line_edit_thickness.setGeometry(120, 10, 100, 30)

        self.label_width = QLabel("Ширина разбиений:", self)
        self.label_width.setGeometry(10, 50, 100, 30)
        self.line_edit_width = QLineEdit(self)
        self.line_edit_width.setGeometry(120, 50, 100, 30)

        self.label_density = QLabel("Плотность:", self)
        self.label_density.setGeometry(10, 130, 100, 30)
        self.line_edit_density = QLineEdit(self)
        self.line_edit_density.setGeometry(120, 130, 100, 30)

        self.label_part = QLabel("Количество разбиений:", self)
        self.label_part.setGeometry(10, 90, 150, 30)
        self.line_edit_part = QLineEdit(self)
        self.line_edit_part.setGeometry(160, 90, 100, 30)

        self.checkbox_auto = QCheckBox("Авто", self)
        self.checkbox_auto.setGeometry(10, 170, 100, 30)
        self.checkbox_auto.stateChanged.connect(self.toggle_auto_save)

        self.button_add = QPushButton("Добавить слой", self)
        self.button_add.setGeometry(10, 210, 210, 30)
        self.button_add.clicked.connect(self.add_rectangle)

        self.button_next = QPushButton("Следующее разбиение", self)
        self.button_next.setGeometry(10, 250, 210, 30)
        self.button_next.clicked.connect(self.next_partition)

        self.button_undo = QPushButton(QIcon("back.png"), "", self)
        self.button_undo.setGeometry(10, 290, 210, 30)
        self.button_undo.clicked.connect(self.undo_action)

        self.button_save = QPushButton("Сохранить разбиения", self)
        self.button_save.setGeometry(10, 330, 210, 30)
        self.button_save.clicked.connect(self.save_partitions)
        self.button_save.setEnabled(False)

        # объект для графика Matplotlib
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)

        # список для хранения прямоугольников
        self.rectangles = []

        # список для хранения разбиений
        self.partitions = []

        # вертикальый компоновщик и добавление виджетов
        layout = QVBoxLayout()
        layout.addWidget(self.label_thickness)
        layout.addWidget(self.line_edit_thickness)
        layout.addWidget(self.label_width)
        layout.addWidget(self.line_edit_width)
        layout.addWidget(self.label_part)
        layout.addWidget(self.line_edit_part)
        layout.addWidget(self.label_density)
        layout.addWidget(self.line_edit_density)
        layout.addWidget(self.checkbox_auto)
        layout.addWidget(self.button_add)
        layout.addWidget(self.button_next)
        layout.addWidget(self.button_undo)
        layout.addWidget(self.button_save)
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

        # Создание книги Excel и листа
        self.workbook = openpyxl.Workbook()
        self.sheet = self.workbook.active
        self.current_partitions = []
        # Заголовки столбцов в Excel
        self.sheet.cell(row=1, column=1).value = "Номер разбиения"
        self.sheet.cell(row=1, column=2).value = "Название"
        self.sheet.cell(row=1, column=3).value = "Плотность"
        self.sheet.cell(row=1, column=4).value = "Толщина"
        self.sheet.cell(row=1, column=5).value = "Цвет"

    def toggle_auto_save(self, state):
        self.auto_save_enabled = state == Qt.Checked
        self.button_save.setEnabled(self.auto_save_enabled)

    def add_rectangle(self):
        height = float(self.line_edit_thickness.text())
        width = float(self.line_edit_width.text())
        part = float(self.line_edit_part.text())
        density = float(self.line_edit_density.text())

        if self.check_first != 0:
            x = 0
            y = self.final_Y
            self.final_Y += y + height
        if self.check_first == 0:
            x = 0
            y = 0 - height
            self.check_first += 1

        # Выбор цвета слоя
        color_dialog = QColorDialog()
        color = color_dialog.getColor()
        if color.isValid():
            rect_color = color.name()
        else:
            rect_color = 'r'  # По умолчанию красный цвет

        # Ввод названия слоя
        name, ok = QInputDialog.getText(self, 'Введите название', 'Название:')
        if ok:
            rect_name = name
        else:
            rect_name = ''  # Пустая строка, если название не введено

        rect = patches.Rectangle((x, y), width, height, facecolor=rect_color)
        rect.set_label(rect_name)
        self.rectangles.append(rect)
        self.draw_rectangles()

        # Блокировка изменения ширины после добавления первого слоя
        if not self.is_width_locked:
            self.line_edit_width.setReadOnly(True)
            self.is_width_locked = True

        if float(self.line_edit_part.text()) == 0:
            self.button_save.setEnabled(True)

        # Добавление информации о слое в текущее разбиение
        current_partition = {
            'name': rect_name,
            'density': density,
            'thickness': height,
            'color': rect_color
        }
        self.current_partitions.append(current_partition)

    def next_partition(self):
        if float(self.line_edit_part.text()) > 0:
            self.save_current_partition()  # Сохранение информации о текущем разбиении
            self.rectangles = []
            self.draw_rectangles()
            part = float(self.line_edit_part.text())
            part -= 1
            self.line_edit_part.setText(str(part))
            self.button_save.setEnabled(False)

    def undo_action(self):
        if self.rectangles:
            self.rectangles.pop()
            self.draw_rectangles()

    def draw_rectangles(self):
        self.axes.clear()
        for rect in self.rectangles:
            self.axes.add_patch(rect)
            self.axes.annotate(rect.get_label(), (rect.get_x() + rect.get_width() / 2, rect.get_y() + rect.get_height() / 2),
                               ha='center', va='center')
        self.axes.set_xlim([0, float(self.line_edit_width.text())])
        self.axes.set_ylim([0 - float(self.line_edit_thickness.text()) * 2, self.final_Y + float(self.line_edit_thickness.text())])
        self.canvas.draw()

    def save_partitions(self):
        self.save_current_partition()  # Сохранение информации о последнем разбиении
        file_name, _ = QFileDialog.getSaveFileName(self, "Сохранить разбиения", "", "Excel Files (*.xlsx)")
        if file_name:
            self.workbook.save(file_name)

    def save_current_partition(self):
        partition_number = int(float(self.line_edit_part.text()))
        if self.auto_save_enabled:
            real_row = 1
            for row in range(partition_number):
                for i, partition in enumerate(self.current_partitions):
                    self.sheet.cell(row=real_row, column=1).value = row+1
                    self.sheet.cell(row=real_row, column=2).value = partition['name']
                    self.sheet.cell(row=real_row, column=3).value = partition['density']
                    self.sheet.cell(row=real_row, column=4).value = partition['thickness']
                    self.sheet.cell(row=real_row, column=5).value = partition['color']
                    real_row +=1

        else:
            for i, partition in enumerate(self.current_partitions):
                row = i + (partition_number - 1) * len(self.current_partitions) + 2
                self.sheet.cell(row=row, column=1).value = partition_number
                self.sheet.cell(row=row, column=2).value = partition['name']
                self.sheet.cell(row=row, column=3).value = partition['density']
                self.sheet.cell(row=row, column=4).value = partition['thickness']
                self.sheet.cell(row=row, column=5).value = partition['color']
            self.current_partitions = []


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
