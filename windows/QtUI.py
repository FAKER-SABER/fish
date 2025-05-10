import threading
import os
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QTime, QObject, pyqtSignal, QDateTime, QEventLoop
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QDialog,QMainWindow
from scipy.constants import golden
from PyQt5.QtWidgets import QApplication, QLabel
# from move_control import mc_control, mc_go_home, mc_move_to_point, mc_follow_line, mc_wait, plc_connect,errormach_follow
from windows.win import Ui_MainWindow  # 导入ui界面文件
from windows.winDia import Ui_Dialog
from windows import picture_rc
import PLC.plcWriteRead as plc_mc
import time as t
import pid_result as pid_r

class Worker(QObject):
    def __init__(self, plc):
        super().__init__()
        self.result_signal = pyqtSignal(str)
        # 用于控制线程是否暂停的标志
        self.paused = False
        # 用于线程间同步的事件对象
        self.pause_event = threading.Event()
        self.pause_event.set()
        self.PLC = plc

    def do_work(self):
        print("开始线程")
        global lock
        global fish_group
        global points_list
        global is_update
        global arg_param
        global plc
        while True:
            with lock:
                fish_group.get_points_list(points_list)
                plc.PLC_cov_vRead()
                print(plc.cov_v)
                fish_group.fish_list_update(plc.cov_v, plc.cov_vlast)
                print(f"获取最新鱼群列表{fish_group.fish_list},\n鱼数量{len(fish_group.fish_list)}")
                # print(points_list)
                if len(fish_group.fish_list) == 0:
                    print("没有鱼")
                    mc_move_to_point(plc, point_set=[0, 0, 0, None, None])


                else:
                    print(fish_group.fish_list)
                    fish_all = len(fish_group.fish_list)
                    delete_set = []

                    for fish_num in range(fish_all):
                        plc.PLC_cov_vRead()
                        fish_group.fish_list_update(plc.cov_v, plc.cov_vlast)
                        if fish_group.fish_list[fish_num][4] > 900:
                            fish_group.delete_fish(fish_num)
                            break
                        if 100 < fish_group.fish_list[fish_num][4] < 850:
                            print("进行整形")
                            pid_set = errormach_follow(plc.x_p, fish_group.fish_list[fish_num][4])
                            arg_param = [pid_set, [fish_group.fish_list[fish_num][4] / 1000, 0.120],
                                         fish_group.fish_list[fish_num][1] + 120, fish_group.fish_list[fish_num][2],
                                         fish_num]
                            is_update = 1
                            fish_group.delete_fish(fish_num)
                            break

                    fish_group.delete_fish(fish_num)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, plc):
        super().__init__()
        self.setupUi(self)  # 使用Ui_MainWindow.setupUi(self, self)来初始化UI
        self.PLC = plc
        self.mcflag=0



        self.pushButton_start.clicked.connect(self.start_SYSTEM)
        self.pushButton_stop.clicked.connect(self.stop_SYSTEM)
        self.pushButton_wait.clicked.connect(self.wait_SYSTEM)

        # 连接 QComboBox 的信号 activated 到槽函数 onActivated


        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.label_show_time)
        self.timer1.start(1000)

        self.timer2 = QTimer(self)
        self.timer2.timeout.connect(self.update_image)

        self.timer3 = QTimer(self)
        self.timer3.timeout.connect(self.update_window_data)
        self.timer3.start(5000)

    def start_SYSTEM(self):
        print("开始线程")
        self.worker = Worker(self.PLC)
        self.worker.paused = False
        self.worker.pause_event.set()
        # self.worker.result_signal.connect(self.handle_result)
        self.thread = threading.Thread(target=self.worker.do_work)
        self.thread.start()





        return 0
    def stop_SYSTEM(self):
        mc_wait(self.PLC)
    def wait_SYSTEM(self):
        self.worker.paused = True
        self.worker.pause_event.clear()
        self.pushButton_stop.setEnabled(False)
        self.pushButton_start.setEnabled(True)

        return 0
        # global window_flag
        # window_flag[2]=1
        # self.PLC.ConnectPlc()
        # # 先将系统停下
        # self.PLC.WritePlcMK(2, 0, form='bit', bit=5)
        # # 擦除相关数据区的数据
        # # 1、将数据写入标志和数据写入完成标志擦除
        # self.PLC.WritePlcMK(2, 0, form='bit', bit=6)
        # self.PLC.WritePlcMK(2, 0, form='bit', bit=7)
        # # 将程序中会被set置位的m线圈进行复位
        # self.PLC.WritePlcMK(4, 0, form='bit', bit=2)
        # self.PLC.WritePlcMK(4, 0, form='bit', bit=3)
        # self.PLC.WritePlcMK(4, 0, form='bit', bit=4)
        # # 2、擦除存储XY轴坐标数据的DB数据块
        # for i in range(25):
        #     # 想PLC写入目标的X轴坐标
        #     self.PLC.WritePlcDB(12, 4 * i, 0.0, form='real')
        #     # 想PLC写入目标的Y轴坐标
        #     self.PLC.WritePlcDB(12, 4 * i + 100, 0.0, form='real')
        #     # Z轴旋转角度
        #     self.PLC.WritePlcDB(12, 4 * i + 200, 0.0, form='real')
        #     # X轴随动
        #     self.PLC.WritePlcDB(12, 4 * i + 300, 0.0, form='real')
        # self.PLC.WritePlcDB(12, 400, 0, form='Uint')
        # self.PLC.WritePlcDB(12, 402, 0, form='Uint')
        # self.PLC.WritePlcDB(12, 404, 0, form='Uint')
        # self.PLC.WritePlcDB(12, 406, 0, form='Uint')
        # self.PLC.WritePlcDB(12, 408, 0, form='Dint')
        #
        # self.PLC.disconnectPlc()
        # print("start_shuaxin_func已运行")

    def label_show_time(self):
        datetime = QDateTime.currentDateTime()
        current_date = datetime.toString('yyyy-MM-dd')
        current_time = datetime.toString('hh:mm:ss')
        self.label_riqi_show.setText(current_date)
        self.label_time_show.setText(current_time)

    def update_window_data(self):
        pass
        return 0
        # # 实时获取多进程全局变量的值
        # global window_flag
        # data = window_flag
        # if data[0] == 0:
        #     print("工业相机无法连接")
        #     self.label_15.setText("工业相机无法连接")
        #     self.label_15.setStyleSheet("background-color:rgb(255, 0, 0);")
        #     font = QFont("宋体", 16)
        #     self.label_15.setFont(font)
        #     self.label_sys_status.setText("系统硬件出错，请在硬件管理中排查")
        #     self.label_sys_status.setStyleSheet("background-color:rgb(255, 0, 0);")
        #     font = QFont("宋体", 22)
        #     self.label_sys_status.setFont(font)
        # elif data[0] == 1:
        #     self.label_15.setText("工业相机正常")
        #     self.label_15.setStyleSheet("background-color:rgb(0, 255， 0);")
        #     font = QFont("宋体", 16)
        #     self.label_15.setFont(font)
        # if data[1] == 0:
        #     print("PLC无法连接")
        #     self.label_12.setText("PLC无法连接")
        #     self.label_12.setStyleSheet("background-color:rgb(255, 0, 0);")
        #     font = QFont("宋体", 16)
        #     self.label_12.setFont(font)
        #     self.label_sys_status.setText("系统硬件出错，请在硬件管理中排查")
        #     self.label_sys_status.setStyleSheet("background-color:rgb(255, 0, 0);")
        #     font = QFont("宋体", 22)
        #     self.label_sys_status.setFont(font)
        # elif data[1] == 1:
        #     self.label_12.setText("工业相机正常")
        #     self.label_12.setStyleSheet("background-color:rgb(0, 255， 0);")
        #     font = QFont("宋体", 16)
        #     self.label_12.setFont(font)
        # if data[0] == 1 and data[1] == 1:
        #     self.label_sys_status.setText("海鱼整形系统正常运行")
        #     self.label_sys_status.setStyleSheet("background-color:rgb(0, 255, 0);")
        #     font = QFont("宋体", 22)
        #     self.label_sys_status.setFont(font)

    def update_image(self):
        pass
        return 0

    # def load_item(self):
    #     # if os.path.exists('./windows/海鱼型号.txt'):
    #     with open('./windows/海鱼型号.txt', 'r') as file:
    #         for line in file:
    #             item = line.strip()
    #             data = item.split(',')
    #             self.comboBox.addItem(data[0])

    def onActivated(self, text):
        # index = self.comboBox.findText(text)
        # print(index)
        # if os.path.exists('./windows/海鱼型号.txt'):
        with open('./windows/海鱼型号.txt', 'r') as file:
            for line in file:
                data = line.strip()
                data = data.split(',')
                if data[0] == text:
                    self.label_19.setText(data[1]+'mm')
                    self.label_21.setText(data[2]+'mm')
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())