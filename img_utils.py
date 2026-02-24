import numpy as np
from PySide6.QtGui import QImage, QPixmap, QPainter
from PySide6.QtCore import Qt
from functools import lru_cache
from typing import Tuple

# 缓存常用颜色转换结果
@lru_cache(maxsize=128)
def _get_color_multiplier(color: Tuple[int, int, int]) -> np.ndarray:
    """缓存颜色乘数计算"""
    return np.array(color, dtype=np.float32) / 255.0

def load_grayscale_image(image_path: str) -> QImage:
    return QImage(image_path)

def split_image_vertically(image: QImage) -> tuple[QImage, QImage]:
    """
    将QImage从中间竖直对半切割
    
    Args:
        image (QImage): 输入的图像
        
    Returns:
        tuple[QImage, QImage]: 包含左半部分和右半部分的元组
    """
    width = image.width()
    height = image.height()
    
    # 计算中间位置
    mid_x = width // 2
    
    # 切割左半部分
    left_image = image.copy(0, 0, mid_x, height)
    
    # 切割右半部分
    right_image = image.copy(mid_x, 0, width - mid_x, height)
    
    return (left_image, right_image)

def slice_image_vertically(image: QImage) -> list[QImage]:
    """
    将QImage按1像素宽度竖直切片
    
    Args:
        image (QImage): 输入的图像
        
    Returns:
        list[QImage]: 包含所有1像素宽竖直切片的列表
    """
    width = image.width()
    height = image.height()
    
    # 预分配列表大小以提高性能
    slices = [None] * width
    
    # 按1像素宽度逐个切割
    for x in range(width):
        slices[x] = image.copy(x, 0, 1, height)
    
    return slices

def change_image_by_grayscale(image: QImage, 
                              color: tuple, 
                              alpha: int, 
                              grayscale_image_transparent: bool=False,
                              impact_on_transparency: int=255, 
                              invert_grayscale: bool=False):
    """
    将灰度图像转换为指定颜色和透明度的彩色图像（使用numpy优化）
    
    Args:
        image (QImage): 输入的灰度图像
        color (tuple): 目标RGB颜色值 (r, g, b)
        alpha (int): 透明度值 (0-255)
        grayscale_image_transparent (bool): 输入的灰度图是否背景透明
        impact_on_transparency (int): 透明度影响因子 (0-255)
        invert_grayscale (bool): 是否反转灰度值
        
    Returns:
        QPixmap: 转换后的彩色图像
    """
    # 确保图像是Format_ARGB32格式
    if image.format() != QImage.Format.Format_ARGB32:
        image = image.convertToFormat(QImage.Format.Format_ARGB32)
    
    # 获取图像尺寸
    width = image.width()
    height = image.height()
    
    # 使用memoryview获取图像数据
    ptr = image.constBits()  # 使用constBits避免修改原图像
    img_array = np.frombuffer(ptr, dtype=np.uint8)
    img_array = img_array.reshape((height, width, 4))  # ARGB格式
    
    # 提取灰度值（假设RGB相同，取其中一个通道）
    gray_values = img_array[:, :, 1].astype(np.float32)  # Green channel
    
    # 处理灰度反转
    if invert_grayscale:
        gray_values = 255 - gray_values
    
    # 归一化灰度值
    gray_normalized = gray_values / 255.0
    
    # 获取预计算的颜色乘数
    color_multiplier = _get_color_multiplier(color)
    target_r, target_g, target_b = color_multiplier * 255
    
    # 预分配结果数组
    result_array = np.empty((height, width, 4), dtype=np.uint8)
    
    # 向量化计算RGB值
    result_array[:, :, 2] = (target_r * gray_normalized).astype(np.uint8)  # R
    result_array[:, :, 1] = (target_g * gray_normalized).astype(np.uint8)  # G
    result_array[:, :, 0] = (target_b * gray_normalized).astype(np.uint8)  # B
    
    # 处理Alpha通道
    if grayscale_image_transparent:
        # 保留原始Alpha通道
        result_array[:, :, 3] = img_array[:, :, 3]
    else:
        # 计算新的Alpha值
        alpha_factor = alpha / impact_on_transparency
        new_alpha = (alpha_factor * gray_values).astype(np.uint8)
        result_array[:, :, 3] = np.clip(new_alpha, 0, 255)
    
    # 创建新的QImage（使用副本确保数据独立性）
    result_image = QImage(result_array.data, width, height, 
                         width * 4, QImage.Format.Format_ARGB32)
    
    # 创建独立副本避免内存问题
    final_image = result_image.copy()
    
    return QPixmap.fromImage(final_image)