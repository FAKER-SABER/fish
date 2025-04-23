# -*- coding: utf-8 -*-
import cv2
import time
import numpy as np
from sympy import Symbol, solve


# PARAMETERS
low_H, low_S, low_V = 111, 16, 80
high_H, high_S, high_V = 160, 78, 121
min_area = 50000
max_area = 120000
# 相机内参矩阵
# K = np.array([[1406.08415449821, 0, 0], [2.20679787308599, 1417.99930662800, 0], [1014.13643417416, 566.347754321696, 1]])
# K = np.array([[2381.899, 0, 0], [0, 2381.866, 0], [1220.222, 1045.207, 1]])  # matlab获得相机内参矩阵
internal_reference = np.array([
    [2381.89876842925, 0                , 1220.22240329899],
    [0               , 2381.86625688522 , 1045.20735498504],
    [0               , 0                , 1               ]
    ])
speed = 0.05
# 坐标转换参数
Y_offset = 10
# 一种黄色的颜色阈值,效果还是不好，需要增加范围大小的筛掉，位置偏的筛掉
# low_H, low_S, low_V = 40, 0, 0
# high_H, high_S, high_V = 179, 255, 255
# min_area = 10000
# max_area = 100000

# 不需要修改的变量
lower_bound = np.array([low_H, low_S, low_V])
upper_bound = np.array([high_H, high_S, high_V])
ellipses = []
colors = [
    (255, 0, 0),  # 红色
    (0, 255, 0),  # 绿色
    (0, 0, 255),  # 蓝色
    (255, 255, 0),  # 黄色
    (255, 0, 255),  # 粉色
    (0, 255, 255),  # 青色
    (128, 0, 128),  # 紫色
    (0, 128, 0),  # 深绿色
    (0, 0, 128),  # 深蓝色
    (128, 128, 128),  # 灰色
    (192, 0, 0),  # 深红色
    (0, 192, 0),  # 深绿色（亮）
    (0, 0, 192),  # 深蓝色（亮）
    (192, 192, 0),  # 深黄色
    (192, 0, 192),  # 深粉色
    (0, 192, 192),  # 深青色
    (64, 0, 64),  # 深紫色
    (0, 64, 0),  # 深绿色（暗）
    (0, 0, 64),  # 深蓝色（暗）
    (64, 64, 64)  # 深灰色
]
def perspectiveTransform(img):
    W = img.shape[1]
    H = img.shape[0]
    W = int(W)
    H = int(H)
    print("W:", W, "H:", H)
    # 手动或自动获取图像中物体四个角点（源点）
    x1, y1 = 0, 0
    x2, y2 = 2448, 0
    x3, y3 = 2448, 2048
    x4, y4 = 0, 2048
    # 假设手动或自动获取图像中物体四个角点（源点）
    src_pts = np.float32([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
    # 定义目标四角点，即矫正后的理想位置（目标点）
    dst_pts = np.float32([[0, 0], [W, 0], [W, H], [0, H]])
    # 计算单应性矩阵
    HM = cv2.getPerspectiveTransform(src_pts, dst_pts)
    # 对图像进行透视变换
    corrected_img = cv2.warpPerspective(img, HM, (W, H))
    # cv2.imwrite('./images/perspective_transform.jpg', corrected_img)
    return corrected_img

def pixel_to_camera(pixel_x, pixel_y, internal_reference):
    z_c = 450  ##单位毫米
    x_camera = Symbol('x_camera')
    y_camera = Symbol('y_camera')
    equation1 = z_c * pixel_x - (internal_reference[0, 0] * x_camera + internal_reference[0, 1] * y_camera + internal_reference[0, 2] * z_c)
    equation2 = z_c * pixel_y - (internal_reference[1, 0] * x_camera + internal_reference[1, 1] * y_camera + internal_reference[1, 2] * z_c)
    result = solve([equation1, equation2], [x_camera, y_camera])  # 求解方程，获得以相机为原点的空间坐标
    x_position = result.get(x_camera)
    y_position = result.get(y_camera)
    return (x_position, y_position)

def camera_to_world(X_camera, Y_camera, ts):
    # 单位mm
    X_offset = -10
    Y_offset = 515
    X_world = X_offset - X_camera
    Y_world = Y_camera - Y_offset
    return (X_world, Y_world)

def recognize_ellipses(img, ts, points_list):
    # 提取边缘
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    Gaussian_blur = cv2.GaussianBlur(mask, (5, 5), 0)
    Median_blur = cv2.medianBlur(Gaussian_blur, 5)
    Eroded = cv2.erode(Median_blur, None, iterations=10)
    Dilated = cv2.dilate(Eroded, None, iterations=10)
    contours, _ = cv2.findContours(Dilated, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    # # 绘制边缘
    # cv2.drawContours(img, contours, -1, (0, 255, 0), 2)
    # img = cv2.resize(img, (int(img.shape[1] / 2), int(img.shape[0] / 2)))
    # cv2.imshow('Contours', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # 筛选并拟合椭圆
    number_of_ellipses = 0
    for contour in contours:
        if cv2.contourArea(contour) < min_area:
            # 如果面积小于阈值，则跳至下一个轮廓contour
            continue
        if cv2.contourArea(contour) > max_area:
            # 如果面积大于阈值，则跳至下一个轮廓contour
            continue
        if len(contour) >= 5:
            # 如果轮廓点数大于等于5，则进行拟合椭圆
            try:
                ellipse = cv2.fitEllipse(contour)
                # ellipse =  [ (x, y) , (a, b), angle ]
                center = ellipse[0]
                angle = ellipse[2]
                # ellipses.append(ellipse)
                # print(f"  Cluster_center_angle: ({number_of_ellipses}, {center[0]:.2f}, {center[1]:.2f}), {angle:.2f} degrees")
                # 绘制簇中椭圆的平均中心
                cluster_color = colors[number_of_ellipses % len(colors)]
                text_pos = (int(center[0]), int(center[1]))
                cv2.putText(img, f"Cluster {number_of_ellipses + 1}", text_pos,
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, cluster_color, 2)
                # 图像像素坐标转换为实际坐标
                X_camera, Y_camera = pixel_to_camera(center[0], center[1], internal_reference)
                # print(f"  Camera_point: ({X_camera:.2f}, {Y_camera:.2f})")
                # 实际坐标转换为地理坐标
                X_world, Y_world = camera_to_world(X_camera, Y_camera, ts)
                # print(f"  World_point: ({X_world:.2f}, {Y_world:.2f})")
                point_offset = (Y_world, X_world, angle, ts)
                points_list.append(point_offset)
                # 绘制拟合椭圆
                number_of_ellipses += 1
                cv2.ellipse(img, ellipse, (0, 0, 255), 2)
            except:
                continue
    if number_of_ellipses == 0:
        print("No ellipses detected")
    print(f"Number of ellipses detected: {number_of_ellipses}")
    return points_list





if __name__ == '__main__':
    # 从文件夹中读取图片
    image_path = './images/image.jpg'
    original_image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if original_image is None:
        print(f"Error: Could not read image from {image_path}")
        exit()
    image = original_image.copy()
    ts = time.time()
    # 识别椭圆
    recognize_ellipses(image, ts, [])
    # 显示纯视觉代码运行时间，效率很高
    te = time.time()
    print(f"Time taken: {te - ts:.2f} seconds")
    # 画面显示，检查结果
    display_image = cv2.resize(image, (int(image.shape[1] / 2), int(image.shape[0] / 2)))
    cv2.imshow('Clustered Ellipses', display_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()