# -*- coding: utf-8 -*-
import cv2
import numpy as np

# 全局变量，用于存储点击的坐标
click_position = None


def mouse_callback(event, x, y, flags, param):
    global click_position
    if event == cv2.EVENT_LBUTTONDOWN:
        click_position = (x, y)
        print(f"点击位置: ({x}, {y})")


# 读取图片
image_path = "../images/image.jpg"  # 替换为你的图片路径
original_image = cv2.imread(image_path)
if original_image is None:
    print("无法加载图片，请检查路径是否正确")
    exit()

# 缩小图片到目标尺寸（例如 640x480）
target_size = (640, 480)  # 目标尺寸 (宽度, 高度)
resized_image = cv2.resize(original_image, target_size, interpolation=cv2.INTER_AREA)

# 创建窗口并绑定鼠标回调
cv2.namedWindow("Resized Image")
cv2.setMouseCallback("Resized Image", mouse_callback)

while True:
    # 显示缩放后的图片
    cv2.imshow("Resized Image", resized_image)

    # 检查是否有点击事件
    if click_position is not None:
        x, y = click_position
        # 检查点击位置是否在缩放后的图片范围内
        if 0 <= x < resized_image.shape[1] and 0 <= y < resized_image.shape[0]:
            # 获取点击点的 BGR 值
            bgr_value = resized_image[y, x]
            # 转换为 HSV 值
            hsv_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2HSV)
            hsv_value = hsv_image[y, x]

            # 打印结果
            print(f"点击点的 BGR 值: {bgr_value}")
            print(f"点击点的 HSV 值: {hsv_value}")
            click_position = None  # 重置点击位置

    # 按 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()