import numpy as np
from scipy.optimize import fsolve

# 数据 (波长 nm 和反射率 Y)
data = {
    1000: 0.977314,
    727.273: 0.960749,
    571.429: 0.950106,
    470.588: 0.918401,
    400: 0.817267
}

# 环境介质折射率
n_env = 1.0

# 定义方程组
def equations(params, R, n_env):
    n, k = params
    numerator = (n - n_env)**2 + k**2
    denominator = (n + n_env)**2 + k**2
    return [
        R - numerator / denominator,
        0  # 此处补充一个恒为 0 的伪方程，用于使返回值形状匹配
    ]

# 数值求解
results = {}
for wavelength, reflectance in data.items():
    # 初始猜测值 (n 和 k)
    initial_guess = (0.2, 3.0)
    solution = fsolve(equations, initial_guess, args=(reflectance, n_env))
    results[wavelength] = solution

# 输出结果
print("Wavelength (nm), n, k")
for wavelength, (n, k) in results.items():
    print(f"{wavelength:.3f}, {n:.6f}, {k:.6f}")