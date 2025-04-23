import time
import pandas as pd

class PIDController:
    def __init__(self, Kp, Ki, Kd, dt):
        """
        PID控制器初始化
        :param Kp: 比例增益
        :param Ki: 积分增益
        :param Kd: 微分增益
        :param dt: 采样时间
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.dt = dt
        self.integral = 0
        self.prev_error = 0
        self.last_time = time.time()
        print(self.last_time)

    def compute(self, error):
        """
        计算PID输出
        :param error: 当前误差
        :return: PID输出值
        """
        current_time = time.time()  # 获取当前时间
        print(current_time)
        self.dt = current_time - self.last_time  # 计算时间差
        print(self.dt)
        if self.dt == 0:
            self.dt =0.1

        self.integral += error * self.dt
        derivative = (error - self.prev_error) / self.dt
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        self.prev_error = error
        self.last_time = current_time  # 更新上一次的时间
        return output


class Actuator:
    def __init__(self, y_initial, v_max, a_max, decel_max, jerk, filter_time, dt):
        """
        执行器初始化
        :param y_initial: 初始位置 (mm)
        :param v_max: 最大速度 (mm/s)
        :param a_max: 最大加速度 (mm/s²)
        :param decel_max: 最大减速度 (mm/s²)
        :param jerk: 加加速度 (mm/s³)
        :param filter_time: 滤波时间 (s)
        :param dt: 采样时间 (s)
        """
        self.y = y_initial  # 初始位置
        self.v = 0  # 初始速度
        self.a = 0  # 初始加速度
        self.v_max = v_max  # 最大速度
        self.a_max = a_max  # 最大加速度
        self.decel_max = decel_max  # 最大减速度
        self.jerk = jerk  # 加加速度
        self.filter_time = filter_time  # 滤波时间
        self.dt = dt  # 采样时间
        self.last_time = time.time()  # 上一次更新时间

    def update(self, a_desired):
        """
        更新执行器状态
        :param a_desired: 期望加速度 (mm/s²)
        """
        current_time = time.time()
        self.dt = current_time - self.last_time  # 计算实际时间差
        if self.dt == 0:
            self.dt = 1e-6  # 设置为一个极小值

        # 1. 限幅期望加速度
        if a_desired > 0:
            a_desired = min(a_desired, self.a_max)
        else:
            a_desired = max(a_desired, -self.decel_max)

        # 2. 根据加加速度（Jerk）更新实际加速度
        jerk_actual = (a_desired - self.a) / self.dt  # 计算所需加加速度
        jerk_actual = max(min(jerk_actual, self.jerk), -self.jerk)  # 限幅加加速度
        self.a += jerk_actual * self.dt  # 更新加速度

        # 3. 根据滤波时间平滑加速度
        alpha = self.dt / (self.filter_time + self.dt)
        self.a = (1 - alpha) * self.a + alpha * a_desired

        # 4. 更新速度
        self.v += self.a * self.dt

        # 5. 限幅速度
        self.v = max(min(self.v, self.v_max), -self.v_max)

        # 6. 更新位置（精确积分）
        self.y += self.v * self.dt + 0.5 * self.a * self.dt**2  # 考虑加速度的影响

        # 7. 更新上一次的时间
        self.last_time = current_time


class Target:
    def __init__(self, y_initial, v_initial):
        """
        目标初始化
        :param y_initial: 初始位置
        :param v_initial: 初始速度
        """
        self.y = y_initial
        self.v = v_initial
        self.last_time = time.time()  # 记录上一次更新的时间

    def update(self):
        """
        更新目标位置
        """
        current_time = time.time()  # 获取当前时间
        dt = current_time - self.last_time  # 计算时间差
        self.y += self.v * dt  # 基于实际时间差更新目标位置
        self.last_time = current_time  # 更新上一次的时间
if __name__ == '__main__':
# PID控制器参数
    Kp = 7.0  # 比例增益
    Ki = 0.3  # 积分增益
    Kd = 3.0  # 微分增益

    # 采样时间
    dt = 0.1  # 采样时间（单位：秒）

    # 目标参数
    y_initial = 0.10  # 目标的初始位置（单位：米）
    v_initial = 0.1  # 目标的初始速度（单位：米/秒）

    # 执行器参数
    y_initial_r = 0.30  # 执行器的初始位置（单位：米）
    v_max = 1.0000  # 执行器的最大速度（单位：毫米/秒）
    a_max = 4.222227  # 执行器的最大加速度（单位：毫米/秒²）
    decel_max = 9.5000  # 执行器的最大减速度（单位：毫米/秒²）
    jerk = 16.88889  # 执行器的加加速度（单位：毫米/秒³）
    filter_time = 0.25  # 滤波时间（单位：秒）

    # 控制变量
    v_control = 0  # 控制速度（初始值）

    # 初始化
    # 初始化PID控制器
    pid = PIDController(Kp, Ki, Kd, dt)

    # 初始化执行器
    actuator = Actuator(
        y_initial=y_initial_r,  # 执行器的初始位置
        v_max=v_max,  # 执行器的最大速度
        a_max=a_max,  # 执行器的最大加速度
        decel_max=decel_max,  # 执行器的最大减速度
        jerk=jerk,  # 执行器的加加速度
        filter_time=filter_time,  # 滤波时间
        dt=dt  # 采样时间
    )

    # 初始化目标
    target = Target(y_initial, v_initial)

    # 用于存储运行结果
    results = []

    # 主循环
    try:
        start_time = time.time()  # 记录程序开始时间
        while time.time() - start_time < 5.0:
            # 更新目标位置
            target.update()
            
            # 计算误差
            error = target.y - actuator.y
            
            # 计算PID输出
            a_desired = pid.compute(error)
            v_control = actuator.v
            # 记录当前时间、目标位置、执行器位置和误差
            current_time = time.time() - start_time
            results.append({
                "Time": current_time,
                "Target Position": target.y,
                "Actuator Position": actuator.y,
                "Error": error,
                "v_control":v_control
            })
            
            # 打印状态
            print(f"Time: {current_time:.4f}, Target: {target.y:.4f}, Actuator: {actuator.y:.4f}, Error: {error:.4f}, v_control: {v_control:.4f}")

            # 更新执行器状态
            actuator.update(a_desired)
            
            # 等待下一个采样时间
            time.sleep(dt)
            # 程序结束时将结果保存到Excel文件
        df = pd.DataFrame(results)
        df.to_excel("tracking_results.xlsx", index=False)
        print("程序结束，结果已保存到 tracking_results.xlsx")
    except KeyboardInterrupt:
        # 程序结束时将结果保存到Excel文件
        df = pd.DataFrame(results)
        df.to_excel("tracking_results.xlsx", index=False)
        print("程序结束，结果已保存到 tracking_results.xlsx")