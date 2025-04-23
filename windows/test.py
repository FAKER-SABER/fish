# import sys
# from datetime import datetime
#
# import cv2
# from PyQt5 import QtGui, Qt
# from PyQt5.QtCore import QTimer, QTime, QDateTime
# from PyQt5.QtGui import QIcon, QPixmap
# from PyQt5.QtWidgets import *
# import os
# from windows.win import Ui_MainWindow  # 导入ui界面文件
# from PLC_demo.plcWriteRead import PLCWriteRead
#
#
# class MainWindow(QMainWindow, Ui_MainWindow):
#     def __init__(self, parent=None):
#         super().__init__()
#         self.setupUi(self)  # 使用Ui_MainWindow.setupUi(self, self)来初始化UI
#
#         self.PLC = PLCWriteRead('192.168.0.1', name='1200')
#         self.image_index = 597
#
#         # self.action_open.triggered.connect(self.open_new_window)
#         self.pushButton_start.clicked.connect(self.start_SYSTEM)
#         self.pushButton_reflash.clicked.connect(self.reflash_SYSTEM)
#
#
#         self.label_10.setText("工业相机无法连接")
#         self.label_10.setStyleSheet("background-color:rgb(255, 0, 0);")
#         self.label_sys_status.setText("设备硬件出错，请检查")
#         self.label_sys_status.setStyleSheet("background-color:rgb(255, 0, 0);")
#         self.label_11.setText("PLC无法连接")
#         self.label_11.setStyleSheet("background-color:rgb(255, 0, 0);")
#         self.label_sys_status.setText("设备硬件出错，请检查")
#         self.label_sys_status.setStyleSheet("background-color:rgb(255, 0, 0);")
#
#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.label_show_time)
#         self.timer.timeout.connect(self.update_image)
#         self.timer.start(1000)
#
#         # self.timer1 = QTimer(self)
#         # self.timer1.timeout.connect(self.update_image)
#         # self.timer1.start(500)
#
#     def start_SYSTEM(self):
#         # self.timer.start()
#         try:
#             self.PLC.ConnectPlc()
#             self.PLC.WritePlcMK(2, 1, form='bit', bit=2)
#         except RuntimeError as e:
#             print("连接该PLC超时：%s" % e)
#             self.label_status.setStyleSheet('background-color: red')
#             self.label_status.setText("无法连接PLC")
#             return
#         self.PLC.disconnectPlc()
#
#     def reflash_SYSTEM(self):
#         try:
#             self.PLC.ConnectPlc()
#             state = self.PLC.PLC.get_connected()
#             if state == False:
#                 print("无法连接到该PLC")
#         except RuntimeError as e:
#             print("连接该PLC超时：%s" % e)
#             return
#
#         # 先将系统停下
#         self.PLC.WritePlcMK(2, 0, form='bit', bit=2)
#         # 擦除相关数据区的数据
#         # 1、将数据写入标志和数据写入完成标志擦除
#         self.PLC.WritePlcMK(2, 0, form='bit', bit=3)
#         self.PLC.WritePlcMK(2, 0, form='bit', bit=4)
#         # 2、擦除存储XY轴坐标数据的DB数据块
#         for i in range(25):
#             # 想PLC写入目标的X轴坐标
#             self.PLC.WritePlcDB(1, 4 * i, 0.0, form='real')
#             # 想PLC写入目标的Y轴坐标
#             self.PLC.WritePlcDB(1, 4 * i + 100, 0.0, form='real')
#         self.PLC.WritePlcDB(1, 200, 0, form='byte')
#         self.PLC.WritePlcDB(1, 201, 0, form='byte')
#
#         self.PLC.disconnectPlc()
#         print("start_shuaxin_func已运行")
#
#     def label_show_time(self):
#         datetime = QDateTime.currentDateTime()
#         current_date = datetime.toString('yyyy-MM-dd')
#         current_time = datetime.toString('hh:mm:ss')
#         self.label_riqi_show.setText(current_date)
#         self.label_time_show.setText(current_time)
#
#     def update_image(self):
#         # image_path = "MvImport/video/"+"{05d}".format(self.image_index)+".jpg"
#         # pixmap = QPixmap(image_path)
#         # self.label.setPixmap(pixmap.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio))
#         # print(image_path)
#         # self.image_index = self.image_index+1
#         picture1 = QtGui.QPixmap('E:/AA_My_code/Pycharm_code/AA_YOLO/Python_Project/yolov5-7.0_WEIHAI/MvImport/video/00604.jpg')
#         self.label_showpic.setScaledContents(True)
#         self.label_showpic.setPixmap(picture1.scaled(950, 640))
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     Main_Window = MainWindow()
#     Main_Window.show()
#     sys.exit(app.exec_())
#
#
#
# import sys
# from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton, QLabel
#
# class Example(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()
#
#     def initUI(self):
#         self.setWindowTitle('ComboBox, LineEdit, and Button Example')
#         layout = QVBoxLayout()
#
#         # 创建一个水平布局来放置组件
#         hbox = QHBoxLayout()
#
#         # ComboBox
#         self.combo = QComboBox(self)
#         self.combo.addItem('Option 1')
#         self.combo.addItem('Option 2')
#         self.combo.addItem('Option 3')
#         hbox.addWidget(self.combo)
#
#         # LineEdit
#         self.line_edit = QLineEdit(self)
#         hbox.addWidget(self.line_edit)
#
#         # Button
#         self.button = QPushButton('Replace', self)
#         self.button.clicked.connect(self.onButtonClicked)
#         hbox.addWidget(self.button)
#
#         layout.addLayout(hbox)
#
#         self.setLayout(layout)
#
#     def onButtonClicked(self):
#         # 获取当前选中的ComboBox中的选项索引
#         current_index = self.combo.currentIndex()
#
#         # 获取LineEdit中的文本
#         new_text = self.line_edit.text()
#
#         # 将LineEdit中的文本替换到选中的ComboBox选项中
#         if current_index != -1:  # 确保有选中的选项
#             self.combo.setItemText(current_index, new_text)
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = Example()
#     ex.show()
#     sys.exit(app.exec_())

