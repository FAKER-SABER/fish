import numpy as np
import matplotlib.pyplot as plt
import time as t

class PIDController:
    def __init__(self, kp, ki, kd, dt, max_accel, max_vel):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.dt = dt
        self.max_accel = max_accel
        self.max_vel = max_vel
        
        # 状态变量
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_control = 0.0
        
    def update(self, target_pos , current_pos , current_vel):
        # 计算误差
        error = target_pos - current_pos
        
        # PID计算
        P = self.kp * error
        self.integral += error * self.dt
        I = self.ki * self.integral
        derivative = (error - self.prev_error) / self.dt
        D = self.kd * derivative
        
        # 原始控制输出（加速度指令）
        raw_accel = P + I + D
        
        # 加速度限幅
        clamped_accel = np.clip(raw_accel, -self.max_accel, self.max_accel)
        
        # 速度计算（积分加速度）
        new_vel = current_vel + clamped_accel * self.dt
        
        # 速度限幅
        clamped_vel = np.clip(new_vel, -self.max_vel, self.max_vel)
        
        # 更新状态
        self.prev_error = error
        
        # 最终输出为速度指令（通过加速度间接控制）
        return clamped_vel
    
class Target:
    def __init__(self, y_initial, v_initial):
        """
        目标初始化
        :param y_initial: 初始位置
        :param v_initial: 初始速度
        """
        self.y = y_initial
        self.v = v_initial
        self.last_time = t.time()  # 记录上一次更新的时间

    def get_pos(self):
        """
        更新目标位置
        """
        current_time = t.time()  # 获取当前时间
        dt = current_time - self.last_time  # 计算时间差
        self.y += self.v * dt  # 基于实际时间差更新目标位置
        self.last_time = current_time  # 更新上一次的时间
        return self.y

    def set_v(self, v):
        self.v = v

        
if __name__ == '__main__':
    print('开始')
    #初始化参数
    pid = PIDController(
        kp = 7.0,
        ki = 0.3,
        kd = 3.0,
        dt = 0.1,
        max_accel = 4.0,
        max_vel = 0.8    
    )

    target = Target(
        y_initial=0.0, 
        v_initial=0.1
    )
    SIMULATION_TIME = 10.0  # 秒
    SAMPLE_INTERVAL = pid.dt
    start_time = t.time()
    while (t.time() - start_time) < 5:
        # 获取当前目标位置（带时间同步的实时更新）
        target_pos = target.get_pos()
        
        #获取执行器状态
        current_pos, current_vel = PLC_get()

        # 执行PID控制计算（current_pos/vel由外部系统反馈）
        control_vel = pid.update(target_pos, current_pos, current_vel)  

        #更新速度
        PLC_set(control_vel)

        #结果显示
        print(
            f"目标位置: {target_pos:.4f}, "
            f"当前位置: {current_pos:.4f}, "
            f"当前速度: {current_vel:.4f}, "
            f"控制速度: {control_vel:.4f}"
        )

        # 保持控制周期（硬件实现时需要精确计时）
        t.sleep(max(0, SAMPLE_INTERVAL - (t.time()%SAMPLE_INTERVAL)))
