import PLC.plcWriteRead as plc_mc
import time as t
import pid_result as pid_r
import threading
import sys
from windows import QtUI #ui
from PLC.plcWriteRead import *#PLC
def plc_connect(ip="192.168.0.1", name='1200'):
    PLC = plc_mc.PLCWriteRead(ip, name)
    PLC.ConnectPlc()
    return PLC

def mc_control(PLC, point_set, mode, pid_pram, target_parm):
    PLC.PLC_RAS(point_set, mode, pid_pram, target_parm)

def mc_go_home(PLC):
    point_set = None
    pid_pram = None
    target_parm = None
    PLC.PLC_RAS(point_set, 0, pid_pram, target_parm)

def mc_move_to_point(PLC, point_set):
    pid_pram = None
    target_parm = None
    PLC.PLC_RAS(point_set, 1, pid_pram, target_parm)

state_lock = threading.Lock()
# 共享的state变量
state = 1
# arg_param = [pid_pram,target_parm,y,zf]
# def mc_follow_line_thread(PLC):##PID参数pid_pram: p i d dt max_acc max_vel  simulation_time  追踪目标参数target_parm: x V
#     global lock
#     global state
#     global arg_param
#     with lock:
#         if arg_param is not None:
#             while True:
#                 if state==1:
#                     state=0
#                     point_set = [0, arg_param[2], arg_param[3], 0, 0]  # [x,y,zf,none,none]
#                     PLC.PLC_RAS(point_set, 2, arg_param[0], arg_param[1])
#                     state=1
#                 else:
#                     pass
def mc_follow_line(PLC, pid_pram,target_parm,y,zf):##PID参数pid_pram: p i d dt max_acc max_vel  simulation_time  追踪目标参数target_parm: x V
    point_set = [0,y,zf,0,0]#[x,y,zf,none,none]
    PLC.PLC_RAS(point_set, 2, pid_pram, target_parm)

def mc_wait(PLC):
    point_set = None
    pid_pram = None
    target_parm = None
    PLC.PLC_RAS(point_set, 3, pid_pram, target_parm)
def mc_restart(PLC):
    PLC.PLC_restart()


