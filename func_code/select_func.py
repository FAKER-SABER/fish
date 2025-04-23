import numpy as np
import cv2
'''
input: 
x_distance 相机在x方向上覆盖的像素长度
speed 传送带移动的速度(pixel)
obj_length 物体长度
obj_position 物体位置集合（像素坐标下）, 此时不需要计算方向，先筛选再拟合椭圆
output: 
grasp_position 抓取位置集合（像素坐标下）
[[x,y],[x,y],...]

example:
objlenth = length_to_pixel(length , z , f)
xrange = find_xrange(x_distance , speed , obj_length)
grasp_position = select_object(obj_position, xrange)
'''
internal_reference = np.array([
    [2381.89876842925, 0                , 1220.22240329899],
    [0               , 2381.86625688522 , 1045.20735498504],
    [0               , 0                , 1               ]
])
img_size = [2048,2448]
RadialDistortion = [-0.075187061347617,0.151786795403540,-0.013124105212395]

def undistort_image(K, dist_coeffs, img):
    #未测试
    h, w = img.shape[:2]
    new_K, roi = cv2.getOptimalNewCameraMatrix(K, dist_coeffs, (w, h), 1, (w, h))
    undistorted_img = cv2.undistort(img, K, dist_coeffs, None, new_K)
    x, y, w, h = roi
    undistorted_img = undistorted_img[y:y+h, x:x+w]
    return undistorted_img , roi , new_K

def find_xrange(x_distance , speed , obj_length):
    x_min = obj_length/2
    intersect_regions = x_distance - speed
    redundant_region = intersect_regions - obj_length
    if redundant_region<0:
        print('需要降低速度才能保证抓取')
        return False
    x_max =x_distance - x_min - redundant_region
    x_range = [x_min, x_max]
    return x_range

def select_object(obj_position, xrange):
    grasp_position = []
    for position in obj_position:
        x = position[0]
        if xrange[0] <= x <= xrange[1]:
            grasp_position.append(position)
    return grasp_position

def generate_array(num = 5, width = 1080):
    '''随机生成数组'''
    pass

def world_to_pixel(world_size, z, K):
    """
    将世界坐标系下的尺寸转换为像素坐标系下的尺寸单位均为米
    :param world_size: 物体在世界坐标系中的尺寸 (width, height)
    :param z: 物体到摄像机的距离
    :param K: 摄像机内参矩阵
    :return: 物体在像素坐标系中的尺寸 (pixel_width, pixel_height)
    """
    w, h = world_size
    f_x = K[0, 0]
    f_y = K[1, 1]
    
    pixel_width = (w * f_x) / z
    pixel_height = (h * f_y) / z
    
    return pixel_width, pixel_height

def length_to_pixel(length,z,f):
    pixel_length = (length * f) / z
    return pixel_length

if __name__ == '__main__':
    x_distance = 1000
    speed = 200
    obj_length = 100
    obj_position = [[150, 200], [250, 300], [450, 400], [850, 600]]

    xrange = find_xrange(x_distance, speed, obj_length)
    if xrange:
        grasp_position = select_object(obj_position, xrange)
        print(grasp_position)
    
    # 示例内参矩阵
    K = np.array([[1000, 0, 640],
                [0, 1000, 360],
                [0, 0, 1]])

    # 示例物体尺寸和距离
    world_size = (0.5, 0.3)  # 世界坐标系中的尺寸 (宽度, 高度) 单位：米
    z = 2.0  # 距离摄像机的距离 单位：米

    pixel_size = world_to_pixel(world_size, z, K)
    print(f"物体在像素坐标系中的尺寸: 宽度 = {pixel_size[0]:.2f} 像素，高度 = {pixel_size[1]:.2f} 像素")