#
# import sys
# from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton
#
# class Example(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()
#
#     def initUI(self):
#         self.setWindowTitle('ComboBox and Button Example')
#         layout = QVBoxLayout()
#
#         # 创建一个水平布局来放置组件
#         hbox = QHBoxLayout()
#
#         # ComboBox
#         self.combo = QComboBox(self)
#         self.combo.addItem('Option 1')
#         self.combo.addItem('Option 2')
#         self.combo.addItem('Option 3')
#         hbox.addWidget(self.combo)
#
#         # LineEdit
#         self.line_edit = QLineEdit(self)
#         hbox.addWidget(self.line_edit)
#
#         # Button
#         self.button = QPushButton('Add Option', self)
#         self.button.clicked.connect(self.onButtonClicked)
#         hbox.addWidget(self.button)
#
#         layout.addLayout(hbox)
#
#         self.setLayout(layout)
#
#     def onButtonClicked(self):
#         # 获取LineEdit中的文本
#         new_option = self.line_edit.text()
#
#         # 将LineEdit中的文本作为新的选项添加到ComboBox中
#         self.combo.addItem(new_option)
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = Example()
#     ex.show()
#     sys.exit(app.exec_())
#
import sys
import multiprocessing
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication


class Worker(QThread):
    process_finished = pyqtSignal()

    def __init__(self):
        super().__init__()

    def run(self):
        # 启动子进程
        self.process = multiprocessing.Process(target=self.sub_process_func)
        self.process.start()

        # 等待子进程结束
        self.process.join()

        # 发送信号，通知主线程子进程已完成
        self.process_finished.emit()

    def sub_process_func(self):
        # 子进程的具体逻辑
        try:
            # 这里写子进程的代码
            pass
        except Exception as e:
            print(f"Exception in sub process: {e}")
            # 可以选择在这里重新启动进程
            self.restart_process()

    def restart_process(self):
        # 关闭旧进程
        if self.process.is_alive():
            self.process.terminate()
            self.process.join()

        # 启动新进程
        self.process = multiprocessing.Process(target=self.sub_process_func)
        self.process.start()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = Worker()
        self.worker.process_finished.connect(self.on_process_finished)
        self.worker.start()

    def on_process_finished(self):
        # 处理进程完成后的操作，比如更新界面或者重新启动进程
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())




