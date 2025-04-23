# -*- coding: utf-8 -*-
import sys
import cv2
import time
import threading
import numpy as np
from PyQt5.QtGui import QIcon
# 导入自定义模块
# from windows import QtUI #ui
from PLC.plcWriteRead import *#PLC
from recognition import recognize_ellipses
from hik_camera import call_back_get_image, start_grab_and_get_data_size, close_and_destroy_device, set_Value, \
    get_Value, image_control
from MvImport.MvCameraControl_class import *

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
    set_Value(cam, param_type="float_value", node_name="ExposureTime", node_value=600)  # 曝光时间
    set_Value(cam, param_type="float_value", node_name="Gain", node_value=17.9)  # 增益值
    set_Value(cam, param_type="float_value", node_name="AcquisitionFrameRate", node_value=0.2)  # 采集帧率
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


#生成窗口对象
# MainWindow = QtUI.MainWindow()
#window标志位
window_flag=[0,0,0]
points_list = []
lock = threading.Lock()
#相机
camera_mode = 'hik'  # 'test':测试模式,'hik':海康相机,'video':USB相机（videocapture）
points_list = []

camera_image = None
if camera_mode == 'test':
    camera_image = cv2.imread('images/11041.jpg')
elif camera_mode == 'hik':
    thread_camera = threading.Thread(target=hik_camera_get, daemon=True)
    thread_camera.start()


while camera_image is None:
    window_flag[0] = 0
    print("等待图像获取...")
    time.sleep(0.5)


while True:
    time.sleep(1)
    with lock:
        print(points_list)
# #PLC
# PLC = PLCWriteRead("192.168.0.1", name='1200')
# plcifc=PLC.ConnectPlc()
# while  plcifc==False:
#     print("未连接PLC")
#     window_flag[1]=0
#     plcifc = PLC.ConnectPlc()
#     MainWindow.show()
#     time.sleep(1)
# window_flag[1] = 1
# PLC_SET= []


#     img_copy = camera_image.copy()
#     ts = time.time()
#     end_time = ts + 5
#     # 获取海鱼在拍摄时相对于夹爪坐标系的坐标
#     # points_list = recognize_ellipses(img_copy, ts, [])
#     recognize_ellipses(img_copy, ts, [])
#     # PLC_SET=[0,points_list[0][1],points_list[0][2],points_list[0][3]]
#
#     # PLC.PLC_RAS(PLC_SET)
#     # print(points_list)
#     # point_offset = (X_PLC, Y_PLC, avg_angle, ts)
#     # XYCAM:47.1363099068624, 137.713521617154
#
#     # 对坐标实时更新并写进plc
#
#
#
#     # MainWindow.show()
#     # PLC.PLC_RAS()
#     # while time.time() < end_time:
#     #     continue









