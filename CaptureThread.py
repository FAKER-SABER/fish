# -*- coding: utf-8 -*-
import sys
import cv2
import time
import threading
import numpy as np
from PyQt5.QtGui import QIcon
# 导入自定义模块
from windows import QtUI #ui
from PLC.plcWriteRead import *#PLC

from recognition import recognize_ellipses
from hik_camera import call_back_get_image, start_grab_and_get_data_size, close_and_destroy_device, set_Value, \
    get_Value, image_control
from MvImport.MvCameraControl_class import *

from move_control import mc_control, mc_go_home, mc_move_to_point, mc_follow_line, mc_wait, plc_connect,errormach_follow
#生成窗口对象

class WorkState:
    IDLE = 0
    RUNNING = 1
    PAUSED = 2
    STOPPED = 3

class CaptureThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.workState = False

    def run(self):
        # 在这里定义你的任务代码
        print("线程正在运行")
        while True:
            if self.workState == WorkState.RUNNING:


                pass
            elif self.workState == WorkState.PAUSED:
                pass
            elif self.workState == WorkState.STOPPED:
                break
            # 在这里定义你的任务代码
            # 读取图像
            continue

    def pause(self):
        self.workState = WorkState.PAUSED
        # 在这里定义暂停任务的代码
        print("线程暂停")

    def resume(self):
        self.workState = WorkState.RUNNING
        # 在这里定义恢复任务的代码
        print("线程恢复")
    def stop(self):
        self.workState = WorkState.STOPPED
        # 在这里定义停止任务的代码
        print("线程停止")