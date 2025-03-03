import os
import cv2 # type: ignore
import numpy as np
from PIL import Image

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

def calculate_average_hue_lab(image_path, brightness_threshold=20):
    # 移除气泡
    img = remove_bubbles(image_path)

    # 将处理后的图片转换为 CIELAB 颜色空间
    lab_img = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

    # 分离 LAB 通道
    L, A, B = cv2.split(lab_img)

    # 创建掩码，去除亮度 L* 低于阈值的像素
    mask = L > brightness_threshold

    # 仅保留有效像素
    A_valid = A[mask]
    B_valid = B[mask]

    # 如果没有有效像素，返回 None
    if len(A_valid) == 0:
        return None

    # 计算色相 (Hue) 值
    hue_values = np.arctan2(B_valid, A_valid)  # 色相角度 (弧度)

    # 将弧度转换为角度 (0° - 360°)
    hue_degrees = np.degrees(hue_values)
    hue_degrees = np.mod(hue_degrees, 360)

    # 计算有效像素的平均色相值
    average_hue = np.mean(hue_degrees)

    return average_hue

def process_images_in_folder(folder_path, brightness_threshold=20):
    print(f"\nProcessing folder: {folder_path}")
    for filename in os.listdir(folder_path):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            image_path = os.path.join(folder_path, filename)
            try:
                average_hue = calculate_average_hue_lab(image_path, brightness_threshold)
                if average_hue is not None:
                    print(f"Image: {filename}, Average Hue (CIELAB, without black and bubbles): {average_hue:.2f}°")
                else:
                    print(f"Image: {filename}, no valid pixels (after black removal and bubble masking).")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

def process_multiple_folders(base_folder_path, brightness_threshold=20):
    # 遍历所有子文件夹
    for root, dirs, files in os.walk(base_folder_path):
        if files:  # 如果当前文件夹有文件，处理图片
            process_images_in_folder(root, brightness_threshold)

# 指定包含多个文件夹的根文件夹路径
base_folder_path = "D:\Research"
process_multiple_folders(base_folder_path)