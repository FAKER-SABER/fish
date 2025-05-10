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
points_list = []
lock = threading.Lock()
arg_param = []
is_update=0

#生成窗口对象

plc = plc_connect()
plc.PLC_cov_vRead()
mc_go_home(plc)
mc_move_to_point(plc,point_set=[0, 0, 0, None, None])
#window标志位


# 海康相机图像获取线程
def hik_camera_get():
    # 获得设备信息
    global camera_image
    global points_list
    deviceList = MV_CC_DEVICE_INFO_LIST()
    tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE

    # ch:枚举设备 | en:Enum device
    # nTLayerType [IN] 枚举传输层 ，pstDevList [OUT] 设备列表
    while 1:
        ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
        if ret != 0:
            print("enum devices fail! ret[0x%x]" % ret)
            # sys.exit()

        if deviceList.nDeviceNum == 0:
            print("find no device!")
            # sys.exit()
        else:
            print("Find %d devices!" % deviceList.nDeviceNum)
            break

    for i in range(0, deviceList.nDeviceNum):
        mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
        if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
            print("\ngige device: [%d]" % i)
            # 输出设备名字
            strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
                strModeName = strModeName + chr(per)
            print("device model name: %s" % strModeName)
            # 输出设备ID
            nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
            nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
            nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
            nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
            print("current ip: %d.%d.%d.%d\n" % (nip1, nip2, nip3, nip4))
        # 输出USB接口的信息
        elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
            print("\nu3v device: [%d]" % i)
            strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
                if per == 0:
                    break
                strModeName = strModeName + chr(per)
            print("device model name: %s" % strModeName)

            strSerialNumber = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                if per == 0:
                    break
                strSerialNumber = strSerialNumber + chr(per)
            print("user serial number: %s" % strSerialNumber)
    # 手动选择设备
    # nConnectionNum = input("please input the number of the device to connect:")
    # 自动选择设备
    nConnectionNum = '0'
    if int(nConnectionNum) >= deviceList.nDeviceNum:
        print("intput error!")
        sys.exit()

    # ch:创建相机实例 | en:Creat Camera Object
    cam = MvCamera()

    # ch:选择设备并创建句柄 | en:Select device and create handle
    # cast(typ, val)，这个函数是为了检查val变量是typ类型的，但是这个cast函数不做检查，直接返回val
    stDeviceList = cast(deviceList.pDeviceInfo[int(nConnectionNum)], POINTER(MV_CC_DEVICE_INFO)).contents

    ret = cam.MV_CC_CreateHandle(stDeviceList)
    if ret != 0:
        print("create handle fail! ret[0x%x]" % ret)
        sys.exit()

    # ch:打开设备 | en:Open device
    ret = cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
    if ret != 0:
        print("open device fail! ret[0x%x]" % ret)
        sys.exit()

    print(get_Value(cam, param_type="float_value", node_name="ExposureTime"),
          get_Value(cam, param_type="float_value", node_name="Gain"),
          get_Value(cam, param_type="enum_value", node_name="TriggerMode"),
          get_Value(cam, param_type="float_value", node_name="AcquisitionFrameRate"))

    # 设置设备的一些参数
    set_Value(cam, param_type="float_value", node_name="ExposureTime", node_value=1060)  # 曝光时间
    set_Value(cam, param_type="float_value", node_name="Gain", node_value=17.9)  # 增益值
    # set_Value(cam, param_type="float_value", node_name="AcquisitionFrameRate", node_value=0.5)  # 采集帧率
    set_Value(cam, param_type="float_value", node_name="AcquisitionFrameRate", node_value=1.0)  # 采集帧率

    # 开启设备取流
    start_grab_and_get_data_size(cam)
    # 主动取流方式抓取图像
    stParam = MVCC_INTVALUE_EX()

    memset(byref(stParam), 0, sizeof(MVCC_INTVALUE_EX))
    ret = cam.MV_CC_GetIntValueEx("PayloadSize", stParam)
    if ret != 0:
        print("get payload size fail! ret[0x%x]" % ret)
        sys.exit()
    nDataSize = stParam.nCurValue
    pData = (c_ubyte * nDataSize)()
    stFrameInfo = MV_FRAME_OUT_INFO_EX()

    memset(byref(stFrameInfo), 0, sizeof(stFrameInfo))
    i = 0  # 初始化保存图片的计数器

    while True:
        ret = cam.MV_CC_GetOneFrameTimeout(pData, nDataSize, stFrameInfo, 1000)
        if ret == 0:
            image = np.asarray(pData)
            # 处理海康相机的图像格式为OPENCV处理的格式，BGR格式
            camera_image = image_control(data=image, stFrameInfo=stFrameInfo)
            # 保存图片
            cv2.imwrite(f"./images/image.jpg", camera_image)
            # cv2.imwrite(f"./images/image_{i}.jpg", camera_image)
            i += 1  # 每保存一次图片，计数器加1
            # print("save image.jpg", i)
            ts = time.time()
            # img_copy = cv2.imread(f"./images/image_{i}.jpg", cv2.IMREAD_COLOR)
            img_copy = cv2.imread(f"./images/image.jpg", cv2.IMREAD_COLOR)
            with lock:

                points_list = recognize_ellipses(img_copy, ts, [])
                print(f"计算完成,结果{points_list}")

            # 注释point_offset = (Y_world, X_world, angle, ts)


        else:
            print("no data[0x%x]" % ret)
        time.sleep(0.016)

