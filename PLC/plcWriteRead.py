from snap7 import util, client
import time as t
from func_code import pid_real as pid_c
import struct



import pandas as pd
from datetime import datetime
import os

# from contral.contral import  *
# my_plc = client.Client()  # 建立一个客户端对象
# my_plc.set_connection_type(3)  # 如果是200smart,必须有此段代码。1200，1500可以不写。
# my_plc.connect("192.168.2.1", 0, 1)  # 连接plc,参数分别为ip ,卡号,槽号。200smart为0和1
#
# state = my_plc.get_connected()  # 用来判读是否连接成功 返回值为true 和false
# print(state)
#
#
# # 注意，这里的参数有坑，最新的snap7协议是这样写，后面1代表V区，0代表起始地址，10代表字节数量
# # 注意，这里0对应VB0,1对应vb1以此类推。
# data = my_plc.read_area(client.Areas.DB, 1, 100, 50)
#
# my_data = util.get_byte(data, 4)
# print(my_data)
# n = util.get_byte(data, 0)
# print(n)
#
#
# my_plc.disconnect()  # 断开连接
# my_plc.destroy()  # 销毁客户端对象


class PLCWriteRead:
    def __init__(self, ip, name=''):
        self.PLC = client.Client()
        self.ip = ip
        self.name = name
        # self.rack = rack
        # self.slot = slot
        self.foundname(name)
        self.x_rP = 0
        self.x_aP = 4
        self.y_rP = 8
        self.y_aP = 12
        self.zf_rP = 16
        self.theta = 20
        self.target_xVP = 24
        self.last_xVP = 28
        self.x_PP = 32
        self.x_VP = 36
        self.y_PP = 40
        self.y_VP = 44
        self.cov_VP = 48
        self.pulseP=64
        self.pulse_highV=68
        self.x_runb = 6
        self.y_runb = 4
        self.zf_runb = 5
        self.getch_runb = 3
        self.follow_runb = 2
        self.gohome_runb = 0

        self.read_Byte = 11
        self.write_Byte = 12


        self.cov_v=0.1
        self.cov_vlast=0.1
        self.ki=0.3
        self.ks = 0.7
        self.x_v=0
        self.x_p=0
        self.pulse=0
    def foundname(self, name):
        if name == '200smart':
            self.rackandslot = [0, 1]
        elif name == '300':
            self.rackandslot = [0, 2]
        elif name == '1200':
            self.rackandslot = [0, 0]
        elif name == '1500':
            self.rackandslot = [0, 1]
        else:
            print("PLC型号输入错误")

    def ConnectPlc(self):
        self.PLC = client.Client()
        self.PLC.connect(self.ip, self.rackandslot[0], self.rackandslot[1])  # 连接plc,参数分别为ip ,卡号,槽号。200smart为0和1
        state = self.PLC.get_connected()  # 用来判读是否连接成功 返回值为true 和false
        print(state)
        self.WritePlcMK(2, 1, form='bit', bit=6)
        return state
    def ReadPlcMK(self, begin_place, long):
        bytes = self.PLC.read_area(client.Areas.MK, 0, begin_place, long)
        # print(bytes)
        # data = util.get_byte(bytes, 0)
        # print("data=", data)
        # self.PLC.write_area(client.Areas.MK, 0, begin_place, int.to_bytes(199, 1, 'big'))
        # bytes1 = self.PLC.read_area(client.Areas.MK, 0, begin_place, 1)
        # # print(bytes)
        # data1 = util.get_byte(bytes1, 0)
        # print("data1=", data1)
        # # 要写入的数据
        # data_to_write = b'\x11\x22\x33\x44'  # 例如，写入四个字节的数据
        #
        # # 写入数据到 M 区域的地址 100
        # self.PLC.write_area(client.Areas.MK, 0, 100, data_to_write)
        #self.PLC.write_area(client.Areas.MK, 0, 11, b'\xc9')

        return bytes

    def WritePlcMK(self, begin_place, data, form='', bit=0):
        if form == 'bit':
            bytes = self.PLC.read_area(client.Areas.MK, 0, begin_place, 1)
            # 三个零，第一个是对字节的索引，第二个是对位的索引，第三个是要写入的值
            util.set_bool(bytes, 0, bit, data)
            self.PLC.write_area(client.Areas.MK, 0, begin_place, bytes)
        elif form == 'byte':
            bytes = self.PLC.read_area(client.Areas.MK, 0, begin_place, 1)
            # 三个零，第一个是对字节的索引，第二个是对位的索引，第三个是要写入的值
            util.set_byte(bytes, 0, data)
            self.PLC.write_area(client.Areas.MK, 0, begin_place, bytes)
        elif form == 'word':
            bytes = self.PLC.read_area(client.Areas.MK, 0, begin_place, 2)
            # 三个零，第一个是对字节的索引，第二个是对位的索引，第三个是要写入的值
            util.set_word(bytes, 0, data)
            self.PLC.write_area(client.Areas.MK, 0, begin_place, bytes)
        elif form == 'dword':
            bytes = self.PLC.read_area(client.Areas.MK, 0, begin_place, 4)
            # 三个零，第一个是对字节的索引，第二个是对位的索引，第三个是要写入的值
            util.set_dword(bytes, 0, data)
            self.PLC.write_area(client.Areas.MK, 0, begin_place, bytes)

    def ReadPlcDB(self, DBindex: int, begin_place: int, long: int, form: str = '', bitindex: int = 0,
                  byteindex: int = 0, wordindex: int = 0, dwordindex: int = 0):
        bytes = self.PLC.db_read(DBindex, begin_place, long)

        if form == '':
            return [util.get_byte(bytes, i) for i in range(long)]
        elif form == 'bit':
            return util.get_bool(bytes, begin_place, bitindex)
        elif form == 'byte':
            return util.get_byte(bytes, byteindex)
        elif form == 'word':
            return util.get_word(bytes, wordindex)
        elif form == 'dword':
            return util.get_dword(bytes, dwordindex)
        elif form == 'real':
            # 直接读取 4 个字节，不依赖外部传入的 long 参数
            real_bytes = self.PLC.db_read(DBindex, begin_place, 4)
            return struct.unpack('>f', real_bytes)[0]  # 大端字节序
        else:
            raise TypeError("Invalid data type form.")

    def WritePlcDB(self, DBindex, begin_place, data, form=''):
        if form == 'real':
            realData = bytearray(4)
            util.set_real(realData, 0, data)
            self.PLC.db_write(DBindex, begin_place, realData)
        elif form == 'byte':
            realData = bytearray(1)
            util.set_byte(realData, 0, data)
            self.PLC.db_write(DBindex, begin_place, realData)
        elif form == 'Uint':
            realData = bytearray(2)
            util.set_uint(realData, 0, data)
            self.PLC.db_write(DBindex, begin_place, realData)
        elif form == 'Dint':
            realData = bytearray(4)
            util.set_dint(realData, 0, data)
            self.PLC.db_write(DBindex, begin_place, realData)


    def ReadPlcV(self, begin_place, long):
        # data = self.PLC.read_area(self.area, dbnumber=1, begin_place, long)
        # dbnumber=1表示读取V区
        data = self.PLC.read_area(client.Areas.DB, 1, begin_place, long)
        return data

    def WritePlcVB(self, data, begin_place):
        bytes = self.PLC.read_area(client.Areas.DB, 1, begin_place, 1)  # 说明 smart200 的V区要填写1，0代表VB0
        # util.set_bool(bytes, 0, 0, 0)
        util.set_byte(bytes, 0, data)
        self.PLC.write_area(client.Areas.DB, 1, begin_place, bytes)  # 说明 smart200 的V区要填写1，0代表VB0
        val = self.PLC.read_area(client.Areas.DB, 1, begin_place, 1)  # 说明 smart200 的V区要填写1，0代表VB0
        value = util.get_byte(val, 0)
        print(value)
        print("完成所有数据写入")

    def WritePlcVD(self, data, begin_place):
        bytes = self.PLC.read_area(client.Areas.DB, 1, begin_place, 4)  # 说明 smart200 的V区要填写1，0代表VB0
        # util.set_bool(bytes, 0, 0, 0)
        util.set_dword(bytes, 0, data)
        self.PLC.write_area(client.Areas.DB, 1, begin_place, bytes)  # 说明 smart200 的V区要填写1，0代表VB0
        val = self.PLC.read_area(client.Areas.DB, 1, begin_place, 4)  # 说明 smart200 的V区要填写1，0代表VB0
        value = util.get_dword(val, 0)
        print(value)
        print("完成所有数据写入")

    def WritePlcVDs(self, data, begin_place):
        i = 0
        for value_1 in data:
            bytes = self.PLC.read_area(client.Areas.DB, 1, begin_place+4*i, 4)  # 说明 smart200 的V区要填写1，0代表VB0
            # util.set_bool(bytes, 0, 0, 0)
            print(value_1)
            util.set_dword(bytes, 0, value_1)
            self.PLC.write_area(client.Areas.DB, 1, begin_place+4*i, bytes)  # 说明 smart200 的V区要填写1，0代表VB0
            i = i + 1
        # 测试数据是否正确写入进PLC，也可以通过PLC直接查看对应地址的值是多少，确定是否正确写入
        # val = self.PLC.read_area(client.Areas.DB, 1, begin_place, 4*long)  # 说明 smart200 的V区要填写1，0代表VB0
        # i = 0
        # while long:
        #     value = util.get_dword(val, 4*i)
        #     print(value)
        #     i = i+1
        #     long = long-1
        print("完成所有数据写入")

    def disconnectPlc(self):
        self.PLC.disconnect()  # 断开连接
        self.PLC.destroy()  # 销毁客户端对象

    def X_RUN(self,target_xap):
        # 向PLC写入目标的X轴坐标
        self.WritePlcDB(13, self.x_aP, target_xap+100, form='real')
        self.WritePlcMK(12, 1, form='bit', bit=self.x_runb)

    def Y_RUN(self, target_yap):
            # 向PLC写入目标的Y轴坐标
        self.WritePlcDB(13, self.y_aP, target_yap+200, form='real')
        self.WritePlcMK(12, 1, form='bit', bit=self.y_runb)

    def ZF_RUN(self, target_zap):
            # 向PLC写入目标的ZF轴坐标
        self.WritePlcDB(13, self.theta, target_zap, form='real')
        self.WritePlcMK(12, 1, form='bit', bit=self.zf_runb)
    def getch_RUN(self):
        #执行整形
        self.WritePlcMK(12, 1, form='bit', bit=self.getch_runb)
        print("getch_RUN")

    def gohome_RUN(self):
    # 执行回原点
        self.WritePlcMK(12, 1, form='bit', bit=self.gohome_runb)
    def follow_RUN(self,PID_PARM,target_parm):
        #######################################
        ###############pid控制#######
        ###################
        #def follow_RUN(self,PID_PARM,target_parm):
        # PID_PARM = []
        ###################
        # 初始化参数
        #执行跟随
        
        self.WritePlcMK(12, 1, form='bit', bit=self.follow_runb)
        pid = pid_c.PIDController(
                    kp=PID_PARM[0],
                    ki=PID_PARM[1],
                    kd=PID_PARM[2],
                    dt=PID_PARM[3],
                    max_accel=PID_PARM[4],
                    max_vel=PID_PARM[5]
                    )   

        target = pid_c.Target(
                    y_initial=target_parm[0]##传送带运行正方向的海鱼位置
                    ,
                    v_initial=target_parm[1]
                )
        simulation_time = PID_PARM[6]  # 秒
        getch_time =1 # 秒
        sample_interval = pid.dt
        start_time = t.time()
        # 用于保存结果的列表
        results = []
        time_0=t.time()
        error = 0.1
        n=0
        z_f = 0
        while (t.time() - start_time) < simulation_time:
            # 获取当前目标位置（带时间同步的实时更新）
            if abs(error) < 0.02 and n == 0 and z_f == 1:
                self.getch_RUN()
                n = 1
            target_pos = target.get_pos()
            show_time = t.time()
            x_p = self.ReadPlcDB(13, 32, 1, form='real') / 1000
            x_v = self.ReadPlcDB(13, 36, 1, form='real') / 1000
            PLC_state = self.PLC_bitread()
            # print(PLC_state)
            z_f = PLC_state[12][8]
            # print(z_f)
            # 获取执行器状态
            current_pos, current_vel = x_p, x_v
            # print(x_p, x_v)  # 输出浮点数

            # 执行PID控制计算（current_pos/vel由外部系统反馈）
            control_vel = pid.update(target_pos, current_pos, current_vel)
            error = target_pos - current_pos
            # 更新速度
            self.WritePlcDB(13, 24, (control_vel * 1000), form='real')

            # 结果显示
            # print(
            #     f"当前时间: {show_time:.4f}, "
            #     f"目标位置: {target_pos:.4f}, "
            #     f"当前位置: {current_pos:.4f}, "
            #     f"当前速度: {current_vel:.4f}, "
            #     f"控制速度: {control_vel:.4f}"
            # )
            results.append({
                        "Time": show_time-time_0,
                        "Target Position": target_pos,
                        "Current Position": current_pos,
                        "Current Velocity": current_vel,
                        "Control Velocity": control_vel,
                        "error": target_pos - current_pos
                    })
            # 保持控制周期（硬件实现时需要精确计时）
            t.sleep(max(0, sample_interval - (t.time() % sample_interval)))

            # 将结果保存到 Excel 文件
        df = pd.DataFrame(results)
        df.to_excel("pid_control_results.xlsx", index=False)
        print("程序结束，结果已保存到 pid_control_results.xlsx")
        # self.WritePlcMK(12, 0, form='bit', bit=7)
        self.WritePlcDB(13, 24, 0, form='real')
         
    def follow_STOP(self):
        # 停止跟随
        self.WritePlcDB(13, self.target_xVP, 0, form='real')
        self.WritePlcMK(12, 0, form='bit', bit=self.follow_runb)
        
    def PLC_bitreset(self):
        # 复位PLC
        self.WritePlcMK(12, 0, form='bit', bit=0)
        self.WritePlcMK(12, 0, form='bit', bit=1)
        self.WritePlcMK(12, 0, form='bit', bit=2)
        self.WritePlcMK(12, 0, form='bit', bit=3)
        self.WritePlcMK(12, 0, form='bit', bit=4)
        self.WritePlcMK(12, 0, form='bit', bit=5)
        self.WritePlcMK(12, 0, form='bit', bit=6)
        self.WritePlcMK(12, 0, form='bit', bit=7)
        # self.WritePlcMK(11, 0, form='bit', bit=0)
        # self.WritePlcMK(11, 0, form='bit', bit=1)
        # self.WritePlcMK(11, 0, form='bit', bit=2)
        # self.WritePlcMK(11, 0, form='bit', bit=3)
        # self.WritePlcMK(11, 0, form='bit', bit=4)
        # self.WritePlcMK(11, 0, form='bit', bit=5)
        # self.WritePlcMK(11, 0, form='bit', bit=6)
        # self.WritePlcMK(11, 0, form='bit', bit=7)



    def PLC_bitread(self):
        # 读取PLC的11和12两个地址的状态
        addresses = [11, 12]
        plc_states = {}

        for addr in addresses:
            # 读取PLC数据
            plc_state = self.ReadPlcMK(addr, 1)

            # 检查读取是否成功
            if plc_state:
                single_byte = plc_state[0]
                # 将字节转换为二进制字符串，并确保长度为16位
                binary_str = bin(single_byte)[2:].zfill(16)
                # 将二进制字符串转换为位列表
                bit_list = [int(bit) for bit in binary_str]
                plc_states[addr] = bit_list
            else:
                # 如果读取失败，记录空列表或处理错误
                plc_states[addr] = []

        plc_states[11] = plc_states[11][::-1]





        return plc_states
    def PLC_allstop(self):
        # 停止所有运动
        print("停止所有运动")
        self.WritePlcMK(2, 0, form='bit', bit=6)
        self.PLC_bitreset()

    def PLC_restart(self):
        self.WritePlcMK(2, 1, form='bit', bit=6)



    def save_speed_to_excel(self,speed: float, pulse: int,excel_path: str = None):
        """
        自动生成时间戳并将速度保存到Excel文件（自动创建或追加数据）

        参数:
            speed (float): 速度值（单位由PLC决定）
            excel_path (str): 可选，Excel文件路径。默认保存到桌面。
        """
        # 生成当前时间戳（精确到毫秒）
        timestamp = datetime.now().strftime('%S.%f')[:-3]

        # 默认路径：桌面
        if excel_path is None:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            excel_path = os.path.join(desktop, "plc_speed_data.xlsx")

        # 新数据行
        new_data = {"时间戳": [timestamp], "速度 ": [speed],"PULSE":[pulse]}
        new_df = pd.DataFrame(new_data)

        # 如果文件存在则追加，否则新建
        if os.path.exists(excel_path):
            existing_df = pd.read_excel(excel_path)
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            updated_df = new_df

        # 保存文件（无索引列）
        updated_df.to_excel(excel_path, index=False)
        print(f"[{timestamp}] 数据已保存 -> {excel_path}")

    def PLC_cov_vRead(self):
        # self.pulse=self.ReadPlcDB(13, 64, 1, form='real')+(self.ReadPlcDB(13, 68, 1, form='real')-1)*65536
        cov_vnow = self.ReadPlcDB(13, self.cov_VP, 1, form='real')
        if abs(cov_vnow)<0.001:
            cov_vnow = 0
            self.cov_v = 0
            self.cov_vlast=0
        self.cov_vlast = self.cov_v
        self.cov_v =cov_vnow / 1000


        return [ self.x_p, self.x_v, self.cov_v,self.pulse]

    def PLC_RAS(self,PLC_SET,mode,PID_PARM,target_parm ):
