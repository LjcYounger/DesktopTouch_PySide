import numpy as np
from PySide6.QtGui import QImage, QPixmap, QPainter
from PySide6.QtCore import Qt

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
    
    # 创建存储切片的列表
    slices = []
    
    # 按1像素宽度逐个切割
    for x in range(width):
        slice_img = image.copy(x, 0, 1, height)
        slices.append(slice_img)
    
    return slices

def repeat_vertical_strip_horizontally(image: QPixmap, length: int) -> QPixmap:
    """
    将竖条窄图像横向复制指定次数
    
    Args:
        image (QPixmap): 输入的竖条图像
        length (int): 复制次数，也是输出图像的最终宽度
        
    Returns:
        QPixmap: 横向重复后的图像
    """
    
    # 将QPixmap转换为QImage以便处理
    img = image.toImage()
    
    # 确保图像是Format_ARGB32格式
    if img.format() != QImage.Format.Format_ARGB32:
        img = img.convertToFormat(QImage.Format.Format_ARGB32)
    
    width = img.width()
    height = img.height()
    
    # 创建结果图像
    result_img = QImage(length, height, QImage.Format.Format_ARGB32)
    result_img.fill(Qt.GlobalColor.transparent)  # 填充透明背景
    
    # 使用 QPainter 进行高效的图像复制
    painter = QPainter(result_img)
    for i in range(length):
        x_offset = i * width
        painter.drawImage(x_offset, 0, img)
    painter.end()
    
    return QPixmap.fromImage(result_img)

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
    
    # 将QImage转换为numpy数组
    width = image.width()
    height = image.height()
    
    # 使用memoryview获取图像数据
    ptr = image.bits()
    img_array = np.frombuffer(ptr, dtype=np.uint8)
    img_array = img_array.reshape((height, width, 4))  # ARGB格式
    
    # 提取灰度值（假设RGB相同，取其中一个通道）
    gray_values = img_array[:, :, 1].astype(np.float32)  # Green channel
    
    # 处理灰度反转
    if invert_grayscale:
        gray_values = 255 - gray_values
    
    # 归一化灰度值
    gray_normalized = gray_values / 255.0
    
    # 解包目标颜色
    target_r, target_g, target_b = color
    
    # 如果grayscale_image_transparent为True，则直接替换RGB值
    if grayscale_image_transparent:
        new_r = (target_r * gray_normalized).astype(np.uint8)
        new_g = (target_g * gray_normalized).astype(np.uint8)
        new_b = (target_b * gray_normalized).astype(np.uint8)
        new_a = img_array[:, :, 3]  # 保留原始Alpha通道
    else:
        # 计算新的RGB值
        new_r = (target_r * gray_normalized).astype(np.uint8)
        new_g = (target_g * gray_normalized).astype(np.uint8)
        new_b = (target_b * gray_normalized).astype(np.uint8)
        
        # 计算新的Alpha值
        new_a = (alpha * gray_values / impact_on_transparency).astype(np.uint8)
        new_a = np.clip(new_a, 0, 255)  # 限制在0-255范围内
    
    # 组合成新的ARGB图像数组（注意Qt使用BGRA顺序）
    result_array = np.stack([new_b, new_g, new_r, new_a], axis=2)
    
    # 创建新的QImage
    result_image = QImage(result_array.data, width, height, QImage.Format.Format_ARGB32)
    # 确保数据独立，避免内存释放问题
    result_image = result_image.copy()
    
    return QPixmap.fromImage(result_image)
