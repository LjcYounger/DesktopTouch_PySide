import numpy as np
from PySide6.QtGui import QImage, QPixmap

def load_grayscale_image(image_path: str) -> QImage:
    return QImage(image_path)

def change_image_by_grayscale(image: QImage, 
                              color: tuple, 
                              alpha: int, 
                              impact_on_transparency: int=255, 
                              invert_grayscale: bool=False):
    """
    将灰度图像转换为指定颜色和透明度的彩色图像（使用numpy优化）
    
    Args:
        image (QImage): 输入的灰度图像
        color (tuple): 目标RGB颜色值 (r, g, b)
        alpha (int): 透明度值 (0-255)
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