def errormach_follow(x_p,x_n):#当前位置 目标位置
    errorpotion=x_p-x_n
    follow_time=3.5
    follow_longtime=4.5
    follow_shorttime=3
    pid_set=[]


    if    errorpotion<=-625:
        pid_set = [4.6, 0.15, 5.3, 0.1, 1.0, 0.8, follow_longtime]
    if -625<errorpotion<=-575:
        pid_set=[4.6,0.15,5.3,0.1, 1.0, 0.8, follow_longtime]
    if -575<errorpotion<=-525:
        pid_set=[4.6,0.15,3.9,0.1, 1.0, 0.8, follow_time]
    if -525<errorpotion<=-475:
        pid_set=[4.6,0.15,3.9,0.1, 1.0, 0.8,follow_time]
    if -475<errorpotion<=-425:
        pid_set=[4.6,0.15,3.2,0.1, 1.0, 0.8, follow_time]
    if -425<errorpotion<=-375:
        pid_set=[4.6,0.15,3.2,0.1, 1.0, 0.8, follow_time]
    if -375<errorpotion<=-325:
        pid_set=[9.0,0.12,5.0,0.1, 1.0, 0.8, follow_time]
    if -325<errorpotion<=-275:
        pid_set=[9.0,0.12,5.0,0.1, 1.0, 0.8, follow_time]
    if -275<errorpotion<=-225:
        pid_set=[9.0,0.12,5.0,0.1, 1.0, 0.8, follow_time]
    if -225<errorpotion<=-175:
        pid_set=[9.0,0.12,5.0,0.1, 1.0, 0.8, follow_shorttime]
    if -175<errorpotion<=-125:
        pid_set=[9.0,0.12,5.0,0.1, 1.0, 0.8,follow_shorttime]
    if -125<errorpotion<=-75:
        pid_set=[9.0,0.12,5.0,0.1, 1.0, 0.8, follow_shorttime]
    if -75 < errorpotion <= -25:
        pid_set=[9.0,0.12,5.0,0.1, 1.0, 0.8, follow_shorttime]
    if -25<errorpotion<=25:
        pid_set=[9.0,0.12,5.0,0.1, 1.0, 0.8, follow_shorttime]
    if 25<errorpotion<=75:
        pid_set =[ 9.0,0.12,5.0,0.1, 1.0, 0.8, follow_shorttime]
    if 75<errorpotion<=125:
        pid_set = [9.0,0.12,5.0,0.1, 1.0, 0.8,follow_shorttime]
    if 125<errorpotion<=175:
        pid_set = [9.0,0.12,5.0,0.1, 1.0, 0.8, follow_shorttime]
    if 175 < errorpotion <= 225:
        pid_set = [9, 0.12, 5.0, 0.1, 1.0, 0.8, follow_shorttime]
    if 225 < errorpotion <= 275:
        pid_set = [9.0,0.12,5.0,0.1, 1.0, 0.8, follow_shorttime]
    if 275 < errorpotion <= 325:
        pid_set = [9.0,0.12,5.0,0.1, 1.0, 0.8, follow_time]
    if 325 < errorpotion <= 375:
        pid_set = [9.0,0.12,5.0,0.1, 1.0, 0.8, follow_time]
    if 375 < errorpotion <= 425:
        pid_set = [9.0,0.12,5.0,0.1, 1.0, 0.8,follow_time]
    if 425 < errorpotion <= 475:
        pid_set = [9.5,0.12,5.0,0.1, 1.0, 0.8, follow_time]
    if 425 < errorpotion <= 475:
        pid_set = [9.5,0.12,5.0,0.1, 1.0, 0.8,  follow_time]
    if 475 < errorpotion <= 525:
        pid_set = [4.6,0.05,3.4,0.1, 1.0, 0.8, follow_time]
    if 525 < errorpotion <= 575:
        pid_set = [4.6,0.05,3.4,0.1, 1.0, 0.8, follow_longtime]
    if 575 < errorpotion <= 625:
        pid_set = [4.6,0.05,3.4,0.1, 1.0, 0.8, follow_longtime]
    if 625 < errorpotion <= 675:
        pid_set = [4.6,0.05,3.4,0.1, 1.0, 0.8,follow_longtime]
    if 675 < errorpotion <= 725:
        pid_set = [4.6,0.05,3.4,0.1, 1.0, 0.8, follow_longtime]
    if 725 < errorpotion <= 775:
        pid_set = [4.6,0.05,3.9,0.1, 1.0, 0.8, follow_longtime]
    if 775 < errorpotion <= 825:
        pid_set = [4.6,0.05,3.9,0.1, 1.0, 0.8, follow_longtime]
    if 825 < errorpotion <= 875:
        pid_set = [4.6,0.05,3.9,0.1, 1.0, 0.8, follow_longtime]
    if 875 < errorpotion <= 925:
        pid_set = [4.6,0.05,3.9,0.1, 1.0, 0.8, follow_longtime]
    if 925 < errorpotion <= 975:
        pid_set = [4.6,0.12,3.9,0.1, 1.0, 0.8, follow_longtime]
    if 975 < errorpotion <= 1025:
        pid_set = [4.6,0.12,3.9,0.1, 1.0, 0.8, follow_longtime]
    if 1025 < errorpotion <= 1075:
        pid_set = [4.0,0.12,3.9,0.1, 1.0, 0.8, follow_longtime]

    return pid_set

if __name__ == '__main__':
    PLC = plc_mc.PLCWriteRead("192.168.0.1", name='1200')
    PLC.ConnectPlc()
    # app = QtUI.QtWidgets.QApplication(sys.argv)
    # MainWindow = QtUI.MainWindow(PLC)
    # MainWindow.show()
    # sys.exit(app.exec_())
    # while True:
    #     mc_go_home()
    #     mc_move_to_point(point_set=[400,0,60,None,None])
    #     t.sleep(2)
    #     mc_follow_line([20,0.12,7.9,0.1, 1.0, 0.8, 4.0], [0.1, 0.1], 100, 0)
    #     t.sleep(2)
    # mc_go_home(PLC)
    #
    mc_move_to_point(PLC, point_set=[1050, 0, 0, None, None])
    t.sleep(8)
    mc_follow_line(PLC, [4.0,0.12,3.9,0.1, 1.0, 0.8,5.0], [0.1 , 0.1], 100, 0)
    print(1)
    pid_r.plot_pid_result()

#20 0.12 8.0 0.1 0.8 0.8 4.0
#

