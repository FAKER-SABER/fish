import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button, Slider
import time

class AdvancedConveyorSystem:
    def __init__(self):
        self.Conveyor_param = {
            'length': 3.0,     # 传送带长度 (m)
            'width': 0.5,      # 传送带宽度 (m)
            'obj_size': 0.1,   # 物体尺寸 (m)
            'buffer': 0.5      # 可视缓冲区 (m)
        }
        self.speed = 0.03  # 初始速度 (m/s)
        
        # 初始化图形界面
        self.fig, self.ax = plt.subplots(figsize=(10, 4.5))
        self._setup_interface()
        
        # 物体管理系统
        self.objects = []  # 存储所有活动物体
        
        # 记录上一帧的时间
        self.last_time = time.time()
        
        # 启动动画引擎
        self._init_animation()

    def _setup_interface(self):
        """构建用户界面"""
        # 传送带本体
        self.conveyor = plt.Rectangle(
            (0, 0), self.Conveyor_param['length'], self.Conveyor_param['width'],
            color='#4682B4', alpha=0.8, zorder=1
        )
        self.ax.add_patch(self.conveyor)
        
        # 生成按钮
        self.btn_ax = plt.axes([0.8, 0.92, 0.15, 0.06])
        self.btn = Button(self.btn_ax, 'generate_obj', color='#4CAF50')
        self.btn.on_clicked(self._generate_object)
        
        # 速度滑块
        self.speed_slider_ax = plt.axes([0.2, 0.92, 0.5, 0.03])
        self.speed_slider = Slider(
            self.speed_slider_ax, 'Speed (m/s)', 0, 1, valinit=self.speed
        )
        self.speed_slider.on_changed(self._update_speed)
        
        # 坐标系设置
        self.ax.set_xlim(-self.Conveyor_param['buffer'], 
                        self.Conveyor_param['length'] + self.Conveyor_param['buffer'])
        self.ax.set_ylim(-self.Conveyor_param['buffer'], 
                        self.Conveyor_param['width'] + self.Conveyor_param['buffer'])
        self.ax.set_aspect('equal')
        self.ax.grid(True, linestyle=':', alpha=0.5)

    def _generate_object(self, event):
        """物体生成算法（带随机分布）"""
        # 随机Y轴位置（保留2mm精度）
        y_pos = np.round(
            np.random.uniform(0, self.Conveyor_param['width'] - self.Conveyor_param['obj_size']),
            3
        )
        
        # 创建新物体
        new_obj = plt.Rectangle(
            (0, y_pos), 
            self.Conveyor_param['obj_size'], 
            self.Conveyor_param['obj_size'],
            color=np.random.choice(['#FF5722', '#FFC107', '#8BC34A']),
            zorder=2
        )

        self.ax.add_patch(new_obj)
        self.objects.append(new_obj)
        print(new_obj, '被生成')
        print(self.objects)

    def _update_positions(self):
        """根据真实时间更新物体位置"""
        # 计算时间差
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        remove_list = []
        
        # 逆序循环避免索引错位
        for i in reversed(range(len(self.objects))):
            obj = self.objects[i]
            # 根据速度和时间差计算移动距离
            new_x = obj.get_x() + self.speed * dt
            
            # 边界检测（物体完全离开传送带时）
            if new_x > self.Conveyor_param['length'] + self.Conveyor_param['buffer']:
                obj.remove()  # 从画布移除
                remove_list.append(i)  # 记录待删除索引
            else:
                obj.set_x(np.round(new_x, 4))
        
        # 批量移除离开物体
        for i in remove_list:
            del self.objects[i]

    def _update_speed(self, val):
        """更新传送带速度"""
        self.speed = val
        print(f"速度更新至: {self.speed} m/s")

    def _init_animation(self):
        """启动动画系统"""
        def animate(frame):
            self._update_positions()
            return self.objects
        
        # 配置高性能动画参数
        self.ani = animation.FuncAnimation(
            self.fig, animate,
            interval=33,  # 30 FPS
            blit=True,
            cache_frame_data=False
        )
        
        plt.show()

# 启动高级控制系统
if __name__ == "__main__":
    AdvancedConveyorSystem()