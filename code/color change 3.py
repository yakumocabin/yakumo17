import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import colour  # 需要先安装： pip install colour-science

# =============================================================================
# 自定义包装类：用于为插值提供采样区间信息
# =============================================================================
class SliceWrapper:
    def __init__(self, start, stop, step):
        self.start = start      # 起始波长
        self.stop = stop        # 终止波长（不包含该值）
        self.step = step        # 步长
        self.end = stop         # end 属性，等同于 stop
        self._interval = step   # interval 属性等于步长

    @property
    def interval(self):
        return self._interval

    def __iter__(self):
        # 返回规则采样的波长序列
        return iter(np.arange(self.start, self.stop, self.step))

# =============================================================================
# 辅助函数：颜色格式转换（用于可视化时将 XYZ 转换到 sRGB 并得到十六进制颜色）
# =============================================================================
def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]*255),
                                        int(rgb[1]*255),
                                        int(rgb[2]*255))

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return np.array([r, g, b])

# =============================================================================
# 1. 从 Excel 读取光谱数据
# =============================================================================
# 假设 Excel 文件 "reflectance.xlsx" 的 Sheet2 中含有 "Wavelength" 和 "Reflectance" 两列
df = pd.read_excel('reflectance.xlsx', sheet_name='Sheet2')
df.columns = df.columns.str.strip()  # 去除列名两端可能的空格

# 将数据转换为浮点型数组
wavelengths = df['Wavelength'].astype(float).values
reflectance = df['Reflectance'].astype(float).values

# 构造字典：{波长: 反射率, ...}
spectrum_data = dict(zip(wavelengths, reflectance))

# =============================================================================
# 2. 创建 SpectralDistribution 对象并重采样
# =============================================================================
sd = colour.SpectralDistribution(spectrum_data)

# 为了满足 ASTM E308-15 要求采样间隔为 1, 5, 10 或 20 nm，
# 这里使用自定义包装类以 5nm 为间隔插值（请根据数据实际情况调整）
regular_wavelengths = SliceWrapper(380, 781, 5)  # 从 380nm 到 780nm，步长 5nm
sd = sd.interpolate(regular_wavelengths)

# =============================================================================
# 3. 利用光谱数据计算 CIE XYZ 值，并转换为 CIELab
# =============================================================================
# 采用标准 illuminant D65（日光），内部使用 CIE 1931 2° 标准观察者数据
illuminant = colour.SDS_ILLUMINANTS['D65']
XYZ = colour.sd_to_XYZ(sd, illuminant=illuminant)
# 注意：sd_to_XYZ 得到的 XYZ 通常以 100 为满值

# 获取 D65 白点（新版使用 CCS_ILLUMINANTS）
whitepoint = colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer']['D65']

# 将 XYZ 转换为 CIELab
Lab = colour.XYZ_to_Lab(XYZ, illuminant=whitepoint)
print("CIELab 值:", Lab)  # Lab = [L*, a*, b*]

# =============================================================================
# 4. 计算 Hue 值
# =============================================================================
# 方法1：手动计算 Hue（单位：度），公式：h = atan2(b*, a*)
L_val, a_val, b_val = Lab
hue_rad = math.atan2(b_val, a_val)  # 得到弧度
hue_deg_manual = math.degrees(hue_rad)
if hue_deg_manual < 0:
    hue_deg_manual += 360  # 保证 hue 在 0~360 度之间
print("Hue（手动计算）: {:.2f}°".format(hue_deg_manual))

# 方法2：利用 colour 库将 Lab 转换为 LCHab，返回值中的第三个分量为 hue
LCH = colour.Lab_to_LCHab(Lab)  # 返回 [L*, C*, h°]
hue_deg_lch = LCH[2]
print("Hue（Lab->LCH转换）: {:.2f}°".format(hue_deg_lch))

# =============================================================================
# 5. （可选）将 CIE 颜色转换为 sRGB 以便可视化显示
# =============================================================================
rgb = colour.XYZ_to_sRGB(XYZ / 100)  # 将 XYZ 归一化至 [0, 1]
rgb = np.clip(rgb, 0, 1)  # 限制 sRGB 数值在 [0, 1]
hex_color = rgb_to_hex(rgb)
print("对应的 sRGB 十六进制颜色:", hex_color)

plt.figure(figsize=(2, 2))
plt.imshow([[rgb]])
plt.axis('off')
plt.title("Calculated Color")
plt.show()






