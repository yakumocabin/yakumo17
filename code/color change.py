import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import colour  # 来自 colour-science 库

# 自定义包装类，提供必要的属性：start、stop、step、end 和 interval
class SliceWrapper:
    def __init__(self, start, stop, step):
        self.start = start      # 开始波长
        self.stop = stop        # 结束波长（不包含该值）
        self.step = step        # 步长
        self.end = stop         # end 属性等于 stop
        # interval 属性也等于步长
        self._interval = step

    @property
    def interval(self):
        return self._interval

    def __iter__(self):
        # 返回一个迭代器，该迭代器生成规则采样的波长序列
        return iter(np.arange(self.start, self.stop, self.step))

# 1. 读取 Excel 中的光谱数据
df = pd.read_excel('reflectance.xlsx', sheet_name='Sheet2')
df.columns = df.columns.str.strip()  # 去除列名两边可能的空白字符

# 提取波长和反射率（转换为浮点型数组）
wavelengths = df['Wavelength'].astype(float).values
reflectance = df['Reflectance'].astype(float).values

# 2. 创建光谱分布对象（SpectralDistribution）
spectrum_data = dict(zip(wavelengths, reflectance))
sd = colour.SpectralDistribution(spectrum_data)

# 3. 根据原始数据的间隔选择合适的重采样间隔
# 这里假设选择 5nm 的间隔，使用我们自定义的 SliceWrapper 对象
regular_wavelengths = SliceWrapper(380, 781, 5)  # 从 380nm 到 780nm，步长 5nm
sd = sd.interpolate(regular_wavelengths)

# 4. 设置标准 illuminant（选择 D65，即日光）
illuminant = colour.SDS_ILLUMINANTS['D65']

# 5. 利用光谱分布计算 XYZ 三刺激值
XYZ = colour.sd_to_XYZ(sd, illuminant=illuminant)

# 6. 将 XYZ 转换为 sRGB
# 注意：XYZ 通常以 100 为满值，因此需要除以 100 后转换为 sRGB
rgb = colour.XYZ_to_sRGB(XYZ / 100)
rgb = np.clip(rgb, 0, 1)  # 限制在 [0, 1] 范围内

# 定义辅助函数，将 sRGB 数值转换为 16 进制颜色代码
def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]*255),
                                        int(rgb[1]*255),
                                        int(rgb[2]*255))

hex_color = rgb_to_hex(rgb)
print("计算得到的颜色:", hex_color)
print("sRGB 数值:", rgb)

# 7. 可视化显示计算得到的颜色
plt.figure(figsize=(2, 2))
plt.imshow([[rgb]])
plt.axis('off')
plt.title("Calculated Color")
plt.show()