##PLC进程函数，读取plc标志位，根据标志位判断执行状态，再决定是否发送数据
###PLC_SET为传入的目标位置，mode为执行模式，0为回原点，1为运动，2为随动与抓取，3为待机
###PLC_SET 0为X轴绝对坐标，1为Y轴绝对坐标，2为ZF轴绝对坐标，3为theta
        
        #定义PLC状态list
        PLC_state=[]
       
     
        # self.WritePlcMK(2, 1, form='bit', bit=6)
        print("开始")
        # 读取PLC状态
        PLC_state=self.PLC_bitread()
        while PLC_state[self.read_Byte][2]==0:
                # 机械初始化未完成
                PLC_state = self.PLC_bitread()
                print("机械初始化未完成")
        if mode==0:
            self.gohome_RUN()
            print("回原点")
            PLC_state = self.PLC_bitread()
            while PLC_state[self.read_Byte][0]==0:
                # 机械初始化未完成
                print("未回原点")
                #print(PLC_state)
                PLC_state=self.PLC_bitread()
                #print(PLC_state)
                if mode==3:
                        self.PLC_allstop()  
                        print("待机")
                        break

        if mode==1:
            self.X_RUN(PLC_SET[0])
            self.Y_RUN(PLC_SET[1])
            self.ZF_RUN(PLC_SET[2])
            while PLC_state[self.read_Byte][2]==0:
                #运动中
                print("运动中")
                PLC_state = self.PLC_bitread()
                if mode==3:
                        self.PLC_allstop()  
                        print("待机")
                        break
                        
        if mode==2:
                print("开始随动与抓取")
                print(PLC_SET)
                # self.getch_RUN()
                self.Y_RUN(PLC_SET[1])
                self.ZF_RUN(PLC_SET[2])
                self.follow_RUN(PID_PARM,target_parm)
                self.follow_STOP()
                # while PLC_state[self.read_Byte][5] == 0:
                #     # 机械初始化未完成
                #print("未完成")
                #
                #     t1=t.time()
                #
                #     t2 = t.time()
                #     #print("总共耗时：", t2 - t1)
                #     PLC_state = self.PLC_bitread()
                #     # if mode==3:
                #     #     self.PLC_allstop()
                #     #     print("待机")
                #     #     break
                #
                print("完成抓取")
        if mode==3:
            self.PLC_allstop()
            print("待机")
        if mode==4:
            cov_v = self.ReadPlcDB(13, self.cov_VP, 1, form='real')
            self.save_speed_to_excel( cov_v)

        self.PLC_bitreset()

        return 1

        




if __name__ == '__main__':
    PLC = PLCWriteRead("192.168.0.1", name='1200')
    PLC.ConnectPlc()

    PLC_SET=[0,0,60,60,-60]
    print(PLC_SET[0])
    PID_PARM=[7.0,0.3,3.0,0.1,2.0,0.8,2.0]
    target_parm=[0.3,0.1]
    while True:
        # mode =int( input("请输入执行模式：0为回原点，1为运动，2为随动与抓取，3为待机："))
        # if mode==1:
        #     PLC_SET[0]=float(input("请输入目标位置x："))
        #     PLC_SET[1]=float(input("请输入目标位置y："))
        # PLC.PLC_RAS(PLC_SET,mode,PID_PARM,target_parm)

        # mode =4
        cov_v = PLC.ReadPlcDB(13, PLC.cov_VP, 1, form='real')
        pulse = PLC.ReadPlcDB(13, 64, 1, form='real')
        PLC.save_speed_to_excel(cov_v, pulse)


