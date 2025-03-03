import os
import cv2
import numpy as np
from PIL import Image
import math

def remove_bubbles(image_path):
    # 读取图片并转换为灰度图
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 使用Canny边缘检测找到边缘
    edges = cv2.Canny(gray, threshold1=50, threshold2=150)

    # 进行形态学操作，膨胀然后腐蚀，增强边缘
    kernel = np.ones((5, 5), np.uint8)
    edges_dilated = cv2.dilate(edges, kernel, iterations=2)
    edges_eroded = cv2.erode(edges_dilated, kernel, iterations=2)

    # 找到轮廓
    contours, _ = cv2.findContours(edges_eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 遮盖气泡区域
    for contour in contours:
        # 过滤掉面积太小或太大的轮廓
        area = cv2.contourArea(contour)
        if 100 < area < 10000:  # 根据实际情况调整气泡大小的范围
            # 画出轮廓并填充
            cv2.drawContours(img, [contour], -1, (0, 0, 0), thickness=cv2.FILLED)

    # 返回遮盖气泡后的图片
    return img

def calculate_average_hue_without_black(image_path, brightness_threshold=0.1):
    # 移除气泡
    img = remove_bubbles(image_path)

    # 将处理后的图片转换为 HSV 色彩空间
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 分离 HSV 三个通道：H, S, V
    h_channel, s_channel, v_channel = cv2.split(hsv_img)

    # 准备两个变量来存储色相的向量和
    sum_x = 0
    sum_y = 0

    # 遍历每个像素，检查亮度并过滤黑色像素
    for i in range(hsv_img.shape[0]):
        for j in range(hsv_img.shape[1]):
            # 亮度 (V) 通道的值归一化到 [0, 1]，并过滤低亮度的黑色区域
            v_value = v_channel[i, j] / 255.0
            
            if v_value >= brightness_threshold:
                # 只计算有效像素的色相（H 通道已经是以色环的度数[0, 180]表示，需要乘2转换到[0, 360]）
                hue = h_channel[i, j] * 2
                
                # 将色相转换为向量 (x, y) 的形式
                angle_rad = math.radians(hue)
                sum_x += math.cos(angle_rad)
                sum_y += math.sin(angle_rad)

    if sum_x == 0 and sum_y == 0:
        return None

    # 计算向量的平均角度
    average_hue_rad = math.atan2(sum_y, sum_x)
    
    # 将弧度转换回色相的度数（范围为 0-360）
    average_hue_deg = math.degrees(average_hue_rad)
    if average_hue_deg < 0:
        average_hue_deg += 360

    return average_hue_deg

def process_images_in_folder(folder_path, brightness_threshold=0.1):
    print(f"\nProcessing folder: {folder_path}")
    for filename in os.listdir(folder_path):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            image_path = os.path.join(folder_path, filename)
            try:
                average_hue = calculate_average_hue_without_black(image_path, brightness_threshold)
                if average_hue is not None:
                    print(f"Image: {filename}, Average Hue (without black and bubbles): {average_hue:.2f}")
                else:
                    print(f"Image: {filename}, no valid pixels (after black removal and bubble masking).")
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