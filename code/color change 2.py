import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import colour
import tkinter as tk
from tkinter import filedialog

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

# =============================================================================
# 选择 Excel 文件
# =============================================================================
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(title="请选择 Excel 文件",
                                       filetypes=[("Excel 文件", "*.xlsx;*.xls")])

if not file_path:
    print("⚠️ 未选择文件，程序退出。")
    exit()

# 需要处理的 sheet 名称
sheet_names = ["1.0", "1.1", "1.2", "1.3", "1.4"]

# 结果存储字典
results = {}

# 读取 Excel 文件的多个 sheet
for sheet in sheet_names:
    try:
        df = pd.read_excel(file_path, sheet_name=sheet)
        df.columns = df.columns.str.strip()  # 去除列名空格

        if "Wavelength" not in df.columns or "Reflectance" not in df.columns:
            print(f"⚠️ {sheet} 缺少必要的列，跳过处理。")
            continue

        # 转换数据格式
        wavelengths = df["Wavelength"].astype(float).values
        reflectance = df["Reflectance"].astype(float).values

        # 组织光谱数据
        spectrum_data = dict(zip(wavelengths, reflectance))

        # 创建 SpectralDistribution 并插值
        sd = colour.SpectralDistribution(spectrum_data)
        regular_wavelengths = SliceWrapper(380, 781, 5)  # 5nm 采样
        sd = sd.interpolate(regular_wavelengths)

        # 计算 CIE XYZ 值
        illuminant = colour.SDS_ILLUMINANTS["D65"]
        XYZ = colour.sd_to_XYZ(sd, illuminant=illuminant)

        # 获取 D65 白点
        whitepoint = colour.CCS_ILLUMINANTS["CIE 1931 2 Degree Standard Observer"]["D65"]

        # 计算 CIELab
        Lab = colour.XYZ_to_Lab(XYZ, illuminant=whitepoint)

        # 计算 Hue（手动计算和 LCH 转换）
        L_val, a_val, b_val = Lab
        hue_rad = math.atan2(b_val, a_val)
        hue_deg_manual = math.degrees(hue_rad)
        if hue_deg_manual < 0:
            hue_deg_manual += 360  # 确保 hue 在 0~360 之间
        LCH = colour.Lab_to_LCHab(Lab)
        hue_deg_lch = LCH[2]

        # 计算 sRGB 颜色
        rgb = colour.XYZ_to_sRGB(XYZ / 100)  # 归一化
        rgb = np.clip(rgb, 0, 1)  # 限制范围 [0,1]
        hex_color = rgb_to_hex(rgb)

        # 存储结果
        results[sheet] = {
            "CIELab": Lab,
            "Hue (Manual)": hue_deg_manual,
            "Hue (LCH)": hue_deg_lch,
            "sRGB": rgb,
            "Hex Color": hex_color
        }

    except Exception as e:
        print(f"❌ 读取 {sheet} 时发生错误: {e}")

# =============================================================================
# 输出计算结果
# =============================================================================
for sheet, data in results.items():
    print(f"\n--- {sheet} 计算结果 ---")
    print(f"CIELab: {data['CIELab']}")
    print(f"Hue (手动计算): {data['Hue (Manual)']:.2f}°")
    print(f"Hue (LCH转换): {data['Hue (LCH)']:.2f}°")
    print(f"sRGB 颜色: {data['sRGB']}")
    print(f"十六进制颜色: {data['Hex Color']}")

# =============================================================================
# 单独为每个 Sheet 生成一个颜色图像
# =============================================================================
for sheet, data in results.items():
    plt.figure(figsize=(2, 2))  # 每个颜色单独一张图
    color = np.array([[data["sRGB"]]])  # 变成 (1,1,3) 数组
    plt.imshow(color)
    plt.axis("off")
    plt.title(sheet)

    # 可选：将颜色图片保存到本地
    save_path = f"{sheet}_color.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"🎨 {sheet} 的颜色已保存为 {save_path}")

    plt.show()