def mc_follow_line_thread(PLC):##PID参数pid_pram: p i d dt max_acc max_vel  simulation_time  追踪目标参数target_parm: x V
    global lock
    global is_update
    global fish_group
    global arg_param
    global delete_set

    while True:
        with lock:

            if is_update:
                print("work")
                point_set = [0, arg_param[2], arg_param[3], 0, 0]  # [x,y,zf,none,none]
                PLC.PLC_RAS(point_set, 2, arg_param[0], arg_param[1])


                is_update = 0
            else:
                print("don't work")
                t.sleep(0.1)
class fish_grab():
    def __init__(self):
        self.last_points_list = []
        self.fish_list = []



    def get_points_list(self,points_list):
        if points_list is not self.last_points_list:


            for point in points_list:
                fish_total =len(self.fish_list)
                point = (point[0], point[1], point[2], point[3], point[0], point[1], point[3], 0) # x y theta time x_n y_n ct num  0
                if fish_total == 0:

                    self.fish_list.append(point)
                    print("first")

                else:

                    for fi in range(0,fish_total):
                        if abs(point[1]-self.fish_list[fi][1]) <= 10 and abs(point[4]-self.fish_list[fi][4]) <= 250:
                            print(fi,"same")
                            self.fish_list[fi] = point

                            break
                        else:

                            if fi == fish_total-1:
                                self.fish_list.append(point)
                                print("new")
            self.last_points_list = points_list
        # print(f"获取最新点位列表{self.last_points_list}")
        #print(f"获取最新鱼群列表{self.fish_list},\n鱼数量{self.fish_list.__len__()}")
        return 1

    def fish_list_update(self,scov_v,scov_vlast,pulse_now=0):
        current_time = time.time()
        print(f"当前时间{current_time}")
        print(len(self.fish_list))
        if len(self.fish_list) ==0:
            print("没有鱼")
            return 1
        else:
            fish_total= len(self.fish_list)
            fish=[]
            for fi in range(fish_total):
                fish = self.fish_list[fi]
                self.fish_list[fi] = (
                    fish[0],  # x
                    fish[1],  # y
                    fish[2],  # theta
                    fish[3],  # time
                    fish[4]+(scov_v*0.7+scov_vlast*0.36)*(current_time-fish[6])*1000,  # x_n
                    # fish[4] + (scov_v * 0.5 + scov_vlast * 0.5) * (current_time - fish[6]) * 1000,  # x_n
                    fish[5],  # y_n（保持不变）
                    current_time,  # 更新时间
                    0  # state

                )
        return self.fish_list

    def delete_fish(self, num_fish):
        fish_total= len(self.fish_list)
        # 检查索引是否有效
        if num_fish in range(fish_total):
            # 删除指定索引的鱼
            del self.fish_list[num_fish]
            print(f"成功删除索引为 {num_fish} 的鱼")
        else:
            print(f"索引 {num_fish} 超出范围，无法删除")
        return 1



#相机
camera_mode = 'hik'  # 'test':测试模式,'hik':海康相机,'video':USB相机（videocapture）

fish_group = fish_grab()
points_list = []
# app = QtUI.QtWidgets.QApplication(sys.argv)
# MainWindow = QtUI.MainWindow(plc)

camera_image = None
if camera_mode == 'test':
    camera_image = cv2.imread('images/11041.jpg')
elif camera_mode == 'hik':
    thread_camera = threading.Thread(target=hik_camera_get, daemon=True)
    thread_camera.start()


while camera_image is None:

    print("等待图像获取...")
    time.sleep(0.5)

# MainWindow.show()

# 共享的state变量

follow_thread = threading.Thread(target=mc_follow_line_thread, args=(plc, ), daemon=True)
follow_thread.start()

while True:


    # sys.exit(app.exec_())
    time.sleep(0.5)
    with lock:
        fish_group.get_points_list(points_list)
        plc.PLC_cov_vRead()
        print(plc.cov_v)
        fish_group.fish_list_update(plc.cov_v,plc.cov_vlast)
        print(f"获取最新鱼群列表{fish_group.fish_list},\n鱼数量{len(fish_group.fish_list)}")
        # print(points_list)
        if len(fish_group.fish_list) ==0:
            print("没有鱼")
            mc_move_to_point(plc, point_set=[0, 0, 0, None, None])


        else:
            print(fish_group.fish_list)
            fish_all= len(fish_group.fish_list)
            delete_set=[]

            for fish_num in range(fish_all):
                plc.PLC_cov_vRead()
                fish_group.fish_list_update(plc.cov_v, plc.cov_vlast)
                if fish_group.fish_list[fish_num][4] > 900:
                    fish_group.delete_fish(fish_num)
                    break
                if 100 < fish_group.fish_list[fish_num][4] < 850 :

                    print("进行整形")
                    pid_set = errormach_follow(plc.x_p, fish_group.fish_list[fish_num][4])
                    arg_param =[pid_set, [fish_group.fish_list[fish_num][4]/1000, 0.120],  fish_group.fish_list[fish_num][1]+120,  fish_group.fish_list[fish_num][2],fish_num]
                    is_update = 1
                    fish_group.delete_fish(fish_num)
                    break

            fish_group.delete_fish(fish_num)