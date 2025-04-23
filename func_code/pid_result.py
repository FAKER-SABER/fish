import pandas as pd
import matplotlib.pyplot as plt

# 读取 Excel 文件
file_path = "tracking_results.xlsx"  # 替换为你的 Excel 文件路径
df = pd.read_excel(file_path)

# 提取横坐标和纵坐标
x_data = df.iloc[:, 0]  # 第一列数据作为横坐标
y_data = df.iloc[:, 1:]  # 其他列数据作为纵坐标

# 绘制图表
plt.figure(figsize=(10, 6))

# 绘制每条曲线
for column in y_data.columns:
    plt.plot(x_data, y_data[column], label=column)

# 设置图表标题和标签
plt.title("Tracking Results")
plt.xlabel(df.columns[0])  # 横坐标标签为第一列的名称
plt.ylabel("Value")

# 添加图例
plt.legend()

# 显示图表
plt.grid(True)
plt.show()