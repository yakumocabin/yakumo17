import os
from PIL import Image
import numpy as np

def calculate_average_hue_without_black(image_path, brightness_threshold=0.3):
    # 打开图片并转换为RGB模式
    img = Image.open(image_path).convert('RGB')
    
    # 转换为 NumPy 数组
    img_np = np.array(img)
    
    # 初始化HSV图像
    hsv_img = np.zeros_like(img_np, dtype=np.float32)
    
    # 准备一个列表来存储有效的色相值（去除黑色区域）
    hue_values = []
    
    # 遍历每个像素，转换为HSV，过滤掉黑色像素
    for i in range(img_np.shape[0]):
        for j in range(img_np.shape[1]):
            r, g, b = img_np[i, j] / 255.0
            max_val = max(r, g, b)
            min_val = min(r, g, b)
            delta = max_val - min_val
            
            # 计算亮度（V）
            value = max_val
            
            # 如果亮度太低，跳过此像素（即认为是黑色）
            if value < brightness_threshold:
                continue
            
            # 计算色相（Hue）
            if delta == 0:
                hue = 0
            elif max_val == r:
                hue = (g - b) / delta
            elif max_val == g:
                hue = (b - r) / delta + 2
            else:
                hue = (r - g) / delta + 4
                
            hue = hue * 60
            if hue < 0:
                hue += 360
            
            # 将有效的色相值存入列表
            hue_values.append(hue)
    
    # 如果没有有效的色相值，返回 None
    if len(hue_values) == 0:
        return None
    
    # 计算剩余像素的平均色相
    average_hue = np.mean(hue_values)
    return average_hue

def process_images_in_folder(folder_path, brightness_threshold=0.1):
    print(f"\nProcessing folder: {folder_path}")
    for filename in os.listdir(folder_path):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            image_path = os.path.join(folder_path, filename)
            try:
                average_hue = calculate_average_hue_without_black(image_path, brightness_threshold)
                if average_hue is not None:
                    print(f"Image: {filename}, Average Hue (without black): {average_hue:.2f}")
                else:
                    print(f"Image: {filename}, no valid pixels (after black removal).")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

def process_multiple_folders(base_folder_path, brightness_threshold=0.1):
    # 遍历所有子文件夹
    for root, dirs, files in os.walk(base_folder_path):
        if files:  # 如果当前文件夹有文件，处理图片
            process_images_in_folder(root, brightness_threshold)

# 指定包含多个文件夹的根文件夹路径
base_folder_path = "D:\Research"
process_multiple_folders(base_folder_path)