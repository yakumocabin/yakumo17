import numpy as np
import matplotlib.pyplot as plt

# 常量
c = 3e8  # 光速 (m/s)
wp = 1.39e16  # 等离子体频率 (rad/s)
gamma = 2.73e13  # 阻尼频率 (rad/s)

# Drude 模型参数
def silver_dielectric_constant(wavelength_nm):
    """通过 Drude 模型计算银的复介电常数，直接使用 nm 单位"""
    omega = 2 * np.pi * c / (wavelength_nm * 1e-9)  # 使用 nm 单位计算角频率
    epsilon_real = 1 - (wp**2 / (omega**2 + gamma**2))
    epsilon_imag = (wp**2 * gamma) / (omega**3 + omega * gamma**2)
    return epsilon_real + 1j * epsilon_imag

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
wavelengths_nm = np.linspace(300, 800, 500)  # 波长范围 (nm)
theta_inc = 0  # 垂直入射
n_env = 1.33  # 周围环境介质折射率 (例如水)

# 计算反射率
reflectance = []
for wavelength_nm in wavelengths_nm:
    epsilon_ag = silver_dielectric_constant(wavelength_nm)
    n_ag = np.sqrt(epsilon_ag)  # 银的复折射率
    reflectance.append(fresnel_reflectance(n_env, n_ag, theta_inc))

# 绘制反射光谱
plt.figure(figsize=(8, 6))
plt.plot(wavelengths_nm, reflectance, label=f"n_env = {n_env}")
plt.xlabel("Wavelength (nm)")
plt.ylabel("Reflectance")
plt.title("Reflectance Spectrum of Silver Plane")
plt.grid(True)
plt.legend()
plt.show()