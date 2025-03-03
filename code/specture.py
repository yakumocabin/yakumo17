import numpy as np
import matplotlib.pyplot as plt

# 实验数据（波长 nm 对应的 n 和 k 值）
experimental_data = {
    400.000: (0.516164, 3.000000),
    470.588: (0.213645, 3.000000),
    571.429: (0.128136, 3.000000),
    727.273: (0.100192, 3.000000),
    1000.000: (0.057385, 3.000000),
}

# 插值折射率函数
def interpolate_refractive_index(wavelength_nm):
    """根据实验数据插值计算特定波长下的复折射率"""
    wavelengths = np.array(list(experimental_data.keys()))
    n_values = np.array([val[0] for val in experimental_data.values()])
    k_values = np.array([val[1] for val in experimental_data.values()])
    
    # 插值 n 和 k
    n = np.interp(wavelength_nm, wavelengths, n_values)
    k = np.interp(wavelength_nm, wavelengths, k_values)
    return n + 1j * k

def fresnel_reflectance(n1, n2, theta_inc):
    """计算菲涅耳反射率"""
    theta_inc_rad = np.radians(theta_inc)
    cos_theta_t = np.sqrt(1 - (n1 / n2 * np.sin(theta_inc_rad))**2)
    r_s = (n1 * np.cos(theta_inc_rad) - n2 * cos_theta_t) / \
          (n1 * np.cos(theta_inc_rad) + n2 * cos_theta_t)
    r_p = (n2 * np.cos(theta_inc_rad) - n1 * cos_theta_t) / \
          (n2 * np.cos(theta_inc_rad) + n1 * cos_theta_t)
    return (np.abs(r_s)**2 + np.abs(r_p)**2) / 2

# 设置波长范围和入射角
wavelengths_nm = np.linspace(400, 800, 500)  # 波长范围 (nm)
theta_inc = 0  # 垂直入射
n_env = 1  # 环境折射率（空气）

# 计算反射率
reflectance = []
for wavelength_nm in wavelengths_nm:
    n_ag = interpolate_refractive_index(wavelength_nm)  # 银的复折射率
    reflectance.append(fresnel_reflectance(n_env, n_ag, theta_inc))

# 绘制反射光谱
plt.figure(figsize=(8, 6))
plt.plot(wavelengths_nm, reflectance, label="Reflectance (Experimental Data)")
plt.xlabel("Wavelength (nm)")
plt.ylabel("Reflectance")
plt.title("Reflectance Spectrum of Silver Plane (400-800 nm)")
plt.grid(True)
plt.legend()
plt.show()

