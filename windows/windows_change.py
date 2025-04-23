# import sys
# import multiprocessing
# import time
# from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget
# from PyQt5.QtCore import QTimer, Qt
#
# def worker(shared_data):
#     for _ in range(10):  # 模拟有限任务
#         shared_data['value'] += 1
#         time.sleep(1)
#     return  # 子进程在执行完任务后结束
#
# class MainWindow(QMainWindow):
#     def __init__(self, shared_data):
#         super().__init__()
#
#         self.shared_data = shared_data
#
#         self.label = QLabel(self)
#         self.label.setAlignment(Qt.AlignCenter)
#         self.setCentralWidget(self.label)
#         self.resize(300, 200)
#
#         self.start_button = QPushButton("Start", self)
#         self.start_button.clicked.connect(start_process)  # 连接到外部函数
#
#         layout = QVBoxLayout()
#         layout.addWidget(self.label)
#         layout.addWidget(self.start_button)
#
#         widget = QWidget()
#         widget.setLayout(layout)
#         self.setCentralWidget(widget)
#
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.update_data)
#         self.timer.start(1000)
#
#     def update_data(self):
#         data = self.shared_data['value']
#         self.label.setText(f'Data from manager: {data}')
#
#         if data % 2 == 0:
#             self.label.setStyleSheet("background-color: lightblue;")
#         else:
#             self.label.setStyleSheet("background-color: lightgreen;")
#
# # 外部函数，用于启动子进程
# def start_process():
#     process = multiprocessing.Process(target=worker, args=(window.shared_data,))
#     process.start()
#
# if __name__ == '__main__':
#     multiprocessing.freeze_support()  # for Windows support
#
#     manager = multiprocessing.Manager()
#     shared_data = manager.dict()
#     shared_data['value'] = 0
#
#     app = QApplication(sys.argv)
#     window = MainWindow(shared_data)
#     window.show()
#
#     sys.exit(app.exec_())
#
#

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QVBoxLayout, QWidget, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ComboBox 示例")
        self.setGeometry(200, 200, 400, 300)

        # 创建一个垂直布局
        layout = QVBoxLayout()

        # 创建一个 ComboBox
        self.comboBox = QComboBox()

        # 添加初始选项
        self.comboBox.addItem("选项1")
        self.comboBox.addItem("选项2")
        self.comboBox.addItem("选项3")

        # 添加更多选项的按钮
        self.button_add = QPushButton("添加更多选项")
        self.button_add.clicked.connect(self.add_items)

        # 将 ComboBox 和按钮添加到布局中
        layout.addWidget(self.comboBox)
        layout.addWidget(self.button_add)

        # 创建主widget并设置布局
        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def add_items(self):
        # 示例：在点击按钮时添加新选项
        new_option = f"选项{self.comboBox.count() + 1}"
        self.comboBox.addItem(new_option)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

