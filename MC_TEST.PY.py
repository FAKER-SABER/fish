import PLC.plcWriteRead as plc_mc
import time as t
import pid_result as pid_r

def mc_control(point_set, mode, pid_pram, target_parm):
    PLC.PLC_RAS(point_set, mode, pid_pram, target_parm)

def mc_go_home():
    point_set = None
    pid_pram = None
    target_parm = None
    PLC.PLC_RAS(point_set, 0, pid_pram, target_parm)

def mc_move_to_point(point_set):
    pid_pram = None
    target_parm = None
    PLC.PLC_RAS(point_set, 1, pid_pram, target_parm)

def mc_follow_line(pid_pram,target_parm,y,zf):##PID参数pid_pram: p i d dt max_acc max_vel  simulation_time  追踪目标参数target_parm: x V
    point_set = [0,y,zf,0,0]#[x,y,zf,none,none]
    PLC.PLC_RAS(point_set, 2, pid_pram, target_parm)

def mc_wait():
    point_set = None
    pid_pram = None
    target_parm = None
    PLC.PLC_RAS(point_set, 3, pid_pram, target_parm)

if __name__ == '__main__':
    PLC = plc_mc.PLCWriteRead("192.168.0.1", name='1200')
    PLC.ConnectPlc()
    # while True:
    #     mc_go_home()
    #     mc_move_to_point(point_set=[400,0,60,None,None])
    #     t.sleep(2)
    #     mc_follow_line([20,0.12,7.9,0.1, 1.0, 0.8, 4.0], [0.1, 0.1], 100, 0)
    #     t.sleep(2)
    mc_go_home()

    mc_move_to_point(point_set=[600, 0, 60, None, None])
    t.sleep(3)
    mc_follow_line([11,0.3,5.5,0.1, 1.0, 0.8, 4.0], [0.1, 0.1], 100, 0)
    pid_r.plot_pid_result()

#20 0.12 8.0 0.1 0.8 0.8 4.0
#

