import numpy as np

class KalmanFilter:
    def __init__(self, dt, process_noise, measurement_noise):
        """
        初始化卡尔曼滤波
        :param dt: 时间间隔
        :param process_noise: 过程噪声协方差
        :param measurement_noise: 测量噪声协方差
        """
        # 状态向量 [位置, 速度]
        self.state = np.array([0, 0])  # 初始状态
        self.state_cov = np.eye(2)     # 初始协方差矩阵

        # 状态转移矩阵 (匀速模型)
        self.F = np.array([[1, dt],
                           [0, 1]])

        # 过程噪声协方差矩阵
        self.Q = process_noise * np.eye(2)

        # 观测矩阵 (测速器只测量速度)
        self.H = np.array([0, 1]).reshape(1, 2)

        # 测量噪声协方差
        self.R = measurement_noise

    def predict(self):
        """
        预测步骤
        """
        # 预测状态
        self.state = self.F @ self.state
        # 预测协方差
        self.state_cov = self.F @ self.state_cov @ self.F.T + self.Q

    def update(self, measurement):
        """
        更新步骤
        :param measurement: 测速器的测量值 (速度)
        """
        # 计算卡尔曼增益
        K = self.state_cov @ self.H.T / (self.H @ self.state_cov @ self.H.T + self.R)
        # 更新状态
        self.state = self.state + K * (measurement - self.H @ self.state)
        # 更新协方差
        self.state_cov = (np.eye(2) - K @ self.H) @ self.state_cov

    def predict_future(self, n_steps):
        """
        预测未来 n_steps 个时间步后的状态
        :param n_steps: 预测的时间步数
        :return: 预测的状态 [位置, 速度]
        """
        F_n = np.linalg.matrix_power(self.F, n_steps)
        future_state = F_n @ self.state
        return future_state

# 参数设置
dt = 1.0                   # 时间间隔
process_noise = 0.1        # 过程噪声协方差
measurement_noise = 0.5    # 测速器的测量噪声协方差

# 初始化卡尔曼滤波
kf = KalmanFilter(dt, process_noise, measurement_noise)

# 模拟数据
true_speed = 10.0          # 真实速度
measurements = [9.8, 10.1, 10.2, 9.9, 10.0]  # 测速器的测量值

# 运行卡尔曼滤波
for z in measurements:
    kf.predict()           # 预测步骤
    kf.update(z)           # 更新步骤
    print(f"当前状态: {kf.state}")

# 预测未来 5 个时间步后的速度
future_state = kf.predict_future(5)
print(f"预测 5 个时间步后的速度: {future_state[1]}")
future_state = kf.predict_future(50)
print(f"预测 5 个时间步后的速度: {future_state}")
future_state = kf.predict_future(500)
print(f"预测 5 个时间步后的速度: {future_state}")