'''
像素坐标：
[575,1392.5]
[1859,663.5]
[321.5,597.5]
'''
import numpy as np
from sympy import *

internal_reference = np.array([
    [2381.89876842925, 0                , 1220.22240329899],
    [0               , 2381.86625688522 , 1045.20735498504],
    [0               , 0                , 1               ]
])
points_uv =[[575,1392.5],[1859,663.5],[321.5,597.5]]
for point_uv in points_uv:
    z_c = 420  ##单位毫米
    x_camera = Symbol('x_camera')
    y_camera = Symbol('y_camera')
    equation1 = z_c * point_uv[0] - (internal_reference[0, 0] * x_camera + internal_reference[0, 1] * y_camera + internal_reference[0, 2] * z_c)
    equation2 = z_c * point_uv[1] - (internal_reference[1, 0] * x_camera + internal_reference[1, 1] * y_camera + internal_reference[1, 2] * z_c)
    result = solve([equation1, equation2], [x_camera, y_camera])  # 求解方程，获得以相机为原点的空间坐标
    x_position = result.get(x_camera)
    y_position = result.get(y_camera)
    print(f'{x_position},{y_position}')
